import sys
import difflib
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt5.QtGui import QFont
from hl7apy.parser import parse_message

def try_autocorrect_segment(segment):
    # Corrige errores comunes en segmentos HL7 (por ahora solo MSH P|2.7)
    if segment.startswith('MSH|') and '|P|2.7|' in segment:
        explicacion = (
            "El campo MSH.12 (versión HL7) y MSH.13 (Processing ID) están invertidos. "
            "La versión HL7 debe ir antes que el Processing ID. Por ejemplo: '|2.7|P|' en vez de '|P|2.7|'."
        )
        return segment.replace('|P|2.7|', '|2.7|P|'), True, 'MSH.12/13', explicacion
    # Ejemplo para PID.5 (nombre del paciente vacío)
    if segment.startswith('PID|'):
        fields = segment.split('|')
        if len(fields) > 5 and not fields[5]:
            explicacion = (
                "El campo PID.5 (Nombre del paciente) está vacío. Debe contener el nombre y apellido del paciente, por ejemplo: 'PEREZ^JUAN'."
            )
            # No autocorrige, solo informa
            return segment, False, 'PID.5', explicacion
        if len(fields) > 7 and not fields[7]:
            explicacion = (
                "El campo PID.7 (Fecha de nacimiento) está vacío. Debe contener la fecha de nacimiento en formato YYYYMMDD."
            )
            return segment, False, 'PID.7', explicacion
    # Puedes agregar más reglas para otros campos aquí
    return segment, False, None, None

def validate_hl7_message(msg):
    logs = []
    autocorrected_segments = set()
    # Intento de validación y autocorrección iterativa
    for _ in range(3):  # Hasta 3 ciclos de autocorrección
        parse_error = None
        try:
            parsed = parse_message(msg, find_groups=False)
            logs.append("[OK] Mensaje HL7 parseado correctamente con hl7apy.")
            # Validar todos los campos de todos los segmentos
            for segment in parsed.children:
                for field in segment.children:
                    if hasattr(field, 'value') and (field.value is None or str(field.value).strip() == ""):
                        logs.append(f"[WARN] {segment.name}.{field.name} está vacío. Por favor complete este campo.")
            break  # Si parsea bien, salimos del ciclo
        except Exception as e:
            parse_error = f"[ERROR] Error al parsear HL7: {e}"
            logs.append(parse_error)
            # Intentar autocorregir segmento problemático
            segments = msg.split('\r')
            changed = False
            for i, seg in enumerate(segments):
                seg_corr, was_corr, campo_humano, explicacion = try_autocorrect_segment(seg)
                if was_corr and seg not in autocorrected_segments:
                    segments[i] = seg_corr
                    autocorrected_segments.add(seg)
                    if campo_humano and explicacion:
                        logs.append(f"[AUTOCORRECT] Se corrigió el campo {campo_humano}: {explicacion}")
                    elif campo_humano:
                        logs.append(f"[AUTOCORRECT] Segmento corregido automáticamente: {seg.split('|')[0]} (campo: {campo_humano})")
                    else:
                        logs.append(f"[AUTOCORRECT] Segmento corregido automáticamente: {seg.split('|')[0]}")
                    changed = True
                elif not was_corr and campo_humano and explicacion:
                    logs.append(f"[ERROR] {campo_humano}: {explicacion}")
            if changed:
                msg = '\r'.join(segments)
                continue  # Reintentar parseo con mensaje corregido
            else:
                break  # No se pudo autocorregir más
    # Validaciones adicionales básicas (siempre se ejecutan)
    REQUIRED_SEGMENTS = ['MSH', 'SCH', 'PID', 'PV1']
    SEGMENT_FIELDS = {
        'MSH': 12,
        'SCH': 5,
        'PID': 5,
        'PV1': 5,
    }
    segments = msg.split('\r')
    for seg in segments:
        if not seg.strip():
            continue
        seg_type = seg.split('|')[0]
        if seg_type in SEGMENT_FIELDS:
            expected = SEGMENT_FIELDS[seg_type]
            actual = seg.count('|')
            if actual < expected:
                logs.append(f"[WARN] Segmento {seg_type} tiene solo {actual} campos, se esperaban al menos {expected}.")
        if seg_type == 'PID':
            fields = seg.split('|')
            if len(fields) > 5 and not fields[5]:
                logs.append("[WARN] PID.5 (Nombre del paciente) está vacío. Por favor complete este campo.")
            if len(fields) > 7 and not fields[7]:
                logs.append("[WARN] PID.7 (Fecha de nacimiento) está vacío. Por favor complete este campo.")
    present = set(s.split('|')[0] for s in segments if s.strip())
    for req in REQUIRED_SEGMENTS:
        if req not in present:
            logs.append(f"[ERROR] Falta el segmento requerido: {req}")
    if parse_error:
        logs.insert(0, parse_error)
    return logs

