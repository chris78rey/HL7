import sys
import os
import base64
import cx_Oracle
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QTextEdit, QPushButton, QLabel, QMessageBox

# Configuración de la base de datos
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from config_db import DB_CONFIG, get_dsn

db_config = {
    'user': DB_CONFIG['user'],
    'password': DB_CONFIG['password'],
    'dsn': get_dsn()
}

class MDMViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visor MDM HL7")
        self.resize(900, 600)
        self.layout = QVBoxLayout(self)

        self.listWidget = QListWidget()
        self.layout.addWidget(QLabel("Registros MDM (ID_UNICO_MSG)"))
        self.layout.addWidget(self.listWidget)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.layout.addWidget(QLabel("Informe HL7 (INFORME_HTML, truncado si es base64)"))
        self.layout.addWidget(self.textEdit)

        self.btnVerPDF = QPushButton("Ver PDF")
        self.layout.addWidget(self.btnVerPDF)

        self.records = []
        self.load_records()

        self.listWidget.currentRowChanged.connect(self.show_record)
        self.btnVerPDF.clicked.connect(self.save_and_open_pdf)

    def load_records(self):
        with cx_Oracle.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT ID_UNICO_MSG, FECHA_INFORME, INFORME_HTML, PDF
                    FROM SEGMENTOS_HL7.MENSAJES_MDM
                    ORDER BY FECHA_INFORME DESC
                """)
                self.records = []
                for rec in cursor.fetchall():
                    id_unico_msg = rec[0]
                    fecha_informe = rec[1]
                    informe_html = rec[2]
                    pdf_base64 = rec[3]
                    # Convertir LOBs a string si es necesario
                    if hasattr(informe_html, 'read'):
                        informe_html = informe_html.read()
                    if hasattr(pdf_base64, 'read'):
                        pdf_base64 = pdf_base64.read()
                    self.records.append((id_unico_msg, fecha_informe, informe_html, pdf_base64))
                    self.listWidget.addItem(str(id_unico_msg))

    def show_record(self, idx):
        if idx < 0 or idx >= len(self.records):
            self.textEdit.clear()
            return
        id_unico_msg, fecha_informe, informe_html, pdf_base64 = self.records[idx]
        detalles = f"ID: {id_unico_msg}\nFecha: {fecha_informe}\n"
        if informe_html:
            informe_html_str = str(informe_html)
            self.textEdit.setPlainText(detalles + "\n" + informe_html_str[:1000])
        else:
            self.textEdit.setPlainText(detalles + "\nSin informe.")

    def save_and_open_pdf(self):
        idx = self.listWidget.currentRow()
        if idx < 0 or idx >= len(self.records):
            return
        id_unico_msg, fecha_informe, informe_html, pdf_base64 = self.records[idx]
        pdf_data = pdf_base64 or informe_html
        if not pdf_data:
            QMessageBox.warning(self, "Sin PDF", "No hay PDF en este registro.")
            return
        try:
            pdf_bytes = base64.b64decode(pdf_data)
            temp_path = f"mdm_{id_unico_msg}_temp.pdf"
            with open(temp_path, "wb") as f:
                f.write(pdf_bytes)
            # Abrir el PDF con el visor del sistema
            if sys.platform.startswith('linux'):
                os.system(f"xdg-open '{temp_path}'")
            elif sys.platform.startswith('win'):
                os.startfile(temp_path)
            elif sys.platform.startswith('darwin'):
                os.system(f"open '{temp_path}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el PDF: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = MDMViewer()
    viewer.show()
    sys.exit(app.exec_())
