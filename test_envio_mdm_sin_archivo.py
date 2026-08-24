import socket
import datetime

# Configura aquí la IP y puerto del servidor MDM
MLLP_HOST = '127.0.0.1'  # Cambia si tu servidor MDM está en otra IP
MLLP_PORT = 2590          # Puerto del servidor MDM

VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'

def generar_mensaje_mdm():
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    msh = f"MSH|^~\\&|HIS|HE1|RIS|HE1|{now}||MDM^T02|123456|P|2.7|||||||UNICODE UTF-8"
    evn = f"EVN|T02|{now}"
    pid = "PID|||12345678^^^^DNI||PEREZ^JUAN^CARLOS||19800101|M|||CALLE FALSA 123||123456789|juan.perez@example.com"
    pv1 = "PV1||I||||||1234^MEDICO^APELLIDO|||||||||||987654"
    txa = f"TXA|1|RAD|{now}|{now}||HE1|123456|P|||"
    obr = "OBR|1|123456||RADIO^RADIOLOGIA|||20250624120000|||||||||||||||||CR"
    obx = "OBX|1|TX|INFORME^INFORME RADIOLOGICO||El paciente presenta hallazgos compatibles con ...||||||F"
    mensaje = "\r".join([msh, evn, pid, pv1, txa, obr, obx]) + "\r"
    return mensaje

def send_mllp_message(host, port, hl7_message):
    print(f"[DEBUG] Enviando mensaje HL7 a {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            print(f"[INFO] Conexión TCP establecida con el servidor MLLP en {host}:{port}")
            data = VT + hl7_message.encode('utf-8') + FS + CR
            print(f"[DEBUG] Bytes enviados: {data}")
            sock.sendall(data)
            ack = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                ack += chunk
                if FS in chunk:
                    break
            if not ack:
                print("[ALERTA] No se recibió ningún ACK del servidor.")
            else:
                print(f"[DEBUG] Bytes ACK recibidos: {ack}")
            ack_str = ack.strip(VT + FS + CR).decode('utf-8', errors='replace')
            print(f"ACK recibido: {ack_str}")
            return ack_str
    except Exception as e:
        print(f"[ERROR] No se pudo enviar o recibir ACK del servidor: {e}")
        return None

def main():
    hl7_message = generar_mensaje_mdm()
    print("\n--- MENSAJE HL7 A ENVIAR ---")
    print(hl7_message.replace('\r', '\n'))
    print("----------------------------\n")
    send_mllp_message(MLLP_HOST, MLLP_PORT, hl7_message)

if __name__ == "__main__":
    main()
