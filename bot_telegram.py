"""Panel seguro de Telegram para controlar los servicios HL7.

El bot no acepta comandos de shell desde Telegram. Solo ejecuta los scripts
locales que están definidos en SERVICES y únicamente para usuarios autorizados.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from dataclasses import dataclass
from html import escape
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


ROOT = Path(__file__).resolve().parent
START_SCRIPT = ROOT / "iniciar_servidores_hl7.sh"
STOP_SCRIPT = ROOT / "detener_servidores_hl7.sh"
ADMINS_FILE = ROOT / "telegram_admins.json"


@dataclass(frozen=True)
class Service:
    key: str
    name: str
    log: Path


SERVICES = (
    Service("mdm", "Servidor MDM", ROOT / "logs/mdm_servidor.log"),
    Service("orm", "Cliente ORM", ROOT / "logs/orm_cliente.log"),
)


def load_settings() -> tuple[str, set[int]]:
    load_dotenv(ROOT / ".env")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    raw_ids = os.getenv("TELEGRAM_ADMIN_IDS", "")
    try:
        admin_ids = {int(value.strip()) for value in raw_ids.split(",") if value.strip()}
    except ValueError as exc:
        raise RuntimeError("TELEGRAM_ADMIN_IDS debe contener IDs numéricos separados por coma") from exc
    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en .env")
    if not admin_ids:
        raise RuntimeError("Falta TELEGRAM_ADMIN_IDS en .env")
    if ADMINS_FILE.exists():
        try:
            saved_ids = json.loads(ADMINS_FILE.read_text(encoding="utf-8"))
            admin_ids.update(int(value) for value in saved_ids)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"No se pudo leer {ADMINS_FILE.name}") from exc
    return token, admin_ids


def save_admin_ids(admin_ids: set[int]) -> None:
    ADMINS_FILE.write_text(
        json.dumps(sorted(admin_ids), indent=2) + "\n", encoding="utf-8"
    )


def authorized(update: Update, admin_ids: set[int]) -> bool:
    user = update.effective_user
    return bool(user and user.id in admin_ids)


async def run_command(*args: str, timeout: int = 45) -> tuple[int, str]:
    """Ejecuta un comando fijo sin usar shell y devuelve código + salida."""
    process = await asyncio.create_subprocess_exec(
        *args,
        cwd=ROOT,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        return 124, "La operación excedió el tiempo límite."
    return process.returncode or 0, stdout.decode("utf-8", errors="replace")


async def service_status(service: Service) -> bool:
    if service.key == "mdm":
        if not shutil.which("lsof"):
            return False
        code, _ = await run_command("lsof", "-Pi", ":2590", "-sTCP:LISTEN", "-t", timeout=10)
        return code == 0
    if not shutil.which("pgrep"):
        return False
    code, _ = await run_command("pgrep", "-f", "orm/orm_cliente_envio.py", timeout=10)
    return code == 0


async def all_status() -> dict[str, bool]:
    values = await asyncio.gather(*(service_status(service) for service in SERVICES))
    return {service.key: value for service, value in zip(SERVICES, values)}


def status_icon(active: bool) -> str:
    return "🟢 ACTIVO" if active else "🔴 DETENIDO"


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("▶️ Iniciar HL7", callback_data="confirm:start"),
                InlineKeyboardButton("⏹️ Detener HL7", callback_data="confirm:stop"),
            ],
            [
                InlineKeyboardButton("🔄 Reiniciar HL7", callback_data="confirm:restart"),
                InlineKeyboardButton("📊 Actualizar", callback_data="refresh"),
            ],
            [InlineKeyboardButton("📜 Ver logs", callback_data="logs")],
            [InlineKeyboardButton("👥 Administrar usuarios", callback_data="users")],
        ]
    )


async def panel_text() -> str:
    statuses = await all_status()
    lines = ["🖥️ <b>Panel de servicios HL7</b>", "", "Estado actual:"]
    for service in SERVICES:
        lines.append(f"{status_icon(statuses[service.key])}  <b>{service.name}</b>")
    lines.extend(["", "Selecciona una acción:"])
    return "\n".join(lines)


async def show_panel(update: Update, *, edit: bool = False) -> None:
    text = await panel_text()
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard()
        )
    elif update.effective_message:
        await update.effective_message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard()
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update, context.bot_data["admin_ids"]):
        if update.effective_message:
            await update.effective_message.reply_text("⛔ No tienes autorización para usar este panel.")
        return
    await show_panel(update)


def users_keyboard(admin_ids: set[int]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton("➕ Agregar usuario", callback_data="users:add")]]
    for user_id in sorted(admin_ids):
        rows.append([
            InlineKeyboardButton(f"🗑️ Quitar {user_id}", callback_data=f"users:remove:{user_id}")
        ])
    rows.append([InlineKeyboardButton("⬅️ Volver al panel", callback_data="refresh")])
    return InlineKeyboardMarkup(rows)


async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    admin_ids = context.bot_data["admin_ids"]
    text = (
        "👥 <b>Usuarios autorizados</b>\n\n"
        + "\n".join(f"• <code>{user_id}</code>" for user_id in sorted(admin_ids))
        + "\n\nPuedes agregar o quitar accesos."
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.HTML, reply_markup=users_keyboard(admin_ids)
    )


async def receive_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recibe un ID solo después de que un administrador pulse Agregar."""
    if not context.user_data.pop("awaiting_user_id", False):
        return
    if not authorized(update, context.bot_data["admin_ids"]):
        return
    raw_id = (update.effective_message.text or "").strip()
    if not raw_id.isdigit():
        await update.effective_message.reply_text(
            "❌ ID inválido. Envía únicamente el número de ID de Telegram."
        )
        context.user_data["awaiting_user_id"] = True
        return
    user_id = int(raw_id)
    if user_id <= 0:
        await update.effective_message.reply_text("❌ El ID debe ser un número positivo.")
        context.user_data["awaiting_user_id"] = True
        return
    admin_ids = context.bot_data["admin_ids"]
    admin_ids.add(user_id)
    save_admin_ids(admin_ids)
    await update.effective_message.reply_text(
        f"✅ Usuario <code>{user_id}</code> autorizado.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )


def confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"run:{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
            ]
        ]
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    if not authorized(update, context.bot_data["admin_ids"]):
        await query.edit_message_text("⛔ No tienes autorización para usar este panel.")
        return

    action = query.data or ""
    if action == "refresh":
        await show_panel(update, edit=True)
        return
    if action == "users":
        await show_users(update, context)
        return
    if action == "users:add":
        context.user_data["awaiting_user_id"] = True
        await query.edit_message_text(
            "➕ <b>Agregar usuario</b>\n\nEnvía ahora su ID numérico de Telegram.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Cancelar", callback_data="users")]]
            ),
        )
        return
    if action.startswith("users:remove:"):
        user_id = int(action.rsplit(":", 1)[1])
        admin_ids = context.bot_data["admin_ids"]
        if user_id == update.effective_user.id and len(admin_ids) == 1:
            await query.answer("No puedes quitar al único administrador.", show_alert=True)
            return
        admin_ids.discard(user_id)
        save_admin_ids(admin_ids)
        await show_users(update, context)
        return
    if action == "cancel":
        await show_panel(update, edit=True)
        return
    if action.startswith("confirm:"):
        requested = action.split(":", 1)[1]
        labels = {"start": "iniciar", "stop": "detener", "restart": "reiniciar"}
        await query.edit_message_text(
            f"⚠️ ¿Confirmas <b>{labels[requested]}</b> los servicios HL7?",
            parse_mode=ParseMode.HTML,
            reply_markup=confirmation_keyboard(requested),
        )
        return
    if action.startswith("run:"):
        operation = action.split(":", 1)[1]
        await query.edit_message_text(f"⏳ Ejecutando <b>{operation}</b> HL7...", parse_mode=ParseMode.HTML)
        if operation == "start":
            code, output = await run_command("bash", str(START_SCRIPT))
        elif operation == "stop":
            code, output = await run_command("bash", str(STOP_SCRIPT))
        elif operation == "restart":
            stop_code, stop_output = await run_command("bash", str(STOP_SCRIPT))
            if stop_code != 0:
                code, output = stop_code, stop_output
            else:
                code, output = await run_command("bash", str(START_SCRIPT))
        else:
            return
        result = "✅ Operación completada" if code == 0 else f"❌ Operación fallida (código {code})"
        tail = escape(output.strip()[-2500:] or "Sin salida del script.")
        await query.edit_message_text(
            f"{result}\n\n<pre>{tail}</pre>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📊 Ver estado", callback_data="refresh")]]
            ),
        )
        return
    if action == "logs":
        chunks = ["📜 <b>Últimas líneas de logs</b>"]
        for service in SERVICES:
            if service.log.exists():
                content = service.log.read_text(encoding="utf-8", errors="replace").splitlines()[-8:]
                log_tail = escape("\n".join(content) or "Sin contenido")
                chunks.append(f"\n<b>{escape(service.name)}</b>\n<pre>{log_tail}</pre>")
            else:
                chunks.append(f"\n<b>{service.name}</b>\n<pre>Log todavía no creado.</pre>")
        await query.edit_message_text(
            "".join(chunks)[-3900:],
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Volver al panel", callback_data="refresh")]]
            ),
        )


def build_application() -> Application:
    token, admin_ids = load_settings()
    application = ApplicationBuilder().token(token).build()
    application.bot_data["admin_ids"] = admin_ids
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_id))
    application.add_handler(CallbackQueryHandler(button))
    return application


if __name__ == "__main__":
    build_application().run_polling(allowed_updates=Update.ALL_TYPES)
