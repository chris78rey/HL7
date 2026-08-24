#!/bin/bash

# Script para crear accesos directos en el escritorio
# Ejecutar este script UNA VEZ para crear los accesos directos

DESKTOP_DIR="$HOME/Desktop"
PROJECT_DIR="/home/integracioneshe1/vscode_proj/HL7FINAL"

echo "================================================"
echo "    CREANDO ACCESOS DIRECTOS EN ESCRITORIO"
echo "================================================"

# Verificar si existe el directorio Desktop
if [ ! -d "$DESKTOP_DIR" ]; then
    echo "❌ No se encontró el directorio Desktop: $DESKTOP_DIR"
    echo "   Creando directorio Desktop..."
    mkdir -p "$DESKTOP_DIR"
fi

echo "📁 Directorio Desktop: $DESKTOP_DIR"
echo "📁 Directorio Proyecto: $PROJECT_DIR"

# 1. Acceso directo para INICIAR servidores HL7
cat > "$DESKTOP_DIR/Iniciar_Servidores_HL7.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Iniciar Servidores HL7
Comment=Inicia el servidor MDM y cliente ORM HL7
Exec=bash -c "cd '$PROJECT_DIR' && gnome-terminal --title='Iniciando Servidores HL7' -- bash -c './iniciar_servidores_hl7.sh; echo; echo \"Presiona Enter para cerrar...\"; read'"
Icon=applications-system
Terminal=false
Categories=Development;
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOF

# 2. Acceso directo para DETENER servidores HL7
cat > "$DESKTOP_DIR/Detener_Servidores_HL7.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Detener Servidores HL7
Comment=Detiene el servidor MDM y cliente ORM HL7
Exec=bash -c "cd '$PROJECT_DIR' && gnome-terminal --title='Deteniendo Servidores HL7' -- bash -c './detener_servidores_hl7.sh; echo; echo \"Presiona Enter para cerrar...\"; read'"
Icon=application-exit
Terminal=false
Categories=Development;
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOF

# 3. Acceso directo para VERIFICAR ESTADO
cat > "$DESKTOP_DIR/Estado_Servidores_HL7.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Estado Servidores HL7
Comment=Verifica el estado de los servidores HL7
Exec=gnome-terminal -- bash -c "echo '=== ESTADO DE SERVIDORES HL7 ==='; echo ''; echo '🔍 Verificando servidor MDM (puerto 2590)...'; if lsof -Pi :2590 -sTCP:LISTEN -t >/dev/null 2>&1; then echo '✅ Servidor MDM: ACTIVO'; else echo '❌ Servidor MDM: INACTIVO'; fi; echo ''; echo '🔍 Verificando cliente ORM...'; if pgrep -f 'orm/orm_cliente_envio.py' > /dev/null 2>&1; then echo '✅ Cliente ORM: ACTIVO'; else echo '❌ Cliente ORM: INACTIVO'; fi; echo ''; echo '📊 Procesos HL7 activos:'; ps aux | grep -E '(mdm_servidor|orm_cliente)' | grep -v grep || echo 'Ninguno'; echo ''; echo 'Presiona Enter para cerrar...'; read"
Icon=system-monitor
Terminal=false
Categories=Development;
StartupNotify=true
EOF

# 4. Acceso directo para ABRIR LOGS
cat > "$DESKTOP_DIR/Ver_Logs_HL7.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ver Logs HL7
Comment=Abre los archivos de log de los servidores HL7
Exec=gnome-terminal -- bash -c "cd '$PROJECT_DIR'; echo '=== LOGS DE SERVIDORES HL7 ==='; echo ''; echo '📄 Últimas 20 líneas del log MDM:'; echo ''; tail -n 20 logs/mdm_servidor.log 2>/dev/null || echo 'Log MDM no encontrado'; echo ''; echo '📄 Últimas 20 líneas del log ORM:'; echo ''; tail -n 20 logs/orm_cliente.log 2>/dev/null || echo 'Log ORM no encontrado'; echo ''; echo 'Presiona Enter para cerrar...'; read"
Icon=text-x-generic
Terminal=false
Categories=Development;
StartupNotify=true
EOF

# 5. Acceso directo para ABRIR PROYECTO
cat > "$DESKTOP_DIR/Abrir_Proyecto_HL7.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Abrir Proyecto HL7
Comment=Abre el directorio del proyecto HL7 en el explorador de archivos
Exec=nautilus '$PROJECT_DIR'
Icon=folder
Terminal=false
Categories=Development;
StartupNotify=true
EOF

# Dar permisos de ejecución a todos los archivos .desktop
chmod +x "$DESKTOP_DIR"/*.desktop

# Marcar archivos .desktop como confiables (Ubuntu/GNOME)
if command -v gio &> /dev/null; then
    echo "🔒 Marcando archivos .desktop como confiables..."
    gio set "$DESKTOP_DIR/Iniciar_Servidores_HL7.desktop" metadata::trusted true 2>/dev/null || true
    gio set "$DESKTOP_DIR/Detener_Servidores_HL7.desktop" metadata::trusted true 2>/dev/null || true
    gio set "$DESKTOP_DIR/Estado_Servidores_HL7.desktop" metadata::trusted true 2>/dev/null || true
    gio set "$DESKTOP_DIR/Ver_Logs_HL7.desktop" metadata::trusted true 2>/dev/null || true
    gio set "$DESKTOP_DIR/Abrir_Proyecto_HL7.desktop" metadata::trusted true 2>/dev/null || true
    echo "   ✅ Archivos marcados como confiables"
fi

echo ""
echo "✅ Accesos directos creados en el escritorio:"
echo "   🚀 Iniciar_Servidores_HL7.desktop"
echo "   🛑 Detener_Servidores_HL7.desktop"
echo "   📊 Estado_Servidores_HL7.desktop"
echo "   📄 Ver_Logs_HL7.desktop"
echo "   📁 Abrir_Proyecto_HL7.desktop"
echo ""
echo "ℹ️  Los accesos directos aparecerán en tu escritorio."
echo "   Puedes hacer doble clic en ellos para ejecutar las acciones."
echo ""
echo "⚠️  Si aparece un diálogo de 'Archivo no confiable':"
echo "   1. Haz clic derecho en el icono del escritorio"
echo "   2. Selecciona 'Permitir ejecutar como programa'"
echo "   3. O haz clic en 'Confiar y ejecutar' cuando aparezca el diálogo"
echo ""
echo "================================================"
echo "       ACCESOS DIRECTOS CREADOS"
echo "================================================"
