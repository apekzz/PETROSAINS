# Graph Report - inventory_app  (2026-09-21)

## Corpus Check
- 16 files · ~25,359 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: .pt 4, .csv 4, .css 3)

## Summary
- 506 nodes · 1098 edges · 28 communities (26 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 49 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `36121c0c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- sam_tool.py
- infer.py
- db.py
- camera_capture_loop
- face.py
- sam-tool.js
- tables
- post
- sql.py
- captureReadyFace
- main.py
- normalize_item_name
- api.py
- _apply_face_embedding
- load_embed_model
- runBrowserFaceLoop
- setup_db.py
- connect_and_prepare
- fetchStats
- applyFaceStatus
- bootstrap_database
- analyzeLocalFrame
- setFaceHint
- _exit_app
- ensure_tables
- README.md

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 28 edges
2. `connect_and_prepare()` - 15 edges
3. `applyFaceStatus()` - 14 edges
4. `run_high_end_boot()` - 14 edges
5. `camera_capture_loop()` - 12 edges
6. `analyzeLocalFrame()` - 11 edges
7. `import_train_catalog()` - 11 edges
8. `face_status_payload()` - 11 edges
9. `is_object_detection_armed()` - 11 edges
10. `ensure_object_detection_ready()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `get_inventory()` --calls--> `fetch_inventory()`  [INFERRED]
  inventory_app/api.py → inventory_app/sql.py
- `get_movements()` --calls--> `fetch_movements()`  [INFERRED]
  inventory_app/api.py → inventory_app/sql.py
- `get_stats()` --calls--> `fetch_stats()`  [INFERRED]
  inventory_app/api.py → inventory_app/sql.py
- `search_inventory()` --calls--> `fetch_inventory()`  [INFERRED]
  inventory_app/api.py → inventory_app/sql.py
- `get_item()` --calls--> `fetch_item()`  [INFERRED]
  inventory_app/api.py → inventory_app/sql.py

## Import Cycles
- None detected.

## Communities (28 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (45): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace, btnImportCatalog (+37 more)

### Community 1 - "sam_tool.py"
Cohesion: 0.08
Nodes (38): base64, collections, choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), ndarray (+30 more)

### Community 2 - "infer.py"
Cohesion: 0.08
Nodes (32): argparse, config, get_lan_ip(), cv2, crop_bgr(), crop_masked_bgr(), load_model(), model_device() (+24 more)

### Community 3 - "db.py"
Cohesion: 0.20
Nodes (17): Compatibility wrappers. All SQL lives in sql.py., startup_event(), clear_check_in_out(), clear_staff_embeddings(), _embedding_from_text(), export_table_snapshots(), fetch_detections_summary(), fetch_inventory_embeddings() (+9 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.12
Nodes (34): arm_object_detection(), boot_status(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), ensure_object_detection_ready() (+26 more)

### Community 5 - "face.py"
Cohesion: 0.11
Nodes (22): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+14 more)

### Community 6 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 7 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 8 - "post"
Cohesion: 0.10
Nodes (28): BaseModel, analyze_face_frame(), api_start_camera(), capture_sam_frame(), detection_preview_active(), embed_captured_face(), face_crop_to_embedding(), _face_embed_worker() (+20 more)

### Community 9 - "sql.py"
Cohesion: 0.15
Nodes (17): contextlib, json, psycopg_rows, check_db(), _checkout_as_detection(), close_boot_connection(), _copy_table_to_file(), _export() (+9 more)

### Community 10 - "captureReadyFace"
Cohesion: 0.33
Nodes (9): blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), sendSegmentedEmbed(), setRegisterProgress(), showRegisterModal(), submitFaceRegister() (+1 more)

### Community 11 - "main.py"
Cohesion: 0.08
Nodes (35): asyncio, datetime, delete, fastapi_middleware_cors, fastapi_responses, camera_status(), catalog_import_status(), cosine_similarity() (+27 more)

### Community 12 - "normalize_item_name"
Cohesion: 0.17
Nodes (19): create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), refresh_inventory_catalog_cache(), register_sam_embedding(), _embedding_to_text(), insert_check_in_out() (+11 more)

### Community 13 - "api.py"
Cohesion: 0.27
Nodes (12): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+4 more)

### Community 14 - "_apply_face_embedding"
Cohesion: 0.40
Nodes (6): _apply_face_embedding(), _auto_arm_detection_after_face(), _encode_image(), _encode_images(), _encode_worker_loop(), _load_clip_weights()

### Community 15 - "load_embed_model"
Cohesion: 0.29
Nodes (8): _catalog_import_job(), _catalog_progress(), images_to_embeddings(), load_embed_model(), queue_face_embedding(), Load CLIP once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API., select_and_import_catalog()

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "setup_db.py"
Cohesion: 0.20
Nodes (11): psycopg, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), fetch_inventory() (+3 more)

### Community 18 - "connect_and_prepare"
Cohesion: 0.17
Nodes (12): connect_and_prepare(), ensure_schema_columns(), _open_connection(), Safely migrate existing installations without dropping data., Reject incompatible existing tables without deleting or replacing them., Tables whose CSV is missing or row-count differs from Postgres., Restore CSV data only into currently empty supported tables., Open the database at boot, keep a live connection, create missing tables. (+4 more)

### Community 19 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 20 - "applyFaceStatus"
Cohesion: 0.20
Nodes (14): applyFaceStatus(), applyMode(), applyObjectRecognitionState(), ensureObjectRecognitionArmed(), escapeHtml(), fetchInventory(), loadCurrentMode(), pollFaceStatus() (+6 more)

### Community 21 - "bootstrap_database"
Cohesion: 0.25
Nodes (8): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), ensure_postgres_running(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only., _run()

### Community 22 - "analyzeLocalFrame"
Cohesion: 0.24
Nodes (10): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), showCaptureAlert(), sizeOverlayToVideo() (+2 more)

### Community 23 - "setFaceHint"
Cohesion: 0.26
Nodes (12): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup(), preferredCameraFacing() (+4 more)

### Community 24 - "_exit_app"
Cohesion: 0.20
Nodes (11): _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event() (+3 more)

### Community 25 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

## Knowledge Gaps
- **56 isolated node(s):** `lastIdentifiedNames`, `inventoryItemNames`, `inventoryDisplayToOriginal`, `inventoryOriginalToDisplay`, `knownMovementIds` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 147 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `import_train_catalog()` connect `sam_tool.py` to `main.py`, `load_embed_model`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `main.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `bootstrap_database()` connect `bootstrap_database` to `infer.py`, `db.py`, `sql.py`, `main.py`, `connect_and_prepare`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `lastIdentifiedNames`, `inventoryItemNames`, `inventoryDisplayToOriginal` to the rest of the system?**
  _56 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03996983408748114 - nodes in this community are weakly interconnected._
- **Should `sam_tool.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07948717948717948 - nodes in this community are weakly interconnected._
- **Should `infer.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0761904761904762 - nodes in this community are weakly interconnected._