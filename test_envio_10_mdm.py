import socket
import datetime
import time

MLLP_HOST = '127.0.0.1'
MLLP_PORT = 2590

VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'

def generar_mensaje_mdm(idx):
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    msh = f"MSH|^~\\&|HIS|HE1|RIS|HE1|{now}||MDM^T02|{100000+idx}|P|2.7|||||||UNICODE UTF-8"
    evn = f"EVN|T02|{now}"
    pid = f"PID|||{10000000+idx}^^^^DNI||PEREZ{idx}^JUAN^CARLOS||19800101|M|||CALLE FALSA 123||123456789|juan.perez{idx}@example.com"
    pv1 = f"PV1||I||||||1234^MEDICO^APELLIDO|||||||||||{900000+idx}"
    txa = f"TXA|1|RAD|{now}|{now}|CR|HE1|{100000+idx}|P||APELLIDO{idx}|NOMBRE{idx}"
    obr = f"OBR|1|{100000+idx}||RADIO^RADIOLOGIA|||{now}|||||||||||||||||CR"
    obx = f"OBX|1|TX|INFORME^INFORME RADIOLOGICO||El paciente {idx} presenta hallazgos compatibles con ...||||||F"
    mensaje = "\r".join([msh, evn, pid, pv1, txa, obr, obx]) + "\r"
    return mensaje

def send_mllp_message(host, port, hl7_message):
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            data = VT + hl7_message.encode('utf-8') + FS + CR
            sock.sendall(data)
            ack = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                ack += chunk
                if FS in chunk:
                    break
            ack_str = ack.strip(VT + FS + CR).decode('utf-8', errors='replace')
            print(f"ACK recibido: {ack_str}")
            return ack_str
    except Exception as e:
        print(f"[ERROR] No se pudo enviar o recibir ACK del servidor: {e}")
        return None

def main():
    for i in range(10):
        hl7_message = generar_mensaje_mdm(i+1)
        print(f"\n--- MENSAJE HL7 MDM #{i+1} ---")
        print(hl7_message.replace('\r', '\n'))
        print("----------------------------\n")
        send_mllp_message(MLLP_HOST, MLLP_PORT, hl7_message)
        time.sleep(0.5)  # Pequeña pausa para no saturar el servidor

if __name__ == "__main__":
    main()
