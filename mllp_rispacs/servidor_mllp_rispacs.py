import socket
import threading
import sys
import os

# =============================
# CONFIGURACIÓN DE ENDPOINTS MLLP PARA PRUEBAS Y PRODUCCIÓN
# Cambia estos valores según el entorno
HOST = '0.0.0.0'  # IP local para pruebas o la IP de la interfaz que desees
PORT = 6661            # Puerto para pruebas o producción

# Si quieres usar la configuración centralizada, descomenta lo siguiente:
# from config_db import MLLP_RISPACS
# HOST = MLLP_RISPACS['host']
# PORT = MLLP_RISPACS['port']

VT = b'\x0b'
FS = b'\x1c'
CR = b'\x0d'

print(f"[MLLP-RISPACS] Servidor MLLP escuchando en {HOST}:{PORT} (recibe cualquier tipo de mensaje HL7)")

def handle_client(conn, addr):
    print(f"Conexión de: {addr}")
    data = b''
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk
        if FS in chunk:
            break
    # Limpia delimitadores MLLP
    if data.startswith(VT):
        data = data[1:]
    if data.endswith(FS + CR):
        data = data[:-2]
    try:
        msg = data.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"[ERROR] Al decodificar mensaje: {e}")
        msg = ''
    # Imprimir mensaje HL7 recibido apenas llega
    print("\n===== HL7 RECIBIDO =====\n" + msg.replace('\r', '\n') + "\n========================\n")
    # ACK simple
    ack = VT + b'MSA|AA|1' + FS + CR
    try:
        conn.sendall(ack)
        print("ACK HL7 enviado al cliente.\n")
    except Exception as e:
        print(f"No se pudo enviar ACK HL7 al cliente: {e}\n¿Servidor de destino no disponible o conexión cerrada?")
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
