import socket
import time
import cx_Oracle
import datetime
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_db import DB_CONFIG, get_dsn, MLLP_RISPACS

DSN = get_dsn()
db_config = {
    'user': DB_CONFIG['user'],
    'password': DB_CONFIG['password'],
    'dsn': DSN
}

# =============================
# CONFIGURACIÓN DE ENDPOINTS MLLP PARA PRUEBAS Y PRODUCCIÓN
# Cambia estos valores según el entorno
MLLP_HOST = '172.16.60.71'  # IP local para pruebas ORM
MLLP_PORT = 6661            # Puerto para pruebas ORM

# Si quieres usar la configuración centralizada, descomenta lo siguiente:
# from config_db import MLLP_RISPACS
# MLLP_HOST = MLLP_RISPACS['host']
# MLLP_PORT = MLLP_RISPACS['port']

VT = b'\x0b'  # Vertical Tab
FS = b'\x1c'   # File Separator
CR = b'\x0d'   # Carriage Return

SELECT_QUERY = """
SELECT * FROM MENSAJES_ORM
WHERE ENVIADO = 0
  AND NVL(INTENTOS_ENVIO, 0) < 500
ORDER BY
  CASE
    WHEN SUBSTR(FECHA_PROGRAMADA, 1, 8) = TO_CHAR(SYSDATE, 'YYYYMMDD') THEN 0
    ELSE 1
  END,
  FECHA_PROGRAMADA,
  ID
"""

DELAY_ENTRE_MENSAJES = 0
# Parámetro para máximo de intentos de envío
MAX_INTENTOS_ENVIO = 500

def update_mensaje(cursor, id, hl7_message):
    cursor.execute(
        """
        UPDATE MENSAJES_ORM SET ENVIADO = 1, RAW_MESSAGE = :hl7, SISTEMA_ENVIA = 'SGH HE1' WHERE ID = :id
        """,
        hl7=hl7_message,
        id=id
    )

def hl7_safe(val):
    if val is None:
        return ''
    if isinstance(val, str) and val.lower() == 'none':
        return ''
    return str(val)

def validar_telefono(telefono):
    if telefono is None:
        return ''
    telefono = str(telefono)
    # Buscar todos los grupos de al menos 6 dígitos (posibles números)
    numeros = re.findall(r'\d{6,}', telefono)
    if numeros:
        return numeros[0]
    return ''

def validar_email(email):
    if email is None:
        return ''
    email = str(email).strip()
    # Validación simple de email
    if re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
        return email
    return ''

# Configuración de formatos de fecha por campo HL7
HL7_DATE_FORMATS = {
    'MSG_TIMESTAMP': '%Y%m%d%H%M%S',  # ejemplo: 20250623153000
    'FECHA_NACIMIENTO': '%Y%m%d',    # ejemplo: 19800101
    'FECHA_PROGRAMADA': '%Y%m%d%H%M%S',
    # Agrega aquí otros campos si es necesario
}

# Función auxiliar para formatear fechas según el campo
def formatear_fecha(valor, campo):
    if not valor:
        return ''
    formato = HL7_DATE_FORMATS.get(campo, '%Y%m%d')
    if isinstance(valor, str):
        # Si ya viene en formato correcto, lo retorna
        if len(valor) == len(datetime.datetime.now().strftime(formato)):
            return valor
        # Intenta parsear y formatear
        for f in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%Y%m%d', '%Y%m%d%H%M%S']:
            try:
                dt = datetime.datetime.strptime(valor, f)
                return dt.strftime(formato)
            except Exception:
                continue
        return valor  # Si no pudo parsear, retorna como está
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
    msh = (
        f"MSH|^~\\&|{sistema_envia}|{facility_envia}|{receiving_app}|{receiving_facility}|{fecha_hora}||ORM^O01|{hl7_safe(row['ID_UNICO_MSG'])}|P|2.7|||||||UNICODE UTF-8"
    )
    pid = (
        f"PID|||{hl7_safe(row['DOCUMENTO_PACIENTE'])}^^^^{hl7_safe(row['TIPO_DOC'])}||{hl7_safe(row['APELLIDO_PACIENTE'])}^{hl7_safe(row['NOMBRE_PACIENTE'])}|{hl7_safe(row['APELLIDO_MATERNO'])}|{hl7_safe(row['FECHA_NACIMIENTO'])}|{hl7_safe(row['SEXO'])}|||{hl7_safe(row['DOMICILIO'])}||{telefono}|{email}"
    )
    pv1 = (
        f"PV1||{hl7_safe(row['TIPO_TURNO'])}||||||{hl7_safe(row['MATRICULA_DERIVANTE'])}^{hl7_safe(row['APELLIDO_DERIVANTE'])}^{hl7_safe(row['NOMBRE_DERIVANTE'])}|||||||||||{hl7_safe(row['NRO_ORDEN_PV1'])}"
    )
    in1 = (
        f"IN1|1|{hl7_safe(row['FINANCIADOR_PLAN'])}||{hl7_safe(row['FINANCIADOR_NOMBRE'])}"
    )
    orc = (
        f"ORC|NW|{hl7_safe(row['NRO_ORDEN_ORC'])}|||||{hl7_safe(row['FECHA_PROGRAMADA'])}|"
    )
    obr = (
        f"OBR|1|{hl7_safe(row['NRO_ORDEN_OBR'])}||{hl7_safe(row['CODIGO_ESTUDIO'])}^{hl7_safe(row['ESTUDIO_DESCRIPCION'])}|||{hl7_safe(row['FECHA_PROGRAMADA'])}|||||||||||||||||{hl7_safe(row['MODALIDAD'])}"
    )
    mensaje = "\r".join([msh, pid, pv1, in1, orc, obr]) + "\r"
    return mensaje

