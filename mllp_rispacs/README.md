# 📋 Servidor MLLP para RIS/PACS

Este directorio contiene los scripts y utilidades necesarios para implementar un servidor MLLP que interactúa con sistemas RIS/PACS mediante mensajes HL7. El servidor está diseñado para recibir, procesar y responder mensajes HL7, asegurando una integración eficiente entre sistemas.

---

## 📂 **Estructura del Proyecto**

### **Archivos principales:**
- **`mllp_server.py`**: Implementación del servidor MLLP que escucha mensajes HL7 en el puerto configurado.
- **`config.py`**: Archivo de configuración que define parámetros como el puerto, IP, y otros ajustes del servidor.
- **`hl7_parser.py`**: Utilidad para parsear y validar mensajes HL7 recibidos.
- **`database_handler.py`**: Módulo para interactuar con la base de datos Oracle, incluyendo inserciones y consultas.
- **`README.md`**: Documentación del proyecto.

### **Directorios relacionados:**
- **`logs/`**: Carpeta donde se almacenan los logs generados por el servidor.
- **`tests/`**: Scripts de prueba para validar el funcionamiento del servidor y la integración con RIS/PACS.
- **`examples/`**: Ejemplos de mensajes HL7 utilizados para pruebas y demostraciones.

---

## ⚙️ **Configuración del Servidor**

### **Parámetros principales:**
- **Puerto:** 2590 (por defecto)
- **IP:** 0.0.0.0 (escucha en todas las interfaces)
- **Protocolo:** MLLP (Minimal Lower Layer Protocol)

### **Requisitos:**
- **Python:** Versión 3.12 o superior
- **Dependencias:** 
  - `cx_Oracle` (para conexión con Oracle)
  - `hl7apy` (para parseo de mensajes HL7)
  - `PyMuPDF` (para manejo de PDFs)
  - `pytesseract` (para OCR en PDFs escaneados)

---

## 🚀 **Cómo Ejecutar el Servidor**

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar el entorno virtual (opcional):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Ejecutar el servidor:**
   ```bash
   python3 mllp_server.py
   ```

4. **Verificar logs:**
   ```bash
   tail -f logs/mllp_server.log
   ```

---

## 🧪 **Pruebas y Validación**

### **Pruebas unitarias:**
Ejecuta los tests para validar el funcionamiento del servidor:
```bash
python3 -m unittest discover tests/
```

### **Pruebas con mensajes HL7:**
Utiliza los ejemplos en `examples/` para enviar mensajes HL7 al servidor y verificar la respuesta.

---

## 📊 **Monitoreo y Troubleshooting**

### **Logs:**
Los logs del servidor se almacenan en `logs/mllp_server.log`. Incluyen:
- Mensajes recibidos
- Errores de conexión
- Respuestas ACK/NACK

### **Problemas comunes:**
1. **Error de conexión:** Verifica que el puerto esté disponible y que el servidor esté ejecutándose.
2. **Problemas con HL7:** Usa `hl7_parser.py` para validar el formato del mensaje.
3. **Base de datos:** Asegúrate de que la configuración de Oracle en `config.py` sea correcta.

---

## 📚 **Documentación Adicional**

- **HL7:** [Guía oficial de HL7](https://www.hl7.org/)
- **MLLP:** [Especificación del protocolo MLLP](https://www.hl7.org/documentcenter/public_temp_5C5E1F2F-1C23-BA17-0C9F2E3B9E3B5E3B/mllp.pdf)
- **Oracle:** [Documentación de cx_Oracle](https://cx-oracle.readthedocs.io/)

---

## 🛠️ **Mantenimiento**

### **Recomendaciones:**
- Actualiza las dependencias regularmente.
- Monitorea los logs para identificar problemas.
- Realiza pruebas periódicas con mensajes HL7.

---

## 👥 **Contacto**

Para soporte técnico o consultas, contacta al equipo de integración:
- **Email:** soporte@hl7integraciones.com
- **Teléfono:** +57 123 456 7890
