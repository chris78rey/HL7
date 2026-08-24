# 📋 DOCUMENTACIÓN COMPLETA - SERVICIOS HL7
## Manual de Operaciones para Personal Técnico

---

## 📑 ÍNDICE

1. [Información General](#información-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Métodos de Gestión](#métodos-de-gestión)
4. [Procedimientos de Inicio](#procedimientos-de-inicio)
5. [Procedimientos de Detención](#procedimientos-de-detención)
6. [Monitoreo y Estado](#monitoreo-y-estado)
7. [Visualización de Logs](#visualización-de-logs)
8. [Resolución de Problemas](#resolución-de-problemas)
9. [Mantenimiento](#mantenimiento)
10. [Contactos y Escalación](#contactos-y-escalación)

---

## 🏥 INFORMACIÓN GENERAL

### **¿Qué son los Servicios HL7?**
Los servicios HL7 (Health Level 7) son componentes críticos para la integración de sistemas de información hospitalaria. Permiten el intercambio estandarizado de datos clínicos entre diferentes sistemas.

### **Servicios Implementados**
1. **Servidor MDM (Medical Document Management)**
   - Puerto: 2590
   - Función: Recibe y procesa documentos médicos (informes, resultados)
   - Protocolo: MLLP (Minimal Lower Layer Protocol)

2. **Cliente ORM (Order Management)**
   - Función: Envía órdenes médicas y solicitudes de estudios
   - Protocolo: MLLP

### **Ubicación del Sistema**
- **Directorio Principal:** `/home/integracioneshe1/vscode_proj/HL7FINAL`
- **Usuario del Sistema:** `integracioneshe1`
- **Sistema Operativo:** Linux (Ubuntu/Debian)

---

## 🏗️ ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA HL7                             │
├─────────────────────────────────────────────────────────────┤
│  🖥️  SERVIDOR MDM                                          │
│     • Puerto: 2590                                         │
│     • Archivo: mdm/mdm_servidor_his.py                     │
│     • Base de Datos: Oracle                                 │
│     • Log: logs/mdm_servidor.log                           │
│     • PID: pids/mdm_servidor.pid                           │
├─────────────────────────────────────────────────────────────┤
│  📤 CLIENTE ORM                                             │
│     • Archivo: orm/orm_cliente_envio.py                    │
│     • Log: logs/orm_cliente.log                            │
│     • PID: pids/orm_cliente.pid                            │
└─────────────────────────────────────────────────────────────┘
```

### **Dependencias del Sistema**
- **Python 3.x** con las siguientes librerías:
  - `cx_Oracle` (conexión a Oracle)
  - `socket` (comunicación de red)
  - `threading` (manejo de hilos)
  - `PyMuPDF` (procesamiento de PDF)
  - `OpenCV` (procesamiento de imágenes)
  - `Tesseract` (OCR)

---

## 🛠️ MÉTODOS DE GESTIÓN

### **1. 🖥️ INTERFAZ GRÁFICA (Recomendado para usuarios no técnicos)**

**Ubicación:** Escritorio del usuario (`~/Desktop`)

#### **Accesos Directos Disponibles:**
- 🚀 **Iniciar_Servidores_HL7.desktop** - Inicia ambos servicios
- 🛑 **Detener_Servidores_HL7.desktop** - Detiene todos los servicios  
- 📊 **Estado_Servidores_HL7.desktop** - Muestra estado actual
- 📄 **Ver_Logs_HL7.desktop** - Visualiza logs en tiempo real
- 📁 **Abrir_Proyecto_HL7.desktop** - Abre el directorio del proyecto

#### **Cómo usar:**
1. Localizar el icono en el escritorio
2. **Doble clic** sobre el icono deseado
3. Se abrirá una terminal con la operación correspondiente

⚠️ **IMPORTANTE:** Los accesos directos se ejecutan con **doble clic**, NO desde terminal con `./`

---

### **2. 💻 LÍNEA DE COMANDOS (Para usuarios técnicos)**

#### **Comandos Rápidos (Alias Globales):**
```bash
# Iniciar servicios
hl7-start

# Detener servicios  
hl7-stop

# Ver estado
hl7-status
```

#### **Scripts Directos:**
```bash
# Desde cualquier ubicación
~/iniciar_hl7.sh
~/detener_hl7.sh
~/estado_hl7.sh

# Desde el directorio del proyecto
cd /home/integracioneshe1/vscode_proj/HL7FINAL
./iniciar_servidores_hl7.sh
./detener_servidores_hl7.sh
./estado_hl7.sh
```

---

## 🚀 PROCEDIMIENTOS DE INICIO

### **Método 1: Interfaz Gráfica**
1. **Doble clic** en `Iniciar_Servidores_HL7.desktop`
2. Esperar que aparezca la terminal
3. Verificar que aparezcan los mensajes de confirmación:
   ```
   ✅ Servidor MDM iniciado (PID: XXXXX)
   ✅ Cliente ORM iniciado (PID: XXXXX)
   ```
4. Presionar Enter para cerrar la terminal

### **Método 2: Línea de Comandos**
```bash
# Opción A: Alias
hl7-start

# Opción B: Script directo
~/iniciar_hl7.sh
```

### **Verificación del Inicio Exitoso**
Al finalizar el proceso, debe ver:
```
🟢 Servidor MDM: ACTIVO (puerto 2590)
🟢 Cliente ORM: ACTIVO
```

### **Archivos Generados:**
- `logs/mdm_servidor.log` - Log del servidor MDM
- `logs/orm_cliente.log` - Log del cliente ORM  
- `pids/mdm_servidor.pid` - ID del proceso MDM
- `pids/orm_cliente.pid` - ID del proceso ORM

---

## 🛑 PROCEDIMIENTOS DE DETENCIÓN

### **Método 1: Interfaz Gráfica**
1. **Doble clic** en `Detener_Servidores_HL7.desktop`
2. Verificar mensajes de confirmación:
   ```
   ✅ Servidor MDM detenido (PID: XXXXX)
   ✅ Cliente ORM detenido (PID: XXXXX)
   ```

### **Método 2: Línea de Comandos**
```bash
# Opción A: Alias
hl7-stop

# Opción B: Script directo
~/detener_hl7.sh
```

### **Detención Manual de Emergencia**
Si los scripts fallan, use estos comandos:

```bash
# Encontrar procesos HL7
ps aux | grep -E "(mdm_servidor|orm_cliente)"

# Terminar por nombre de proceso
pkill -f mdm_servidor_his.py
pkill -f orm_cliente_envio.py

# Terminar por puerto (MDM)
lsof -ti:2590 | xargs kill -9

# Verificar que no queden procesos
ps aux | grep -E "(mdm_servidor|orm_cliente)" | grep -v grep
```

---

## 📊 MONITOREO Y ESTADO

### **Verificación Rápida**

#### **Método 1: Interfaz Gráfica**
**Doble clic** en `Estado_Servidores_HL7.desktop`

#### **Método 2: Línea de Comandos**
```bash
hl7-status
```

### **Verificación Manual Detallada**

#### **Estado del Servidor MDM:**
```bash
# Verificar puerto 2590
lsof -i :2590
netstat -tulpn | grep 2590

# Verificar proceso
ps aux | grep mdm_servidor_his.py | grep -v grep
```

#### **Estado del Cliente ORM:**
```bash
# Verificar proceso
ps aux | grep orm_cliente_envio.py | grep -v grep
pgrep -f orm_cliente_envio.py
```

#### **Verificar PIDs Guardados:**
```bash
# Ver PIDs almacenados
cat /home/integracioneshe1/vscode_proj/HL7FINAL/pids/mdm_servidor.pid
cat /home/integracioneshe1/vscode_proj/HL7FINAL/pids/orm_cliente.pid

# Verificar si los procesos existen
kill -0 $(cat /home/integracioneshe1/vscode_proj/HL7FINAL/pids/mdm_servidor.pid) && echo "MDM activo" || echo "MDM inactivo"
```

### **Indicadores de Estado Normal**
- ✅ **MDM Activo:** Puerto 2590 escuchando
- ✅ **ORM Activo:** Proceso orm_cliente_envio.py ejecutándose
- ✅ **Logs creciendo:** Archivos de log con timestamps recientes
- ✅ **PIDs válidos:** Archivos .pid contienen números de proceso válidos

---

## 📄 VISUALIZACIÓN DE LOGS

### **Logs en Tiempo Real**

#### **Método 1: Interfaz Gráfica**
**Doble clic** en `Ver_Logs_HL7.desktop`

#### **Método 2: Línea de Comandos**
```bash
# Ver logs combinados
tail -f /home/integracioneshe1/vscode_proj/HL7FINAL/logs/servidores_hl7.log

# Ver log específico del MDM
tail -f /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log

# Ver log específico del ORM  
tail -f /home/integracioneshe1/vscode_proj/HL7FINAL/logs/orm_cliente.log
```

### **Análisis de Logs**

#### **Logs del Servidor MDM**
```bash
# Últimas 50 líneas
tail -n 50 /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log

# Buscar errores
grep -i error /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log

# Buscar conexiones
grep -i "conexión" /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log
```

#### **Logs del Cliente ORM**
```bash
# Últimas 50 líneas
tail -n 50 /home/integracioneshe1/vscode_proj/HL7FINAL/logs/orm_cliente.log

# Buscar envíos exitosos
grep -i "enviado" /home/integracioneshe1/vscode_proj/HL7FINAL/logs/orm_cliente.log
```

### **Rotación de Logs**
Los logs pueden crecer considerablemente. Para gestionar el espacio:

```bash
# Verificar tamaño de logs
du -sh /home/integracioneshe1/vscode_proj/HL7FINAL/logs/

# Comprimir logs antiguos (ejemplo)
gzip /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log.old

# Limpiar logs muy antiguos (con precaución)
find /home/integracioneshe1/vscode_proj/HL7FINAL/logs/ -name "*.log.old" -mtime +30 -delete
```

---

## 🔧 RESOLUCIÓN DE PROBLEMAS

### **Problema 1: "Puerto 2590 ya está en uso"**

**Síntomas:**
```
⚠️ Puerto 2590 (MDM) ya está en uso
```

**Solución:**
```bash
# Identificar proceso que usa el puerto
lsof -i :2590

# Terminar proceso específico
kill -9 [PID_DEL_PROCESO]

# O terminar por puerto
lsof -ti:2590 | xargs kill -9

# Reintentar inicio
hl7-start
```

---

### **Problema 2: "Error al conectar con Oracle"**

**Síntomas:**
```
[ERROR] No se pudo conectar a la base de datos: ORA-12541
```

**Verificaciones:**
```bash
# Verificar conectividad de red
ping [IP_DEL_SERVIDOR_ORACLE]

# Verificar puerto Oracle
telnet [IP_DEL_SERVIDOR_ORACLE] 1521

# Verificar variables de entorno
echo $ORACLE_HOME
echo $TNS_ADMIN
```

**Solución:**
1. Verificar configuración en `config_db.py`
2. Contactar al administrador de base de datos
3. Verificar credenciales de conexión

---

### **Problema 3: "Proceso no responde"**

**Síntomas:**
- El proceso aparece activo pero no procesa mensajes
- Logs no se actualizan

**Solución:**
```bash
# Detener servicios forzadamente
pkill -9 -f mdm_servidor_his.py
pkill -9 -f orm_cliente_envio.py

# Limpiar archivos PID
rm -f /home/integracioneshe1/vscode_proj/HL7FINAL/pids/*.pid

# Reiniciar servicios
hl7-start
```

---

### **Problema 4: "Permisos insuficientes"**

**Síntomas:**
```
Permission denied
```

**Solución:**
```bash
# Verificar propietario de archivos
ls -la /home/integracioneshe1/vscode_proj/HL7FINAL/

# Corregir permisos si es necesario
chown -R integracioneshe1:integracioneshe1 /home/integracioneshe1/vscode_proj/HL7FINAL/
chmod +x /home/integracioneshe1/vscode_proj/HL7FINAL/*.sh
```

---

### **Problema 5: "Dependencias de Python faltantes"**

**Síntomas:**
```
ModuleNotFoundError: No module named 'cx_Oracle'
```

**Solución:**
```bash
# Verificar entorno virtual
cd /home/integracioneshe1/vscode_proj/HL7FINAL
ls -la venv/

# Activar entorno virtual manualmente
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import cx_Oracle; print('cx_Oracle OK')"
```

---

## 🔍 COMANDOS DE DIAGNÓSTICO

### **Diagnóstico Completo del Sistema**
```bash
#!/bin/bash
echo "=== DIAGNÓSTICO COMPLETO HL7 ==="
echo ""

echo "1. ESTADO DE PROCESOS:"
ps aux | grep -E "(mdm_servidor|orm_cliente)" | grep -v grep || echo "No hay procesos HL7 activos"

echo ""
echo "2. ESTADO DE PUERTOS:"
lsof -i :2590 || echo "Puerto 2590 libre"

echo ""
echo "3. ARCHIVOS PID:"
for pid_file in /home/integracioneshe1/vscode_proj/HL7FINAL/pids/*.pid; do
    if [ -f "$pid_file" ]; then
        echo "$(basename $pid_file): $(cat $pid_file)"
    fi
done

echo ""
echo "4. TAMAÑO DE LOGS:"
du -sh /home/integracioneshe1/vscode_proj/HL7FINAL/logs/* 2>/dev/null || echo "No hay logs"

echo ""
echo "5. ÚLTIMA ACTIVIDAD EN LOGS:"
for log_file in /home/integracioneshe1/vscode_proj/HL7FINAL/logs/*.log; do
    if [ -f "$log_file" ]; then
        echo "$(basename $log_file): $(stat -c %y $log_file)"
    fi
done

echo ""
echo "6. ESPACIO EN DISCO:"
df -h /home/integracioneshe1/vscode_proj/HL7FINAL

echo ""
echo "7. CONECTIVIDAD ORACLE:"
python3 -c "
try:
    import sys, os
    sys.path.append('/home/integracioneshe1/vscode_proj/HL7FINAL')
    from config_db import DB_CONFIG, get_dsn
    import cx_Oracle
    conn = cx_Oracle.connect(user=DB_CONFIG['user'], password=DB_CONFIG['password'], dsn=get_dsn())
    print('✅ Conexión Oracle: OK')
    conn.close()
except Exception as e:
    print(f'❌ Conexión Oracle: {e}')
"
```

---

## 📅 MANTENIMIENTO

### **Tareas Diarias**
- [ ] Verificar estado de servicios (mañana y tarde)
- [ ] Revisar logs por errores
- [ ] Verificar espacio en disco

### **Tareas Semanales**
- [ ] Revisar tamaño de logs y archivar si es necesario
- [ ] Verificar conectividad con Oracle
- [ ] Comprobar rendimiento del sistema

### **Tareas Mensuales**
- [ ] Limpiar logs antiguos (>30 días)
- [ ] Verificar versiones de dependencias
- [ ] Revisar configuración de backup

### **Script de Mantenimiento Automático**
```bash
#!/bin/bash
# Script de mantenimiento semanal

LOG_DIR="/home/integracioneshe1/vscode_proj/HL7FINAL/logs"
BACKUP_DIR="/home/integracioneshe1/backup_hl7_logs"

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

# Comprimir logs antiguos
find "$LOG_DIR" -name "*.log" -mtime +7 -exec gzip {} \;

# Mover logs comprimidos a backup
find "$LOG_DIR" -name "*.log.gz" -mtime +1 -exec mv {} "$BACKUP_DIR" \;

# Limpiar backups muy antiguos
find "$BACKUP_DIR" -name "*.log.gz" -mtime +90 -delete

echo "Mantenimiento completado: $(date)"
```

---

## 📞 CONTACTOS Y ESCALACIÓN

### **Niveles de Escalación**

#### **Nivel 1: Problemas Básicos**
- **Personal de Operaciones TI**
- **Acciones:** Reiniciar servicios, verificar logs básicos
- **Tiempo de resolución:** 15 minutos

#### **Nivel 2: Problemas de Conectividad**
- **Administrador de Redes**
- **Administrador de Base de Datos**
- **Acciones:** Verificar conectividad, permisos de BD
- **Tiempo de resolución:** 1 hora

#### **Nivel 3: Problemas de Aplicación**
- **Desarrollador de Integración HL7**
- **Arquitecto de Sistemas**
- **Acciones:** Análisis de código, debugging avanzado
- **Tiempo de resolución:** 4 horas

### **Información de Contacto**
```
┌─────────────────────────────────────────────┐
│ CONTACTOS DE EMERGENCIA                     │
├─────────────────────────────────────────────┤
│ Operaciones TI:    ext. 1234               │
│ Admin BD Oracle:   ext. 5678               │
│ Desarrollador HL7: ext. 9012               │
│ Supervisor TI:     ext. 3456               │
│                                             │
│ EMAIL ALERTAS: hl7-alerts@hospital.com     │
│ SLACK CHANNEL: #hl7-monitoring             │
└─────────────────────────────────────────────┘
```

## **📄 DELIMITADORES Y PROCESAMIENTO DE PDF**

### **🔍 Identificación de PDF en Mensajes HL7**

El servidor MDM identifica automáticamente los PDFs dentro de los mensajes HL7 utilizando los siguientes criterios en los segmentos OBX:

#### **Criterios de Identificación de PDF:**
```python
# El sistema busca en el campo OBX|5 (valor observado) un PDF en base64
if (fields[2].strip().upper() == 'ED' or      # Tipo de dato: Encapsulated Data
    fields[2].strip().upper() == 'RP' or      # Tipo de dato: Reference Pointer  
    (len(valor) > 100 and fields[5].startswith('^'))):  # String largo que inicia con ^
```

#### **Delimitadores de Texto en PDF:**
El sistema extrae automáticamente el contenido relevante del PDF usando delimitadores específicos:

**Función de Extracción:**
```python
def extract_delimited_text(text):
    start = text.find("Informe")      # Delimitador de INICIO
    end = text.rfind("Atentamente")   # Delimitador de FIN
    if start != -1 and end != -1 and end > start:
        start += len("Informe")
        contenido = text[start:end]
        lineas = [line.strip() for line in contenido.splitlines()]
        lineas = [line for line in lineas if line]
        return "\n".join(lineas)
    return ""
```

#### **Delimitadores Configurados:**
- **INICIO:** `"Informe"` - El sistema busca esta palabra para iniciar la extracción
- **FIN:** `"Atentamente"` - El sistema busca esta palabra para finalizar la extracción

#### **Proceso de Extracción:**
1. **Decodificación Base64:** El PDF codificado en base64 se decodifica a bytes
2. **Extracción de Texto:** Se usa PyMuPDF (fitz) para extraer texto del PDF
3. **OCR Fallback:** Si no hay texto, se usa Tesseract OCR en las imágenes del PDF
4. **Aplicación de Delimitadores:** Se extrae solo el contenido entre "Informe" y "Atentamente"
5. **Limpieza:** Se eliminan líneas vacías y se normaliza el formato

#### **Campos de Base de Datos Relacionados:**
- `INFORME_HTML`: Contiene el PDF original en base64
- `INFORME_TXT`: Contiene el texto extraído y delimitado del PDF

### **📋 EJEMPLO DE MENSAJE HL7 CON PDF**

#### **Estructura Típica de Mensaje MDM con PDF:**
```
MSH|^~\&|HIS|HOSPITAL||RIS|RIS|20250627141000||MDM^T02|654321|2.7|||||||UNICODE UTF-8
PID|||9876543210^^^^DNI||GARCIA^MARIA|LOPEZ|19900202|F|||CALLE FALSA 456^CORDOBA^CORDOBA^CORDOBA^^ARGENTINA||2233445566^maria.garcia@email.com^|
PV1|||^^^^^^^^|E|||DR. PEREZ|||INTERNACION||||||||||PAMI||||||||||||||||||||||||||||||||EQUIPO2
TXA|1|AUT|20250627141000|20250627141500|CDI|123456|INFORME FINAL|DR. PEREZ|20250627141500
OBX|1|ED|PDF^Informe||^JVBERi0xLjMKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwov...||||||F
```

#### **Contenido Típico del PDF (después de la extracción):**
```
Informe
Paciente: García, María
DNI: 9876543210
Fecha: 27/06/2025

RADIOGRAFÍA DE TÓRAX

Técnica: Radiografía simple de tórax en proyección PA y lateral.

Hallazgos:
- Campos pulmonares conservados
- Silueta cardíaca normal
- Sin evidencia de patología pleural
- Estructuras óseas sin alteraciones

Conclusión:
Estudio radiológico sin evidencia de patología torácica aguda.

Atentamente
```

#### **Texto Extraído (INFORME_TXT):**
El sistema extraerá automáticamente solo el contenido entre los delimitadores:
```
Paciente: García, María
DNI: 9876543210
Fecha: 27/06/2025

RADIOGRAFÍA DE TÓRAX

Técnica: Radiografía simple de tórax en proyección PA y lateral.

Hallazgos:
- Campos pulmonares conservados
- Silueta cardíaca normal
- Sin evidencia de patología pleural
- Estructuras óseas sin alteraciones

Conclusión:
Estudio radiológico sin evidencia de patología torácica aguda.
```

### **🔧 CONFIGURACIÓN DE DELIMITADORES PERSONALIZADOS**

Si tu organización usa diferentes delimitadores, puedes personalizarlos editando el archivo:
`/home/integracioneshe1/vscode_proj/HL7FINAL/mdm/mdm_servidor_his.py`

#### **Ubicación del Código:**
```python
def extract_delimited_text(text):
    start = text.find("Informe")        # ← CAMBIAR AQUÍ
    end = text.rfind("Atentamente")     # ← CAMBIAR AQUÍ
    if start != -1 and end != -1 and end > start:
        start += len("Informe")         # ← AJUSTAR LONGITUD
        contenido = text[start:end]
        lineas = [line.strip() for line in contenido.splitlines()]
        lineas = [line for line in lineas if line]
        return "\n".join(lineas)
    return ""
```

#### **Ejemplos de Delimitadores Alternativos:**
```python
# Para informes que usan INICIO/FIN
start = text.find("INICIO INFORME")
end = text.rfind("FIN INFORME")

# Para informes que usan marcadores específicos
start = text.find("=== REPORTE ===")
end = text.rfind("=== FIN REPORTE ===")

# Para informes que terminan con firma
start = text.find("INFORME MÉDICO")
end = text.rfind("Dr.")
```

**⚠️ IMPORTANTE:** Después de modificar los delimitadores:
1. Guardar el archivo
2. Reiniciar el servicio: `hl7-stop && hl7-start`
3. Verificar los logs para confirmar el funcionamiento

## **🚨 TROUBLESHOOTING ESPECÍFICO PARA PDFs**

### **❌ Problema: No se extrae texto del PDF**

#### **Síntomas:**
- El campo `INFORME_TXT` está vacío en la base de datos
- Los logs muestran: `"No se pudo extraer texto del PDF para INFORME_TXT"`

#### **Posibles Causas y Soluciones:**

**1. PDF es una imagen escaneada:**
```bash
# Verificar si Tesseract OCR está instalado
tesseract --version

# Si no está instalado:
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa
```

**2. Delimitadores no encontrados:**
```bash
# Ver el contenido real del PDF extraído
tail -f /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log | grep "Texto que se guardará"
```

**3. PDF corrupto o mal codificado:**
```bash
# Verificar logs de decodificación
grep -i "base64" /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log
```

### **❌ Problema: Delimitadores no reconocidos**

#### **Síntomas:**
- Se extrae todo el texto del PDF sin filtrar
- `INFORME_TXT` contiene información no deseada

#### **Solución:**
1. **Identificar los delimitadores reales:**
   ```bash
   # Guardar temporalmente el PDF para análisis
   # Activar modo debug en mdm_servidor_his.py
   ```

2. **Modificar la función extract_delimited_text():**
   ```python
   # Ejemplo para diferentes formatos de informe
   def extract_delimited_text(text):
       # Buscar múltiples patrones de inicio
       patterns_start = ["Informe", "INFORME", "Reporte", "REPORTE"]
       patterns_end = ["Atentamente", "ATENTAMENTE", "Cordialmente", "Dr.", "Dra."]
       
       start_pos = -1
       end_pos = -1
       
       for pattern in patterns_start:
           pos = text.find(pattern)
           if pos != -1:
               start_pos = pos + len(pattern)
               break
               
       for pattern in patterns_end:
           pos = text.rfind(pattern)
           if pos != -1 and pos > start_pos:
               end_pos = pos
               break
               
       if start_pos != -1 and end_pos != -1:
           contenido = text[start_pos:end_pos]
           lineas = [line.strip() for line in contenido.splitlines()]
           lineas = [line for line in lineas if line]
           return "\n".join(lineas)
       return ""
   ```

### **❌ Problema: PDF no se identifica en el mensaje HL7**

#### **Síntomas:**
- El campo `INFORME_HTML` está vacío
- Los logs no muestran "PDF encontrado"

#### **Verificaciones:**
1. **Formato del segmento OBX:**
   ```
   Correcto: OBX|1|ED|PDF^Informe||^JVBERi0xLjMK...
   Incorrecto: OBX|1|TX|PDF^Informe||JVBERi0xLjMK...  # Sin ^ al inicio
   ```

2. **Tipo de dato en OBX[2]:**
   - Debe ser `ED` (Encapsulated Data) o `RP` (Reference Pointer)
   - No funciona con `TX` (Text)

3. **Longitud del contenido:**
   - El contenido base64 debe tener más de 100 caracteres
   - Debe comenzar con `^` (caret)

### **🔧 HERRAMIENTAS DE DIAGNÓSTICO**

#### **Script de Prueba de PDF:**
Crear archivo `/home/integracioneshe1/vscode_proj/HL7FINAL/test_pdf_extraction.py`:
```python
#!/usr/bin/env python3
import base64
import fitz
import tempfile
import os

def test_pdf_base64(base64_string):
    try:
        # Decodificar base64
        pdf_bytes = base64.b64decode(base64_string)
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpf:
            tmpf.write(pdf_bytes)
            tmp_path = tmpf.name
        
        # Extraer texto
        doc = fitz.open(tmp_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        print(f"Texto extraído ({len(text)} caracteres):")
        print("=" * 50)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("=" * 50)
        
        # Buscar delimitadores
        start = text.find("Informe")
        end = text.rfind("Atentamente")
        
        print(f"Delimitador 'Informe' encontrado en posición: {start}")
        print(f"Delimitador 'Atentamente' encontrado en posición: {end}")
        
        if start != -1 and end != -1:
            extracted = text[start:end]
            print("Texto que sería extraído:")
            print("-" * 30)
            print(extracted)
        
        # Limpiar
        os.unlink(tmp_path)
        
    except Exception as e:
        print(f"Error procesando PDF: {e}")

if __name__ == "__main__":
    # Pegar aquí el string base64 del PDF para probar
    pdf_base64 = input("Pegar el string base64 del PDF: ")
    test_pdf_base64(pdf_base64)
```

#### **Comandos de Diagnóstico Rápido:**
```bash
# Ver últimos PDFs procesados
grep -A 5 -B 5 "PDF base64" /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log

# Ver texto extraído
grep -A 20 "Texto que se guardará" /home/integracioneshe1/vscode_proj/HL7FINAL/logs/mdm_servidor.log

# Verificar dependencias OCR
python3 -c "import pytesseract; print('Tesseract OK')"
python3 -c "import fitz; print('PyMuPDF OK')"
```

### **📋 CHECKLIST DE VERIFICACIÓN PDF**

**✅ Pre-procesamiento:**
- [ ] El mensaje HL7 contiene segmento OBX
- [ ] El campo OBX[2] es ED o RP
- [ ] El campo OBX[5] comienza con ^
- [ ] El contenido base64 tiene más de 100 caracteres

**✅ Procesamiento:**
- [ ] PyMuPDF (fitz) está instalado
- [ ] Tesseract OCR está instalado (para PDFs escaneados)
- [ ] Los delimitadores están configurados correctamente
- [ ] La función extract_delimited_text() retorna contenido

**✅ Post-procesamiento:**
- [ ] El campo INFORME_HTML se guarda en base de datos
- [ ] El campo INFORME_TXT se guarda en base de datos
- [ ] Los logs no muestran errores de extracción