def print_alert(msg):
    print("\n" + "#"*60)
    print(f"##  {msg.center(54)}  ##")
    print("#"*60 + "\n")
    print("\a")  # Beep sonoro

def send_mllp_message(host, port, hl7_message):
    print(f"[DEBUG] Enviando mensaje HL7 a {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=3) as sock:
            print(f"[INFO] Conexión TCP establecida con el servidor MLLP en {host}:{port}")
            sock.settimeout(1)
            data = VT + hl7_message.encode('utf-8') + FS + CR
            print(f"[DEBUG] Bytes enviados: {data}")
            sock.sendall(data)
            ack = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                ack += chunk
                if FS in chunk:
                    break
            if not ack:
                print_alert("ATENCIÓN: NO SE RECIBIÓ NINGÚN ACK DEL SERVIDOR")
                print("# POSIBLES CAUSAS:")
                print("# 1. El servidor está caído o no está escuchando en el puerto.")
                print("# 2. Hay un firewall o problema de red que bloquea la respuesta.")
                print("# 3. El mensaje llegó pero el servidor no responde con ACK.")
                print("# SUGERENCIAS:")
                print("# - Verifica conectividad con: telnet", host, port)
                print("# - Consulta al admin del servidor si recibió el mensaje.")
                print("# - Haz un tcpdump o wireshark para ver si hay tráfico de respuesta.")
            else:
                print(f"[DEBUG] Bytes ACK recibidos: {ack}")
            ack_str = ack.strip(VT + FS + CR).decode('utf-8', errors='replace')
            if not ack_str:
                print_alert("ATENCIÓN: EL ACK RECIBIDO ESTÁ VACÍO O NO ES VÁLIDO")
                print("# POSIBLES CAUSAS:")
                print("# 1. El servidor respondió pero el mensaje no es un ACK HL7 válido.")
                print("# 2. Hay un proxy o equipo de red que modifica la respuesta.")
                print("# SUGERENCIAS:")
                print("# - Pide al admin del servidor que te muestre el ACK que envía.")
                print("# - Haz una captura de red para ver el contenido real del ACK.")
            else:
                print(f"[DEBUG] ACK decodificado: '{ack_str}'")
            return ack_str
    except Exception as e:
        print_alert(f"ERROR: NO SE PUDO ENVIAR O RECIBIR ACK DEL SERVIDOR\n{e}")
        print("# POSIBLES CAUSAS:")
        print("# 1. El servidor está apagado o la IP/puerto es incorrecto.")
        print("# 2. Hay un firewall o problema de red (timeout o rechaza conexión).")
        print("# 3. El servidor está saturado o no acepta conexiones.")
        print("# SUGERENCIAS:")
        print("# - Prueba ping a la IP y telnet al puerto.")
        print("# - Consulta al admin del servidor si está activo y escuchando.")
        print("# - Haz una captura de red para ver si hay SYN/ACK o rechazos.")
        raise

def incrementar_intentos(cursor, id):
    # Forzar a 0 si es NULL y luego incrementar
    cursor.execute(
        "UPDATE MENSAJES_ORM SET INTENTOS_ENVIO = CASE WHEN INTENTOS_ENVIO IS NULL THEN 1 ELSE INTENTOS_ENVIO + 1 END WHERE ID = :id",
        {"id": id}
    )

def main():
    while True:
        any_sent = False
        with cx_Oracle.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(SELECT_QUERY)
                rows = cursor.fetchall()
                if cursor.description is not None:
                    columns = [col[0] for col in cursor.description]
                else:
                    columns = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    hl7_message = armar_mensaje_orm(row_dict)
                    print("\n--- MENSAJE HL7 ORM A ENVIAR (segmentos separados) ---")
                    for i, segmento in enumerate(hl7_message.strip().split('\r')):
                        print(f"[{i+1}] {segmento}")
                    print("-----------------------------------------------------\n")
                    # NUEVO: Imprimir mensaje HL7 completo, listo para copiar y pegar
                    print("--- MENSAJE HL7 ORM COMPLETO (COPIAR Y PEGAR) ---")
                    print(hl7_message.replace('\r', '\n').strip())
                    print("-------------------------------------------------")
                    # Guardar el mensaje HL7 en la base antes de enviar
                    cursor.execute(
                        "UPDATE MENSAJES_ORM SET RAW_MESSAGE = :hl7 WHERE ID = :id",
                        hl7=hl7_message,
                        id=row_dict['ID']
                    )
                    conn.commit()
                    try:
                        ack = send_mllp_message(MLLP_HOST, MLLP_PORT, hl7_message)
                        print(f"[DEBUG] ACK recibido para mensaje ID {row_dict['ID']}: '{ack}'")
                    except Exception as e:
                        print(f"Error enviando mensaje ID {row_dict['ID']}: {e}")
                    # Marcar como enviado SIEMPRE, sin importar el resultado del ACK
                    cursor.execute(
                        "UPDATE MENSAJES_ORM SET ENVIADO = 1, SISTEMA_ENVIA = 'SGH HE1' WHERE ID = :id",
                        id=row_dict['ID']
                    )
                    conn.commit()
                    print(f"[DEBUG] Mensaje ID {row_dict['ID']} marcado como ENVIADO=1 (sin importar ACK).")
                    any_sent = True
        if not any_sent:
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Proceso detenido por el usuario (Ctrl+C). Cerrando cliente ORM de forma segura.")
        sys.exit(0)
