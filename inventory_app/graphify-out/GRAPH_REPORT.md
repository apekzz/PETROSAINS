# Graph Report - inventory_app  (2026-09-26)

## Corpus Check
- 24 files · ~41,386 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .csv 6, .pt 5, .css 4)

## Summary
- 670 nodes · 1411 edges · 37 communities (35 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `05896f39`
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
- connect_and_prepare
- loader.py
- updateTriggerStatus
- main.py
- _encode_worker_loop
- get_db
- sam_tool.py
- noise_transfer.py
- runBrowserFaceLoop
- fetchStats
- register_sam_embedding
- startLocalCamera
- OneShot Inventory (`inventory_app`)
- Saved PostgreSQL tables
- sql.py
- post
- _catalog_import_job
- export_table_snapshots
- analyzeLocalFrame
- bootstrap_database
- _clear_session_movements
- capture_sam_frame
- db.py
- ensure_tables
- setup_db.py
- applyMode
- consultant.js
- reload_embedding_snapshots_from_csv

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `pair_features()` - 16 edges
3. `advise()` - 15 edges
4. `connect_and_prepare()` - 15 edges
5. `normalize_item_name()` - 14 edges
6. `camera_capture_loop()` - 14 edges
7. `import_train_catalog()` - 13 edges
8. `applyFaceStatus()` - 13 edges
9. `rank()` - 12 edges
10. `capture_laptop_noise_profile()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `run_high_end_boot()` --calls--> `get_lan_ip()`  [INFERRED]
  main.py → backend/config.py
- `select_and_import_catalog()` --indirect_call--> `choose_folder()`  [INFERRED]
  main.py → backend/dataset_importer.py
- `_catalog_import_job()` --calls--> `import_train_catalog()`  [INFERRED]
  main.py → backend/dataset_importer.py
- `face_status_payload()` --indirect_call--> `landmarks_complete()`  [INFERRED]
  main.py → backend/face.py
- `face_status_payload()` --indirect_call--> `face_in_region()`  [INFERRED]
  main.py → backend/face.py

## Import Cycles
- None detected.

## Communities (37 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (48): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+40 more)

### Community 1 - "consultant_model.py"
Cohesion: 0.07
Nodes (62): advise(), age_bounds(), _blank(), blocking_rule(), _by_setup(), setup(), _check_items(), _cloud_reply() (+54 more)

### Community 2 - "run_high_end_boot"
Cohesion: 0.22
Nodes (11): get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API. (+3 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.13
Nodes (32): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode() (+24 more)

### Community 5 - "face.py"
Cohesion: 0.06
Nodes (36): argparse, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+28 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "connect_and_prepare"
Cohesion: 0.15
Nodes (13): check_db(), close_boot_connection(), connect_and_prepare(), ensure_schema_columns(), _lock(), _open_connection(), Safely migrate existing installations without dropping data., Reject incompatible existing tables without deleting or replacing them. (+5 more)

### Community 9 - "loader.py"
Cohesion: 0.24
Nodes (8): _bar(), finish(), set_progress(), start(), _width(), shutil, sys, time

### Community 10 - "updateTriggerStatus"
Cohesion: 0.21
Nodes (12): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), loadCatalogCompare(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream() (+4 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (38): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+30 more)

### Community 12 - "_encode_worker_loop"
Cohesion: 0.14
Nodes (18): analyze_face_frame(), _apply_face_embedding(), cosine_similarity(), embed_captured_face(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding() (+10 more)

### Community 13 - "get_db"
Cohesion: 0.14
Nodes (25): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+17 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.15
Nodes (16): create_mask(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model(), _mask_data_url(), ndarray (+8 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.08
Nodes (45): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+37 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 18 - "register_sam_embedding"
Cohesion: 0.31
Nodes (9): create_masked_crop(), Create a tight, black-background crop for the shared OpenCLIP encoder., save_object_embedding(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), refresh_inventory_catalog_cache() (+1 more)

### Community 19 - "startLocalCamera"
Cohesion: 0.31
Nodes (10): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferLaptopDeviceId(), preferredCameraFacing() (+2 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "sql.py"
Cohesion: 0.13
Nodes (19): contextlib, _app_db_up(), _checkout_as_detection(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_live_dual_embeddings() (+11 more)

### Community 24 - "post"
Cohesion: 0.10
Nodes (26): BaseModel, api_noise_capture(), api_start_camera(), _cancel_app_exit(), consultant_advise(), consultant_talk(), ConsultantRequest, dashboard_hello() (+18 more)

### Community 25 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir, noise_capture_dir?}., select_and_import_catalog(), _start_catalog_import()

### Community 26 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…, Export supported application tables to atomic CSV snapshots. only: optional…

### Community 27 - "analyzeLocalFrame"
Cohesion: 0.32
Nodes (8): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo(), updateFacePreviews()

### Community 28 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 29 - "_clear_session_movements"
Cohesion: 0.33
Nodes (7): _clear_session_movements(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event(), stop_camera(), on_event

### Community 30 - "capture_sam_frame"
Cohesion: 0.33
Nodes (6): sam_status(), capture_sam_frame(), generate_sam_mask(), get_sam_status(), SamMaskBody, _touch_heartbeat()

### Community 31 - "db.py"
Cohesion: 0.13
Nodes (23): Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), compare_mobileclip2_vs_noise(), _embedding_to_text(), insert_check_in_out(), insert_staff(), mean_name_vectors(), _mobileclip2_id_skeleton() (+15 more)

### Community 32 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 33 - "setup_db.py"
Cohesion: 0.22
Nodes (9): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), psycopg (+1 more)

### Community 34 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 35 - "consultant.js"
Cohesion: 0.24
Nodes (14): advise(), ageFrom(), askNext(), block(), clearTime(), hasAudience(), ingest(), payload() (+6 more)

### Community 36 - "reload_embedding_snapshots_from_csv"
Cohesion: 0.40
Nodes (5): TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Restore CSV data only into currently empty supported tables., reload_embedding_snapshots_from_csv(), _reset_serial_sequence(), restore_empty_tables_from_snapshots()

## Knowledge Gaps
- **67 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 198 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `_catalog_import_job` to `run_high_end_boot`, `main.py`, `noise_transfer.py`, `register_sam_embedding`, `db.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `import_train_catalog()` connect `noise_transfer.py` to `_catalog_import_job`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03634085213032581 - nodes in this community are weakly interconnected._
- **Should `consultant_model.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07086247086247087 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.12701612903225806 - nodes in this community are weakly interconnected._