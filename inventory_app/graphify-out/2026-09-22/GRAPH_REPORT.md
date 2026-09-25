# Graph Report - inventory_app  (2026-09-22)

## Corpus Check
- 17 files · ~25,389 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 17 file(s) not represented in the graph (top: .csv 4, .pt 4, .css 3)

## Summary
- 516 nodes · 1079 edges · 25 communities (23 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e05c8407`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- register_sam_embedding
- run_high_end_boot
- sam-tool.js
- camera_capture_loop
- face.py
- analyzeLocalFrame
- tables
- capture_sam_frame
- sql.py
- updateTriggerStatus
- main.py
- infer.py
- api.py
- sam_tool.py
- loader.py
- runBrowserFaceLoop
- fetchStats
- get
- applyFaceStatus
- OneShot Inventory (`inventory_app`)
- saved_tables/README.md
- embed_captured_face
- post

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 28 edges
2. `connect_and_prepare()` - 15 edges
3. `camera_capture_loop()` - 14 edges
4. `applyFaceStatus()` - 13 edges
5. `normalize_item_name()` - 11 edges
6. `analyzeLocalFrame()` - 11 edges
7. `startLocalCamera()` - 11 edges
8. `face_status_payload()` - 11 edges
9. `import_train_catalog()` - 10 edges
10. `generateMask()` - 10 edges

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

## Communities (25 total, 2 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (47): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+39 more)

### Community 1 - "register_sam_embedding"
Cohesion: 0.32
Nodes (8): create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), parse_yolo_boxes(), refresh_inventory_catalog_cache(), register_sam_embedding(), SamRegisterBody

### Community 2 - "run_high_end_boot"
Cohesion: 0.14
Nodes (17): get_lan_ip(), _clear_session_movements(), _exit_app(), _force_close(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model() (+9 more)

### Community 3 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 4 - "camera_capture_loop"
Cohesion: 0.15
Nodes (26): arm_object_detection(), camera_capture_loop(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), ingest_scan_frame(), is_object_detection_armed() (+18 more)

### Community 5 - "face.py"
Cohesion: 0.12
Nodes (21): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+13 more)

### Community 6 - "analyzeLocalFrame"
Cohesion: 0.18
Nodes (17): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), drawLandmarks(), grabLocalFrame(), grabSegmentedFace() (+9 more)

### Community 7 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 8 - "capture_sam_frame"
Cohesion: 0.18
Nodes (11): sam_status(), BaseModel, capture_sam_frame(), FaceModeBody, generate_sam_mask(), get_sam_status(), post_face_register(), _register_staff_face() (+3 more)

### Community 9 - "sql.py"
Cohesion: 0.05
Nodes (82): config, contextlib, init_schema(), Compatibility wrappers. All SQL lives in sql.py., Boot helper — create missing tables only. Never seeds or overwrites., ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory() (+74 more)

### Community 10 - "updateTriggerStatus"
Cohesion: 0.24
Nodes (11): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showCaptureAlert() (+3 more)

### Community 11 - "main.py"
Cohesion: 0.08
Nodes (30): api, asyncio, dataset_importer, delete, face, fastapi_middleware_cors, fastapi_responses, infer (+22 more)

### Community 12 - "infer.py"
Cohesion: 0.11
Nodes (16): argparse, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon., Run the v2 segmentation model. Same call shape as the notebook. (+8 more)

### Community 13 - "api.py"
Cohesion: 0.24
Nodes (13): get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements(), get_staff_list() (+5 more)

### Community 14 - "sam_tool.py"
Cohesion: 0.07
Nodes (40): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), ndarray, Import YOLO-seg train crops into the inventory embedding catalog., Mask-crop, OpenCLIP-encode, and atomically replace catalog rows. (+32 more)

### Community 15 - "loader.py"
Cohesion: 0.24
Nodes (8): _bar(), finish(), set_progress(), start(), _width(), shutil, sys, time

### Community 16 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 17 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 18 - "get"
Cohesion: 0.15
Nodes (16): boot_status(), camera_status(), catalog_import_status(), db_status(), detection_preview(), generate_frames(), get_detection_mode(), get_mode() (+8 more)

### Community 19 - "applyFaceStatus"
Cohesion: 0.24
Nodes (15): applyFaceStatus(), captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup() (+7 more)

### Community 20 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 23 - "embed_captured_face"
Cohesion: 0.18
Nodes (13): analyze_face_frame(), _apply_face_embedding(), cosine_similarity(), embed_captured_face(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker(), handle_face_info() (+5 more)

### Community 24 - "post"
Cohesion: 0.21
Nodes (13): api_start_camera(), _cancel_app_exit(), dashboard_hello(), dashboard_leave(), detection_preview_active(), face_status_payload(), get_face_status(), _maybe_exit_after_leave() (+5 more)

## Knowledge Gaps
- **57 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 160 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FaceGate` connect `face.py` to `run_high_end_boot`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `_catalog_import_job()` connect `sam_tool.py` to `sql.py`, `run_high_end_boot`, `main.py`, `register_sam_embedding`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `camera_capture_loop()` (e.g. with `draw_landmarks()` and `run_backend_capture()`) actually correct?**
  _`camera_capture_loop()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _57 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.039057239057239054 - nodes in this community are weakly interconnected._
- **Should `run_high_end_boot` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._
- **Should `camera_capture_loop` be split into smaller, more focused modules?**
  _Cohesion score 0.1476923076923077 - nodes in this community are weakly interconnected._