# Integración Telegram y operación automática HL7

## Componentes

- `bot_telegram.py`: bot de control basado en `python-telegram-bot`.
- `.env`: contiene `TELEGRAM_BOT_TOKEN` y `TELEGRAM_ADMIN_IDS`; no se versiona.
- `hl7-telegram.service`: servicio `systemd` que ejecuta el bot con el entorno virtual.
- `iniciar_servidores_hl7.sh` y `detener_servidores_hl7.sh`: controlan MDM y ORM.

## Flujo

1. `systemd` inicia el bot después de que la red esté disponible.
2. Telegram entrega `/start` y acciones de los administradores autorizados.
3. El bot consulta el puerto MLLP del MDM y el proceso ORM.
4. Las acciones de inicio, detención y reinicio ejecutan únicamente los scripts HL7 definidos.
5. El ORM envía mensajes MLLP al destino configurado y registra la respuesta ACK en `logs/orm_cliente.log`.

## Operación persistente

El servicio se instala y activa con:

```bash
sudo install -m 0644 hl7-telegram.service /etc/systemd/system/hl7-telegram.service
sudo systemctl daemon-reload
sudo systemctl enable --now hl7-telegram.service
```

El servicio define `LD_LIBRARY_PATH` y `TNS_ADMIN` para que `cx_Oracle` encuentre Oracle Instant Client al iniciar desde `systemd`.

## Seguridad y límites

- Los secretos permanecen en `.env` y no se incluyen en Git ni en Graphify.
- El bot no ejecuta comandos arbitrarios recibidos desde Telegram.
- Los usuarios autorizados se mantienen en `TELEGRAM_ADMIN_IDS` y `telegram_admins.json`.
- Los logs se conservan localmente en `logs/`.
