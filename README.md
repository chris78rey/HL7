# Sistema de Intercambio HL7 MDM y ORM (HIS-RIS/PACS) vía MLLP

Este proyecto implementa un sistema completo en Python para el envío y recepción de mensajes HL7 (tipos MDM y ORM) entre un sistema HIS y un RIS/PACS, utilizando el protocolo MLLP y una base de datos Oracle. Incluye scripts de cliente y servidor para ambos flujos, validación y ejemplos de mensajes, así como utilidades para automatización y pruebas.

## Novedades

- [23/06/2025] Validación mejorada de teléfono en ORM: ahora, si el campo contiene varios números, solo se toma el primero válido (6+ dígitos) tanto en el cliente como en el servidor. Esto aplica al mensaje HL7 y al campo RAW_MESSAGE en la base de datos.
- [20/06/2025] Se incorpora ORM: ahora el sistema soporta envío y recepción de mensajes HL7 ORM^O01, con scripts de cliente y servidor de pruebas, y sección dedicada en el tutorial interactivo.
- Configuración centralizada y clara de endpoints para pruebas locales y producción.

## Tabla de Contenidos
- [Sistema de Intercambio HL7 MDM y ORM (HIS-RIS/PACS) vía MLLP](#sistema-de-intercambio-hl7-mdm-y-orm-his-rispacs-vía-mllp)
  - [Novedades](#novedades)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Descripción General](#descripción-general)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Instalación y Dependencias](#instalación-y-dependencias)
  - [Ejecución de Scripts](#ejecución-de-scripts)
    - [MDM: Envío y Recepción](#mdm-envío-y-recepción)
    - [ORM: Envío y Recepción](#orm-envío-y-recepción)
  - [Validación y Ejemplos HL7](#validación-y-ejemplos-hl7)
  - [Automatización y Utilidades](#automatización-y-utilidades)
  - [Notas para Producción y Pruebas](#notas-para-producción-y-pruebas)

---

## Descripción General

El sistema permite:
- Recibir mensajes MDM en HIS, decodificarlos y almacenarlos en Oracle.
- Generar y enviar mensajes MDM aleatorios desde RIS/PACS a HIS para pruebas.
- Enviar y recibir mensajes ORM^O01 entre HIS y RIS/PACS.
- Validar mensajes HL7 con una interfaz gráfica, autocorrección y comparación con ejemplos.
- Automatizar el manejo de procesos y pruebas mediante scripts bash.

## Estructura del Proyecto

```
HL7FINAL/
├── mdm/
│   ├── mdm_cliente_envio.py     # Cliente: envía mensajes MDM desde RIS/PACS a HIS
│   ├── mdm_servidor_his.py      # Servidor: recibe MDM en HIS y almacena en Oracle
├── orm/
│   ├── orm_cliente_envio.py     # Cliente: envía mensajes ORM^O01 desde HIS a RIS/PACS
│   ├── orm_servidor_ris.py      # Servidor: recibe ORM^O01 en RIS/PACS y responde ACK
├── servidor_mllp_his.py         # Servidor MLLP genérico para HIS (recibe cualquier HL7)
├── servidor_mllp_rispacs.py     # Servidor MLLP genérico para RIS/PACS (recibe cualquier HL7)
├── kill_mllp_siu_mdm.sh         # Mata todos los procesos MDM (renombrar sugerido)
├── validador_hl7.py             # Validador gráfico de mensajes HL7
├── ejemplos_hl7.txt             # Ejemplos de mensajes MDM, ORM y ACK válidos
├── requirements.txt             # Dependencias Python
├── test_oracle.py               # Script de prueba de conexión Oracle
└── README.md                    # Documentación del proyecto
```

## Instalación y Dependencias

1. **Python 3.7+**
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   # Para el validador gráfico:
   pip install PyQt5
   ```
3. Acceso a una base de datos Oracle (ajustar credenciales en los scripts si es necesario).

## Ejecución de Scripts

### MDM: Envío y Recepción

- **Servidor (HIS):**
  ```bash
  python mdm/mdm_servidor_his.py
  ```
  - Recibe mensajes MDM, los decodifica y almacena en Oracle.

- **Cliente (RIS/PACS → HIS, para pruebas):**
  ```bash
  python mdm/mdm_cliente_envio.py
  ```
  - Genera y envía mensajes MDM aleatorios al servidor HIS.

### ORM: Envío y Recepción

- **Cliente (HIS → RIS/PACS):**
  ```bash
  python orm/orm_cliente_envio.py
  ```
  - Lee mensajes ORM^O01 pendientes de Oracle y los envía por MLLP al RIS/PACS.
  - Actualiza la base tras recibir ACK.

- **Servidor (RIS/PACS):**
  ```bash
  python orm/orm_servidor_ris.py
  ```
  - Recibe mensajes ORM^O01, valida campos y responde con ACK HL7.

## Validación y Ejemplos HL7

- **Validador gráfico:**
  ```bash
  python validador_hl7.py
  ```
  - Permite pegar un mensaje HL7, validarlo, autocorregir errores comunes y comparar con ejemplos.
  - Los ejemplos de mensajes válidos están en `ejemplos_hl7.txt`.

## Automatización y Utilidades

- **Matar todos los procesos MDM:**
  ```bash
  ./kill_mllp_siu_mdm.sh
  ```
- **Probar conexión Oracle:**
  ```bash
  python test_oracle.py
  ```

## Notas para Producción y Pruebas

- Ajustar IPs, puertos y credenciales de Oracle según el entorno.
- Los scripts están preparados para pruebas locales (localhost), pero pueden adaptarse fácilmente a entornos reales.
- El validador HL7 ayuda a depurar y asegurar la calidad de los mensajes antes de enviarlos.
- Los scripts cliente pueden ejecutarse en modo batch para pruebas de carga.
- Consultar y modificar los ejemplos de mensajes en `ejemplos_hl7.txt` para adaptarlos a los requerimientos de la institución.

---

*Documentación actualizada al 23 de junio de 2025*
