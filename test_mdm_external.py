import socket
import time
import datetime
import os
import sys
import cx_Oracle
import re
import random

# --- Configuración ---
MDM_HOST = "127.0.0.1" # La IP donde el servidor MDM está escuchando
MDM_PORT = 2590
DB_USER = "SEGMENTOS_HL7"
DB_PASS = "SEGMENTOS_HL7"
DB_HOST = "172.16.60.21"
DB_PORT = 1521
DB_SID = "prdsgh2"
PROJECT_ROOT = "/home/integracioneshe1/vscode_proj/HL7FINAL"

# Añadir el directorio padre al path para importar config_db
sys.path.append(os.path.abspath(os.path.join(PROJECT_ROOT)))

import cx_Oracle # Importar cx_Oracle (asumiendo venv activado externamente)
from config_db import DB_CONFIG, get_dsn # Importar config_db también

# --- Mensaje HL7 MDM de prueba ---
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
unique_id = f"TESTMDM_{int(time.time() * 1000)}"
patient_id = str(random.randint(1000000000, 9999999999)) # ID de 10 dígitos
obr_id = str(random.randint(100000, 999999)) # ID de 6 dígitos

HL7_MESSAGE = (
    f"MSH|^~\\&|TEST_APP|TEST_FACILITY||MDM_HIS|MDM_FACILITY|{timestamp}||MDM^T02|{unique_id}|P|2.3.1\r"
    f"PID|||{patient_id}^^^DNI||DOE^JOHN|||19800101|M|||123 MAIN ST^^ANYTOWN^ST^12345|||||||\r"
    f"OBR|1|{obr_id}||STUDY_CODE^Study Desc|||{timestamp}|||||||||||||||\r"
    f"OBX|1|TX|REPORT_CODE^Report Desc||Este es un informe de prueba generado externamente.||||||F\r"
)

# Delimitadores MLLP
VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'

# --- Funciones de logging ---
def log_info(msg): sys.stdout.write(f"[INFO] {msg}\n")
def log_success(msg): sys.stdout.write(f"[SUCCESS] {msg}\n")
def log_error(msg): sys.stderr.write(f"[ERROR] {msg}\n"); sys.exit(1)

# --- Función para verificar la base de datos ---
max_db_check_attempts = 3
db_check_interval_seconds = 2
def verify_mdm_in_db(unique_id_to_check):
    log_info(f"Verificando inserción del mensaje (ID: {unique_id_to_check}) en la base de datos Oracle...")
    
    # Usamos db_config directamente desde config_db
    dsn_str = get_dsn()
    
    conn = None
    try:
        conn = cx_Oracle.connect(user=DB_CONFIG['user'], password=DB_CONFIG['password'], dsn=dsn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM SEGMENTOS_HL7.MENSAJES_MDM WHERE ID_UNICO_MSG = :unique_id", unique_id=unique_id_to_check)
        count = cursor.fetchone()[0]
        if count > 0:
            log_success(f"Mensaje (ID: {unique_id_to_check}) encontrado en la base de datos Oracle.")
            return True
        else:
            log_error(f"Mensaje (ID: {unique_id_to_check}) NO encontrado en la base de datos Oracle después de {max_db_check_attempts * db_check_interval_seconds} segundos.")
            return False
    except Exception as e:
        log_error(f"Error al consultar la base de datos: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Función principal de la prueba ---
def main():
    log_info("Iniciando prueba externa MDM...")

    # --- Paso 1: Enviar mensaje MDM via MLLP ---
    log_info(f"Enviando mensaje HL7 MDM con ID único: {unique_id} a {MDM_HOST}:{MDM_PORT}...")
    
    full_mllp_message = VT + HL7_MESSAGE.encode('utf-8') + FS + CR
    
    sock = None
    try:
        log_info("--- Mensaje HL7 MDM a enviar ---")
        log_info(HL7_MESSAGE.replace('\r', '\n'))
        log_info("--------------------------------")
        sock = socket.create_connection((MDM_HOST, MDM_PORT), timeout=10) # Timeout de conexión
        sock.sendall(full_mllp_message)
        log_info(f"Mensaje MLLP enviado. Tamaño: {len(full_mllp_message)} bytes.")
        
        # Intentar recibir ACK (Silent-ACK strategy)
        sock.settimeout(5) # Timeout para la respuesta ACK
        ack_response = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            ack_response += chunk
            if FS in chunk: # MLLP end frame
                break
        
        ack_status = "NO_ACK"
        if ack_response:
            ack_str = ack_response.strip(VT + FS + CR).decode('utf-8', errors='replace')
            if "MSA|AA" in ack_str: ack_status = "AA"
            elif "MSA|AE" in ack_str: ack_status = "AE"
            elif "MSA|AR" in ack_str: ack_status = "AR"
            log_info(f"ACK recibido del servidor: '{ack_str}'")
        
        if ack_status == "AA":
            log_success("Mensaje MDM enviado con éxito y ACK (AA) recibido.")
        else:
            log_info(f"Mensaje MDM enviado. No se recibió ACK (AA) o fue de error ({ack_status}). Procediendo a verificar en DB (Silent-ACK strategy).")

    except socket.timeout:
        log_error(f"Timeout al conectar o esperar ACK del servidor {MDM_HOST}:{MDM_PORT}.")
    except Exception as e:
        log_error(f"Fallo al conectar o enviar el mensaje MLLP: {e}")
    finally:
        if sock: sock.close()

    # --- Paso 2: Verificar inserción en la base de datos (con reintentos) ---
    max_db_check_attempts = 3
    db_check_interval_seconds = 2
    
    for i in range(max_db_check_attempts):
        try:
            if verify_mdm_in_db(unique_id):
                log_success("¡Prueba MDM externa completada con éxito!")
                return
        except SystemExit: # verify_mdm_in_db puede llamar sys.exit(1)
            pass # No salir aún, reintentar si es un error temporal de DB

        log_info(f"Reintento {i+1}/{max_db_check_attempts}: Mensaje aún no encontrado en DB. Esperando {db_check_interval_seconds}s...")
        time.sleep(db_check_interval_seconds)
    
    log_error(f"Mensaje (ID: {unique_id}) NO encontrado en la base de datos Oracle después de {max_db_check_attempts} intentos.")

if __name__ == '__main__':
    # Asegurarse de que el script se ejecuta en el directorio del proyecto para path relativo
    os.chdir(PROJECT_ROOT)
    main()
