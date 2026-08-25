import socket
import threading
import cx_Oracle
import random
import string
import datetime
import sys
import os
import base64
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import pytesseract
import io
import traceback


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_db import DB_CONFIG, get_dsn

# =============================
# CONFIGURACIÓN DE ENDPOINTS MLLP PARA PRUEBAS Y PRODUCCIÓN
# Cambia estos valores según el entorno
HOST = '0.0.0.0'  # IP local para pruebas o la IP de la interfaz que desees
PORT = 2590            # Puerto para pruebas o producción

# Si quieres usar la configuración centralizada, descomenta lo siguiente:
# from config_db import DB_CONFIG, get_dsn, MLLP_HIS
# HOST = MLLP_HIS['host']
# PORT = MLLP_HIS['port']

VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'

# Configuración de la base de datos Oracle
DSN = get_dsn()
db_config = {
    'user': DB_CONFIG['user'],
    'password': DB_CONFIG['password'],
    'dsn': DSN
}

def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def random_date():
    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime.now()
    return (start + (end - start) * random.random()).strftime('%Y%m%d')

def parse_mdm_message(msg):
    campos = {}
    # Usar \r como separador de segmentos principal
    segments = msg.split('\r')
    
    msh_seg = None
    pid_seg = None
    obr_seg = None
    txa_seg = None
    obx_segs = []

    # Identificar segmentos relevantes (soporta \r y \n)
    for seg in msg.replace('\n', '\r').split('\r'):
        seg = seg.strip()
        if seg.startswith('MSH|'):
            msh_seg = seg
        elif seg.startswith('PID|'):
            pid_seg = seg
        elif seg.startswith('OBR|'):
            obr_seg = seg
        elif seg.startswith('TXA|'):
            txa_seg = seg
        elif seg.startswith('OBX|'):
            obx_segs.append(seg)

    # Parsear MSH
    if msh_seg:
        fields = msh_seg.split('|')
        if len(fields) > 6 and fields[6]:
            try:
                dt = datetime.datetime.strptime(fields[6], '%Y%m%d%H%M%S')
                campos['MSG_TIMESTAMP'] = dt.strftime('%Y%m%d%H%M%S')
            except ValueError:
                print(f"[WARN] Formato de fecha inválido en MSH-7: {fields[6]}. Se usará valor por defecto.")
                campos['MSG_TIMESTAMP'] = ''
        else:
            campos['MSG_TIMESTAMP'] = ''
        campos['ID_UNICO_MSG'] = fields[9] if len(fields) > 9 else ''

    # Parsear PID
    if pid_seg:
        fields = pid_seg.split('|')
        if len(fields) > 3:
            campos['DOC_PACIENTE'] = fields[3].split('^')[0]
            campos['TIPO_DOC'] = fields[3].split('^')[4] if len(fields[3].split('^')) > 4 else 'DNI'
        if len(fields) > 5:
            apellidos = fields[5].split('^')
            campos['APELLIDO_PACIENTE'] = apellidos[0] if len(apellidos) > 0 else ''
            campos['NOMBRE_PACIENTE'] = apellidos[1] if len(apellidos) > 1 else ''
        if len(fields) > 7 and fields[7]:
            try:
                dt = datetime.datetime.strptime(fields[7], '%Y%m%d')
                campos['FECHA_NACIMIENTO'] = dt.strftime('%Y%m%d')
            except ValueError:
                print(f"[WARN] Formato de fecha inválido en PID-7: {fields[7]}. Se usará valor por defecto.")
                campos['FECHA_NACIMIENTO'] = ''
        else:
            campos['FECHA_NACIMIENTO'] = ''
        campos['SEXO'] = fields[8] if len(fields) > 8 else ''

    # Parsear OBR
    if obr_seg:
        fields = obr_seg.split('|')
        print(f"[DEBUG][PARSER] OBR detectado: {obr_seg}")
        if len(fields) > 3:
            numero_obr = fields[3].strip()
            print(f"[DEBUG][PARSER] NUMERO_OBR extraído (OBR-3): '{numero_obr}'")
            if not numero_obr:
                print(f"[WARN][PARSER] NUMERO_OBR extraído está vacío para OBR: {obr_seg}")
            campos['NUMERO_OBR'] = numero_obr
        else:
            print(f"[WARN][PARSER] OBR-3 no encontrado en OBR: {obr_seg}")
            campos['NUMERO_OBR'] = ''
        # OBR-4 puede contener el accession y descripción
        if len(fields) > 4:
            filler_order_number = fields[4].split('^')
            campos['ACCESSION_NUMBER'] = filler_order_number[0] if len(filler_order_number) > 0 else ''
            campos['ESTUDIO_DESC'] = filler_order_number[1] if len(filler_order_number) > 1 else ''
        # OBR-22 es Results Rpt/Status Chng - Date/Time
        if not campos.get('FECHA_INFORME'):
            campos['FECHA_INFORME'] = fields[22] if len(fields) > 22 and fields[22] else ''

    # Parsear TXA
    if txa_seg:
        fields = txa_seg.split('|')
        campos['ACCESSION_NUMBER'] = fields[6] if len(fields) > 6 else ''
        campos['ESTUDIO_DESC'] = fields[7] if len(fields) > 7 else ''
        if len(fields) > 4 and fields[4]:
            try:
                # Intentar parsear la fecha para asegurar que es válida
                dt = datetime.datetime.strptime(fields[4], '%Y%m%d%H%M%S')
                campos['FECHA_INFORME'] = dt.strftime('%Y%m%d%H%M%S')
            except ValueError:
                print(f"[WARN] Formato de fecha inválido en TXA-4: {fields[4]}. Se usará valor por defecto.")
                campos['FECHA_INFORME'] = '' # Dejar que el default lo maneje
        else:
            campos['FECHA_INFORME'] = ''
        campos['STUDY_INSTANCE_UID'] = fields[8] if len(fields) > 8 else '' # Asumiendo que este campo es el UID
        
        if len(fields) > 9:
            medico_informante = fields[9].split('^')
            campos['DOC_MED_INFORMANTE'] = medico_informante[0] if len(medico_informante) > 0 else ''
            campos['APELLIDO_MED_INFORMANTE'] = medico_informante[1] if len(medico_informante) > 1 else ''
            campos['NOMBRE_MED_INFORMANTE'] = medico_informante[2] if len(medico_informante) > 2 else ''
        
        campos['ESTADO_RESULTADO'] = fields[13] if len(fields) > 13 else 'FI'
        campos['SERVICIO'] = fields[14] if len(fields) > 14 else ''
        if len(fields) > 15 and fields[15].strip().isdigit():
            campos['TURNO_ID'] = int(fields[15].strip())
        else:
            campos['TURNO_ID'] = None # El default se encargará


    # Parsear OBX para el informe en base64
    pdf_base64 = None
    # Búsqueda de OBX en todo el mensaje por si viene separado por \n
    for sep in ['\r', '\n']:
        for line in msg.split(sep):
            if line.startswith('OBX|'):
                fields = line.split('|')
                if len(fields) > 5:
                    valor = fields[5].lstrip('^')
                    # Criterios para identificar el PDF en base64
                    if (fields[2].strip().upper() == 'ED' or
                        fields[2].strip().upper() == 'RP' or
                        (len(valor) > 100 and fields[5].startswith('^'))):
                        pdf_base64 = valor
                        break
        if pdf_base64:
            break
    if pdf_base64:
        campos['INFORME_HTML'] = pdf_base64
    
    # --- Valores derivados y por defecto ---
    if campos.get('ACCESSION_NUMBER') and not campos.get('ESTUDIO_ID'):
        campos['ESTUDIO_ID'] = campos['ACCESSION_NUMBER']
    
    # Valores fijos o por defecto que no están en el mensaje de muestra
    campos['MODALIDAD'] = 'CR' # O se podría sacar de TXA si estuviera disponible

    # --- Asegurar que todos los campos requeridos para la BBDD tengan un valor ---
    required_fields_defaults = {
        'MSG_TIMESTAMP': lambda: datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        'ID_UNICO_MSG': lambda: random_string(10),
        'DOC_PACIENTE': lambda: random_string(8),
        'TIPO_DOC': lambda: 'DNI',
        'APELLIDO_PACIENTE': lambda: 'APELLIDO',
        'NOMBRE_PACIENTE': lambda: 'NOMBRE',
        'FECHA_NACIMIENTO': lambda: random_date(),
        'SEXO': lambda: 'U',
        # Solo asignar default a NUMERO_OBR si no existe la clave (no sobrescribir si ya fue asignado)
        'NUMERO_OBR': lambda: campos['NUMERO_OBR'] if 'NUMERO_OBR' in campos else '',
        'ACCESSION_NUMBER': lambda: random_string(8),
        'TURNO_ID': lambda: random.randint(10000, 99999),
        'MODALIDAD': lambda: 'CR',
        'ESTUDIO_ID': lambda: campos.get('ACCESSION_NUMBER') or random_string(8),
        'ESTUDIO_DESC': lambda: 'ESTUDIO',
        'DOC_MED_INFORMANTE': lambda: random_string(8),
        'APELLIDO_MED_INFORMANTE': lambda: 'SIN_APELLIDO',
        'NOMBRE_MED_INFORMANTE': lambda: 'SIN_NOMBRE',
        'STUDY_INSTANCE_UID': lambda: campos.get('ACCESSION_NUMBER') or random_string(12),
        'INFORME_HTML': lambda: '<b>INFORME NO DISPONIBLE</b>',
        'ESTADO_RESULTADO': lambda: 'FI',
        'FECHA_INFORME': lambda: datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        'SERVICIO': lambda: 'RADIOLOGIA' # Valor más específico
    }

    for field, default_func in required_fields_defaults.items():
        if field not in campos or campos[field] in (None, ''):
            campos[field] = default_func()

    print(f"[DEBUG][PARSER] NUMERO_OBR final: {campos.get('NUMERO_OBR')}")
    return campos

