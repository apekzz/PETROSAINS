# Graph Report - inventory_app  (2026-09-26)

## Corpus Check
- 24 files · ~41,715 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .csv 6, .pt 5, .css 4)

## Summary
- 677 nodes · 1430 edges · 34 communities (32 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d145690d`
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
- reload_embedding_snapshots_from_csv
- loader.py
- updateTriggerStatus
- main.py
- _encode_worker_loop
- get_db
- sam_tool.py
- noise_transfer.py
- runBrowserFaceLoop
- fetchStats
- BaseModel
- startLocalCamera
- OneShot Inventory (`inventory_app`)
- Saved PostgreSQL tables
- sql.py
- post
- close_boot_connection
- replace_inventory_embeddings
- analyzeLocalFrame
- fetch_inventory_embeddings
- db.py
- ensure_tables
- setup_db.py
- applyMode
- consultant.js

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
  inventory_app/main.py → inventory_app/backend/config.py
- `create_session()` --indirect_call--> `_sessions()`  [INFERRED]
  inventory_app/backend/sam_tool.py → inventory_app/backend/consultant_model.py
- `face_status_payload()` --indirect_call--> `landmarks_complete()`  [INFERRED]
  inventory_app/main.py → inventory_app/backend/face.py
- `face_status_payload()` --indirect_call--> `face_in_region()`  [INFERRED]
  inventory_app/main.py → inventory_app/backend/face.py
- `_apply_face_embedding()` --calls--> `choose_staff_match()`  [INFERRED]
  inventory_app/main.py → inventory_app/backend/face.py

## Import Cycles
- None detected.

## Communities (34 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (49): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+41 more)

### Community 1 - "consultant_model.py"
Cohesion: 0.06
Nodes (65): advise(), age_bounds(), _blank(), blocking_rule(), _boundary_reply(), _by_setup(), setup(), _check_items() (+57 more)

### Community 2 - "run_high_end_boot"
Cohesion: 0.14
Nodes (16): get_lan_ip(), cosine_similarity(), image_to_embedding(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), match_inventory_name() (+8 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.14
Nodes (31): arm_object_detection(), camera_capture_loop(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state() (+23 more)

### Community 5 - "face.py"
Cohesion: 0.07
Nodes (34): argparse, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+26 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "reload_embedding_snapshots_from_csv"
Cohesion: 0.40
Nodes (5): TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Restore CSV data only into currently empty supported tables., reload_embedding_snapshots_from_csv(), _reset_serial_sequence(), restore_empty_tables_from_snapshots()

### Community 9 - "loader.py"
Cohesion: 0.24
Nodes (8): _bar(), finish(), set_progress(), start(), _width(), shutil, sys, time

### Community 10 - "updateTriggerStatus"
Cohesion: 0.21
Nodes (12): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), loadCatalogCompare(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream() (+4 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (40): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+32 more)

### Community 12 - "_encode_worker_loop"
Cohesion: 0.20
Nodes (12): _apply_face_embedding(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker(), handle_face_info() (+4 more)

### Community 13 - "get_db"
Cohesion: 0.12
Nodes (28): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+20 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.13
Nodes (19): create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model(), _mask_data_url() (+11 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.08
Nodes (50): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+42 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 18 - "BaseModel"
Cohesion: 0.18
Nodes (11): BaseModel, consultant_advise(), consultant_talk(), ConsultantRequest, FaceModeBody, post_face_register(), _register_staff_face(), SamRegisterBody (+3 more)

### Community 19 - "startLocalCamera"
Cohesion: 0.31
Nodes (10): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferLaptopDeviceId(), preferredCameraFacing() (+2 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "sql.py"
Cohesion: 0.11
Nodes (25): contextlib, _app_db_up(), bootstrap_database(), check_db(), connect_and_prepare(), _drop_stale_postmaster_pid(), ensure_database(), ensure_postgres_running() (+17 more)

### Community 24 - "post"
Cohesion: 0.12
Nodes (23): sam_status(), analyze_face_frame(), api_noise_capture(), api_start_camera(), capture_sam_frame(), detection_preview_active(), embed_captured_face(), face_status_payload() (+15 more)

### Community 25 - "close_boot_connection"
Cohesion: 0.27
Nodes (10): close_boot_connection(), _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave() (+2 more)

### Community 26 - "replace_inventory_embeddings"
Cohesion: 0.18
Nodes (12): clear_staff_embeddings(), _copy_table_to_file(), _embedding_to_text(), export_table_snapshots(), _export(), insert_staff(), _mobileclip2_id_skeleton(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive… (+4 more)

### Community 27 - "analyzeLocalFrame"
Cohesion: 0.32
Nodes (8): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo(), updateFacePreviews()

### Community 28 - "fetch_inventory_embeddings"
Cohesion: 0.33
Nodes (6): _embedding_from_text(), fetch_inventory_embeddings(), fetch_live_dual_embeddings(), fetch_staff_embeddings(), Fetch one emb table. Default = friend mobileclip2 (abubu)., mobileclip2 + noise catalogs for dual live match (legacy unused).

### Community 31 - "db.py"
Cohesion: 0.13
Nodes (23): init_schema(), Compatibility wrappers. All SQL lives in sql.py., Boot helper — create missing tables only. Never seeds or overwrites., clear_check_in_out(), compare_mobileclip2_vs_noise(), insert_check_in_out(), mean_name_vectors(), normalize_item_name() (+15 more)

### Community 32 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 33 - "setup_db.py"
Cohesion: 0.20
Nodes (10): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), psycopg (+2 more)

### Community 34 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 35 - "consultant.js"
Cohesion: 0.20
Nodes (20): advise(), ageFrom(), askNext(), block(), boundaryText(), decline(), foldFacts(), hasAudience() (+12 more)

## Knowledge Gaps
- **68 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 198 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `run_high_end_boot`, `replace_inventory_embeddings`, `main.py`, `db.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _68 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03634085213032581 - nodes in this community are weakly interconnected._
- **Should `consultant_model.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06338028169014084 - nodes in this community are weakly interconnected._
- **Should `run_high_end_boot` be split into smaller, more focused modules?**
  _Cohesion score 0.14166666666666666 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.13548387096774195 - nodes in this community are weakly interconnected._