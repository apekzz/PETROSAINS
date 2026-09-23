# Graph Report - inventory_app  (2026-09-23)

## Corpus Check
- 18 files · ~26,416 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: .csv 4, .pt 4, .css 3)

## Summary
- 550 nodes · 1143 edges · 33 communities (31 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `18a757f4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- _encode_worker_loop
- run_high_end_boot
- sam-tool.js
- camera_capture_loop
- face.py
- analyzeLocalFrame
- tables
- _clear_session_movements
- sql.py
- updateTriggerStatus
- main.py
- loader.py
- api.py
- sam_tool.py
- noise_transfer.py
- runBrowserFaceLoop
- fetchStats
- free_port
- applyFaceStatus
- OneShot Inventory (`inventory_app`)
- saved_tables/README.md
- db.py
- post
- normalize_item_name
- connect_and_prepare
- setup_db.py
- clear_check_in_out
- export_table_snapshots
- BaseModel
- bootstrap_database
- ensure_tables

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 28 edges
2. `connect_and_prepare()` - 15 edges
3. `camera_capture_loop()` - 14 edges
4. `import_train_catalog()` - 13 edges
5. `capture_laptop_noise_profile()` - 13 edges
6. `applyFaceStatus()` - 13 edges
7. `normalize_item_name()` - 11 edges
8. `analyzeLocalFrame()` - 11 edges
9. `startLocalCamera()` - 11 edges
10. `face_status_payload()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Blur residual: mean(|gray − soft blur|) — grain estimate.` --rationale_for--> `noise_score()`  [EXTRACTED]
  backend/noise_transfer.py → inventory_app/backend/noise_transfer.py
- `Sample FaceTime at fixed size; raise if capture/profile invalid.` --rationale_for--> `capture_laptop_noise_profile()`  [EXTRACTED]
  backend/noise_transfer.py → inventory_app/backend/noise_transfer.py
- `Stamp laptop residual grain onto RGB crop; clip to uint8.` --rationale_for--> `apply_noise_to_image()`  [EXTRACTED]
  backend/noise_transfer.py → inventory_app/backend/noise_transfer.py
- `Fail if apply was a no-op or missed target band.` --rationale_for--> `assert_noise_applied()`  [EXTRACTED]
  backend/noise_transfer.py → inventory_app/backend/noise_transfer.py
- `No camera: synthetic residual map must raise crop grain.` --rationale_for--> `_synthetic_self_check()`  [EXTRACTED]
  backend/noise_transfer.py → inventory_app/backend/noise_transfer.py

## Import Cycles
- None detected.

## Communities (33 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (48): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+40 more)

### Community 1 - "_encode_worker_loop"
Cohesion: 0.16
Nodes (14): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker() (+6 more)

### Community 2 - "run_high_end_boot"
Cohesion: 0.22
Nodes (11): get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API. (+3 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.14
Nodes (30): arm_object_detection(), camera_capture_loop(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state(), ingest_browser_scan() (+22 more)

### Community 5 - "face.py"
Cohesion: 0.06
Nodes (38): argparse, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+30 more)

### Community 6 - "analyzeLocalFrame"
Cohesion: 0.18
Nodes (17): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), drawLandmarks(), grabLocalFrame(), grabSegmentedFace() (+9 more)

### Community 7 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 8 - "_clear_session_movements"
Cohesion: 0.40
Nodes (6): _clear_session_movements(), _exit_app(), _force_close(), shutdown_event(), stop_camera(), on_event

### Community 9 - "sql.py"
Cohesion: 0.19
Nodes (13): contextlib, _checkout_as_detection(), ensure_postgres_running(), fetch_detections(), fetch_detections_today(), fetch_item(), fetch_movements(), _format_dt() (+5 more)

### Community 10 - "updateTriggerStatus"
Cohesion: 0.24
Nodes (11): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showCaptureAlert() (+3 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (39): api, asyncio, sam_status(), dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses (+31 more)

### Community 12 - "loader.py"
Cohesion: 0.24
Nodes (8): _bar(), finish(), set_progress(), start(), _width(), shutil, sys, time

### Community 13 - "api.py"
Cohesion: 0.24
Nodes (13): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+5 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model(), _mask_data_url() (+10 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.07
Nodes (51): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+43 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 18 - "free_port"
Cohesion: 0.67
Nodes (3): free_port(), Kill whatever is still bound to this app's port so a restart can bind., Kill whatever is still bound to this app's port so a restart can bind.

### Community 19 - "applyFaceStatus"
Cohesion: 0.24
Nodes (15): applyFaceStatus(), captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup() (+7 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "db.py"
Cohesion: 0.24
Nodes (14): Compatibility wrappers. All SQL lives in sql.py., migrate_sqlite_inventory(), check_db(), close_boot_connection(), _embedding_from_text(), fetch_detections_summary(), fetch_inventory(), fetch_inventory_embeddings() (+6 more)

### Community 24 - "post"
Cohesion: 0.12
Nodes (23): analyze_face_frame(), api_noise_capture(), api_start_camera(), _cancel_app_exit(), capture_sam_frame(), dashboard_hello(), dashboard_leave(), detection_preview_active() (+15 more)

### Community 25 - "normalize_item_name"
Cohesion: 0.24
Nodes (14): _embedding_to_text(), normalize_item_name(), Rebuild summary counts from inventory_emb. Keeps existing registered_date., Atomically replace the catalog and rebuild unique inventory counts., refresh_main_inventory(), replace_inventory_embeddings(), save_inventory_embedding(), save_object_embedding() (+6 more)

### Community 26 - "connect_and_prepare"
Cohesion: 0.17
Nodes (12): connect_and_prepare(), ensure_schema_columns(), _open_connection(), Safely migrate existing installations without dropping data., Reject incompatible existing tables without deleting or replacing them., Tables whose CSV is missing or row-count differs from Postgres., Restore CSV data only into currently empty supported tables., Open the database at boot, keep a live connection, create missing tables. (+4 more)

### Community 27 - "setup_db.py"
Cohesion: 0.22
Nodes (9): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), fetch_stats(), psycopg (+1 more)

### Community 28 - "clear_check_in_out"
Cohesion: 0.29
Nodes (7): clear_check_in_out(), insert_check_in_out(), IN / OUT writes check_in_out. SCAN is view-only., Clear transient movement history without touching catalog/staff tables., recalculate_available_quantities(), record_yolo_capture(), _refresh()

### Community 29 - "export_table_snapshots"
Cohesion: 0.29
Nodes (7): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), insert_staff(), Export supported application tables to atomic CSV snapshots. only: optional…, Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…

### Community 30 - "BaseModel"
Cohesion: 0.33
Nodes (6): BaseModel, FaceModeBody, post_face_register(), _register_staff_face(), SamRegisterBody, StaffRegisterBody

### Community 31 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 32 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

## Knowledge Gaps
- **58 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 177 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `normalize_item_name`, `run_high_end_boot`, `main.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `camera_capture_loop()` (e.g. with `draw_landmarks()` and `run_backend_capture()`) actually correct?**
  _`camera_capture_loop()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `import_train_catalog()` (e.g. with `NoiseProfile` and `_catalog_import_job()`) actually correct?**
  _`import_train_catalog()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.039057239057239054 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.1425287356321839 - nodes in this community are weakly interconnected._