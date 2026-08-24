# 📋 GUÍA RÁPIDA - SERVICIOS HL7
## Referencia de Comandos y Procedimientos

---

## 🚀 COMANDOS ESENCIALES

### **Inicio de Servicios**
```bash
# Método más fácil
hl7-start

# Alternativas
~/iniciar_hl7.sh
./iniciar_servidores_hl7.sh  # (desde el directorio del proyecto)
```

### **Detención de Servicios**
```bash
# Método más fácil
hl7-stop

# Alternativas
~/detener_hl7.sh
./detener_servidores_hl7.sh  # (desde el directorio del proyecto)
```

### **Estado de Servicios**
```bash
# Verificación rápida
hl7-status

# Verificación manual
ps aux | grep -E "(mdm_servidor|orm_cliente)" | grep -v grep
lsof -i :2590  # Puerto MDM
```

---

## 📊 VERIFICACIONES RÁPIDAS

### **¿Están activos los servicios?**
```bash
# Comando único para verificar todo
hl7-status

# O verificar individualmente:
lsof -i :2590 && echo "✅ MDM OK" || echo "❌ MDM Falló"
pgrep -f orm_cliente_envio.py && echo "✅ ORM OK" || echo "❌ ORM Falló"
```

### **¿Hay errores en los logs?**
```bash
# Ver últimos errores MDM
tail -n 20 /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log | grep -i error

# Ver últimos errores ORM  
tail -n 20 /home/integracioneshe1/vscode_proj/HL7FINAL/logs/orm_cliente.log | grep -i error
```

### **¿Cuánto espacio usan los logs?**
```bash
du -sh /home/integracioneshe1/vscode_proj/HL7FINAL/logs/
```

---

## 🔧 SOLUCIONES RÁPIDAS

### **Puerto 2590 ocupado**
```bash
# Encontrar y terminar proceso
lsof -ti:2590 | xargs kill -9
hl7-start
```

### **Servicios colgados**
```bash
# Detener todo forzadamente
pkill -9 -f mdm_servidor_his.py
pkill -9 -f orm_cliente_envio.py

# Limpiar PIDs
rm -f /home/integracioneshe1/vscode_proj/HL7FINAL/pids/*.pid

# Reiniciar
hl7-start
```

### **Problema de permisos**
```bash
# Corregir propietario
chown -R integracioneshe1:integracioneshe1 /home/integracioneshe1/vscode_proj/HL7FINAL/

# Corregir permisos de ejecución
chmod +x /home/integracioneshe1/vscode_proj/HL7FINAL/*.sh
chmod +x /home/integracioneshe1/*.sh
```

---

## 📱 ACCESOS DIRECTOS ESCRITORIO

**Ubicación:** `~/Desktop/`

- 🚀 **Iniciar_Servidores_HL7.desktop** → Doble clic para iniciar
- 🛑 **Detener_Servidores_HL7.desktop** → Doble clic para detener  
- 📊 **Estado_Servidores_HL7.desktop** → Doble clic para ver estado
- 📄 **Ver_Logs_HL7.desktop** → Doble clic para ver logs
- 📁 **Abrir_Proyecto_HL7.desktop** → Doble clic para abrir proyecto

⚠️ **IMPORTANTE:** Usar **doble clic**, NO ejecutar desde terminal con `./`

---

## 📂 UBICACIONES IMPORTANTES

```
/home/integracioneshe1/vscode_proj/HL7FINAL/
├── mdm/mdm_servidor_his.py          # Servidor MDM
├── orm/orm_cliente_envio.py         # Cliente ORM
├── logs/                            # Logs de servicios
│   ├── mdm_servidor.log
│   └── orm_cliente.log
├── pids/                            # IDs de procesos
│   ├── mdm_servidor.pid
│   └── orm_cliente.pid
├── iniciar_servidores_hl7.sh        # Script inicio
├── detener_servidores_hl7.sh        # Script detención
└── estado_hl7.sh                    # Script estado
```

---

## 🔍 DIAGNÓSTICO RÁPIDO

