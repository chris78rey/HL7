import cx_Oracle
import traceback

# Usar el alias TNS definido en tnsnames.ora
usuario = "SEGMENTOS_HL7"
contrasena = "SEGMENTOS_HL7"
dsn = "RAC_NODO2"

print(f"Intentando conectar usando DSN '{dsn}' con usuario {usuario}")

try:
    connection = cx_Oracle.connect(user=usuario, password=contrasena, dsn=dsn)
    print("Conexión exitosa a la base de datos Oracle!")
    cursor = connection.cursor()
    cursor.execute("SELECT sysdate FROM dual")
    result = cursor.fetchone()
    print(f"Fecha y hora en Oracle: {result[0]}")
    cursor.close()
    connection.close()
except Exception as e:
    print(f"Error al conectar: {e}")
    traceback.print_exc()
