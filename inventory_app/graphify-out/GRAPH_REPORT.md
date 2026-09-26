# Graph Report - inventory_app  (2026-09-26)

## Corpus Check
- 24 files · ~44,315 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: .csv 6, .pt 5, .css 4)

## Summary
- 720 nodes · 1534 edges · 39 communities (33 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9b41302`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- consultant_model.py
- infer.py
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
- db.py
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
- normalize_item_name
- analyzeLocalFrame
- BaseModel
- close_boot_connection
- export_table_snapshots
- ref_fs
- sql.py
- ensure_tables
- setup_db.py
- run_high_end_boot
- consultant.js
- bootstrap_database
- loader.py
- ref_https_cdn_jsdelivr_net_npm_mediapipe_tasks_vision_0_10_14_vision_bundle_mjs

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `pair_features()` - 16 edges
3. `advise()` - 16 edges
4. `connect_and_prepare()` - 16 edges
5. `startLocalCamera()` - 15 edges
6. `normalize_item_name()` - 14 edges
7. `ingest()` - 14 edges
8. `camera_capture_loop()` - 14 edges
9. `import_train_catalog()` - 13 edges
10. `applyFaceStatus()` - 13 edges

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

## Communities (39 total, 6 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (52): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs (+44 more)

### Community 1 - "consultant_model.py"
Cohesion: 0.06
Nodes (73): advise(), age_bounds(), _blank(), blocking_rule(), _boundary_reply(), _by_setup(), setup(), _check_items() (+65 more)

### Community 2 - "infer.py"
Cohesion: 0.16
Nodes (12): argparse, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon., Run the v2 segmentation model. Same call shape as the notebook. (+4 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.13
Nodes (31): arm_object_detection(), boot_status(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active() (+23 more)

### Community 5 - "face.py"
Cohesion: 0.12
Nodes (21): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+13 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.23
Nodes (15): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+7 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "register_sam_embedding"
Cohesion: 0.36
Nodes (8): save_object_embedding(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), parse_yolo_boxes(), refresh_inventory_catalog_cache(), register_sam_embedding()

### Community 10 - "updateTriggerStatus"
Cohesion: 0.21
Nodes (12): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), loadCatalogCompare(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream() (+4 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (38): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+30 more)

### Community 12 - "_encode_worker_loop"
Cohesion: 0.13
Nodes (17): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker() (+9 more)

### Community 13 - "db.py"
Cohesion: 0.13
Nodes (29): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+21 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model(), _mask_data_url() (+10 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.08
Nodes (50): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+42 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.22
Nodes (11): applyLocalFace(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate(), runBrowserFaceLoop() (+3 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 19 - "startLocalCamera"
Cohesion: 0.27
Nodes (10): cameraChoiceSaved(), hideRemoteCameraPicker(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), preferLaptopDeviceId(), readCameraPermission(), refreshCameraList() (+2 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "connect_and_prepare"
Cohesion: 0.10
Nodes (22): apply_saved_stock_totals(), clear_check_in_out(), connect_and_prepare(), ensure_schema_columns(), _open_connection(), Clear transient movement history without touching catalog/staff tables., Safely migrate existing installations without dropping data., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is). (+14 more)

### Community 24 - "post"
Cohesion: 0.12
Nodes (23): sam_status(), analyze_face_frame(), api_noise_capture(), api_start_camera(), capture_sam_frame(), detection_preview_active(), embed_captured_face(), face_status_payload() (+15 more)

### Community 25 - "normalize_item_name"
Cohesion: 0.16
Nodes (15): compare_mobileclip2_vs_noise(), _embedding_to_text(), insert_staff(), mean_name_vectors(), _mobileclip2_id_skeleton(), normalize_item_name(), Average embedding per inventory_name (for compare)., Per-name compare: mobileclip2 vs noise (mean vectors). Returns crop counts,… (+7 more)

### Community 26 - "analyzeLocalFrame"
Cohesion: 0.21
Nodes (13): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), captureButtonLabel(), drawLandmarks(), drawMediaPipeLandmarks(), enableCaptureFallback(), grabLocalFrame() (+5 more)

### Community 27 - "BaseModel"
Cohesion: 0.22
Nodes (10): BaseModel, consultant_advise(), _consultant_tables(), consultant_talk(), ConsultantRequest, FaceModeBody, Live quantity tables. Photo embedding tables have no stock counts., SamRegisterBody (+2 more)

### Community 28 - "close_boot_connection"
Cohesion: 0.24
Nodes (11): close_boot_connection(), _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave() (+3 more)

### Community 29 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…, Export supported application tables to atomic CSV snapshots. only: optional…

### Community 31 - "sql.py"
Cohesion: 0.11
Nodes (22): contextlib, _app_db_up(), check_db(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_live_dual_embeddings() (+14 more)

### Community 32 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 33 - "setup_db.py"
Cohesion: 0.13
Nodes (13): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), json (+5 more)

### Community 34 - "run_high_end_boot"
Cohesion: 0.18
Nodes (13): ensure_lan_cert(), get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there. (+5 more)

### Community 35 - "consultant.js"
Cohesion: 0.13
Nodes (36): advise(), ageForLevel(), ageFrom(), askNext(), blankChat(), block(), boundaryText(), clearSide() (+28 more)

### Community 36 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 37 - "loader.py"
Cohesion: 0.24
Nodes (8): _bar(), finish(), set_progress(), start(), _width(), shutil, sys, time

## Knowledge Gaps
- **68 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 206 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `register_sam_embedding`, `normalize_item_name`, `run_high_end_boot`, `main.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _68 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03559322033898305 - nodes in this community are weakly interconnected._
- **Should `consultant_model.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06220095693779904 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.12688172043010754 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1164021164021164 - nodes in this community are weakly interconnected._