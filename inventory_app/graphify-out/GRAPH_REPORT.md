# Graph Report - inventory_app  (2026-09-23)

## Corpus Check
- 18 files · ~26,416 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: .csv 4, .pt 4, .css 3)

## Summary
- 544 nodes · 1136 edges · 24 communities (22 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `18a757f4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- _apply_face_embedding
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
- applyFaceStatus
- OneShot Inventory (`inventory_app`)
- saved_tables/README.md
- post
- capture_sam_frame

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 28 edges
2. `connect_and_prepare()` - 15 edges
3. `camera_capture_loop()` - 14 edges
4. `import_train_catalog()` - 13 edges
5. `applyFaceStatus()` - 13 edges
6. `capture_laptop_noise_profile()` - 12 edges
7. `normalize_item_name()` - 11 edges
8. `analyzeLocalFrame()` - 11 edges
9. `startLocalCamera()` - 11 edges
10. `face_status_payload()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `get_inventory()` --calls--> `fetch_inventory()`  [INFERRED]
  backend/api.py → database/sql.py
- `get_movements()` --calls--> `fetch_movements()`  [INFERRED]
  backend/api.py → database/sql.py
- `get_stats()` --calls--> `fetch_stats()`  [INFERRED]
  backend/api.py → database/sql.py
- `search_inventory()` --calls--> `fetch_inventory()`  [INFERRED]
  backend/api.py → database/sql.py
- `get_item()` --calls--> `fetch_item()`  [INFERRED]
  backend/api.py → database/sql.py

## Import Cycles
- None detected.

## Communities (24 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (47): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+39 more)

### Community 1 - "_apply_face_embedding"
Cohesion: 0.15
Nodes (13): _apply_face_embedding(), cosine_similarity(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker(), get_inventory_catalog(), handle_face_info(), match_inventory_name() (+5 more)

### Community 2 - "run_high_end_boot"
Cohesion: 0.15
Nodes (16): get_lan_ip(), _encode_image(), _encode_images(), _encode_worker_loop(), images_to_embeddings(), _load_clip_weights(), load_embed_model(), load_face_gate() (+8 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.14
Nodes (30): arm_object_detection(), camera_capture_loop(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state() (+22 more)

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
Cohesion: 0.33
Nodes (7): _clear_session_movements(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event(), stop_camera(), on_event

### Community 9 - "sql.py"
Cohesion: 0.05
Nodes (85): config, contextlib, init_schema(), Compatibility wrappers. All SQL lives in sql.py., Boot helper — create missing tables only. Never seeds or overwrites., ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory() (+77 more)

### Community 10 - "updateTriggerStatus"
Cohesion: 0.24
Nodes (11): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showCaptureAlert() (+3 more)

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (39): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+31 more)

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
Cohesion: 0.08
Nodes (46): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+38 more)

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 19 - "applyFaceStatus"
Cohesion: 0.24
Nodes (15): applyFaceStatus(), captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup() (+7 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 24 - "post"
Cohesion: 0.15
Nodes (19): analyze_face_frame(), api_noise_capture(), api_start_camera(), _cancel_app_exit(), dashboard_hello(), dashboard_leave(), detection_preview_active(), embed_captured_face() (+11 more)

### Community 30 - "capture_sam_frame"
Cohesion: 0.22
Nodes (9): sam_status(), BaseModel, capture_sam_frame(), generate_sam_mask(), get_sam_status(), SamMaskBody, SamRegisterBody, StaffRegisterBody (+1 more)

## Knowledge Gaps
- **57 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 171 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_catalog_import_job()` connect `noise_transfer.py` to `sql.py`, `run_high_end_boot`, `main.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `camera_capture_loop()` (e.g. with `draw_landmarks()` and `run_backend_capture()`) actually correct?**
  _`camera_capture_loop()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `import_train_catalog()` (e.g. with `NoiseProfile` and `_catalog_import_job()`) actually correct?**
  _`import_train_catalog()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _57 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.039057239057239054 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.14022988505747128 - nodes in this community are weakly interconnected._