def insert_mdm_to_db(campos, raw_message):
    # --- CHEQUEO PREVIO DE CAMPOS REQUERIDOS ---
    required_fields = [
        'MSG_TIMESTAMP', 'ID_UNICO_MSG', 'DOC_PACIENTE', 'TIPO_DOC', 'APELLIDO_PACIENTE', 'NOMBRE_PACIENTE',
        'FECHA_NACIMIENTO', 'SEXO', 'ACCESSION_NUMBER', 'TURNO_ID', 'MODALIDAD', 'ESTUDIO_ID', 'ESTUDIO_DESC',
        'DOC_MED_INFORMANTE', 'APELLIDO_MED_INFORMANTE', 'NOMBRE_MED_INFORMANTE', 'STUDY_INSTANCE_UID',
        'INFORME_HTML', 'ESTADO_RESULTADO', 'FECHA_INFORME', 'SERVICIO'
    ]
    missing = [f for f in required_fields if f not in campos or campos[f] in (None, '')]
    if missing:
        print(f"[ERROR][PRE-INSERT] Faltan campos requeridos para el insert: {missing}")
        print(f"[ERROR][PRE-INSERT] Campos actuales: {campos}")
        raise Exception(f"Faltan campos requeridos para el insert: {missing}")
    try:
        print("[DEBUG] Datos a insertar en Oracle:")
        for k, v in campos.items():
            print(f"  {k}: {repr(v)}")
        print(f"  RAW_MESSAGE: {repr(raw_message)[:200]}... (truncado)")
        with cx_Oracle.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT NVL(MAX(ID),0)+1 FROM SEGMENTOS_HL7.MENSAJES_MDM')
                new_id = cursor.fetchone()[0]
                try:
                    # --- NUEVO: Extraer PDF base64 antes de insertar ---
                    pdf_base64 = None
                    for sep in ['\r', '\n']:
                        for line in raw_message.split(sep):
                            if line.startswith('OBX|'):
                                fields = line.split('|')
                                if len(fields) > 5:
                                    valor = fields[5].lstrip('^')
                                    if (fields[2].strip().upper() == 'ED' or
                                        fields[2].strip().upper() == 'RP' or
                                        (len(valor) > 100 and fields[5].startswith('^'))):
                                        pdf_base64 = valor
                                        break
                        if pdf_base64:
                            break
                    informe_txt = None
                    if pdf_base64:
                        try:
                            import tempfile
                            import base64
                            pdf_bytes = base64.b64decode(pdf_base64)
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpf:
                                tmpf.write(pdf_bytes)
                                tmp_pdf_path = tmpf.name
                            text_pdf = extract_text_from_pdf(tmp_pdf_path)
                            if not text_pdf:
                                doc = fitz.open(tmp_pdf_path)
                                page = doc.load_page(0)
                                pix = page.get_pixmap()
                                img_bytes = pix.tobytes("png")
                                text_pdf = extract_text_from_image(img_bytes)
                            informe_txt = extract_delimited_text(text_pdf)
                            if not informe_txt:
                                informe_txt = text_pdf
                            print(f"[DEBUG][INSERT] Texto que se guardará en INFORME_TXT:\n{informe_txt}")
                            os.unlink(tmp_pdf_path)
                        except Exception as e:
                            print(f"[ERROR][INSERT] No se pudo extraer texto del PDF para INFORME_TXT: {e}")
                    # --- FIN NUEVO ---
                    try:
                        # --- REFACTOR: Construir el diccionario de parámetros de forma segura ---
                        insert_params = campos.copy()
                        insert_params['ID'] = new_id
                        insert_params['RAW_MESSAGE'] = raw_message
                        insert_params['INFORME_TXT'] = informe_txt
                        
                        # El parser ya se asegura de que NUMERO_OBR exista con un valor por defecto.
                        print(f"[DEBUG][INSERT] Valor de NUMERO_OBR enviado a Oracle: {insert_params.get('NUMERO_OBR')}")
                        cursor.execute('''
                            INSERT INTO SEGMENTOS_HL7.MENSAJES_MDM (
                                ID, MSG_TIMESTAMP, ID_UNICO_MSG, DOC_PACIENTE, TIPO_DOC, APELLIDO_PACIENTE, NOMBRE_PACIENTE, FECHA_NACIMIENTO, SEXO,
                                ACCESSION_NUMBER, TURNO_ID, MODALIDAD, ESTUDIO_ID, ESTUDIO_DESC, DOC_MED_INFORMANTE, APELLIDO_MED_INFORMANTE, NOMBRE_MED_INFORMANTE,
                                STUDY_INSTANCE_UID, ESTADO_RESULTADO, FECHA_INFORME, SERVICIO, NUMERO_OBR,
                                RAW_MESSAGE, INFORME_HTML, INFORME_TXT
                            ) VALUES (
                                :ID, :MSG_TIMESTAMP, :ID_UNICO_MSG, :DOC_PACIENTE, :TIPO_DOC, :APELLIDO_PACIENTE, :NOMBRE_PACIENTE, :FECHA_NACIMIENTO, :SEXO,
                                :ACCESSION_NUMBER, :TURNO_ID, :MODALIDAD, :ESTUDIO_ID, :ESTUDIO_DESC, :DOC_MED_INFORMANTE, :APELLIDO_MED_INFORMANTE, :NOMBRE_MED_INFORMANTE,
                                :STUDY_INSTANCE_UID, :ESTADO_RESULTADO, :FECHA_INFORME, :SERVICIO, :NUMERO_OBR,
                                :RAW_MESSAGE, :INFORME_HTML, :INFORME_TXT
                            )''',
                            {
                                'ID': new_id,
                                'MSG_TIMESTAMP': insert_params['MSG_TIMESTAMP'],
                                'ID_UNICO_MSG': insert_params['ID_UNICO_MSG'],
                                'DOC_PACIENTE': insert_params['DOC_PACIENTE'],
                                'TIPO_DOC': insert_params['TIPO_DOC'],
                                'APELLIDO_PACIENTE': insert_params['APELLIDO_PACIENTE'],
                                'NOMBRE_PACIENTE': insert_params['NOMBRE_PACIENTE'],
                                'FECHA_NACIMIENTO': insert_params['FECHA_NACIMIENTO'],
                                'SEXO': insert_params['SEXO'],
                                'ACCESSION_NUMBER': insert_params['ACCESSION_NUMBER'],
                                'TURNO_ID': insert_params['TURNO_ID'],
                                'MODALIDAD': insert_params['MODALIDAD'],
                                'ESTUDIO_ID': insert_params['ESTUDIO_ID'],
                                'ESTUDIO_DESC': insert_params['ESTUDIO_DESC'],
                                'DOC_MED_INFORMANTE': insert_params['DOC_MED_INFORMANTE'],
                                'APELLIDO_MED_INFORMANTE': insert_params['APELLIDO_MED_INFORMANTE'],
                                'NOMBRE_MED_INFORMANTE': insert_params['NOMBRE_MED_INFORMANTE'],
                                'STUDY_INSTANCE_UID': insert_params['STUDY_INSTANCE_UID'],
                                'ESTADO_RESULTADO': insert_params['ESTADO_RESULTADO'],
                                'FECHA_INFORME': insert_params['FECHA_INFORME'],
                                'SERVICIO': insert_params['SERVICIO'],
                                'NUMERO_OBR': insert_params['NUMERO_OBR'],
                                'RAW_MESSAGE': insert_params['RAW_MESSAGE'],
                                'INFORME_HTML': insert_params['INFORME_HTML'],
                                'INFORME_TXT': insert_params['INFORME_TXT']
                            }
                        )
                        conn.commit()
                        print(f"[DB] Insertado MENSAJE_MDM ID={new_id} (con INFORME_TXT)")
                    except Exception as e:
                        print(f"[ERROR][ORACLE][INSERT] Al insertar en MENSAJES_MDM: {e}")
                        # Para depuración, imprimir los parámetros que fallaron
                        debug_params = insert_params.copy() if 'insert_params' in locals() else campos.copy()
                        # No imprimir LOBs completos en el log
                        for key in ['RAW_MESSAGE', 'INFORME_HTML', 'INFORME_TXT']:
                            if debug_params.get(key) and isinstance(debug_params[key], (str, bytes)):
                                debug_params[key] = repr(debug_params[key][:200]) + '...'
                        print(f"[ERROR][ORACLE][INSERT] Datos enviados: {debug_params}")
                        raise  # Lanzar la excepción para que se vea el error en consola
                except Exception as e:
                    print(f"[ERROR][ORACLE][INNER] Error inesperado en bloque de inserción: {e}")
                    raise
    except Exception as e:
        print(f"[ERROR][ORACLE] Error general en insert_mdm_to_db: {e}")
        raise

