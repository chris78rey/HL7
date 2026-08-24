# Configuración de base de datos Oracle
DB_CONFIG = {
    'user': 'SEGMENTOS_HL7',
    'password': 'SEGMENTOS_HL7',
    'host': '172.16.60.21',  # IP real de la base de datos
    'port': 1521,
    'sid': 'prdsgh2'
}

def get_dsn():
    import cx_Oracle
    return cx_Oracle.makedsn(DB_CONFIG['host'], DB_CONFIG['port'], sid=DB_CONFIG['sid'])

# =============================
# CONFIGURACIÓN CENTRALIZADA DE MLLP POR SISTEMA
# Cambia aquí la IP y el puerto único para cada sistema principal
MLLP_HIS = {
    'host': '0.0.0.0',  # Cambia por la IP real en producción
    'port': 6661          # Puerto único para el HIS
}
MLLP_RISPACS = {
    'host': '172.16.60.74',  # IP local de tu equipo para pruebas ORM
    'port': 6661          # Puerto único para el RIS/PACS
}
# Ejemplo de uso en scripts:
#   from config_db import MLLP_HIS
#   HOST = MLLP_HIS['host']
#   PORT = MLLP_HIS['port']
#
# Los scripts de servidor MLLP para HIS y RIS/PACS se encuentran en:
#   mllp_his/servidor_mllp_his.py
#   mllp_rispacs/servidor_mllp_rispacs.py
