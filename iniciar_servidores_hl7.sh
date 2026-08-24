#!/bin/bash

# Script para iniciar los servidores HL7
# Ubicación: /home/integracioneshe1/vscode_proj/HL7FINAL/

echo "================================================"
echo "         INICIADOR DE SERVIDORES HL7"
echo "================================================"

# Obtener el directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Directorio del proyecto: $SCRIPT_DIR"

# Cambiar al directorio del proyecto
cd "$SCRIPT_DIR"

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "⚠️  No se encontró entorno virtual, usando Python del sistema"
fi

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 0  # Puerto en uso
    else
        return 1  # Puerto libre
    fi
}

echo ""
echo "🔍 Verificando puertos..."

# Verificar puerto 2590 (MDM)
if check_port 2590; then
    echo "⚠️  Puerto 2590 (MDM) ya está en uso"
    echo "   Proceso actual: $(lsof -ti:2590 | xargs ps -p | tail -n +2)"
else
    echo "✅ Puerto 2590 (MDM) disponible"
fi

echo ""
echo "🚀 Iniciando servidores HL7..."

# 1. Iniciar servidor MDM
echo ""
echo "📥 Iniciando servidor MDM HL7 (puerto 2590)..."
if check_port 2590; then
    echo "   ⚠️  El servidor MDM ya está ejecutándose"
else
    nohup python3 mdm/mdm_servidor_his.py > logs/mdm_servidor.log 2>&1 &
    MDM_PID=$!
    sleep 2
    if kill -0 $MDM_PID 2>/dev/null; then
        echo "   ✅ Servidor MDM iniciado (PID: $MDM_PID)"
        echo $MDM_PID > pids/mdm_servidor.pid
    else
        echo "   ❌ Error al iniciar servidor MDM"
        echo "   Ver logs en: logs/mdm_servidor.log"
    fi
fi

# 2. Iniciar cliente ORM
echo ""
echo "📤 Iniciando cliente ORM..."
# Verificar si ya está ejecutándose
if pgrep -f "orm/orm_cliente_envio.py" > /dev/null; then
    echo "   ⚠️  El cliente ORM ya está ejecutándose"
    echo "   PID actual: $(pgrep -f 'orm/orm_cliente_envio.py')"
else
    nohup python3 orm/orm_cliente_envio.py > logs/orm_cliente.log 2>&1 &
    ORM_PID=$!
    sleep 2
    if kill -0 $ORM_PID 2>/dev/null; then
        echo "   ✅ Cliente ORM iniciado (PID: $ORM_PID)"
        echo $ORM_PID > pids/orm_cliente.pid
    else
        echo "   ❌ Error al iniciar cliente ORM"
        echo "   Ver logs en: logs/orm_cliente.log"
    fi
fi

echo ""
echo "📊 Estado final de los servicios:"
echo "=================================="

# Estado del servidor MDM
if check_port 2590; then
    echo "🟢 Servidor MDM: ACTIVO (puerto 2590)"
else
    echo "🔴 Servidor MDM: INACTIVO"
fi

# Estado del cliente ORM
if pgrep -f "orm/orm_cliente_envio.py" > /dev/null; then
    echo "🟢 Cliente ORM: ACTIVO"
else
    echo "🔴 Cliente ORM: INACTIVO"
fi

echo ""
echo "📁 Archivos de logs:"
echo "   - Servidor MDM: logs/mdm_servidor.log"
echo "   - Cliente ORM: logs/orm_cliente.log"
echo ""
echo "📁 Archivos PID:"
echo "   - Servidor MDM: pids/mdm_servidor.pid"
echo "   - Cliente ORM: pids/orm_cliente.pid"
echo ""
echo "🛑 Para detener los servicios, ejecuta: ./detener_servidores_hl7.sh"
echo ""
echo "================================================"
echo "         INICIALIZACIÓN COMPLETADA"
echo "================================================"
