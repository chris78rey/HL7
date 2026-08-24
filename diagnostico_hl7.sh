#!/bin/bash

# ========================================================
# SCRIPT DE DIAGNÓSTICO COMPLETO - SERVICIOS HL7
# ========================================================
# Ejecutar este script para obtener un reporte completo
# del estado del sistema HL7
# ========================================================

PROJECT_DIR="/home/integracioneshe1/vscode_proj/HL7FINAL"
LOG_FILE="/tmp/diagnostico_hl7_$(date +%Y%m%d_%H%M%S).log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_and_print() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Función para verificar comando
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Encabezado
clear
log_and_print "${BLUE}================================================${NC}"
log_and_print "${BLUE}      DIAGNÓSTICO COMPLETO - SERVICIOS HL7     ${NC}"
log_and_print "${BLUE}================================================${NC}"
log_and_print "${BLUE}Fecha: $(date)${NC}"
log_and_print "${BLUE}Usuario: $(whoami)${NC}"
log_and_print "${BLUE}Hostname: $(hostname)${NC}"
log_and_print "${BLUE}Reporte guardado en: $LOG_FILE${NC}"
log_and_print "${BLUE}================================================${NC}"
log_and_print ""

# 1. VERIFICACIÓN DE SISTEMA
log_and_print "${YELLOW}🖥️  1. INFORMACIÓN DEL SISTEMA${NC}"
log_and_print "----------------------------------------"
log_and_print "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"')"
log_and_print "Kernel: $(uname -r)"
log_and_print "Uptime: $(uptime -p)"
log_and_print "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
log_and_print "Memoria: $(free -h | awk 'NR==2{printf "Usado: %s/%s (%.2f%%)", $3,$2,$3*100/$2 }')"
log_and_print ""

# 2. VERIFICACIÓN DE DIRECTORIOS
log_and_print "${YELLOW}📁 2. VERIFICACIÓN DE DIRECTORIOS${NC}"
log_and_print "----------------------------------------"
if [ -d "$PROJECT_DIR" ]; then
    log_and_print "${GREEN}✅ Directorio principal: $PROJECT_DIR${NC}"
    log_and_print "   Propietario: $(ls -ld $PROJECT_DIR | awk '{print $3":"$4}')"
    log_and_print "   Permisos: $(ls -ld $PROJECT_DIR | awk '{print $1}')"
else
    log_and_print "${RED}❌ Directorio principal NO encontrado: $PROJECT_DIR${NC}"
fi

# Verificar subdirectorios importantes
for dir in "logs" "pids" "mdm" "orm"; do
    if [ -d "$PROJECT_DIR/$dir" ]; then
        log_and_print "${GREEN}✅ Subdirectorio: $dir${NC}"
    else
        log_and_print "${RED}❌ Subdirectorio NO encontrado: $dir${NC}"
    fi
done
log_and_print ""

# 3. VERIFICACIÓN DE PROCESOS HL7
log_and_print "${YELLOW}🔄 3. ESTADO DE PROCESOS HL7${NC}"
log_and_print "----------------------------------------"

# Verificar servidor MDM
MDM_PROCESS=$(ps aux | grep mdm_servidor_his.py | grep -v grep)
if [ -n "$MDM_PROCESS" ]; then
    MDM_PID=$(echo "$MDM_PROCESS" | awk '{print $2}')
    MDM_CPU=$(echo "$MDM_PROCESS" | awk '{print $3}')
    MDM_MEM=$(echo "$MDM_PROCESS" | awk '{print $4}')
    log_and_print "${GREEN}✅ Servidor MDM: ACTIVO${NC}"
    log_and_print "   PID: $MDM_PID | CPU: $MDM_CPU% | Memoria: $MDM_MEM%"
    log_and_print "   Tiempo ejecución: $(ps -o etime= -p $MDM_PID 2>/dev/null | tr -d ' ')"
else
    log_and_print "${RED}❌ Servidor MDM: INACTIVO${NC}"
fi

# Verificar cliente ORM
ORM_PROCESS=$(ps aux | grep orm_cliente_envio.py | grep -v grep)
if [ -n "$ORM_PROCESS" ]; then
    ORM_PID=$(echo "$ORM_PROCESS" | awk '{print $2}')
    ORM_CPU=$(echo "$ORM_PROCESS" | awk '{print $3}')
    ORM_MEM=$(echo "$ORM_PROCESS" | awk '{print $4}')
    log_and_print "${GREEN}✅ Cliente ORM: ACTIVO${NC}"
    log_and_print "   PID: $ORM_PID | CPU: $ORM_CPU% | Memoria: $ORM_MEM%"
    log_and_print "   Tiempo ejecución: $(ps -o etime= -p $ORM_PID 2>/dev/null | tr -d ' ')"
