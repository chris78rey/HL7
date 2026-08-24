import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mdm_servidor_his import parse_mdm_message, insert_mdm_to_db

if __name__ == "__main__":
    # Buscar el archivo en la ruta absoluta correcta
    hl7_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ultimo_mdm_recibido.hl7'))
    if not os.path.exists(hl7_path):
        hl7_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../HL7FINAL/ultimo_mdm_recibido.hl7'))
    if not os.path.exists(hl7_path):
        raise FileNotFoundError(f"No se encontró el archivo HL7 en {hl7_path}")
    with open(hl7_path, "r", encoding="utf-8") as f:
        msg = f.read()
    campos = parse_mdm_message(msg)
    print("[TEST] Campos parseados:", campos)
    insert_mdm_to_db(campos, msg)
    print("[TEST] Proceso de inserción ejecutado para el último mensaje HL7 recibido.")
