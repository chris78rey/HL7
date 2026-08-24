# Arquitectura Inferida del Proyecto HL7

## 1. Resumen del Sistema

El proyecto implementa una integración HL7 bidireccional entre el sistema hospitalario (HIS) y el sistema de imágenes (RIS/PACS):

```
                    ┌─────────────────┐
                    │  RIS/PACS 172.16.60.74 │
                    └────────┬────────┘
                             │ MLLP MDM^T02 (puerto 6661)
                             ▼
                    ┌─────────────────┐
                    │  MDM Server      │  ◄─── Puerto TCP 2590
                    │  mdm_servidor_his.py            │
                    └────────┬────────┘
                             │ Inserta en Oracle
                             ▼
                    ┌─────────────────┐
                    │  Oracle DB      │
                    │  SEGMENTOS_HL7.MENSAJES_MDM      │
                    └─────────────────┘
                             ▲
                             │ Lee de Oracle
                             │
                    ┌────────┴────────┐
                    │  ORM Client    │
                    │  orm_cliente_envio.py          │
                    └────────┬────────┘
                             │ MLLP ORM^O01 (puerto 6661)
                             ▼
                    ┌─────────────────┐
                    │  RIS/PACS 172.16.60.71 │
                    └─────────────────┘
```

---

## 2. Contratos de Datos Implícitos

### 2.1 Tablas compartidas (conceptually_related_to)

- `config_db.py` (a través de `get_dsn()` y `DB_CONFIG`) es importado por `mdm/mdm_servidor_his.py` (L20) y `orm/orm_cliente_envio.py` (L9), creando un puente de configuración centralizada entre ambos servicios.

- La tabla `SEGMENTOS_HL7.MENSAJES_MDM` es el sumidero final del servidor MDM. La función `insert_mdm_to_db()` en `mdm/mdm_servidor_his.py:227` inserta 25 campos incluyendo `RAW_MESSAGE`, `INFORME_HTML` (base64 del PDF), e `INFORME_TXT` (texto extraído).

- La tabla `SEGMENTOS_HL7.MENSAJES_ORM` es la cola de salida del cliente ORM. La consulta `SELECT_QUERY` en `orm/orm_cliente_envio.py:33` filtra por `ENVIADO = 0` y `INTENTOS_ENVIO < 500`.

