# Graph Report - HL7  (2026-08-24)

## Corpus Check
- Corpus is ~5,757 words - fits in a single context window. You may not need a graph.

## Summary
- 47 nodes · 79 edges · 9 communities (6 shown, 3 thin omitted)
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- ORM Client Core
- PDF Data Flow Pipeline
- HL7 Message Validation
- Dead PDF Storage Code
- MDM Server & DB Operations
- DB Connection Layer
- Config and Server Lifecycle
- HL7 Service Stop
- HL7 Service Start

## God Nodes (most connected - your core abstractions)
1. `parse_mdm_message()` - 9 edges
2. `insert_mdm_to_db()` - 8 edges
3. `armar_mensaje_orm()` - 6 edges
4. `validar_email()` - 5 edges
5. `PDF processing chain hyperedge` - 5 edges
6. `handle_client()` - 4 edges
7. `extract_text_from_image()` - 4 edges
8. `validar_telefono()` - 4 edges
9. `main()` - 4 edges
10. `get_dsn()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `INFORME_HTML data flow` --rationale_for--> `parse_mdm_message()`  [INFERRED]
  docs/arquitectura_inferida.md → mdm/mdm_servidor_his.py
- `Validación ORM vs. generación aleatoria MDM` --rationale_for--> `parse_mdm_message()`  [INFERRED]
  docs/arquitectura_inferida.md → mdm/mdm_servidor_his.py
- `Puerto 2590 hardcodeado vs config centralizada` --rationale_for--> `start_server()`  [INFERRED]
  docs/arquitectura_inferida.md → mdm/mdm_servidor_his.py
- `Validación ORM vs. generación aleatoria MDM` --rationale_for--> `validar_email()`  [INFERRED]
  docs/arquitectura_inferida.md → orm/orm_cliente_envio.py
- `validar_email()` --semantically_similar_to--> `parse_mdm_message()`  [INFERRED] [semantically similar]
  orm/orm_cliente_envio.py → mdm/mdm_servidor_his.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **PDF extraction fallback chain** — mdm_mdm_servidor_his_extract_text_from_pdf, mdm_mdm_servidor_his_extract_text_from_image, mdm_mdm_servidor_his_extract_delimited_text [INFERRED 0.95]

## Communities (9 total, 3 thin omitted)

### Community 0 - "ORM Client Core"
Cohesion: 0.27
Nodes (8): ACK no verificado en ORM client, Integración HL7 bidireccional HIS-RIS, armar_mensaje_orm(), formatear_fecha(), hl7_safe(), main(), print_alert(), send_mllp_message()

### Community 1 - "PDF Data Flow Pipeline"
Cohesion: 0.48
Nodes (7): INFORME_HTML data flow, PDF processing chain hyperedge, extract_delimited_text(), extract_text_from_image(), extract_text_from_pdf(), insert_mdm_to_db(), preprocess_image_for_ocr()

### Community 2 - "HL7 Message Validation"
Cohesion: 0.47
Nodes (6): Validación ORM vs. generación aleatoria MDM, parse_mdm_message(), random_date(), random_string(), validar_email(), validar_telefono()

### Community 3 - "Dead PDF Storage Code"
Cohesion: 0.40
Nodes (5): Código muerto: guardar_pdf_desde_base64 e insert_pdf_file_to_db, guardar_pdf_desde_base64(), insert_pdf_file_to_db(), Decodifica un string base64 y lo guarda como archivo PDF., Lee un archivo PDF y lo guarda como base64 en el campo PDF (CLOB) de la base de…

### Community 4 - "MDM Server & DB Operations"
Cohesion: 0.50
Nodes (3): MENSAJES_MDM y MENSAJES_ORM sin correlación, handle_client(), start_server()

### Community 5 - "DB Connection Layer"
Cohesion: 0.50
Nodes (4): get_db_connection(), get_mensajes_mdm_ordenados(), Establece y devuelve una conexión a la base de datos Oracle., Recupera todos los mensajes de la tabla MENSAJES_MDM, lee los LOBs y devuelve…

## Knowledge Gaps
- **1 isolated node(s):** `ACK no verificado en ORM client`
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_mdm_message()` connect `HL7 Message Validation` to `PDF Data Flow Pipeline`, `MDM Server & DB Operations`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `guardar_pdf_desde_base64()` connect `Dead PDF Storage Code` to `MDM Server & DB Operations`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `insert_pdf_file_to_db()` connect `Dead PDF Storage Code` to `MDM Server & DB Operations`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `parse_mdm_message()` (e.g. with `INFORME_HTML data flow` and `Validación ORM vs. generación aleatoria MDM`) actually correct?**
  _`parse_mdm_message()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `insert_mdm_to_db()` (e.g. with `INFORME_HTML data flow` and `PDF processing chain hyperedge`) actually correct?**
  _`insert_mdm_to_db()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `validar_email()` (e.g. with `Validación ORM vs. generación aleatoria MDM` and `parse_mdm_message()`) actually correct?**
  _`validar_email()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `PDF processing chain hyperedge` (e.g. with `INFORME_HTML data flow` and `extract_delimited_text()`) actually correct?**
  _`PDF processing chain hyperedge` has 5 INFERRED edges - model-reasoned connections that need verification._