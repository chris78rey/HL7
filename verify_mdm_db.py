import cx_Oracle
import os
import sys

def verify_mdm_message_in_db(unique_id, db_user, db_pass, db_host, db_port, db_sid):
    # Añadir el directorio padre al path para importar config_db y activar venv
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    VENV_PATH = "/home/integracioneshe1/vscode_proj/HL7FINAL/venv"
    # Activar el entorno virtual si no está activo
    if "VIRTUAL_ENV" not in os.environ:
        activate_this_file = os.path.join(VENV_PATH, "bin", "activate_this.py")
        if os.path.exists(activate_this_file):
            with open(activate_this_file) as f:
                exec(f.read(), dict(__file__=activate_this_file))
        else:
            sys.stderr.write("Advertencia: Entorno virtual no encontrado o no activado.\n")

    from config_db import get_dsn # Solo necesitamos get_dsn()

    os.environ['DB_USER'] = db_user
    os.environ['DB_PASS'] = db_pass
    
    # Reconstruir el DSN si los parámetros cambian
    dsn_obj = cx_Oracle.makedsn(db_host, db_port, sid=db_sid)
    dsn_str = str(dsn_obj)

    conn = None
    try:
        conn = cx_Oracle.connect(user=db_user, password=db_pass, dsn=dsn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM SEGMENTOS_HL7.MENSAJES_MDM WHERE ID_UNICO_MSG = :unique_id", unique_id=unique_id)
        count = cursor.fetchone()[0]
        if count > 0:
            sys.stdout.write("FOUND")
        else:
            sys.stdout.write("NOT_FOUND")
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.stderr.write("Uso: python verify_mdm_db.py <unique_id> <db_user> <db_pass> <db_host> <db_port> <db_sid>\n")
        sys.exit(1)
    
    unique_id = sys.argv[1]
    db_user = sys.argv[2]
    db_pass = sys.argv[3]
    db_host = sys.argv[4]
    db_port = int(sys.argv[5])
    db_sid = sys.argv[6]
    
    verify_mdm_message_in_db(unique_id, db_user, db_pass, db_host, db_port, db_sid)
