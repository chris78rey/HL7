import base64
import os

# Lee el mensaje HL7 desde el archivo
with open('ultimo_mdm_recibido.hl7', 'r', encoding='utf-8') as f:
    hl7 = f.read()

# Intenta ambos separadores de línea
for sep in ['\r', '\n']:
    pdf_base64 = None
    for line in hl7.split(sep):
        if line.startswith('OBX|'):
            fields = line.split('|')
            if len(fields) > 5:
                valor = fields[5].lstrip('^')
                # Decodifica si: tipo ED, o tipo RP, o valor largo con carets
                if (fields[2].strip().upper() == 'ED' or
                    fields[2].strip().upper() == 'RP' or
                    (len(valor) > 100 and fields[5].startswith('^'))):
                    pdf_base64 = valor
                    print(f"[INFO] Encontrado base64 en OBX-5 (limpio): {pdf_base64[:40]}...")
                    break
    if pdf_base64:
        break

print(f"Directorio actual: {os.getcwd()}")

if not pdf_base64:
    print('No se encontró PDF en base64 en el mensaje HL7.')
else:
    try:
        pdf_bytes = base64.b64decode(pdf_base64)
        with open('informe_mdm.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print('PDF generado exitosamente: informe_mdm.pdf')
    except Exception as e:
        print(f'Error al decodificar o guardar el PDF: {e}')
