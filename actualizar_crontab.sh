#!/bin/bash

# Script para garantizar que la tarea de cron esté configurada correctamente
# y eliminar cualquier otra entrada en crontab.

# Configuración
CRON_JOB="*/4 * * * * /home/integracioneshe1/vscode_proj/HL7FINAL/verificar_y_reiniciar_servicios.sh >> /home/integracioneshe1/vscode_proj/HL7FINAL/logs/cron_verificar.log 2>&1"

# Crear un archivo temporal para la nueva crontab
TEMP_CRON=$(mktemp)

# Agregar la tarea deseada al archivo temporal
echo "$CRON_JOB" > "$TEMP_CRON"

# Reemplazar la crontab actual con el archivo temporal
crontab "$TEMP_CRON"

# Eliminar el archivo temporal
rm "$TEMP_CRON"

# Confirmar que la tarea se ha configurado correctamente
echo "✅ Tarea de cron configurada correctamente:"
crontab -l
