import cx_Oracle
import base64
import os
import sys

# Importa la configuración de la base de datos desde config_db.py
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from config_db import DB_CONFIG, get_dsn

db_config = {
    'user': DB_CONFIG['user'],
    'password': DB_CONFIG['password'],
    'dsn': get_dsn()
}

# Carpeta de salida
os.makedirs('pdfs_extraidos', exist_ok=True)

with cx_Oracle.connect(**db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute('''
            SELECT ID_UNICO_MSG, PDF, INFORME_HTML FROM SEGMENTOS_HL7.MENSAJES_MDM
            WHERE PDF IS NOT NULL OR INFORME_HTML IS NOT NULL
        ''')
        for id_unico_msg, pdf_clob, informe_html_clob in cursor.fetchall():
            # PDF desde campo PDF
            if pdf_clob:
                pdf_base64 = pdf_clob.read() if hasattr(pdf_clob, 'read') else pdf_clob
                try:
                    pdf_bytes = base64.b64decode(pdf_base64)
                    pdf_path = f"pdfs_extraidos/pdf_{id_unico_msg}_PDF.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_bytes)
                    print(f"[OK] PDF extraído de campo PDF: {pdf_path}")
                except Exception as e:
                    print(f"[ERROR] PDF campo PDF ID {id_unico_msg}: {e}")
            # PDF desde campo INFORME_HTML
            if informe_html_clob:
                informe_base64 = informe_html_clob.read() if hasattr(informe_html_clob, 'read') else informe_html_clob
                try:
                    pdf_bytes = base64.b64decode(informe_base64)
                    pdf_path = f"pdfs_extraidos/pdf_{id_unico_msg}_INFORME_HTML.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_bytes)
                    print(f"[OK] PDF extraído de campo INFORME_HTML: {pdf_path}")
                except Exception as e:
                    print(f"[ERROR] PDF campo INFORME_HTML ID {id_unico_msg}: {e}")
