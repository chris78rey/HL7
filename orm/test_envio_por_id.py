import socket
import time
import cx_Oracle
import datetime
import sys
import os
import re

# Añadir el directorio padre al path para importar config_db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_db import DB_CONFIG, get_dsn

# Configuración de base de datos
DSN = get_dsn()
db_config = {
    'user': DB_CONFIG['user'],
    'password': DB_CONFIG['password'],
    'dsn': DSN
}

# Configuración de MLLP (por defecto para pruebas)
# Se puede ajustar si es necesario, o usar config_db
MLLP_HOST = '172.16.60.71'
MLLP_PORT = 6661

VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'

def hl7_safe(val):
    if val is None: return ''
    if isinstance(val, str) and val.lower() == 'none': return ''
    return str(val)

def validar_telefono(telefono):
    if telefono is None: return ''
    telefono = str(telefono)
    numeros = re.findall(r'\d{6,}', telefono)
    return numeros[0] if numeros else ''

def validar_email(email):
    if email is None: return ''
    email = str(email).strip()
    if re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
        return email
    return ''

HL7_DATE_FORMATS = {
    'MSG_TIMESTAMP': '%Y%m%d%H%M%S',
    'FECHA_NACIMIENTO': '%Y%m%d',
    'FECHA_PROGRAMADA': '%Y%m%d%H%M%S',
}

def formatear_fecha(valor, campo):
    if not valor: return ''
    formato = HL7_DATE_FORMATS.get(campo, '%Y%m%d')
    if isinstance(valor, str):
        if len(valor) == len(datetime.datetime.now().strftime(formato)):
            return valor
        for f in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%Y%m%d', '%Y%m%d%H%M%S']:
            try:
                dt = datetime.datetime.strptime(valor, f)
                return dt.strftime(formato)
            except: continue
        return valor
    elif isinstance(valor, datetime.datetime):
        return valor.strftime(formato)
    return str(valor)

def armar_mensaje_orm(row):
    fecha_hora = formatear_fecha(row.get('MSG_TIMESTAMP', datetime.datetime.now()), 'MSG_TIMESTAMP')
    telefono = validar_telefono(row.get('TELEFONO'))
    email = validar_email(row.get('EMAIL')) if 'EMAIL' in row else ''
    sistema_envia = row.get('SISTEMA_ENVIA', 'HIS HE1') or 'HIS HE1'
    facility_envia = row.get('FACILITY_ENVIA', 'HE1') or 'HE1'
    receiving_app = row.get('RECEIVING_APP', 'VMGESTION') or 'VMGESTION'
    receiving_facility = row.get('RECEIVING_FACILITY', 'VMGESTION') or 'VMGESTION'
    msh = f"MSH|^~\\&|{sistema_envia}|{facility_envia}|{receiving_app}|{receiving_facility}|{fecha_hora}||ORM^O01|{hl7_safe(row['ID_UNICO_MSG'])}|P|2.7|||||||UNICODE UTF-8"
    pid = f"PID|||{hl7_safe(row['DOCUMENTO_PACIENTE'])}^^^^{hl7_safe(row['TIPO_DOC'])}||{hl7_safe(row['APELLIDO_PACIENTE'])}^{hl7_safe(row['NOMBRE_PACIENTE'])}|{hl7_safe(row['APELLIDO_MATERNO'])}|{hl7_safe(row['FECHA_NACIMIENTO'])}|{hl7_safe(row['SEXO'])}|||{hl7_safe(row['DOMICILIO'])}||{telefono}|{email}"
    pv1 = f"PV1||{hl7_safe(row['TIPO_TURNO'])}||||||{hl7_safe(row['MATRICULA_DERIVANTE'])}^{hl7_safe(row['APELLIDO_DERIVANTE'])}^{hl7_safe(row['NOMBRE_DERIVANTE'])}|||||||||||{hl7_safe(row['NRO_ORDEN_PV1'])}"
    in1 = f"IN1|1|{hl7_safe(row['FINANCIADOR_PLAN'])}||{hl7_safe(row['FINANCIADOR_NOMBRE'])}"
    orc = f"ORC|NW|{hl7_safe(row['NRO_ORDEN_ORC'])}|||||{hl7_safe(row['FECHA_PROGRAMADA'])}|"
    obr = f"OBR|1|{hl7_safe(row['NRO_ORDEN_OBR'])}||{hl7_safe(row['CODIGO_ESTUDIO'])}^{hl7_safe(row['ESTUDIO_DESCRIPCION'])}|||{hl7_safe(row['FECHA_PROGRAMADA'])}|||||||||||||||||{hl7_safe(row['MODALIDAD'])}"
    return "\r".join([msh, pid, pv1, in1, orc, obr]) + "\r"

def send_mllp_message(host, port, hl7_message):
    print(f"[DEBUG] Conectando a {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            data = VT + hl7_message.encode('utf-8') + FS + CR
            sock.sendall(data)
            ack = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk: break
                ack += chunk
                if FS in chunk: break
            return ack.strip(VT + FS + CR).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el mensaje: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_envio_por_id.py <ID_DE_MENSAJES_ORM>")
        sys.exit(1)
    
    msg_id = sys.argv[1]
    
    try:
        with cx_Oracle.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM MENSAJES_ORM WHERE ID = :id", id=msg_id)
                row = cursor.fetchone()
                if not row:
                    print(f"No se encontró ningún mensaje con ID={msg_id}")
                    sys.exit(1)
                
                columns = [col[0] for col in cursor.description]
                row_dict = dict(zip(columns, row))
                
                print(f"--- Datos del Registro (ID={msg_id}) ---")
                for k, v in row_dict.items():
                    print(f"{k}: {v}")
                
                hl7_message = armar_mensaje_orm(row_dict)
                print("\n--- Mensaje HL7 Generado ---")
                print(hl7_message.replace('\r', '\n').strip())
                print("----------------------------\n")
                
                print("Intentando enviar...")
                ack = send_mllp_message(MLLP_HOST, MLLP_PORT, hl7_message)
                
                if ack:
                    print(f"ACK Recibido del Servidor:\n{ack}")
                else:
                    print("No se recibió respuesta ACK (verificar timeout o conexión).")
                    
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    main()
