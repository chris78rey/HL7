import sys
import os
import datetime
import random
import string
import re

# Añadir el directorio padre al path para poder importar config_db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def random_date():
    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime.now()
    return (start + (end - start) * random.random()).strftime('%Y%m%d')

def parse_mdm_message_debug(msg):
    print("--- INICIANDO PARSEO DEBUG ---")
    campos = {}
    # Normalizar saltos de línea a \r
    msg_normalizada = re.sub(r'\r\n?|\n', '\r', msg)
    segments = msg_normalizada.split('\r')
    print(f"Número de segmentos: {len(segments)}")

    for i, seg in enumerate(segments):
        print(f"\n--- Procesando Segmento {i+1}: {seg[:30]}... ---")
        fields = seg.split('|')
        seg_type = fields[0] if fields else ""
        print(f"Tipo de segmento: {seg_type}")

        if seg.startswith('MSH|'):
            print("Parseando MSH...")
            campos['MSG_TIMESTAMP'] = fields[6] if len(fields) > 6 else ''
            campos['ID_UNICO_MSG'] = fields[9] if len(fields) > 9 else random_string(10)
            print(f"  MSG_TIMESTAMP: {campos.get('MSG_TIMESTAMP')}")
            print(f"  ID_UNICO_MSG: {campos.get('ID_UNICO_MSG')}")

        elif seg.startswith('PID|'):
            print("Parseando PID...")
            campos['DOC_PACIENTE'] = fields[3].split('^')[0] if len(fields) > 3 else random_string(8)
            campos['TIPO_DOC'] = fields[3].split('^')[4] if len(fields) > 3 and len(fields[3].split('^')) > 4 else 'DNI'
            if len(fields) > 5:
                apellidos = fields[5].split('^')
                campos['APELLIDO_PACIENTE'] = apellidos[0] if len(apellidos) > 0 else 'APELLIDO'
                campos['NOMBRE_PACIENTE'] = apellidos[1] if len(apellidos) > 1 else 'NOMBRE'
            campos['FECHA_NACIMIENTO'] = fields[7] if len(fields) > 7 else random_date()
            campos['SEXO'] = fields[8] if len(fields) > 8 else 'M'
            print(f"  DOC_PACIENTE: {campos.get('DOC_PACIENTE')}")
            print(f"  APELLIDO_PACIENTE: {campos.get('APELLIDO_PACIENTE')}")
            print(f"  NOMBRE_PACIENTE: {campos.get('NOMBRE_PACIENTE')}")

        elif seg.startswith('OBR|'):
            print("Parseando OBR...")
            campos['NUMERO_OBR'] = fields[2] if len(fields) > 2 else ''
            print(f"  NUMERO_OBR: {campos.get('NUMERO_OBR')}")
            # Datos que deberían estar en TXA, los pongo aquí temporalmente desde OBR para probar
            campos['ACCESSION_NUMBER'] = fields[3] if len(fields) > 3 else random_string(8)
            campos['TURNO_ID'] = int(fields[3]) if len(fields) > 3 and fields[3].isdigit() else random.randint(10000,99999)
            campos['ESTUDIO_ID'] = fields[3] if len(fields) > 3 else random_string(8)
            campos['ESTUDIO_DESC'] = fields[4].split('^')[1] if len(fields) > 4 and len(fields[4].split('^')) > 1 else 'ESTUDIO'
            campos['STUDY_INSTANCE_UID'] = fields[18] if len(fields) > 18 else random_string(12)
            print(f"  ACCESSION_NUMBER (de OBR): {campos.get('ACCESSION_NUMBER')}")
            print(f"  ESTUDIO_ID (de OBR): {campos.get('ESTUDIO_ID')}")
            print(f"  ESTUDIO_DESC (de OBR): {campos.get('ESTUDIO_DESC')}")
            print(f"  STUDY_INSTANCE_UID (de OBR): {campos.get('STUDY_INSTANCE_UID')}")


        elif seg.startswith('TXA|'):
            print("Parseando TXA...")
            campos['FECHA_INFORME'] = fields[6] if len(fields) > 6 else datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            if len(fields) > 9 and fields[9]:
                med_info = fields[9].split('^')
                campos['DOC_MED_INFORMANTE'] = med_info[0] if len(med_info) > 0 else random_string(8)
                campos['APELLIDO_MED_INFORMANTE'] = med_info[1] if len(med_info) > 1 else 'SIN_APELLIDO'
                campos['NOMBRE_MED_INFORMANTE'] = med_info[2] if len(med_info) > 2 else 'SIN_NOMBRE'
            else:
                campos['DOC_MED_INFORMANTE'] = random_string(8)
                campos['APELLIDO_MED_INFORMANTE'] = 'SIN_APELLIDO'
                campos['NOMBRE_MED_INFORMANTE'] = 'SIN_NOMBRE'
            
            print(f"  DOC_MED_INFORMANTE: {campos.get('DOC_MED_INFORMANTE')}")
            print(f"  APELLIDO_MED_INFORMANTE: {campos.get('APELLIDO_MED_INFORMANTE')}")
            print(f"  NOMBRE_MED_INFORMANTE: {campos.get('NOMBRE_MED_INFORMANTE')}")
            print(f"  FECHA_INFORME: {campos.get('FECHA_INFORME')}")


    # Lógica para OBX (PDF)
    print("\n--- Buscando PDF en OBX ---")
    pdf_base64 = None
    for sep in ['\r', '\n']:
        for line in msg.split(sep):
            if line.startswith('OBX|'):
                fields = line.split('|')
                if len(fields) > 5:
                    valor = fields[5].lstrip('^')
                    if (fields[2].strip().upper() == 'ED' or
                        fields[2].strip().upper() == 'RP' or
                        (len(valor) > 100 and fields[5].startswith('^'))):
                        pdf_base64 = valor
                        print("PDF encontrado en OBX.")
                        break
        if pdf_base64:
            break
    
    if pdf_base64:
        campos['INFORME_HTML'] = "PDF_ENCONTRADO_Y_DECODIFICADO" # Simulación
    else:
        print("PDF no encontrado en OBX.")
        campos['INFORME_HTML'] = '<b>INFORME VACIO</b>'

    # Valores fijos o por defecto que faltaban
    print("\n--- Asignando valores por defecto ---")
    campos['MODALIDAD'] = campos.get('MODALIDAD', 'CR')
    campos['ESTADO_RESULTADO'] = 'FI'
    campos['SERVICIO'] = 'RADIOLOGIA'
    print(f"MODALIDAD: {campos.get('MODALIDAD')}")
    print(f"ESTADO_RESULTADO: {campos.get('ESTADO_RESULTADO')}")
    print(f"SERVICIO: {campos.get('SERVICIO')}")


    print("\n--- Resumen de campos extraídos ---")
    for k, v in campos.items():
        print(f"  {k}: {str(v)[:70]}...")

    # Chequeo final de campos requeridos
    required_fields = [
        'MSG_TIMESTAMP', 'ID_UNICO_MSG', 'DOC_PACIENTE', 'TIPO_DOC', 'APELLIDO_PACIENTE', 'NOMBRE_PACIENTE',
        'FECHA_NACIMIENTO', 'SEXO', 'ACCESSION_NUMBER', 'TURNO_ID', 'MODALIDAD', 'ESTUDIO_ID', 'ESTUDIO_DESC',
        'DOC_MED_INFORMANTE', 'APELLIDO_MED_INFORMANTE', 'NOMBRE_MED_INFORMANTE', 'STUDY_INSTANCE_UID',
        'INFORME_HTML', 'ESTADO_RESULTADO', 'FECHA_INFORME', 'SERVICIO'
    ]
    missing = [f for f in required_fields if f not in campos or campos[f] in (None, '')]
    if missing:
        print(f"\n[ERROR] Faltan campos requeridos: {missing}")
    else:
        print("\n[SUCCESS] Todos los campos requeridos están presentes.")

    return campos

if __name__ == "__main__":
    try:
        with open('ultimo_mdm_recibido.hl7', 'r', encoding='utf-8') as f:
            hl7_message = f.read()
        
        parse_mdm_message_debug(hl7_message)

    except FileNotFoundError:
        print("Error: No se encontró el archivo 'ultimo_mdm_recibido.hl7'.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
