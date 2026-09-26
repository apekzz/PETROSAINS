# Graph Report - inventory_app  (2026-09-26)

## Corpus Check
- 24 files · ~42,369 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: .csv 6, .pt 5, .css 4)

## Summary
- 689 nodes · 1449 edges · 37 communities (31 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 86 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3f30865`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- consultant_model.py
- run_high_end_boot
- sam-tool.js
- camera_capture_loop
- face.py
- applyFaceStatus
- tables
- normalize_item_name
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
- post
- db.py
- bootstrap_database
- loader.py
- _clear_session_movements
- export_table_snapshots
- ref_fs
- sql.py
- ensure_tables
- applyMode
- consultant.js
- face_status_payload
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
- `camera_capture_loop()` --calls--> `draw_landmarks()`  [INFERRED]
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

### Community 2 - "run_high_end_boot"
Cohesion: 0.18
Nodes (13): ensure_lan_cert(), get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there. (+5 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.13
Nodes (32): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_trigger_state() (+24 more)

### Community 5 - "face.py"
Cohesion: 0.13
Nodes (19): _align_template(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate, _five_from_yunet() (+11 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.23
Nodes (15): analyzeLocalFrame(), applyFaceStatus(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), grabLocalFrame(), grabSegmentedFace(), hasCapturedRegisterFace() (+7 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "normalize_item_name"
Cohesion: 0.20
Nodes (16): _embedding_to_text(), insert_staff(), _mobileclip2_id_skeleton(), normalize_item_name(), SAM / one-shot register → mobileclip2 (abubu live primary)., Read-only (id, name) from mobileclip2 — never write that table. Prefer live PG…, Noise train import → replace inventory_emb_noise only (leave friend catalogs).…, replace_inventory_embeddings() (+8 more)

### Community 10 - "updateTriggerStatus"
Cohesion: 0.38
Nodes (7): applyObjectRecognitionState(), maybeToastCapture(), restoreLiveDetectionStream(), showCaptureAlert(), showFrozenDetectionPreview(), startObjectRecognition(), updateTriggerStatus()

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (41): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+33 more)

### Community 12 - "_encode_worker_loop"
Cohesion: 0.20
Nodes (11): _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _load_clip_weights(), post_face_register(), _prepare_embed_image(), _prepare_inventory_model_image() (+3 more)

### Community 13 - "get_db"
Cohesion: 0.12
Nodes (29): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+21 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.05
Nodes (41): argparse, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon., Run the v2 segmentation model. Same call shape as the notebook. (+33 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.07
Nodes (51): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+43 more)

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
Cohesion: 0.13
Nodes (17): apply_saved_stock_totals(), clear_check_in_out(), connect_and_prepare(), ensure_schema_columns(), _open_connection(), Clear transient movement history without touching catalog/staff tables., Safely migrate existing installations without dropping data., Reject incompatible existing tables without deleting or replacing them. (+9 more)

### Community 24 - "post"
Cohesion: 0.11
Nodes (24): sam_status(), BaseModel, api_noise_capture(), api_start_camera(), capture_sam_frame(), consultant_advise(), consultant_talk(), ConsultantRequest (+16 more)

### Community 25 - "db.py"
Cohesion: 0.19
Nodes (12): Compatibility wrappers. All SQL lives in sql.py., check_db(), close_boot_connection(), insert_check_in_out(), _lock(), IN / OUT writes check_in_out. SCAN is view-only., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Restore CSV data only into currently empty supported tables. (+4 more)

### Community 26 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 27 - "loader.py"
Cohesion: 0.24
Nodes (8): _bar(), finish(), set_progress(), start(), _width(), shutil, sys, time

### Community 28 - "_clear_session_movements"
Cohesion: 0.22
Nodes (10): _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event() (+2 more)

### Community 29 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…, Export supported application tables to atomic CSV snapshots. only: optional…

### Community 31 - "sql.py"
Cohesion: 0.13
Nodes (19): contextlib, _app_db_up(), compare_mobileclip2_vs_noise(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_live_dual_embeddings() (+11 more)

### Community 32 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 34 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 35 - "consultant.js"
Cohesion: 0.20
Nodes (21): advise(), ageFrom(), askNext(), block(), boundaryText(), decline(), foldFacts(), followUp() (+13 more)

### Community 52 - "face_status_payload"
Cohesion: 0.15
Nodes (15): choose_staff_match(), One face at a time, matched against every enrolled staff. Full-threshold hits…, analyze_face_frame(), _apply_face_embedding(), cosine_similarity(), detection_preview_active(), embed_captured_face(), _face_detect_job() (+7 more)

## Knowledge Gaps
- **68 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 203 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `normalize_item_name`, `run_high_end_boot`, `main.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _68 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03634085213032581 - nodes in this community are weakly interconnected._
- **Should `consultant_model.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0684811237928007 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.12701612903225806 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12615384615384614 - nodes in this community are weakly interconnected._