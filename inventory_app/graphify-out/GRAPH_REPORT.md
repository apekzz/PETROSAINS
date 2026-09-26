# Graph Report - inventory_app  (2026-09-26)

## Corpus Check
- 24 files · ~43,446 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: .csv 6, .pt 5, .css 4)

## Summary
- 708 nodes · 1503 edges · 37 communities (31 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 87 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `548a389a`
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
- post
- db.py
- analyzeLocalFrame
- BaseModel
- close_boot_connection
- export_table_snapshots
- ref_fs
- sql.py
- ensure_tables
- setup_db.py
- reload_embedding_snapshots_from_csv
- consultant.js
- ref_https_cdn_jsdelivr_net_npm_mediapipe_tasks_vision_0_10_14_vision_bundle_mjs

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `pair_features()` - 16 edges
3. `advise()` - 16 edges
4. `connect_and_prepare()` - 16 edges
5. `startLocalCamera()` - 15 edges
6. `normalize_item_name()` - 14 edges
7. `camera_capture_loop()` - 14 edges
8. `import_train_catalog()` - 13 edges
9. `applyFaceStatus()` - 13 edges
10. `rank()` - 12 edges

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
Nodes (52): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs (+44 more)

### Community 1 - "consultant_model.py"
Cohesion: 0.06
Nodes (73): advise(), age_bounds(), _blank(), blocking_rule(), _boundary_reply(), _by_setup(), setup(), _check_items() (+65 more)

### Community 2 - "config.py"
Cohesion: 0.07
Nodes (26): ensure_lan_cert(), get_lan_ip(), _bar(), finish(), set_progress(), start(), _width(), init_schema() (+18 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.12
Nodes (33): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode() (+25 more)

### Community 5 - "face.py"
Cohesion: 0.07
Nodes (34): argparse, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+26 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.23
Nodes (15): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+7 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "register_sam_embedding"
Cohesion: 0.11
Nodes (22): sam_status(), save_object_embedding(), capture_sam_frame(), cosine_similarity(), create_object_embedding(), generate_sam_mask(), get_inventory_catalog(), get_sam_status() (+14 more)

### Community 10 - "updateTriggerStatus"
Cohesion: 0.21
Nodes (12): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), loadCatalogCompare(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream() (+4 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (39): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+31 more)

### Community 12 - "_encode_worker_loop"
Cohesion: 0.21
Nodes (12): _apply_face_embedding(), embed_captured_face(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_embed_worker(), _load_clip_weights() (+4 more)

### Community 13 - "get_db"
Cohesion: 0.14
Nodes (25): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+17 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model(), _mask_data_url() (+10 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.08
Nodes (49): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+41 more)

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
Cohesion: 0.13
Nodes (15): apply_saved_stock_totals(), check_db(), connect_and_prepare(), ensure_schema_columns(), _lock(), _open_connection(), Safely migrate existing installations without dropping data., Reject incompatible existing tables without deleting or replacing them. (+7 more)

### Community 24 - "post"
Cohesion: 0.16
Nodes (16): analyze_face_frame(), api_noise_capture(), api_start_camera(), detection_preview_active(), _face_detect_job(), face_status_payload(), get_face_status(), handle_face_info() (+8 more)

### Community 25 - "db.py"
Cohesion: 0.14
Nodes (22): Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), compare_mobileclip2_vs_noise(), _embedding_to_text(), insert_check_in_out(), insert_staff(), mean_name_vectors(), _mobileclip2_id_skeleton() (+14 more)

### Community 26 - "analyzeLocalFrame"
Cohesion: 0.21
Nodes (13): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), captureButtonLabel(), drawLandmarks(), drawMediaPipeLandmarks(), enableCaptureFallback(), grabLocalFrame() (+5 more)

### Community 27 - "BaseModel"
Cohesion: 0.18
Nodes (12): BaseModel, consultant_advise(), _consultant_tables(), consultant_talk(), ConsultantRequest, FaceModeBody, post_face_register(), Live quantity tables. Photo embedding tables have no stock counts. (+4 more)

### Community 28 - "close_boot_connection"
Cohesion: 0.27
Nodes (10): close_boot_connection(), _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave() (+2 more)

### Community 29 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…, Export supported application tables to atomic CSV snapshots. only: optional…

### Community 31 - "sql.py"
Cohesion: 0.13
Nodes (19): contextlib, _app_db_up(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_live_dual_embeddings(), fetch_staff_embeddings() (+11 more)

### Community 32 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 33 - "setup_db.py"
Cohesion: 0.20
Nodes (10): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), os (+2 more)

### Community 34 - "reload_embedding_snapshots_from_csv"
Cohesion: 0.40
Nodes (5): TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Restore CSV data only into currently empty supported tables., reload_embedding_snapshots_from_csv(), _reset_serial_sequence(), restore_empty_tables_from_snapshots()

### Community 35 - "consultant.js"
Cohesion: 0.19
Nodes (24): advise(), ageFrom(), askNext(), block(), boundaryText(), decline(), foldFacts(), followUp() (+16 more)

## Knowledge Gaps
- **68 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 206 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `register_sam_embedding`, `db.py`, `main.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `config.py`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _68 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03559322033898305 - nodes in this community are weakly interconnected._
- **Should `consultant_model.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06220095693779904 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07459677419354839 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.12310606060606061 - nodes in this community are weakly interconnected._