import socket
import base64
import sys

PDF_PATH = "pdfs_extraidos/pdf_20250624170900_INFORME_HTML.pdf"
HOST = "127.0.0.1"
PORT = 2590

# Leer y codificar el PDF en base64
with open(PDF_PATH, "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

# Construir mensaje HL7 MDM^T02 con OBX que contiene el PDF en base64
hl7_msg = f"""
MSH|^~\&|PYTEST|PYCLIENT|HIS|HOSPITAL|20250625120000||MDM^T02|MSGID1234|P|2.3.1
PID|1|12345678||APELLIDO^NOMBRE||19800101|M
TXA|1|RAD|CR|20250625120000|CR|123456|ESTUDIO|12345678|MEDAPELLIDO|MEDNOMBRE
OBX|1|ED|PDF^Informe||^{pdf_b64}|
""".replace("\n", "\r")

# MLLP framing
VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'
msg_bytes = VT + hl7_msg.encode("utf-8") + FS + CR

# Enviar mensaje al servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(msg_bytes)
    print("Mensaje HL7 enviado al servidor MDM.")
    # Esperar ACK
    ack = b''
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        ack += chunk
        if FS in chunk:
            break
    print("ACK recibido del servidor:")
    print(ack)