- **Razón de diseño (# WHY):** No existe una relación explícita entre `MENSAJES_MDM` y `MENSAJES_ORM` en la base de datos. El cliente ORM no sabe si la orden que está enviando ya fue procesada por el servidor MDM porque cada servicio opera sobre tablas independientes sin clave de correlación.

### 2.2 Semantically similar_to (Validación de datos)

- La función `validar_email()` en `orm/orm_cliente_envio.py:76` y `validar_telefono()` en `orm/orm_cliente_envio.py:66` validan campos HL7 del segmento PID en el cliente ORM, pero no existen funciones equivalentes en `parse_mdm_message()` (`mdm/mdm_servidor_his.py:53`). El servidor MDM usa valores por defecto generados por `random_string()` y `random_date()` cuando faltan campos, sin validación semántica.

- **Razón de diseño (# WHY):** El servidor MDM está diseñado para aceptar cualquier mensaje y "arreglarlo" con valores aleatorios, priorizando la recepción sobre la integridad. El cliente ORM, en cambio, necesita producir mensajes válidos para ser aceptados por RIS/PACS, por eso valida antes de armar.

### 2.3 Pipeline de extracción de PDF (cadena de fallback)

La función `insert_mdm_to_db()` (`mdm/mdm_servidor_his.py:274-281`) orquesta una cadena de extracción de texto con fallback:

```
1. extract_text_from_pdf()     → PyMuPDF (fitz)
   Si falla o devuelve vacío:
2. extract_text_from_image()    → OpenCV + Tesseract OCR
   Devuelve texto de imagen:
3. extract_delimited_text()     → Recorta entre "informe" y "atentamente"
```

- `extract_text_from_pdf()` en `mdm/mdm_servidor_his.py:515` itera sobre cada página con `page.get_text("text")`.
- Si el PDF es escaneado (sin texto), `extract_text_from_image()` (`mdm/mdm_servidor_his.py:537`) convierte a imagen PNG mediante `preprocess_image_for_ocr()` (`mdm/mdm_servidor_his.py:528`) que usa `cv2.adaptiveThreshold` con umbral gaussiano.
- `extract_delimited_text()` (`mdm/mdm_servidor_his.py:542`) post-procesa buscando `informe` y `atentamente` como delimitadores.

---

## 3. Flujo de Datos Entre Comunidades

### 3.1 `armar_mensaje_orm()` — el nodo más conectado

`armar_mensaje_orm()` en `orm/orm_cliente_envio.py:114` es el god node del grafo con 6 aristas. Construye el mensaje HL7 ORM^O01 concatenando segmentos MSH, PID, PV1, IN1, ORC y OBR. Depende de `formatear_fecha()`, `validar_telefono()`, `validar_email()` y `hl7_safe()` — todas dentro de la misma comunidad "ORM Message Builder".

### 3.2 `get_dsn()` — puente entre comunidades

`get_dsn()` en `config_db.py:13` es importado por `mdm/mdm_servidor_his.py` (L20) y `orm/orm_cliente_envio.py` (L9), conectando la comunidad "DB Config" con las comunidades "MDM Server" y "ORM Client". Su betweenness centrality de 0.156 lo convierte en el puente topológico más importante del grafo.

### 3.3 `insert_mdm_to_db()` — orquestador del pipeline MDM

`insert_mdm_to_db()` en `mdm/mdm_servidor_his.py:227` coordina cuatro funciones de comunidades diferentes:
- `extract_text_from_pdf()` (comunidad 6)
- `extract_text_from_image()` (comunidad 8)
- `extract_delimited_text()` (comunidad 6)
- `get_db_connection()` (comunidad 3, llamada indirectamente vía cx_Oracle.connect)

### 3.4 Flujo de datos del PDF (INFORME_HTML)

El campo `INFORME_HTML` es la variable que transporta el PDF en base64 a través del pipeline. El flujo de datos es:

1. `parse_mdm_message()` (`mdm/mdm_servidor_his.py:53`) extrae el OBX tipo `ED` o `RP` y asigna `campos['INFORME_HTML'] = pdf_base64` (L183). Este es el único punto donde el PDF entra al sistema.
2. `insert_mdm_to_db()` recibe `campos['INFORME_HTML']` y lo pasa a `extract_text_from_pdf()` como `pdf_bytes` decodificado desde base64 (L268-274). El campo `INFORME_HTML` es escrito directamente a la columna `INFORME_HTML` de `SEGMENTOS_HL7.MENSAJES_MDM` (L334).
3. El texto extraído se guarda en `INFORME_TXT` (L294, L335).

**Razón de diseño (# WHY):** El PDF nunca se guarda como archivo en el servidor MDM — se procesa en memoria como stream de bytes, se decodifica, se extrae el texto, y el archivo temporal se elimina. Esto evita acumulación de archivos PDF en disco. La extracción de texto se hace como paso previo a la inserción en BD para tener `INFORME_TXT` disponible junto al `INFORME_HTML` original.

### 3.5 Hiperedge: PDF processing chain

Las tres funciones de extracción de texto participan en un hyperedge de tipo `participate_in` con id `pdf_extraction_fallback_chain`, representando la cadena de fallback: PyMuPDF → OCR (OpenCV+Tesseract) → delimitación. Este patrón es compartido por `insert_mdm_to_db()` y no por `guardar_pdf_desde_base64()` (código muerto).

---

## 4. Patrones de Diseño Observados

### 4.1 Simetría ORM ↔ MDM

| Aspecto              | Cliente ORM                      | Servidor MDM                     |
|----------------------|----------------------------------|----------------------------------|
| tabla                | `MENSAJES_ORM` (leo)            | `MENSAJES_MDM` (escribo)        |
| Puerto               | 6661                             | 2590                             |
| Tipo de mensaje      | ORM^O01                          | MDM^T02                          |
| Retry logic          | `incrementar_intentos()` (L202)  | `INTENTOS_ENVIO < 500` en query |
| MLLP role            | Client (`send_mllp_message`)     | Server (`handle_client`)         |

### 4.2 Falta de validación de ACK

En `orm/orm_cliente_envio.py:243-248`, el cliente ORM marca el mensaje como `ENVIADO = 1` independientemente del contenido del ACK recibido. LaMSA|AA` (acknowledgement) no se parsea ni se verifica.

**Razón de diseño (# WHY):** El comentario en L243 dice "Marcar como enviado SIEMPRE, sin importar el resultado del ACK". Esto sugiere que el equipo decidió que si el socket no lanzó excepción, el mensaje se considera entregado, delegando la responsabilidad de rechazo al servidor RIS.

### 4.3 Puerto 2590 hardcodeado vs. config centralizada

El archivo `mdm/mdm_servidor_his.py:26` tiene `PORT = 2590` hardcodeado, pero `config_db.py` define `MLLP_HIS['port'] = 6661`. El comentario en L29-31 indica que la configuración centralizada está comentada. Esto implica que el servidor MDM usa un puerto distinto al definido en `MLLP_HIS` para desarrollo/pruebas.

---

## 5. Conocimiento Faltante (Inferido sin Soporte Directo)

Las siguientes relaciones no están en el código pero son inferencias arquitectónicas:

- **No existe función `delete_mdm_message()`** en el servidor MDM para marcar mensajes como procesados o eliminarlos después de un tiempo.
- **No existe función `notify_orm_client()`** para notificar al cliente ORM que llegó un nuevo mensaje MDM que pueda afectar una orden pendiente.
- **No existe retry logic en el servidor MDM** para reconectarse a la base de datos si la conexión se pierde durante el procesamiento.
- **El log `ultimo_mdm_recibido.hl7`** en `mdm/mdm_servidor_his.py:389` es un efecto colateral del debug y no tiene propósito en producción.
- **Las funciones `guardar_pdf_desde_base64()`** (`mdm/mdm_servidor_his.py:481`) y `insert_pdf_file_to_db()` (`mdm/mdm_servidor_his.py:495`) no son llamadas desde ningún flujo activo — son código muerto (comentado en L579-620).

---

## 6. Dependencias Externas

| Librería              | Uso                                             | Archivo que la importa              |
|-----------------------|------------------------------------------------|-----------------------------------|
| `cx_Oracle`           | Conexión Oracle                                 | `config_db.py`, `mdm_servidor_his.py`, `orm_cliente_envio.py` |
| `hl7apy`              | (en requirements.txt, no se usa directamente)  | —                                 |
| `fitz` (PyMuPDF)      | Extracción de texto de PDF                      | `mdm_servidor_his.py:10`          |
| `cv2` (OpenCV)        | Preprocesamiento de imagen para OCR             | `mdm_servidor_his.py:11`          |
| `pytesseract`         | OCR                                             | `mdm_servidor_his.py:14`          |
| `PIL` (Pillow)        | Lectura de imagen para OCR                      | `mdm_servidor_his.py:13`          |