def compare_with_ejemplo(msg):
    # Mensaje ejemplo bien estructurado (puedes ajustar este ejemplo si lo deseas)
    ejemplo = (
        "MSH|^~\\&|HIS|HOSPITAL||VMGESTION|VMGESTION|20250611120000||SIU^S12|123456|2.7|||||||UNICODE UTF-8\r"
        "SCH|1|CENTRAL|78910||||Consulta de control|MR|^^20250612100000^|\r"
        "PID|||1234567890^^^^DNI||PEREZ^JUAN|GOMEZ|19800101|M|||AV. SIEMPRE VIVA 123^BUENOS AIRES^CABA^BUENOS AIRES^^ARGENTINA||1122334455^juan.perez@email.com^|\r"
        "PV1|||^^^^^^^^|E|||DR. LOPEZ|||CONSULTA||||||||||OSDE||||||||||||||||||||||||||||||||EQUIPO1\r"
        "AIS|1||RX001^RADIOGRAFÍA DE TÓRAX^||\r"
        "AIL|||DR. MARTINEZ^EQUIPO1\r"
    )
    # Normalizar saltos de línea
    msg_lines = msg.strip().split('\r')
    ejemplo_lines = ejemplo.strip().split('\r')
    diff = list(difflib.unified_diff(ejemplo_lines, msg_lines, fromfile='Ejemplo', tofile='Mensaje', lineterm=''))
    if diff:
        return ['[DIFERENCIAS] Diferencias entre el mensaje ingresado y un ejemplo válido:'] + diff
    else:
        return ['[OK] El mensaje es idéntico al ejemplo válido.']

def resumen_diferencias(msg):
    ejemplo = (
        "MSH|^~\\&|HIS|HOSPITAL||VMGESTION|VMGESTION|20250611120000||SIU^S12|123456|2.7|||||||UNICODE UTF-8\r"
        "SCH|1|CENTRAL|78910||||Consulta de control|MR|^^20250612100000^|\r"
        "PID|||1234567890^^^^DNI||PEREZ^JUAN|GOMEZ|19800101|M|||AV. SIEMPRE VIVA 123^BUENOS AIRES^CABA^BUENOS AIRES^^ARGENTINA||1122334455^juan.perez@email.com^|\r"
        "PV1|||^^^^^^^^|E|||DR. LOPEZ|||CONSULTA||||||||||OSDE||||||||||||||||||||||||||||||||EQUIPO1\r"
        "AIS|1||RX001^RADIOGRAFÍA DE TÓRAX^||\r"
        "AIL|||DR. MARTINEZ^EQUIPO1\r"
    )
    msg_lines = msg.strip().split('\r')
    ejemplo_lines = ejemplo.strip().split('\r')
    resumen = []
    for i, (ej, ms) in enumerate(zip(ejemplo_lines, msg_lines)):
        if ej != ms:
            seg_ej = ej.split('|')[0]
            seg_ms = ms.split('|')[0]
            if seg_ej == seg_ms:
                # Comparar campo a campo
                ej_fields = ej.split('|')
                ms_fields = ms.split('|')
                for idx, (f_ej, f_ms) in enumerate(zip(ej_fields, ms_fields)):
                    if f_ej != f_ms:
                        resumen.append(f"Diferencia en {seg_ej}.{idx}: ejemplo='{f_ej}' vs tu mensaje='{f_ms}'")
            else:
                resumen.append(f"Diferencia en segmento {i+1}: ejemplo='{seg_ej}' vs tu mensaje='{seg_ms}'")
    if len(msg_lines) != len(ejemplo_lines):
        resumen.append(f"El número de segmentos es diferente: ejemplo={len(ejemplo_lines)}, tu mensaje={len(msg_lines)}")
    if not resumen:
        resumen.append('[OK] No hay diferencias campo a campo con el ejemplo válido.')
    return resumen

class HL7Validator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Validador HL7 SIU')
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
        self.input = QTextEdit()
        self.input.setFont(QFont('Courier', 10))
        self.input.setPlaceholderText('Pega aquí tu mensaje HL7 (usa "\\r" para separar segmentos)')
        self.validate_btn = QPushButton('Validar')
        self.result = QTextEdit()
        self.result.setFont(QFont('Courier', 10))
        self.result.setReadOnly(True)
        layout.addWidget(QLabel('Mensaje HL7:'))
        layout.addWidget(self.input)
        layout.addWidget(self.validate_btn)
        layout.addWidget(QLabel('Resultado de validación:'))
        layout.addWidget(self.result)
        self.setLayout(layout)
        self.validate_btn.clicked.connect(self.run_validation)

    def run_validation(self):
        msg = self.input.toPlainText().replace('\n', '\r').strip()
        logs = validate_hl7_message(msg)
        diff_logs = compare_with_ejemplo(msg)
        resumen_logs = resumen_diferencias(msg)
        if logs:
            self.result.setPlainText('\n'.join(logs) + '\n\n' + '\n'.join(diff_logs) + '\n\n' + '\n'.join(resumen_logs))
        else:
            self.result.setPlainText('Mensaje HL7 válido.\n\n' + '\n'.join(diff_logs) + '\n\n' + '\n'.join(resumen_logs))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HL7Validator()
    window.show()
    sys.exit(app.exec_())