else
    log_and_print "${RED}❌ Cliente ORM: INACTIVO${NC}"
fi
log_and_print ""

# 4. VERIFICACIÓN DE PUERTOS
log_and_print "${YELLOW}🌐 4. ESTADO DE PUERTOS${NC}"
log_and_print "----------------------------------------"

# Puerto 2590 (MDM)
if check_command "lsof"; then
    PORT_2590=$(lsof -i :2590 2>/dev/null)
    if [ -n "$PORT_2590" ]; then
        log_and_print "${GREEN}✅ Puerto 2590 (MDM): EN USO${NC}"
        echo "$PORT_2590" | while read line; do
            log_and_print "   $line"
        done
    else
        log_and_print "${RED}❌ Puerto 2590 (MDM): LIBRE${NC}"
    fi
else
    log_and_print "${YELLOW}⚠️  Comando 'lsof' no disponible${NC}"
fi
log_and_print ""

# 5. VERIFICACIÓN DE ARCHIVOS PID
log_and_print "${YELLOW}🆔 5. ARCHIVOS PID${NC}"
log_and_print "----------------------------------------"
for pid_file in "$PROJECT_DIR/pids"/*.pid; do
    if [ -f "$pid_file" ]; then
        PID_VALUE=$(cat "$pid_file" 2>/dev/null)
        PID_NAME=$(basename "$pid_file")
        if kill -0 "$PID_VALUE" 2>/dev/null; then
            log_and_print "${GREEN}✅ $PID_NAME: $PID_VALUE (proceso activo)${NC}"
        else
            log_and_print "${RED}❌ $PID_NAME: $PID_VALUE (proceso inactivo)${NC}"
        fi
    else
        log_and_print "${YELLOW}⚠️  No se encontraron archivos PID${NC}"
        break
    fi
done
log_and_print ""

# 6. VERIFICACIÓN DE LOGS
log_and_print "${YELLOW}📄 6. ESTADO DE LOGS${NC}"
log_and_print "----------------------------------------"
if [ -d "$PROJECT_DIR/logs" ]; then
    LOG_COUNT=$(find "$PROJECT_DIR/logs" -name "*.log" | wc -l)
    log_and_print "Archivos de log encontrados: $LOG_COUNT"
    
    for log_file in "$PROJECT_DIR/logs"/*.log; do
        if [ -f "$log_file" ]; then
            LOG_NAME=$(basename "$log_file")
            LOG_SIZE=$(du -sh "$log_file" | awk '{print $1}')
            LOG_MODIFIED=$(stat -c %y "$log_file" | cut -d'.' -f1)
            
            # Verificar si el log es reciente (menos de 1 hora)
            LOG_AGE=$(find "$log_file" -mmin -60)
            if [ -n "$LOG_AGE" ]; then
                log_and_print "${GREEN}✅ $LOG_NAME: $LOG_SIZE (modificado: $LOG_MODIFIED)${NC}"
            else
                log_and_print "${YELLOW}⚠️  $LOG_NAME: $LOG_SIZE (modificado: $LOG_MODIFIED) - Antiguo${NC}"
            fi
            
            # Mostrar últimas líneas con errores
            ERROR_COUNT=$(grep -i error "$log_file" 2>/dev/null | wc -l)
            if [ "$ERROR_COUNT" -gt 0 ]; then
                log_and_print "   ${RED}⚠️  Errores encontrados: $ERROR_COUNT${NC}"
                log_and_print "   Último error:"
                grep -i error "$log_file" 2>/dev/null | tail -1 | sed 's/^/   /'
            fi
        fi
    done
else
    log_and_print "${RED}❌ Directorio de logs no encontrado${NC}"
fi
log_and_print ""

# 7. VERIFICACIÓN DE ESPACIO EN DISCO
log_and_print "${YELLOW}💾 7. ESPACIO EN DISCO${NC}"
log_and_print "----------------------------------------"
df -h "$PROJECT_DIR" 2>/dev/null | while read line; do
    log_and_print "$line"
done

# Verificar espacio específico del proyecto
PROJECT_SIZE=$(du -sh "$PROJECT_DIR" 2>/dev/null | awk '{print $1}')
LOGS_SIZE=$(du -sh "$PROJECT_DIR/logs" 2>/dev/null | awk '{print $1}')
log_and_print ""
log_and_print "Tamaño del proyecto HL7: $PROJECT_SIZE"
log_and_print "Tamaño de logs: $LOGS_SIZE"
log_and_print ""

# 8. VERIFICACIÓN DE DEPENDENCIAS PYTHON
log_and_print "${YELLOW}🐍 8. DEPENDENCIAS PYTHON${NC}"
log_and_print "----------------------------------------"
if check_command "python3"; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    log_and_print "Versión Python: $PYTHON_VERSION"
    
    # Verificar módulos críticos
    MODULES=("cx_Oracle" "socket" "threading")
    for module in "${MODULES[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            log_and_print "${GREEN}✅ Módulo $module: OK${NC}"
        else
            log_and_print "${RED}❌ Módulo $module: NO DISPONIBLE${NC}"
        fi
    done
else
    log_and_print "${RED}❌ Python3 no encontrado${NC}"
fi
log_and_print ""

# 9. VERIFICACIÓN DE CONECTIVIDAD ORACLE
log_and_print "${YELLOW}🗄️  9. CONECTIVIDAD ORACLE${NC}"
log_and_print "----------------------------------------"
cd "$PROJECT_DIR" 2>/dev/null
ORACLE_TEST=$(python3 -c "
try:
    import sys, os
    sys.path.append('$PROJECT_DIR')
    from config_db import DB_CONFIG, get_dsn
    import cx_Oracle
    conn = cx_Oracle.connect(user=DB_CONFIG['user'], password=DB_CONFIG['password'], dsn=get_dsn())
    print('OK')
    conn.close()
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)

if [[ "$ORACLE_TEST" == "OK" ]]; then
    log_and_print "${GREEN}✅ Conexión Oracle: EXITOSA${NC}"
else
    log_and_print "${RED}❌ Conexión Oracle: FALLIDA${NC}"
    log_and_print "   Error: $ORACLE_TEST"
fi
log_and_print ""

# 10. VERIFICACIÓN DE CONFIGURACIÓN
log_and_print "${YELLOW}⚙️  10. ARCHIVOS DE CONFIGURACIÓN${NC}"
log_and_print "----------------------------------------"
CONFIG_FILES=("config_db.py" "requirements.txt")
for config in "${CONFIG_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$config" ]; then
        log_and_print "${GREEN}✅ $config: Existe${NC}"
        if [ "$config" = "config_db.py" ]; then
            # Verificar configuración sin mostrar credenciales
            log_and_print "   Configuración Oracle verificada (credenciales ocultas)"
        fi
    else
        log_and_print "${RED}❌ $config: NO ENCONTRADO${NC}"
    fi
done
log_and_print ""

# 11. VERIFICACIÓN DE SCRIPTS DE GESTIÓN
log_and_print "${YELLOW}📜 11. SCRIPTS DE GESTIÓN${NC}"
log_and_print "----------------------------------------"
SCRIPTS=("iniciar_servidores_hl7.sh" "detener_servidores_hl7.sh" "estado_hl7.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -f "$PROJECT_DIR/$script" ]; then
        if [ -x "$PROJECT_DIR/$script" ]; then
            log_and_print "${GREEN}✅ $script: Existe y es ejecutable${NC}"
        else
            log_and_print "${YELLOW}⚠️  $script: Existe pero no es ejecutable${NC}"
        fi
    else
        log_and_print "${RED}❌ $script: NO ENCONTRADO${NC}"
    fi
done

# Verificar scripts globales
GLOBAL_SCRIPTS=("$HOME/iniciar_hl7.sh" "$HOME/detener_hl7.sh" "$HOME/estado_hl7.sh")
for script in "${GLOBAL_SCRIPTS[@]}"; do
    script_name=$(basename "$script")
    if [ -f "$script" ]; then
        log_and_print "${GREEN}✅ $script_name (global): Existe${NC}"
    else
        log_and_print "${YELLOW}⚠️  $script_name (global): NO ENCONTRADO${NC}"
    fi
done
log_and_print ""

# 12. VERIFICACIÓN DE ALIAS
log_and_print "${YELLOW}🔗 12. ALIAS DE COMANDOS${NC}"
log_and_print "----------------------------------------"
if grep -q "hl7-start" "$HOME/.bashrc" 2>/dev/null; then
    log_and_print "${GREEN}✅ Alias hl7-start: Configurado${NC}"
else
    log_and_print "${YELLOW}⚠️  Alias hl7-start: NO CONFIGURADO${NC}"
fi

if grep -q "hl7-stop" "$HOME/.bashrc" 2>/dev/null; then
    log_and_print "${GREEN}✅ Alias hl7-stop: Configurado${NC}"
else
    log_and_print "${YELLOW}⚠️  Alias hl7-stop: NO CONFIGURADO${NC}"
fi

if grep -q "hl7-status" "$HOME/.bashrc" 2>/dev/null; then
    log_and_print "${GREEN}✅ Alias hl7-status: Configurado${NC}"
else
    log_and_print "${YELLOW}⚠️  Alias hl7-status: NO CONFIGURADO${NC}"
fi
log_and_print ""

# 13. VERIFICACIÓN DE ACCESOS DIRECTOS
log_and_print "${YELLOW}🖱️  13. ACCESOS DIRECTOS ESCRITORIO${NC}"
log_and_print "----------------------------------------"
DESKTOP_FILES=("Iniciar_Servidores_HL7.desktop" "Detener_Servidores_HL7.desktop" "Estado_Servidores_HL7.desktop" "Ver_Logs_HL7.desktop" "Abrir_Proyecto_HL7.desktop")
for desktop_file in "${DESKTOP_FILES[@]}"; do
    if [ -f "$HOME/Desktop/$desktop_file" ]; then
        log_and_print "${GREEN}✅ $desktop_file: Existe${NC}"
    else
        log_and_print "${YELLOW}⚠️  $desktop_file: NO ENCONTRADO${NC}"
    fi
done
log_and_print ""

# RESUMEN FINAL
log_and_print "${BLUE}================================================${NC}"
log_and_print "${BLUE}                RESUMEN FINAL                  ${NC}"
log_and_print "${BLUE}================================================${NC}"

# Calcular score general
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Verificar servicios críticos
if [ -n "$(ps aux | grep mdm_servidor_his.py | grep -v grep)" ]; then
    log_and_print "${GREEN}✅ Servidor MDM: Operativo${NC}"
    ((PASSED_CHECKS++))
else
    log_and_print "${RED}❌ Servidor MDM: No operativo${NC}"
fi
((TOTAL_CHECKS++))

if [ -n "$(ps aux | grep orm_cliente_envio.py | grep -v grep)" ]; then
    log_and_print "${GREEN}✅ Cliente ORM: Operativo${NC}"
    ((PASSED_CHECKS++))
else
    log_and_print "${RED}❌ Cliente ORM: No operativo${NC}"
fi
((TOTAL_CHECKS++))

if [[ "$ORACLE_TEST" == "OK" ]]; then
    log_and_print "${GREEN}✅ Conectividad Oracle: OK${NC}"
    ((PASSED_CHECKS++))
else
    log_and_print "${RED}❌ Conectividad Oracle: Fallida${NC}"
fi
((TOTAL_CHECKS++))

# Calcular porcentaje
SCORE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
log_and_print ""
log_and_print "Puntuación del sistema: $PASSED_CHECKS/$TOTAL_CHECKS ($SCORE%)"

if [ $SCORE -ge 100 ]; then
    log_and_print "${GREEN}🟢 Estado del sistema: EXCELENTE${NC}"
elif [ $SCORE -ge 67 ]; then
    log_and_print "${YELLOW}🟡 Estado del sistema: BUENO (revisar elementos fallidos)${NC}"
else
    log_and_print "${RED}🔴 Estado del sistema: CRÍTICO (requiere atención inmediata)${NC}"
fi

log_and_print ""
log_and_print "${BLUE}Diagnóstico completado: $(date)${NC}"
log_and_print "${BLUE}Reporte guardado en: $LOG_FILE${NC}"
log_and_print "${BLUE}================================================${NC}"

# Preguntar si desea ver el log completo
echo ""
read -p "¿Desea abrir el reporte completo? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    if check_command "less"; then
        less "$LOG_FILE"
    elif check_command "more"; then
        more "$LOG_FILE"
    else
        cat "$LOG_FILE"
    fi
fi

echo ""
echo "Para ver el reporte más tarde: cat $LOG_FILE"
echo "Para enviar el reporte: adjuntar el archivo $LOG_FILE"
