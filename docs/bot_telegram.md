# Panel de control HL7 por Telegram

El bot está en `bot_telegram.py`. Presenta botones inline para consultar el
estado de MDM y ORM, iniciar/detener/reiniciar los servicios y ver las últimas
líneas de sus logs.

## Configuración

1. Crea un bot con `@BotFather` y obtén el token.
2. Obtén tu ID numérico de Telegram con un bot como `@userinfobot`.
3. Copia `.env.example` a `.env` y completa:

```env
TELEGRAM_BOT_TOKEN=token_entregado_por_BotFather
TELEGRAM_ADMIN_IDS=123456789
```

Se pueden agregar varios administradores separados por coma. El archivo `.env`
está excluido de Git.

## Agregar usuarios desde Telegram

Desde el panel, pulsa `👥 Administrar usuarios` y después `➕ Agregar usuario`.
Envía el ID numérico del usuario. El bot lo guardará en
`telegram_admins.json`, que también está excluido de Git. Desde el mismo menú
se puede quitar un usuario; el último administrador no puede quitarse a sí
mismo.

## Ejecutar

```bash
source venv/bin/activate
python bot_telegram.py
```

El bot solo ejecuta `iniciar_servidores_hl7.sh` y
`detener_servidores_hl7.sh`; no acepta comandos de shell desde Telegram.

## Operaciones disponibles

- `📊 Actualizar`: estado del puerto 2590 y del proceso ORM.
- `▶️ Iniciar HL7`: ejecuta el script de inicio.
- `⏹️ Detener HL7`: ejecuta el script de detención, con confirmación.
- `🔄 Reiniciar HL7`: detiene y vuelve a iniciar, con confirmación.
- `📜 Ver logs`: muestra las últimas líneas de cada log.
