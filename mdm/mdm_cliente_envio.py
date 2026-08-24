import socket
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# =============================
# CONFIGURACIÓN DE ENDPOINTS MLLP
HOST = '127.0.0.1'
PORT = 10000 # Asegúrate de que este puerto coincida con el del servidor
# =============================

VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'

def send_hl7_from_file(host, port, filepath):
    """
    Lee un mensaje HL7 desde un archivo y lo envía a un servidor MLLP.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            hl7_message = f.read()
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {filepath}")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    print(f"Intentando conectar a {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=15) as sock:
            print("Conexión exitosa.")
            # Envolver el mensaje con los caracteres MLLP
            data_to_send = VT + hl7_message.encode('utf-8') + FS + CR
            
            print("Enviando mensaje HL7...")
            sock.sendall(data_to_send)
            print("Mensaje enviado:\n" + hl7_message)

            # Esperar y recibir el ACK
            ack = b''
            sock.settimeout(10) # Timeout para la respuesta
            try:
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    ack += chunk
                    if FS in ack and CR in ack:
                        break
            except socket.timeout:
                print("Timeout esperando el ACK.")
                return

            # Procesar y mostrar el ACK
            ack_processed = ack.strip(VT + FS + CR)
            print("\nACK recibido:")
            print(ack_processed.decode('utf-8', errors='replace'))

    except ConnectionRefusedError:
        print(f"Error: Conexión rechazada. ¿Está el servidor corriendo en {host}:{port}?")
    except socket.timeout:
        print(f"Error: Timeout al intentar conectar con {host}:{port}.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python mdm_cliente_envio.py <host> <port> <ruta_al_archivo_hl7>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    filepath = sys.argv[3]
    
    send_hl7_from_file(host, port, filepath)
