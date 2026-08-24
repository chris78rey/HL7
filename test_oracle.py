import cx_Oracle

# Configuración de la base de datos Oracle
DSN = cx_Oracle.makedsn('172.16.60.21', 1521, sid='prdsgh2')
db_config = {
    'user': 'SEGMENTOS_HL7',
    'password': 'SEGMENTOS_HL7',
    'dsn': DSN
}

try:
    with cx_Oracle.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM MENSAJES_MDM')
            count, = cursor.fetchone()
            print(f"Registros en MENSAJES_MDM: {count}")
except Exception as e:
    print(f"Error de conexión o consulta: {e}")