### **Script de Diagnóstico Completo**
```bash
# Crea y ejecuta este script para diagnóstico completo
cat << 'EOF' > /tmp/diagnostico_hl7.sh
#!/bin/bash
echo "=== DIAGNÓSTICO HL7 $(date) ==="
echo ""
echo "🔍 PROCESOS:"
ps aux | grep -E "(mdm_servidor|orm_cliente)" | grep -v grep || echo "Sin procesos HL7"
echo ""
echo "🔍 PUERTOS:"
lsof -i :2590 || echo "Puerto 2590 libre"
echo ""
echo "🔍 LOGS RECIENTES:"
ls -la /home/integracioneshe1/vscode_proj/HL7FINAL/logs/ 2>/dev/null || echo "Sin logs"
echo ""
echo "🔍 ESPACIO:"
df -h /home/integracioneshe1/vscode_proj/HL7FINAL 2>/dev/null || echo "Directorio no encontrado"
EOF

chmod +x /tmp/diagnostico_hl7.sh
/tmp/diagnostico_hl7.sh
```

---

## 📞 ESCALACIÓN RÁPIDA

### **Problemas de Nivel 1 (Resuelve local):**
- Servicios caídos → `hl7-start`
- Puerto ocupado → Matar proceso y reiniciar
- Logs grandes → Archivar o limpiar

### **Problemas de Nivel 2 (Contactar Admin):**
- Error de conexión Oracle persistente
- Servicios se caen constantemente  
- Problemas de red/conectividad

### **Problemas de Nivel 3 (Contactar Desarrollador):**
- Errores de código/aplicación
- Corrupción de datos
- Cambios de configuración

---

## ⏰ RUTINAS DE MONITOREO

### **Cada 15 minutos:**
```bash
hl7-status
```

### **Cada hora:**
```bash
# Verificar logs por errores
tail -n 10 /home/integracioneshe1/vscode_proj/HL7FINAL/logs/*.log | grep -i error
```

### **Cada turno:**
```bash
# Diagnóstico completo
/tmp/diagnostico_hl7.sh
```

---

## 🆘 EMERGENCIAS

### **Servicios no responden (CRÍTICO):**
```bash
# 1. Detener todo
pkill -9 -f mdm_servidor_his.py
pkill -9 -f orm_cliente_envio.py

# 2. Limpiar
rm -f /home/integracioneshe1/vscode_proj/HL7FINAL/pids/*.pid

# 3. Reiniciar
hl7-start

# 4. Verificar
hl7-status

# 5. Si sigue fallando → ESCALAR
```

### **Sistema sin respuesta:**
1. **No reiniciar el servidor** sin autorización
2. **Contactar inmediatamente** al supervisor
3. **Documentar** todo lo que se hizo antes del fallo
4. **Preservar logs** para análisis

---

## 📝 CÓDIGOS DE ESTADO

### **Estados Normales:**
- `🟢 Servidor MDM: ACTIVO (puerto 2590)` ✅
- `🟢 Cliente ORM: ACTIVO` ✅

### **Estados de Alerta:**
- `⚠️ Puerto 2590 (MDM) ya está en uso` → Revisar proceso duplicado
- `🔴 Servidor MDM: INACTIVO` → Reiniciar servicio
- `🔴 Cliente ORM: INACTIVO` → Reiniciar servicio

### **Estados Críticos:**
- `[ERROR] No se pudo conectar a la base de datos` → Contactar DBA
- `Permission denied` → Verificar permisos
- `ModuleNotFoundError` → Verificar dependencias Python

---

## 💡 TIPS ÚTILES

### **Comandos de una línea útiles:**
```bash
# Ver servicios HL7 en una línea
ps aux | awk '/[m]dm_servidor|[o]rm_cliente/ {print $2, $11}' | column -t

# Logs en tiempo real de ambos servicios
tail -f /home/integracioneshe1/vscode_proj/HL7FINAL/logs/*.log

# Verificar espacio en disco rápidamente
df -h | grep -E "(/$|/home)"

# Ver últimos 5 errores
grep -i error /home/integracioneshe1/vscode_proj/HL7FINAL/logs/*.log | tail -5
```

### **Alias útiles para agregar a ~/.bashrc:**
```bash
alias hl7-log='tail -f /home/integracioneshe1/vscode_proj/HL7FINAL/logs/*.log'
alias hl7-error='grep -i error /home/integracioneshe1/vscode_proj/HL7FINAL/logs/*.log | tail -10'
alias hl7-space='du -sh /home/integracioneshe1/vscode_proj/HL7FINAL/logs/'
alias hl7-ps='ps aux | grep -E "(mdm_servidor|orm_cliente)" | grep -v grep'
```

---

**🚨 RECORDATORIO:** Si tienes dudas, siempre es mejor escalar que experimentar con servicios críticos.

---

*Guía actualizada: Junio 2025 | Para emergencias críticas: Contactar supervisor de turno*
