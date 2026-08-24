#!/bin/bash

# Script para detener los servidores HL7
# Ubicación: /home/integracioneshe1/vscode_proj/HL7FINAL/

echo "================================================"
echo "        DETENIENDO SERVIDORES HL7"
echo "================================================"

# Obtener el directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Directorio del proyecto: $SCRIPT_DIR"

# Cambiar al directorio del proyecto
cd "$SCRIPT_DIR"

echo ""
echo "🛑 Deteniendo servicios HL7..."

# Función para terminar proceso por PID
kill_by_pid() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo "   🔄 Deteniendo $service_name (PID: $pid)..."
            kill -TERM $pid
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                echo "   ⚠️  Forzando cierre de $service_name..."
                kill -KILL $pid
            fi
            echo "   ✅ $service_name detenido"
        else
            echo "   ℹ️  $service_name ya estaba detenido"
        fi
        rm -f "$pid_file"
    else
        echo "   ℹ️  No se encontró archivo PID para $service_name"
    fi
}

# 1. Detener servidor MDM
echo ""
echo "📥 Deteniendo servidor MDM..."
kill_by_pid "pids/mdm_servidor.pid" "Servidor MDM"

# También buscar por puerto 2590
MDM_PIDS=$(lsof -ti:2590 2>/dev/null)
if [ ! -z "$MDM_PIDS" ]; then
    echo "   🔄 Deteniendo procesos adicionales en puerto 2590..."
    for pid in $MDM_PIDS; do
        kill -TERM $pid 2>/dev/null
    done
    sleep 1
    for pid in $MDM_PIDS; do
        if kill -0 $pid 2>/dev/null; then
            kill -KILL $pid 2>/dev/null
        fi
    done
fi

# 2. Detener cliente ORM
echo ""
echo "📤 Deteniendo cliente ORM..."
kill_by_pid "pids/orm_cliente.pid" "Cliente ORM"

# También buscar por nombre de proceso
ORM_PIDS=$(pgrep -f "orm/orm_cliente_envio.py" 2>/dev/null)
if [ ! -z "$ORM_PIDS" ]; then
    echo "   🔄 Deteniendo procesos adicionales del cliente ORM..."
    for pid in $ORM_PIDS; do
        kill -TERM $pid 2>/dev/null
    done
    sleep 1
    for pid in $ORM_PIDS; do
        if kill -0 $pid 2>/dev/null; then
            kill -KILL $pid 2>/dev/null
        fi
    done
fi

echo ""
echo "📊 Estado final de los servicios:"
echo "=================================="

# Verificar estado final
if lsof -Pi :2590 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔴 Servidor MDM: AÚN ACTIVO (revisar manualmente)"
else
    echo "✅ Servidor MDM: DETENIDO"
fi

if pgrep -f "orm/orm_cliente_envio.py" > /dev/null 2>&1; then
    echo "🔴 Cliente ORM: AÚN ACTIVO (revisar manualmente)"
else
    echo "✅ Cliente ORM: DETENIDO"
fi

echo ""
echo "🧹 Limpiando archivos temporales..."
rm -f pids/*.pid 2>/dev/null
echo "   ✅ Archivos PID eliminados"

echo ""
echo "ℹ️  Los logs se mantienen en:"
echo "   - logs/mdm_servidor.log"
echo "   - logs/orm_cliente.log"
echo ""
echo "🚀 Para reiniciar los servicios, ejecuta: ./iniciar_servidores_hl7.sh"
echo ""
echo "================================================"
echo "           SERVICIOS DETENIDOS"
echo "================================================"
