#!/bin/bash

# Script para verificar y reiniciar servicios HL7 si están caídos
# Servicios: Servidor MDM y Cliente ORM

# Configuración
PROJECT_ROOT="/home/integracioneshe1/vscode_proj/HL7FINAL"
MDM_PORT=2590
MDM_SCRIPT="$PROJECT_ROOT/mdm/mdm_servidor_his.py"
ORM_SCRIPT="$PROJECT_ROOT/orm/orm_cliente_envio.py"
LOG_DIR="logs"
PID_DIR="pids"
PYTHON_BIN="$VENV_PATH/bin/python3"
LSOF_BIN="/usr/bin/lsof"
PGREP_BIN="/usr/bin/pgrep"
VENV_PATH="/home/integracioneshe1/vscode_proj/HL7FINAL/venv"

# Activar entorno virtual
source $VENV_PATH/bin/activate

# Crear directorios si no existen
mkdir -p $LOG_DIR $PID_DIR

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    if $LSOF_BIN -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 0  # Puerto en uso
    else
        return 1  # Puerto libre
    fi
}

# Función para verificar si un proceso está corriendo
check_process() {
    local script=$1
    if $PGREP_BIN -f "$script" >/dev/null; then
        return 0  # Proceso corriendo
    else
        return 1  # Proceso detenido
    fi
}

# Verificar estado del servidor MDM
echo "🔍 Verificando estado del servidor MDM..."
if check_port $MDM_PORT; then
    echo "✅ Servidor MDM está activo en el puerto $MDM_PORT"
else
    echo "⚠️  Servidor MDM no está activo. Reiniciando..."
    nohup $PYTHON_BIN $MDM_SCRIPT > "$PROJECT_ROOT/$LOG_DIR/mdm_servidor.log" 2>&1 &
    MDM_PID=$!
    sleep 2
    if kill -0 $MDM_PID 2>/dev/null; then
        echo "✅ Servidor MDM reiniciado (PID: $MDM_PID)"
        echo $MDM_PID > $PID_DIR/mdm_servidor.pid
    else
        echo "❌ Error al reiniciar el servidor MDM. Ver logs en: $LOG_DIR/mdm_servidor.log"
        echo "$(date): Error al reiniciar el servidor MDM (PID: $MDM_PID)" >> $LOG_DIR/mdm_servidor.log
    fi
fi

# Verificar estado del cliente ORM
echo "🔍 Verificando estado del cliente ORM..."
if check_process $ORM_SCRIPT; then
    echo "✅ Cliente ORM está activo"
else
    echo "⚠️  Cliente ORM no está activo. Reiniciando..."
    nohup $PYTHON_BIN $ORM_SCRIPT > "$PROJECT_ROOT/$LOG_DIR/orm_cliente.log" 2>&1 &
    ORM_PID=$!
    sleep 2
    if kill -0 $ORM_PID 2>/dev/null; then
        echo "✅ Cliente ORM reiniciado (PID: $ORM_PID)"
        echo $ORM_PID > $PID_DIR/orm_cliente.pid
    else
        echo "❌ Error al reiniciar el cliente ORM. Ver logs en: $LOG_DIR/orm_cliente.log"
        echo "$(date): Error al reiniciar el cliente ORM (PID: $ORM_PID)" >> $LOG_DIR/orm_cliente.log
    fi
fi

echo "✅ Verificación y reinicio completados."