def handle_client(conn, addr):
    print(f"Conexión de: {addr}")
    data = b''
    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if FS in chunk:
                break
    except ConnectionResetError:
        print(f"[WARN] Conexión cerrada por el cliente {addr}")
        return

    print("[DEBUG] Datos crudos recibidos:", data)
    try:
        msg = data.strip(VT + FS + CR).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"[ERROR] Al decodificar mensaje: {e}")
        msg = ''
    
    if not msg:
        print("[INFO] Mensaje vacío recibido. Cerrando conexión.")
        conn.close()
        return

    print("Mensaje MDM recibido (sin validar):")
    print(msg.replace('\r', '\n'))
    
    # Guardar el último mensaje HL7 recibido en un archivo
    try:
        with open("ultimo_mdm_recibido.hl7", "w", encoding="utf-8") as f:
            f.write(msg)
        print("[INFO] Mensaje HL7 recibido guardado en 'ultimo_mdm_recibido.hl7'")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el HL7 recibido: {e}")

    try:
        campos = parse_mdm_message(msg)
        insert_mdm_to_db(campos, msg)
        # El manejo del PDF ahora está centralizado dentro de insert_mdm_to_db y funciones posteriores
        # por lo que la llamada a guardar_pdf_desde_obx se puede eliminar de aquí para evitar duplicados.

        # ACK simple
        ack = f"MSH|^~\\&|RIS|RIS|HIS|HIS|{campos.get('MSG_TIMESTAMP','')}||ACK^T02|{campos.get('ID_UNICO_MSG','')}|P|2.3.1\rMSA|AA|{campos.get('ID_UNICO_MSG','')}\r"
        conn.sendall(VT + ack.encode('utf-8') + FS + CR)
    
    except Exception as e:
        print(f"[FATAL] Error procesando el mensaje de {addr}: {e}")
        traceback.print_exc()  # Imprimir el traceback completo
        # Enviar un ACK de error si es posible
        try:
            id_unico_msg = msg.split('|')[9] if '|' in msg else ''
            nack = f"MSH|^~\\&|RIS|RIS|HIS|HIS|{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}||ACK^T02|{id_unico_msg}|P|2.3.1\rMSA|AE|{id_unico_msg}\r"
            conn.sendall(VT + nack.encode('utf-8') + FS + CR)
        except Exception as ack_e:
            print(f"[ERROR] No se pudo enviar NACK: {ack_e}")

    finally:
        # Ya no se guardan ni abren PDFs automáticamente
        conn.close()
        print("Conexión cerrada.\n")


