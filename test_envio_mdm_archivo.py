import socket
import sys
import os

# Configura aquí la IP y puerto del servidor MDM (ajusta según tu entorno)
MLLP_HOST = '172.16.60.71'  # Cambia si tu servidor MDM está en otra IP
MLLP_PORT = 6662            # Cambia al puerto real de tu servidor MDM

VT = b'\x0b'  # Vertical Tab
FS = b'\x1c'  # File Separator
CR = b'\x0d'  # Carriage Return


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
    if len(sys.argv) < 2:
        print("Uso: python3 test_envio_mdm_archivo.py <archivo_hl7>")
        sys.exit(1)
    archivo = sys.argv[1]
    if not os.path.isfile(archivo):
        print(f"El archivo '{archivo}' no existe.")
        sys.exit(1)
    with open(archivo, 'r', encoding='utf-8') as f:
        hl7_message = f.read().strip()
    print("\n--- MENSAJE HL7 A ENVIAR ---")
    print(hl7_message.replace('\r', '\n'))
    print("----------------------------\n")
    send_mllp_message(MLLP_HOST, MLLP_PORT, hl7_message)

if __name__ == "__main__":
    main()
