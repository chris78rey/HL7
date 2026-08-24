import socket
import threading
import sys
import os
import datetime
import cx_Oracle
import random
import string

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_db import MLLP_HIS, DB_CONFIG, get_dsn

# =============================
# CONFIGURACIÓN DE ENDPOINTS MLLP PARA PRUEBAS Y PRODUCCIÓN
# Cambia estos valores según el entorno
HOST = '172.16.60.74'  # IP local para pruebas o la IP de la interfaz que desees
PORT = 6661            # Puerto para pruebas o producción

# Si quieres usar la configuración centralizada, descomenta lo siguiente:
# from config_db import MLLP_HIS
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

print(f"[MLLP-HIS] Servidor MLLP escuchando en {HOST}:{PORT} (recibe cualquier tipo de mensaje HL7)")

def handle_client(conn, addr):
    print(f"Conexión de: {addr}")
    data = b''
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk
        if FS in chunk:
            break
    print("[DEBUG] Datos crudos recibidos:", data)
    try:
        msg = data.strip(VT + FS + CR).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"[ERROR] Al decodificar mensaje: {e}")
        msg = ''
    print("Mensaje HL7 recibido (sin validar):")
    print(msg.replace('\r', '\n'))
    # Determinar tipo de mensaje HL7
    tipo_msg = ''
    for seg in msg.split('\r'):
        if seg.startswith('MSH|'):
            fields = seg.split('|')
            if len(fields) > 8:
                tipo_msg = fields[8]  # Ejemplo: 'MDM^T02', 'ORM^O01', etc.
            break
    if tipo_msg.startswith('MDM'):
        print("[INFO] Es un mensaje MDM. Procesando y guardando en base de datos...")
        campos = parse_mdm_message(msg)
        insert_mdm_to_db(campos, msg)
        ack = f"MSH|^~\\&|RIS|RIS|HIS|HIS|{campos.get('MSG_TIMESTAMP','')}||ACK^T02|{campos.get('ID_UNICO_MSG','')}|P|2.3.1\rMSA|AA|{campos.get('ID_UNICO_MSG','')}\r"
    else:
        print(f"[INFO] Tipo de mensaje no MDM recibido: {tipo_msg}. Solo se envía ACK genérico.")
        ack = "MSH|^~\\&|GEN|GEN|GEN|GEN|{0}||ACK|1|P|2.3.1\rMSA|AA|1\r".format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    conn.sendall(VT + ack.encode('utf-8') + FS + CR)
    conn.close()
    print("ACK enviado y conexión cerrada.\n")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def random_date():
    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime.now()
    return (start + (end - start) * random.random()).strftime('%Y%m%d')

def parse_mdm_message(msg):
    campos = {}
    segments = msg.split('\r')
    for seg in segments:
        fields = seg.split('|')
        if seg.startswith('MSH|'):
            campos['MSG_TIMESTAMP'] = fields[6] if len(fields) > 6 else ''
            campos['ID_UNICO_MSG'] = fields[9] if len(fields) > 9 else random_string(10)
        elif seg.startswith('PID|'):
            campos['DOC_PACIENTE'] = fields[3].split('^')[0] if len(fields) > 3 else random_string(8)
            campos['TIPO_DOC'] = fields[3].split('^')[4] if len(fields) > 3 and len(fields[3].split('^')) > 4 else 'DNI'
            if len(fields) > 5:
                apellidos = fields[5].split('^')
                campos['APELLIDO_PACIENTE'] = apellidos[0] if len(apellidos) > 0 else 'APELLIDO'
                campos['NOMBRE_PACIENTE'] = apellidos[1] if len(apellidos) > 1 else 'NOMBRE'
            campos['FECHA_NACIMIENTO'] = fields[7] if len(fields) > 7 else random_date()
            campos['SEXO'] = fields[8] if len(fields) > 8 else 'M'
        elif seg.startswith('TXA|'):
            campos['ACCESSION_NUMBER'] = fields[6] if len(fields) > 6 else random_string(8)
            campos['TURNO_ID'] = int(fields[6]) if len(fields) > 6 and fields[6].isdigit() else random.randint(10000,99999)
            campos['MODALIDAD'] = fields[5] if len(fields) > 5 else 'CR'
            campos['ESTUDIO_ID'] = fields[6] if len(fields) > 6 else random_string(8)
            campos['ESTUDIO_DESC'] = fields[7] if len(fields) > 7 else 'ESTUDIO'
            campos['DOC_MED_INFORMANTE'] = fields[8] if len(fields) > 8 else random_string(8)
            campos['APELLIDO_MED_INFORMANTE'] = fields[9] if len(fields) > 9 else 'MEDAPELLIDO'
            campos['NOMBRE_MED_INFORMANTE'] = fields[10] if len(fields) > 10 else 'MEDNOMBRE'
            campos['STUDY_INSTANCE_UID'] = fields[6] if len(fields) > 6 else random_string(12)
            campos['INFORME_HTML'] = fields[8] if len(fields) > 8 else '<b>INFORME</b>'
            campos['ESTADO_RESULTADO'] = 'FI'
            campos['FECHA_INFORME'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            campos['SERVICIO'] = 'SERVICIO'
        elif seg.startswith('OBX|'):
            if len(fields) > 5 and fields[2].strip().upper() == 'ED':
                campos['INFORME_HTML'] = fields[5]
    return campos

def insert_mdm_to_db(campos, raw_message):
    with cx_Oracle.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT NVL(MAX(ID),0)+1 FROM SEGMENTOS_HL7.MENSAJES_MDM')
            new_id = cursor.fetchone()[0]
            cursor.execute('''
                INSERT INTO SEGMENTOS_HL7.MENSAJES_MDM (
                    ID, MSG_TIMESTAMP, ID_UNICO_MSG, DOC_PACIENTE, TIPO_DOC, APELLIDO_PACIENTE, NOMBRE_PACIENTE, FECHA_NACIMIENTO, SEXO,
                    ACCESSION_NUMBER, TURNO_ID, MODALIDAD, ESTUDIO_ID, ESTUDIO_DESC, DOC_MED_INFORMANTE, APELLIDO_MED_INFORMANTE, NOMBRE_MED_INFORMANTE,
                    STUDY_INSTANCE_UID, INFORME_HTML, ESTADO_RESULTADO, FECHA_INFORME, SERVICIO, RAW_MESSAGE
                ) VALUES (
                    :ID, :MSG_TIMESTAMP, :ID_UNICO_MSG, :DOC_PACIENTE, :TIPO_DOC, :APELLIDO_PACIENTE, :NOMBRE_PACIENTE, :FECHA_NACIMIENTO, :SEXO,
                    :ACCESSION_NUMBER, :TURNO_ID, :MODALIDAD, :ESTUDIO_ID, :ESTUDIO_DESC, :DOC_MED_INFORMANTE, :APELLIDO_MED_INFORMANTE, :NOMBRE_MED_INFORMANTE,
                    :STUDY_INSTANCE_UID, :INFORME_HTML, :ESTADO_RESULTADO, :FECHA_INFORME, :SERVICIO, :RAW_MESSAGE
                )''',
                dict(ID=new_id, RAW_MESSAGE=raw_message, **campos)
            )
            conn.commit()
            print(f"[DB] Insertado MENSAJE_MDM ID={new_id}")

if __name__ == "__main__":
    start_server()
