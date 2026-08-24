#!/bin/bash
# Mata todos los procesos de MLLP SIU y MDM (cliente y servidor)

PIDS=$(ps aux | grep -E '[s]iu_|[m]dm_' | awk '{print $2}')
if [ -z "$PIDS" ]; then
  echo "No se encontró ningún proceso SIU o MDM ejecutándose."
else
  echo "Matando proceso(s) SIU/MDM con PID(s): $PIDS"
  kill $PIDS
fi
