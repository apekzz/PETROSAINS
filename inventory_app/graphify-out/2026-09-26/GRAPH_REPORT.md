# Graph Report - inventory_app  (2026-09-26)

## Corpus Check
- 24 files · ~40,910 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .csv 6, .pt 5, .css 4)

## Summary
- 661 nodes · 1392 edges · 32 communities (30 shown, 2 thin omitted)
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
- face_crop_to_embedding
- get_db
- sam_tool.py
- noise_transfer.py
- runBrowserFaceLoop
- fetchStats
- startLocalCamera
- OneShot Inventory (`inventory_app`)
- Saved PostgreSQL tables
- sql.py
- post
- export_table_snapshots
- analyzeLocalFrame
- db.py
- get
- normalize_item_name
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
  main.py → backend/config.py
- `face_status_payload()` --indirect_call--> `landmarks_complete()`  [INFERRED]
  main.py → backend/face.py
- `face_status_payload()` --indirect_call--> `face_in_region()`  [INFERRED]
  main.py → backend/face.py
- `camera_capture_loop()` --calls--> `draw_landmarks()`  [INFERRED]
  main.py → backend/face.py
- `load_face_gate()` --uses--> `FaceGate`  [INFERRED]
  main.py → backend/face.py

## Import Cycles
- None detected.

## Communities (32 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (48): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+40 more)

### Community 1 - "consultant_model.py"
Cohesion: 0.07
Nodes (61): advise(), age_bounds(), _blank(), blocking_rule(), _by_setup(), setup(), _check_items(), _cover() (+53 more)

### Community 2 - "run_high_end_boot"
Cohesion: 0.20
Nodes (12): get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API. (+4 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.13
Nodes (31): arm_object_detection(), boot_status(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active() (+23 more)

### Community 5 - "face.py"
Cohesion: 0.07
Nodes (34): argparse, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+26 more)

### Community 6 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 7 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 8 - "connect_and_prepare"
Cohesion: 0.11
Nodes (20): clear_check_in_out(), connect_and_prepare(), ensure_schema_columns(), _open_connection(), Clear transient movement history without touching catalog/staff tables., Safely migrate existing installations without dropping data., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Reject incompatible existing tables without deleting or replacing them. (+12 more)

### Community 9 - "loader.py"
Cohesion: 0.24
Nodes (8): _bar(), finish(), set_progress(), start(), _width(), shutil, sys, time

### Community 10 - "updateTriggerStatus"
Cohesion: 0.21
Nodes (12): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), loadCatalogCompare(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream() (+4 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (39): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+31 more)

### Community 12 - "face_crop_to_embedding"
Cohesion: 0.20
Nodes (10): face_crop_to_embedding(), _face_detect_job(), _face_embed_worker(), handle_face_info(), maybe_start_face_job(), post_face_register(), _prepare_embed_image(), CPU 512-d face vector matching saved staff.csv (grid + RGB hist). (+2 more)

### Community 13 - "get_db"
Cohesion: 0.12
Nodes (28): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+20 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model(), _mask_data_url() (+10 more)

### Community 15 - "noise_transfer.py"
Cohesion: 0.07
Nodes (52): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+44 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 19 - "startLocalCamera"
Cohesion: 0.31
Nodes (10): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferLaptopDeviceId(), preferredCameraFacing() (+2 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "sql.py"
Cohesion: 0.13
Nodes (19): contextlib, _app_db_up(), compare_mobileclip2_vs_noise(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_live_dual_embeddings() (+11 more)

### Community 24 - "post"
Cohesion: 0.11
Nodes (26): sam_status(), BaseModel, analyze_face_frame(), api_noise_capture(), api_start_camera(), capture_sam_frame(), consultant_advise(), ConsultantRequest (+18 more)

### Community 26 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…, Export supported application tables to atomic CSV snapshots. only: optional…

### Community 27 - "analyzeLocalFrame"
Cohesion: 0.32
Nodes (8): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo(), updateFacePreviews()

### Community 28 - "db.py"
Cohesion: 0.18
Nodes (13): init_schema(), Compatibility wrappers. All SQL lives in sql.py., Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), check_db(), close_boot_connection(), ensure_database(), insert_check_in_out() (+5 more)

### Community 29 - "get"
Cohesion: 0.13
Nodes (17): camera_status(), catalog_compare(), catalog_import_status(), db_status(), detection_preview(), generate_frames(), get_detection_mode(), get_mode() (+9 more)

### Community 31 - "normalize_item_name"
Cohesion: 0.20
Nodes (16): _embedding_to_text(), insert_staff(), _mobileclip2_id_skeleton(), normalize_item_name(), SAM / one-shot register → mobileclip2 (abubu live primary)., Read-only (id, name) from mobileclip2 — never write that table. Prefer live PG…, Noise train import → replace inventory_emb_noise only (leave friend catalogs).…, replace_inventory_embeddings() (+8 more)

### Community 33 - "setup_db.py"
Cohesion: 0.13
Nodes (14): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), ensure_tables() (+6 more)

### Community 34 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 35 - "consultant.js"
Cohesion: 0.25
Nodes (13): advise(), ageFrom(), askNext(), block(), clearTime(), hasAudience(), ingest(), payload() (+5 more)

## Knowledge Gaps
- **67 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 198 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `run_high_end_boot`, `main.py`, `normalize_item_name`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03634085213032581 - nodes in this community are weakly interconnected._
- **Should `consultant_model.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06804214223002635 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.12688172043010754 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06765327695560254 - nodes in this community are weakly interconnected._