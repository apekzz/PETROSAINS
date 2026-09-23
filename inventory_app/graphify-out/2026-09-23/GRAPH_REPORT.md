# Graph Report - inventory_app  (2026-09-23)

## Corpus Check
- 18 files · ~28,014 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .csv 6, .pt 4, .css 3)

## Summary
- 579 nodes · 1194 edges · 35 communities (33 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `80c3a4b4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- get
- run_high_end_boot
- sam-tool.js
- camera_capture_loop
- face.py
- applyFaceStatus
- tables
- connect_and_prepare
- db.py
- updateTriggerStatus
- main.py
- loader.py
- api.py
- sam_tool.py
- noise_transfer.py
- runBrowserFaceLoop
- fetchStats
- setup_db.py
- startLocalCamera
- OneShot Inventory (`inventory_app`)
- Saved PostgreSQL tables
- sql.py
- post
- normalize_item_name
- export_table_snapshots
- analyzeLocalFrame
- refresh_main_inventory
- close_boot_connection
- _catalog_import_job
- refresh_inventory_catalog_cache
- bootstrap_database
- ensure_tables
- applyMode

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `connect_and_prepare()` - 15 edges
3. `camera_capture_loop()` - 14 edges
4. `import_train_catalog()` - 13 edges
5. `normalize_item_name()` - 13 edges
6. `applyFaceStatus()` - 13 edges
7. `capture_laptop_noise_profile()` - 12 edges
8. `analyzeLocalFrame()` - 11 edges
9. `startLocalCamera()` - 11 edges
10. `face_status_payload()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `_prep()` --calls--> `normalize_item_name()`  [INFERRED]
  main.py → database/sql.py
- `get_inventory()` --calls--> `fetch_inventory()`  [INFERRED]
  backend/api.py → database/sql.py
- `get_movements()` --calls--> `fetch_movements()`  [INFERRED]
  backend/api.py → database/sql.py
- `get_stats()` --calls--> `fetch_stats()`  [INFERRED]
  backend/api.py → database/sql.py
- `search_inventory()` --calls--> `fetch_inventory()`  [INFERRED]
  backend/api.py → database/sql.py

## Import Cycles
- None detected.

## Communities (35 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (46): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnHeaderRegisterFace (+38 more)

### Community 1 - "get"
Cohesion: 0.14
Nodes (16): camera_status(), catalog_compare(), catalog_import_status(), db_status(), detection_preview(), generate_frames(), get_detection_mode(), get_mode() (+8 more)

### Community 2 - "run_high_end_boot"
Cohesion: 0.22
Nodes (11): get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API. (+3 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.13
Nodes (31): arm_object_detection(), boot_status(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active() (+23 more)

### Community 5 - "face.py"
Cohesion: 0.06
Nodes (38): argparse, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+30 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "connect_and_prepare"
Cohesion: 0.18
Nodes (11): check_db(), connect_and_prepare(), ensure_schema_columns(), _lock(), _open_connection(), Safely migrate existing installations without dropping data., Reject incompatible existing tables without deleting or replacing them., Tables whose CSV is missing or row-count differs from Postgres. (+3 more)

### Community 9 - "db.py"
Cohesion: 0.22
Nodes (14): Compatibility wrappers. All SQL lives in sql.py., clear_staff_embeddings(), _embedding_from_text(), fetch_detections_summary(), fetch_inventory_embeddings(), fetch_staff(), fetch_staff_embeddings(), get_db() (+6 more)

### Community 10 - "updateTriggerStatus"
Cohesion: 0.21
Nodes (12): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), loadCatalogCompare(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream() (+4 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (41): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+33 more)

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
Cohesion: 0.09
Nodes (43): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+35 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 18 - "setup_db.py"
Cohesion: 0.20
Nodes (11): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), fetch_inventory() (+3 more)

### Community 19 - "startLocalCamera"
Cohesion: 0.31
Nodes (10): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferLaptopDeviceId(), preferredCameraFacing() (+2 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "sql.py"
Cohesion: 0.19
Nodes (13): contextlib, _checkout_as_detection(), ensure_postgres_running(), fetch_detections(), fetch_detections_today(), fetch_item(), fetch_movements(), _format_dt() (+5 more)

### Community 24 - "post"
Cohesion: 0.12
Nodes (24): sam_status(), BaseModel, analyze_face_frame(), api_noise_capture(), api_start_camera(), capture_sam_frame(), detection_preview_active(), embed_captured_face() (+16 more)

### Community 25 - "normalize_item_name"
Cohesion: 0.19
Nodes (14): compare_mobileclip2_vs_noise(), fetch_item_summary(), fetch_live_dual_embeddings(), mean_name_vectors(), normalize_item_name(), mobileclip2 + noise catalogs for dual live match (legacy unused)., Average embedding per inventory_name (for compare)., Per-name compare: mobileclip2 vs noise (mean vectors). Returns crop counts,… (+6 more)

### Community 26 - "export_table_snapshots"
Cohesion: 0.29
Nodes (8): _copy_table_to_file(), _embedding_to_text(), export_table_snapshots(), _export(), insert_staff(), Export supported application tables to atomic CSV snapshots. only: optional…, Noise train import → replace inventory_emb_noise only (leave friend catalogs)., replace_inventory_embeddings()

### Community 27 - "analyzeLocalFrame"
Cohesion: 0.32
Nodes (8): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo(), updateFacePreviews()

### Community 28 - "refresh_main_inventory"
Cohesion: 0.18
Nodes (11): clear_check_in_out(), TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Restore CSV data only into currently empty supported tables., Rebuild summary from mobileclip2 (abubu rule); fallback legacy inventory_emb., Clear transient movement history without touching catalog/staff tables., recalculate_available_quantities(), refresh_main_inventory(), _refresh() (+3 more)

### Community 29 - "close_boot_connection"
Cohesion: 0.24
Nodes (11): close_boot_connection(), _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave() (+3 more)

### Community 30 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir}., select_and_import_catalog(), _start_catalog_import()

### Community 31 - "refresh_inventory_catalog_cache"
Cohesion: 0.22
Nodes (9): catalog_dual_status(), get_inventory_catalog(), get_inventory_catalogs(), match_inventory_name(), parse_yolo_boxes(), Backward-compat: mobileclip2 rows only., Dual live: score mobileclip2 + noise. Accept if either clears threshold., refresh_inventory_catalog_cache() (+1 more)

### Community 32 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 33 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 34 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

## Knowledge Gaps
- **65 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 191 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `_catalog_import_job` to `run_high_end_boot`, `main.py`, `noise_transfer.py`, `export_table_snapshots`, `refresh_inventory_catalog_cache`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `import_train_catalog()` connect `noise_transfer.py` to `_catalog_import_job`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `camera_capture_loop()` (e.g. with `draw_landmarks()` and `run_backend_capture()`) actually correct?**
  _`camera_capture_loop()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03771043771043771 - nodes in this community are weakly interconnected._
- **Should `get` be split into smaller, more focused modules?**
  _Cohesion score 0.14166666666666666 - nodes in this community are weakly interconnected._