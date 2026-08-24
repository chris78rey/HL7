# Graph Report - HL7  (2026-08-24)

## Corpus Check
- Corpus is ~5,499 words - fits in a single context window. You may not need a graph.

## Summary
- 47 nodes · 73 edges · 10 communities (7 shown, 3 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- ORM Client Core
- HL7 Bidirectional Integration
- HL7 Message Validation
- Config and Server Lifecycle
- Dead PDF Storage Code
- MDM PDF Extraction Pipeline
- DB Connection Layer
- HL7 Service Stop
- HL7 Service Start
- System Architecture

## God Nodes (most connected - your core abstractions)
1. `parse_mdm_message()` - 7 edges
2. `insert_mdm_to_db()` - 6 edges
3. `armar_mensaje_orm()` - 6 edges
4. `validar_email()` - 5 edges
5. `handle_client()` - 4 edges
6. `validar_telefono()` - 4 edges
7. `send_mllp_message()` - 4 edges
8. `main()` - 4 edges
9. `get_dsn()` - 3 edges
10. `start_server()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Validación ORM vs. generación aleatoria MDM` --rationale_for--> `parse_mdm_message()`  [INFERRED]
  docs/arquitectura_inferida.md → mdm/mdm_servidor_his.py
- `PDF extraction pipeline con fallback OCR` --rationale_for--> `insert_mdm_to_db()`  [INFERRED]
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

## Communities (10 total, 3 thin omitted)

### Community 0 - "ORM Client Core"
Cohesion: 0.33
Nodes (7): ACK no verificado en ORM client, armar_mensaje_orm(), formatear_fecha(), hl7_safe(), main(), print_alert(), send_mllp_message()

### Community 1 - "HL7 Bidirectional Integration"
Cohesion: 0.40
Nodes (4): Integración HL7 bidireccional HIS-RIS, MENSAJES_MDM y MENSAJES_ORM sin correlación, extract_text_from_image(), preprocess_image_for_ocr()

### Community 2 - "HL7 Message Validation"
Cohesion: 0.47
Nodes (6): Validación ORM vs. generación aleatoria MDM, parse_mdm_message(), random_date(), random_string(), validar_email(), validar_telefono()

### Community 3 - "Config and Server Lifecycle"
Cohesion: 0.40
Nodes (4): get_dsn(), Puerto 2590 hardcodeado vs config centralizada, handle_client(), start_server()

### Community 4 - "Dead PDF Storage Code"
Cohesion: 0.40
Nodes (5): Código muerto: guardar_pdf_desde_base64 e insert_pdf_file_to_db, guardar_pdf_desde_base64(), insert_pdf_file_to_db(), Decodifica un string base64 y lo guarda como archivo PDF., Lee un archivo PDF y lo guarda como base64 en el campo PDF (CLOB) de la base de…

### Community 5 - "MDM PDF Extraction Pipeline"
Cohesion: 0.50
Nodes (4): PDF extraction pipeline con fallback OCR, extract_delimited_text(), extract_text_from_pdf(), insert_mdm_to_db()

### Community 6 - "DB Connection Layer"
Cohesion: 0.50
Nodes (4): get_db_connection(), get_mensajes_mdm_ordenados(), Establece y devuelve una conexión a la base de datos Oracle., Recupera todos los mensajes de la tabla MENSAJES_MDM, lee los LOBs y devuelve…

## Knowledge Gaps
- **2 isolated node(s):** `MDM to RIS unidirectional pipeline`, `PDF extraction pipeline con fallback OCR`
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_mdm_message()` connect `HL7 Message Validation` to `HL7 Bidirectional Integration`, `Config and Server Lifecycle`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `guardar_pdf_desde_base64()` connect `Dead PDF Storage Code` to `HL7 Bidirectional Integration`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `insert_pdf_file_to_db()` connect `Dead PDF Storage Code` to `HL7 Bidirectional Integration`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `parse_mdm_message()` (e.g. with `Validación ORM vs. generación aleatoria MDM` and `validar_email()`) actually correct?**
  _`parse_mdm_message()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `validar_email()` (e.g. with `Validación ORM vs. generación aleatoria MDM` and `parse_mdm_message()`) actually correct?**
  _`validar_email()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `MDM to RIS unidirectional pipeline`, `PDF extraction pipeline con fallback OCR` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._