# Graph Report - inventory_app  (2026-09-26)

## Corpus Check
- 24 files · ~42,438 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: .csv 6, .pt 5, .css 4)

## Summary
- 691 nodes · 1457 edges · 37 communities (31 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 86 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3f30865`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- consultant_model.py
- config.py
- sam-tool.js
- camera_capture_loop
- face.py
- applyFaceStatus
- tables
- register_sam_embedding
- ref_path
- updateTriggerStatus
- main.py
- _encode_worker_loop
- get_db
- sam_tool.py
- noise_transfer.py
- runBrowserFaceLoop
- fetchStats
- ref_crypto
- startLocalCamera
- OneShot Inventory (`inventory_app`)
- Saved PostgreSQL tables
- connect_and_prepare
- BaseModel
- db.py
- bootstrap_database
- setup_db.py
- _clear_session_movements
- replace_inventory_embeddings
- ref_fs
- sql.py
- ensure_tables
- applyMode
- consultant.js
- post
- ref_https_cdn_jsdelivr_net_npm_mediapipe_tasks_vision_0_10_14_vision_bundle_mjs

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `pair_features()` - 16 edges
3. `connect_and_prepare()` - 16 edges
4. `advise()` - 15 edges
5. `normalize_item_name()` - 14 edges
6. `camera_capture_loop()` - 14 edges
7. `import_train_catalog()` - 13 edges
8. `applyFaceStatus()` - 13 edges
9. `rank()` - 12 edges
10. `capture_laptop_noise_profile()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `run_high_end_boot()` --calls--> `get_lan_ip()`  [INFERRED]
  main.py → backend/config.py
- `run_high_end_boot()` --calls--> `ensure_lan_cert()`  [INFERRED]
  main.py → backend/config.py
- `face_status_payload()` --indirect_call--> `landmarks_complete()`  [INFERRED]
  main.py → backend/face.py
- `face_status_payload()` --indirect_call--> `face_in_region()`  [INFERRED]
  main.py → backend/face.py
- `_apply_face_embedding()` --calls--> `choose_staff_match()`  [INFERRED]
  main.py → backend/face.py

## Import Cycles
- None detected.

## Communities (37 total, 6 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (49): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+41 more)

### Community 1 - "consultant_model.py"
Cohesion: 0.07
Nodes (64): advise(), age_bounds(), _blank(), blocking_rule(), _boundary_reply(), _by_setup(), setup(), _check_items() (+56 more)

### Community 2 - "config.py"
Cohesion: 0.08
Nodes (24): ensure_lan_cert(), get_lan_ip(), _bar(), finish(), set_progress(), start(), _width(), json (+16 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.13
Nodes (32): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode() (+24 more)

### Community 5 - "face.py"
Cohesion: 0.07
Nodes (33): argparse, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+25 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.23
Nodes (15): analyzeLocalFrame(), applyFaceStatus(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), grabLocalFrame(), grabSegmentedFace(), hasCapturedRegisterFace() (+7 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "register_sam_embedding"
Cohesion: 0.36
Nodes (8): save_object_embedding(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), refresh_inventory_catalog_cache(), register_sam_embedding(), SamRegisterBody

### Community 10 - "updateTriggerStatus"
Cohesion: 0.38
Nodes (7): applyObjectRecognitionState(), maybeToastCapture(), restoreLiveDetectionStream(), showCaptureAlert(), showFrozenDetectionPreview(), startObjectRecognition(), updateTriggerStatus()

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (39): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+31 more)

### Community 12 - "_encode_worker_loop"
Cohesion: 0.12
Nodes (18): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker() (+10 more)

### Community 13 - "get_db"
Cohesion: 0.12
Nodes (28): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+20 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model(), _mask_data_url() (+10 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.08
Nodes (49): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+41 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.16
Nodes (14): applyLocalFace(), drawLandmarks(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan() (+6 more)

### Community 17 - "fetchStats"
Cohesion: 0.14
Nodes (16): animateValue(), escapeHtml(), fetchInventory(), fetchSelectedItemStats(), fetchStats(), loadCatalogCompare(), loadItemOptions(), pollCatalogImport() (+8 more)

### Community 19 - "startLocalCamera"
Cohesion: 0.21
Nodes (16): applyCapturedPhoto(), captureButtonLabel(), enableCaptureFallback(), hideRemoteCameraPicker(), ingestScanFrame(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback() (+8 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "connect_and_prepare"
Cohesion: 0.12
Nodes (19): apply_saved_stock_totals(), connect_and_prepare(), ensure_schema_columns(), _open_connection(), Safely migrate existing installations without dropping data., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Reject incompatible existing tables without deleting or replacing them., Tables whose CSV is missing or row-count differs from Postgres. (+11 more)

### Community 24 - "BaseModel"
Cohesion: 0.15
Nodes (13): sam_status(), BaseModel, capture_sam_frame(), consultant_advise(), consultant_talk(), ConsultantRequest, FaceModeBody, generate_sam_mask() (+5 more)

### Community 25 - "db.py"
Cohesion: 0.20
Nodes (14): Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), compare_mobileclip2_vs_noise(), insert_check_in_out(), mean_name_vectors(), normalize_item_name(), IN / OUT writes check_in_out. SCAN is view-only., Clear transient movement history without touching catalog/staff tables. (+6 more)

### Community 26 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 27 - "setup_db.py"
Cohesion: 0.20
Nodes (10): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), os (+2 more)

### Community 28 - "_clear_session_movements"
Cohesion: 0.40
Nodes (6): _clear_session_movements(), _exit_app(), _force_close(), shutdown_event(), stop_camera(), on_event

### Community 29 - "replace_inventory_embeddings"
Cohesion: 0.18
Nodes (12): clear_staff_embeddings(), _copy_table_to_file(), _embedding_to_text(), export_table_snapshots(), _export(), insert_staff(), _mobileclip2_id_skeleton(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive… (+4 more)

### Community 31 - "sql.py"
Cohesion: 0.12
Nodes (20): contextlib, _app_db_up(), check_db(), close_boot_connection(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings() (+12 more)

### Community 32 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 34 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 35 - "consultant.js"
Cohesion: 0.20
Nodes (23): advise(), ageFrom(), askNext(), block(), boundaryText(), decline(), foldFacts(), followUp() (+15 more)

### Community 52 - "post"
Cohesion: 0.13
Nodes (21): analyze_face_frame(), api_noise_capture(), api_start_camera(), _cancel_app_exit(), dashboard_hello(), dashboard_leave(), detection_preview_active(), embed_captured_face() (+13 more)

## Knowledge Gaps
- **68 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 203 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `register_sam_embedding`, `config.py`, `main.py`, `replace_inventory_embeddings`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `config.py`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _68 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03634085213032581 - nodes in this community are weakly interconnected._
- **Should `consultant_model.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0684811237928007 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08045977011494253 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.12701612903225806 - nodes in this community are weakly interconnected._