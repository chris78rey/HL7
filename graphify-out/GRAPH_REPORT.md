# Graph Report - HL7  (2026-10-19)

## Corpus Check
- 9 files · ~7,186 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 85 nodes · 148 edges · 15 communities (13 shown, 2 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `77d7f0e1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- orm_cliente_envio.py
- bot_telegram.py
- insert_mdm_to_db
- guardar_pdf_desde_base64
- button
- DB Connection Layer
- Panel de control HL7 por Telegram
- detener_servidores_hl7.sh
- iniciar_servidores_hl7.sh
- show_panel
- receive_user_id
- build_application
- mdm_servidor_his.py
- Integración Telegram y operación automática HL7
- config_db.py

## God Nodes (most connected - your core abstractions)
1. `button()` - 11 edges
2. `parse_mdm_message()` - 9 edges
3. `receive_user_id()` - 8 edges
4. `insert_mdm_to_db()` - 8 edges
5. `show_panel()` - 6 edges
6. `start()` - 6 edges
7. `build_application()` - 6 edges
8. `armar_mensaje_orm()` - 6 edges
9. `authorized()` - 5 edges
10. `show_users()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `INFORME_HTML data flow` --rationale_for--> `parse_mdm_message()`  [INFERRED]
  docs/arquitectura_inferida.md → mdm/mdm_servidor_his.py
- `Validación ORM vs. generación aleatoria MDM` --rationale_for--> `parse_mdm_message()`  [INFERRED]
  docs/arquitectura_inferida.md → mdm/mdm_servidor_his.py
- `Validación ORM vs. generación aleatoria MDM` --rationale_for--> `validar_email()`  [INFERRED]
  docs/arquitectura_inferida.md → orm/orm_cliente_envio.py
- `validar_email()` --semantically_similar_to--> `parse_mdm_message()`  [INFERRED] [semantically similar]
  orm/orm_cliente_envio.py → mdm/mdm_servidor_his.py
- `validar_telefono()` --semantically_similar_to--> `parse_mdm_message()`  [INFERRED] [semantically similar]
  orm/orm_cliente_envio.py → mdm/mdm_servidor_his.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **PDF extraction fallback chain** — mdm_mdm_servidor_his_extract_text_from_pdf, mdm_mdm_servidor_his_extract_text_from_image, mdm_mdm_servidor_his_extract_delimited_text [INFERRED 0.95]

## Communities (15 total, 2 thin omitted)

### Community 0 - "orm_cliente_envio.py"
Cohesion: 0.25
Nodes (11): ACK no verificado en ORM client, Validación ORM vs. generación aleatoria MDM, parse_mdm_message(), armar_mensaje_orm(), formatear_fecha(), hl7_safe(), main(), print_alert() (+3 more)

### Community 1 - "bot_telegram.py"
Cohesion: 0.36
Nodes (8): all_status(), panel_text(), Panel seguro de Telegram para controlar los servicios HL7. El bot no acepta…, Ejecuta un comando fijo sin usar shell y devuelve código + salida., run_command(), Service, service_status(), status_icon()

### Community 2 - "insert_mdm_to_db"
Cohesion: 0.60
Nodes (6): INFORME_HTML data flow, PDF processing chain hyperedge, extract_delimited_text(), extract_text_from_image(), extract_text_from_pdf(), insert_mdm_to_db()

### Community 3 - "guardar_pdf_desde_base64"
Cohesion: 0.40
Nodes (5): Código muerto: guardar_pdf_desde_base64 e insert_pdf_file_to_db, guardar_pdf_desde_base64(), insert_pdf_file_to_db(), Decodifica un string base64 y lo guarda como archivo PDF., Lee un archivo PDF y lo guarda como base64 en el campo PDF (CLOB) de la base de…

### Community 4 - "button"
Cohesion: 0.53
Nodes (6): button(), confirmation_keyboard(), show_users(), users_keyboard(), DEFAULT_TYPE, InlineKeyboardMarkup

### Community 5 - "DB Connection Layer"
Cohesion: 0.50
Nodes (4): get_db_connection(), get_mensajes_mdm_ordenados(), Establece y devuelve una conexión a la base de datos Oracle., Recupera todos los mensajes de la tabla MENSAJES_MDM, lee los LOBs y devuelve…

### Community 6 - "Panel de control HL7 por Telegram"
Cohesion: 0.33
Nodes (5): Agregar usuarios desde Telegram, Configuración, Ejecutar, Operaciones disponibles, Panel de control HL7 por Telegram

### Community 9 - "show_panel"
Cohesion: 0.83
Nodes (4): authorized(), show_panel(), start(), Update

### Community 10 - "receive_user_id"
Cohesion: 0.50
Nodes (4): main_keyboard(), Recibe un ID solo después de que un administrador pulse Agregar., receive_user_id(), save_admin_ids()

### Community 11 - "build_application"
Cohesion: 0.67
Nodes (3): Application, build_application(), load_settings()

### Community 12 - "mdm_servidor_his.py"
Cohesion: 0.29
Nodes (5): Integración HL7 bidireccional HIS-RIS, MENSAJES_MDM y MENSAJES_ORM sin correlación, preprocess_image_for_ocr(), random_date(), random_string()

### Community 13 - "Integración Telegram y operación automática HL7"
Cohesion: 0.33
Nodes (5): Componentes, Flujo, Integración Telegram y operación automática HL7, Operación persistente, Seguridad y límites

### Community 14 - "config_db.py"
Cohesion: 0.40
Nodes (4): get_dsn(), Puerto 2590 hardcodeado vs config centralizada, handle_client(), start_server()

## Knowledge Gaps
- **9 isolated node(s):** `Configuración`, `Agregar usuarios desde Telegram`, `Ejecutar`, `Operaciones disponibles`, `Componentes` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_mdm_message()` connect `orm_cliente_envio.py` to `insert_mdm_to_db`, `mdm_servidor_his.py`, `config_db.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `guardar_pdf_desde_base64()` connect `guardar_pdf_desde_base64` to `mdm_servidor_his.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `insert_pdf_file_to_db()` connect `guardar_pdf_desde_base64` to `mdm_servidor_his.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `parse_mdm_message()` (e.g. with `INFORME_HTML data flow` and `Validación ORM vs. generación aleatoria MDM`) actually correct?**
  _`parse_mdm_message()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `insert_mdm_to_db()` (e.g. with `INFORME_HTML data flow` and `PDF processing chain hyperedge`) actually correct?**
  _`insert_mdm_to_db()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Configuración`, `Agregar usuarios desde Telegram`, `Ejecutar` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._