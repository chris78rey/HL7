import socket
import sys
import os
import re
import cx_Oracle
import datetime

# Añadir el directorio padre al path para importar config_db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_db import DB_CONFIG, get_dsn

DSN = get_dsn()
db_config = {
    'user': DB_CONFIG['user'],
    'password': DB_CONFIG['password'],
    'dsn': DSN
}

# Configuración de MLLP (IP del RIS/PACS externo)
# Se toma de config_db si es posible, o hardcoded como fallback
try:
    from config_db import MLLP_RISPACS
    MLLP_HOST = MLLP_RISPACS['host']
    MLLP_PORT = MLLP_RISPACS['port']
except ImportError:
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
    numeros = re.findall(r'\d{6,}', str(telefono))
    return numeros[0] if numeros else ''

def formatear_fecha(valor, campo):
    if not valor: return ''
    formato = '%Y%m%d%H%M%S'
    if isinstance(valor, str):
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
    email = row.get('EMAIL', '') or ''
    sistema_envia = row.get('SISTEMA_ENVIA', 'SGH HE1') or 'SGH HE1'
    
    msh = f"MSH|^~\\&|{sistema_envia}|HE1|VMGESTION|VMGESTION|{fecha_hora}||ORM^O01|{hl7_safe(row['ID_UNICO_MSG'])}|P|2.7|||||||UNICODE UTF-8"
    pid = f"PID|||{hl7_safe(row['DOCUMENTO_PACIENTE'])}^^^^{hl7_safe(row['TIPO_DOC'])}||{hl7_safe(row['APELLIDO_PACIENTE'])}^{hl7_safe(row['NOMBRE_PACIENTE'])}|{hl7_safe(row['APELLIDO_MATERNO'])}|{hl7_safe(row['FECHA_NACIMIENTO'])}|{hl7_safe(row['SEXO'])}|||{hl7_safe(row['DOMICILIO'])}||{telefono}|{email}"
    pv1 = f"PV1||{hl7_safe(row['TIPO_TURNO'])}||||||{hl7_safe(row['MATRICULA_DERIVANTE'])}^{hl7_safe(row['APELLIDO_DERIVANTE'])}^{hl7_safe(row['NOMBRE_DERIVANTE'])}|||||||||||{hl7_safe(row['NRO_ORDEN_PV1'])}"
    in1 = f"IN1|1|{hl7_safe(row['FINANCIADOR_PLAN'])}||{hl7_safe(row['FINANCIADOR_NOMBRE'])}"
    orc = f"ORC|NW|{hl7_safe(row['NRO_ORDEN_ORC'])}|||||{hl7_safe(row['FECHA_PROGRAMADA'])}|"
    obr = f"OBR|1|{hl7_safe(row['NRO_ORDEN_OBR'])}||{hl7_safe(row['CODIGO_ESTUDIO'])}^{hl7_safe(row['ESTUDIO_DESCRIPCION'])}|||{hl7_safe(row['FECHA_PROGRAMADA'])}|||||||||||||||||{hl7_safe(row['MODALIDAD'])}"
    return "\r".join([msh, pid, pv1, in1, orc, obr]) + "\r"

def main():
    if len(sys.argv) < 2:
        print("[-] Uso: python orm/enviar_por_id.py <ID>")
        sys.exit(1)
    
    msg_id = sys.argv[1]
    print(f"[*] Procesando envío manual para ID: {msg_id}")

    try:
        conn = cx_Oracle.connect(**db_config)
    except Exception as e:
        print(f"[-] Error al conectar a la base de datos: {e}")
        return

    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM MENSAJES_ORM WHERE ID = :id", id=msg_id)
        row = cursor.fetchone()
        if not row:
            print(f"[-] Error: No se encontró el ID {msg_id}")
            return

        columns = [col[0] for col in cursor.description]
        row_dict = dict(zip(columns, row))
        
        hl7_message = armar_mensaje_orm(row_dict)
        
        # Guardar RAW_MESSAGE y resetear ENVIADO temporalmente para asegurar procesamiento
        cursor.execute("UPDATE MENSAJES_ORM SET RAW_MESSAGE = :hl7, ENVIADO = 0 WHERE ID = :id", 
                      hl7=hl7_message, id=msg_id)
        conn.commit()
        
        print(f"[*] Conectando a RIS/PACS ({MLLP_HOST}:{MLLP_PORT})...")
        try:
            with socket.create_connection((MLLP_HOST, MLLP_PORT), timeout=3) as sock:
                data = VT + hl7_message.encode('utf-8') + FS + CR
                sock.sendall(data)
                print(f"[+] Mensaje enviado con éxito ({len(data)} bytes).")
                
                # Intentar recibir ACK (Silent-ACK strategy)
                sock.settimeout(1)
                try:
                    ack_bytes = sock.recv(4096)
                    if ack_bytes:
                        ack_str = ack_bytes.strip(VT + FS + CR).decode('utf-8', errors='replace')
                        print(f"[+] ACK recibido: {ack_str}")
                except socket.timeout:
                    print("[!] Timeout esperando ACK (Silent-ACK strategy: procediendo con éxito)")
        except Exception as e:
            print(f"[-] Error de conexión/envío: {e}")
            return

        # Marcar como enviado definitivamente
        cursor.execute("UPDATE MENSAJES_ORM SET ENVIADO = 1, SISTEMA_ENVIA = 'SGH HE1 (MANUAL)' WHERE ID = :id", id=msg_id)
        conn.commit()
        print(f"[+] Transacción para ID {msg_id} finalizada correctamente.")
        
    except Exception as e:
        print(f"[-] Error en base de datos: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    main()
