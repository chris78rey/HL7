import os

# Configuración de base de datos Oracle
DB_CONFIG = {
    "user": os.environ.get("ORACLE_USER", "SEGMENTOS_HL7"),
    "password": os.environ.get("ORACLE_PASSWORD", "SEGMENTOS_HL7"),
    "host": os.environ.get("ORACLE_HOST", "172.16.60.21"),
    "port": int(os.environ.get("ORACLE_PORT", 1521)),
    "sid": os.environ.get("ORACLE_SID", "prdsgh2"),
}


def get_dsn():
    import cx_Oracle

    return cx_Oracle.makedsn(DB_CONFIG["host"], DB_CONFIG["port"], sid=DB_CONFIG["sid"])


# CONFIGURACIÓN CENTRALIZADA DE MLLP POR SISTEMA
MLLP_HIS = {
    "host": os.environ.get("MLLP_HIS_HOST", "0.0.0.0"),
    "port": int(os.environ.get("MLLP_HIS_PORT", 6661)),
}
MLLP_RISPACS = {
    "host": os.environ.get("MLLP_RISPACS_HOST", "172.16.60.74"),
    "port": int(os.environ.get("MLLP_RISPACS_PORT", 6661)),
}
