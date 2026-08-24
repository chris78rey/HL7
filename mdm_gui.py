# GUI para inserción de mensajes HL7 MDM en Oracle
# Requiere: pip install PyQt5

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox, QHBoxLayout, QFormLayout, QScrollArea, QGroupBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Importar funciones existentes
dir_actual = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dir_actual, 'mdm'))
try:
    from mdm_servidor_his import parse_mdm_message, insert_mdm_to_db
except ImportError:
    from .mdm_servidor_his import parse_mdm_message, insert_mdm_to_db

class MDMGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('HL7 MDM Loader')
        self.setMinimumSize(600, 500)
        self.setStyleSheet('background-color: #f7f7fa;')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel('Cargar y enviar mensaje HL7 MDM')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.btn_load = QPushButton('Seleccionar archivo HL7')
        self.btn_load.setStyleSheet('padding: 10px; font-size: 14px;')
        self.btn_load.clicked.connect(self.load_hl7_file)
        layout.addWidget(self.btn_load)

        self.lbl_file = QLabel('Ningún archivo seleccionado')
        self.lbl_file.setStyleSheet('color: #888;')
        layout.addWidget(self.lbl_file)

        self.fields_group = QGroupBox('Campos parseados')
        self.fields_layout = QFormLayout()
        self.fields_group.setLayout(self.fields_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.fields_group)
        layout.addWidget(scroll, 1)

        self.btn_insert = QPushButton('Insertar en base de datos')
        self.btn_insert.setStyleSheet('padding: 10px; font-size: 14px; background-color: #4caf50; color: white;')
        self.btn_insert.clicked.connect(self.insert_to_db)
        self.btn_insert.setEnabled(False)
        layout.addWidget(self.btn_insert)

        self.setLayout(layout)
        self.campos = None
        self.msg = None

    def load_hl7_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Seleccionar archivo HL7', '', 'Archivos HL7 (*.hl7 *.txt);;Todos los archivos (*)')
        if file_path:
            self.lbl_file.setText(f'Archivo: {os.path.basename(file_path)}')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.msg = f.read()
                self.campos = parse_mdm_message(self.msg)
                self.show_fields(self.campos)
                self.btn_insert.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'No se pudo leer o parsear el archivo HL7:\n{e}')
                self.btn_insert.setEnabled(False)
                self.fields_layout = QFormLayout()
                self.fields_group.setLayout(self.fields_layout)
        else:
            self.lbl_file.setText('Ningún archivo seleccionado')
            self.btn_insert.setEnabled(False)

    def show_fields(self, campos):
        # Limpiar campos previos
        for i in reversed(range(self.fields_layout.count())):
            self.fields_layout.removeRow(i)
        if not campos:
            self.fields_layout.addRow(QLabel('No se pudieron extraer campos.'))
            return
        for k, v in campos.items():
            key_lbl = QLabel(str(k))
            key_lbl.setStyleSheet('font-weight: bold; color: #333;')
            val_lbl = QLabel(str(v))
            val_lbl.setStyleSheet('color: #222;')
            self.fields_layout.addRow(key_lbl, val_lbl)

    def insert_to_db(self):
        if not self.campos or not self.msg:
            QMessageBox.warning(self, 'Advertencia', 'No hay mensaje HL7 cargado.')
            return
        try:
            insert_mdm_to_db(self.campos, self.msg)
            QMessageBox.information(self, 'Éxito', 'Mensaje insertado correctamente en la base de datos.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al insertar en la base de datos:\n{e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MDMGui()
    gui.show()
    sys.exit(app.exec_())