def start_server():
    # Asegurarse de que el puerto se lee de los argumentos si se proporcionan
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        s.listen()
        print(f"Servidor MLLP MDM escuchando en {HOST}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos Oracle."""
    try:
        return cx_Oracle.connect(**db_config)
    except cx_Oracle.Error as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        return None

def get_mensajes_mdm_ordenados():
    """Recupera todos los mensajes de la tabla MENSAJES_MDM, lee los LOBs y devuelve una lista de diccionarios."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SEGMENTOS_HL7.MENSAJES_MDM WHERE ROWNUM <= 1 ORDER BY FECHA_INFORME DESC")
        
        columns = [col[0] for col in cursor.description]
        fetched_rows = cursor.fetchall()
        
        results = []
        for row in fetched_rows:
            row_dict = {}
            for i, col_name in enumerate(columns):
                val = row[i]
                if isinstance(val, cx_Oracle.LOB):
                    try:
                        row_dict[col_name] = val.read()
                    except cx_Oracle.Error as lob_error:
                        print(f"[WARN] No se pudo leer el LOB para la columna {col_name}: {lob_error}")
                        row_dict[col_name] = None # O un valor por defecto
                else:
                    row_dict[col_name] = val
            results.append(row_dict)
            
        print(f"[INFO] Se procesaron {len(results)} mensajes.")
        return results
        
    except cx_Oracle.Error as e:
        print(f"[ERROR] Error al conectar o consultar la base de datos: {e}")
        return []
    finally:
        if conn:
            conn.close()

def guardar_pdf_desde_base64(base64_str, nombre_archivo):
    """
    Decodifica un string base64 y lo guarda como archivo PDF.
    """
    try:
        pdf_bytes = base64.b64decode(base64_str)
        with open(nombre_archivo, 'wb') as f:
            f.write(pdf_bytes)
        print(f"[INFO] PDF guardado en: {nombre_archivo}")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el PDF: {e}")
        return False

def insert_pdf_file_to_db(pdf_path, id_unico_msg):
    """
    Lee un archivo PDF y lo guarda como base64 en el campo PDF (CLOB) de la base de datos, usando el ID_UNICO_MSG para identificar el registro.
    """
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        with cx_Oracle.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE SEGMENTOS_HL7.MENSAJES_MDM
                    SET PDF = :pdf_base64
                    WHERE ID_UNICO_MSG = :id_unico_msg
                ''', {'pdf_base64': pdf_base64, 'id_unico_msg': id_unico_msg})
                conn.commit()
        print(f"[INFO] PDF de {pdf_path} almacenado en la base de datos en el campo PDF para ID_UNICO_MSG={id_unico_msg}")
    except Exception as e:
        print(f"[ERROR] No se pudo almacenar el PDF en la base de datos: {e}")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if not text.strip():
            text = page.get_text("blocks")
            if isinstance(text, list):
                text = "\n".join([b[4] for b in text if len(b) > 4 and isinstance(b[4], str)])
        all_text.append(text.strip())
    return "\n".join(all_text)

def preprocess_image_for_ocr(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 2)
    is_success, buffer = cv2.imencode(".png", thresh)
    return buffer.tobytes() if is_success else img_bytes

def extract_text_from_image(img_bytes):
    pre_img_bytes = preprocess_image_for_ocr(img_bytes)
    img = Image.open(io.BytesIO(pre_img_bytes))
    return pytesseract.image_to_string(img, lang='spa')

def extract_delimited_text(text):
    # Convertir el texto a minúsculas para la búsqueda, pero mantener el original
    text_lower = text.lower()
    
    # Buscar los delimitadores en minúsculas (insensible a mayúsculas/minúsculas)
    start = text_lower.find("informe")
    end = text_lower.rfind("atentamente")
    
    if start != -1 and end != -1 and end > start:
        # Usar las posiciones encontradas en el texto original
        start += len("informe")
        contenido = text[start:end]
        
        # Eliminar las palabras específicas sin destruir el caso original
        import re
        contenido = re.sub(r"hospital de especialidades", "", contenido, flags=re.IGNORECASE)
        contenido = re.sub(r"ff\.aa nº 1", "", contenido, flags=re.IGNORECASE)

        lineas = [line.strip() for line in contenido.splitlines()]
        # Solo incluir líneas que no estén vacías después de quitar espacios
        lineas = [line for line in lineas if line]
        return "\n".join(lineas)
    return ""

def update_informe_txt_in_db(id_unico_msg, informe_txt):
    try:
        with cx_Oracle.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE SEGMENTOS_HL7.MENSAJES_MDM
                    SET INFORME_TXT = :informe_txt
                    WHERE ID_UNICO_MSG = :id_unico_msg
                ''', {'informe_txt': informe_txt, 'id_unico_msg': id_unico_msg})
                conn.commit()
        print(f"[INFO] INFORME_TXT actualizado para ID_UNICO_MSG={id_unico_msg}")
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar INFORME_TXT: {e}")

# Eliminar función guardar_pdf_desde_obx y guardar_pdf_desde_base64, y la llamada en el bloque if __name__ == "__main__"
# def guardar_pdf_desde_obx(campos, raw_message, nombre_archivo=None):
#     import base64
#     pdf_base64 = None
#     for sep in ['\r', '\n']:
#         for line in raw_message.split(sep):
#             if line.startswith('OBX|'):
#                 fields = line.split('|')
#                 if len(fields) > 5:
#                     valor = fields[5].lstrip('^')
#                     if (fields[2].strip().upper() == 'ED' or
#                         fields[2].strip().upper() == 'RP' or
#                         (len(valor) > 100 and fields[5].startswith('^'))):
#                         pdf_base64 = valor
#                         break
#         if pdf_base64:
#             break
#     if pdf_base64:
#         try:
#             pdf_bytes = base64.b64decode(pdf_base64)
#             if not nombre_archivo:
#                 nombre_archivo = f"mdm_{campos.get('ID_UNICO_MSG','')}.pdf"
#             with open(nombre_archivo, 'wb') as f:
#                 f.write(pdf_bytes)
#             print(f"[INFO] PDF extraído y guardado en: {nombre_archivo}")
#             insert_pdf_file_to_db(nombre_archivo, campos.get('ID_UNICO_MSG',''))
#             # --- NUEVO: extraer texto y guardar en INFORME_TXT ---
#             text_pdf = extract_text_from_pdf(nombre_archivo)
#             if not text_pdf:
#                 import fitz
#                 doc = fitz.open(nombre_archivo)
#                 page = doc.load_page(0)
#                 pix = page.get_pixmap()
#                 img_bytes = pix.tobytes("png")
#                 text_pdf = extract_text_from_image(img_bytes)
#             informe_text = extract_delimited_text(text_pdf)
#             update_informe_txt_in_db(campos.get('ID_UNICO_MSG',''), informe_text)
#         except Exception as e:
#             print(f"[ERROR] No se pudo decodificar, guardar el PDF o extraer el informe: {e}")
#     else:
#         print("[INFO] No se encontró PDF en base64 en el mensaje HL7.")

# Ejemplo de uso: guardar el PDF del último mensaje recibido
if __name__ == "__main__":
    try:
        mensajes = get_mensajes_mdm_ordenados()
        if mensajes:
            # Ya no se guarda el PDF, solo se informa si hay mensaje
            print("[INFO][STARTUP] Último mensaje cargado en memoria.")
        else:
            print("[INFO][STARTUP] No hay mensajes previos en la base de datos.")
    except Exception as e:
        print(f"[ERROR][STARTUP] No se pudo procesar el mensaje inicial: {e}")
    
    start_server()
