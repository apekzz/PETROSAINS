# Graph Report - hilman_21Sep  (2026-09-22)

## Corpus Check
- 50 files · ~1,373,880 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 487 file(s) not represented in the graph (top: (none) 414, .ipynb 19, .pt 19)

## Summary
- 880 nodes · 1876 edges · 50 communities (44 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `345ebceb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- face.py
- evaluate_embedding_similarity.py
- main.py
- eval.py
- camera_capture_loop
- embed.py
- PETROSAINS
- sam-tool.js
- get_db
- applyFaceStatus
- tables
- sql.py
- detectron2_recipe.py
- _encode_worker_loop
- pathlib
- dataset_importer.py
- download_dataset.py
- dice_loss.py
- run_high_end_boot
- ensure_tables
- utils_db/infer.py
- sam_tool.py
- visualize.py
- post
- db.py
- backend/infer.py
- EarlyStopHook
- setup_db.py
- updateTriggerStatus
- _clear_session_movements
- runBrowserFaceLoop
- BaseModel
- V2DatasetMapper
- .__init__
- setFaceHint
- list_camera_devices
- ObjectTrainer
- PETROSAINS inventory similarity (`test_pg`)
- EpochMetricPrinter
- export_table_snapshots
- OneShot Inventory (`inventory_app`)
- MosaicProb
- saved_tables/README.md
- test_sahi.py
- apply_bce_dice_mask_loss
- inventory_app_config
- normalize_item_name
- inventory_app_sam_tool

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 28 edges
2. `PgConfig` - 19 edges
3. `load_image_and_label()` - 16 edges
4. `connect_and_prepare()` - 15 edges
5. `applyFaceStatus()` - 14 edges
6. `camera_capture_loop()` - 14 edges
7. `get_image_embedding()` - 14 edges
8. `drive_folder()` - 14 edges
9. `predict_labeled_image()` - 14 edges
10. `crop_labeled_objects()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `How to run` --references--> `load_clip_model()`  [INFERRED]
  test_pg/README.md → utils/embed.py
- `3. Evaluate on val / test` --references--> `save_query_objects()`  [INFERRED]
  test_pg/README.md → utils_db/cache.py
- `C. Generate training embeddings with OpenCLIP` --references--> `bbox_xyxy()`  [INFERRED]
  test_pg/README.md → utils/dataset.py
- `main()` --calls--> `drive_folder()`  [EXTRACTED]
  export_train_official.py → utils/gdrive.py
- `main()` --calls--> `drive_folder()`  [EXTRACTED]
  test_pg/embed_train_official.py → utils/gdrive.py

## Import Cycles
- None detected.

## Communities (50 total, 6 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (51): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+43 more)

### Community 1 - "face.py"
Cohesion: 0.10
Nodes (23): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+15 more)

### Community 2 - "evaluate_embedding_similarity.py"
Cohesion: 0.07
Nodes (42): datetime, _bar(), finish(), set_progress(), start(), _width(), json, platform (+34 more)

### Community 3 - "main.py"
Cohesion: 0.08
Nodes (34): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, boot_status(), camera_status(), catalog_import_active() (+26 more)

### Community 4 - "eval.py"
Cohesion: 0.14
Nodes (29): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), embed_split_crops(), evaluate_rule() (+21 more)

### Community 5 - "camera_capture_loop"
Cohesion: 0.14
Nodes (31): arm_object_detection(), camera_capture_loop(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state() (+23 more)

### Community 6 - "embed.py"
Cohesion: 0.13
Nodes (27): pandas, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights() (+19 more)

### Community 7 - "PETROSAINS"
Cohesion: 0.18
Nodes (10): Daily use (after first setup), Files, Folders, How to run the inventory app, PETROSAINS, Root layout, Steps, `test_pg/` (similarity pipeline) (+2 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "get_db"
Cohesion: 0.13
Nodes (28): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+20 more)

### Community 10 - "applyFaceStatus"
Cohesion: 0.24
Nodes (14): analyzeLocalFrame(), applyFaceStatus(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), pollFaceStatus() (+6 more)

### Community 11 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 12 - "sql.py"
Cohesion: 0.10
Nodes (26): contextlib, init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), connect_and_prepare(), _embedding_from_text(), ensure_database(), ensure_postgres_running() (+18 more)

### Community 13 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 14 - "_encode_worker_loop"
Cohesion: 0.21
Nodes (12): _apply_face_embedding(), embed_captured_face(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_embed_worker(), _load_clip_weights() (+4 more)

### Community 15 - "pathlib"
Cohesion: 0.13
Nodes (27): dataclasses, numpy, pathlib, pgvector_psycopg, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1). (+19 more)

### Community 16 - "dataset_importer.py"
Cohesion: 0.22
Nodes (15): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+7 more)

### Community 17 - "download_dataset.py"
Cohesion: 0.15
Nodes (23): google_colab, re, _copy_tree(), download_dataset(), _drive_folder(), _iter_files(), _looks_like_dataset(), main() (+15 more)

### Community 18 - "dice_loss.py"
Cohesion: 0.15
Nodes (16): Tensor, torch, torch_nn_functional, Label-aware Ultralytics train() kwargs. Aggressive geometry (mosaic, mixup,…, apply_bce_dice_mask_loss(), apply_dice_mask_loss(), bce_dice_single_mask_loss(), dice_single_mask_loss() (+8 more)

### Community 19 - "run_high_end_boot"
Cohesion: 0.18
Nodes (14): get_lan_ip(), _catalog_import_job(), _catalog_progress(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding() (+6 more)

### Community 20 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 21 - "utils_db/infer.py"
Cohesion: 0.18
Nodes (14): matplotlib, matplotlib_patches, crop_labeled_objects(), Image, Crop each labeled object from ``image`` and attach bbox metadata., _color_for_name(), draw_predictions(), predict_labeled_image() (+6 more)

### Community 22 - "sam_tool.py"
Cohesion: 0.10
Nodes (30): base64, collections, csv, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes() (+22 more)

### Community 23 - "visualize.py"
Cohesion: 0.13
Nodes (31): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., math, pil, sys, build_embedding_dataframe() (+23 more)

### Community 24 - "post"
Cohesion: 0.14
Nodes (19): sam_status(), analyze_face_frame(), api_start_camera(), capture_sam_frame(), detection_preview_active(), _face_detect_job(), face_status_payload(), generate_sam_mask() (+11 more)

### Community 25 - "db.py"
Cohesion: 0.24
Nodes (9): Compatibility wrappers. All SQL lives in sql.py., check_db(), clear_check_in_out(), close_boot_connection(), insert_check_in_out(), _lock(), IN / OUT writes check_in_out. SCAN is view-only., Clear transient movement history without touching catalog/staff tables. (+1 more)

### Community 26 - "backend/infer.py"
Cohesion: 0.11
Nodes (23): argparse, cv2, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon. (+15 more)

### Community 27 - "EarlyStopHook"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "setup_db.py"
Cohesion: 0.22
Nodes (9): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), psycopg, sqlite3 (+1 more)

### Community 29 - "updateTriggerStatus"
Cohesion: 0.12
Nodes (22): animateValue(), applyObjectRecognitionState(), escapeHtml(), fetchInventory(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), maybeToastCapture() (+14 more)

### Community 30 - "_clear_session_movements"
Cohesion: 0.22
Nodes (10): _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event() (+2 more)

### Community 31 - "runBrowserFaceLoop"
Cohesion: 0.16
Nodes (14): applyLocalFace(), drawLandmarks(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan() (+6 more)

### Community 32 - "BaseModel"
Cohesion: 0.22
Nodes (9): BaseModel, api_camera_select(), CameraSelectBody, FaceModeBody, post_face_register(), _register_staff_face(), SamRegisterBody, StaffRegisterBody (+1 more)

### Community 33 - "V2DatasetMapper"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 34 - ".__init__"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 35 - "setFaceHint"
Cohesion: 0.19
Nodes (17): applyCapturedPhoto(), captureButtonLabel(), enableCaptureFallback(), grabLocalFrame(), ingestScanFrame(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback() (+9 more)

### Community 36 - "list_camera_devices"
Cohesion: 0.33
Nodes (5): api_camera_devices(), list_camera_devices(), _mac_camera_names(), Best-effort camera labels from macOS (FaceTime, Camo, Continuity…)., List cameras for the dashboard chooser. FaceTime/laptop first, then Camo/phone.

### Community 37 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 39 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.08
Nodes (23): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, C. Generate training embeddings with OpenCLIP, D. Development mode: prediction and evaluation (+15 more)

### Community 40 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 42 - "export_table_snapshots"
Cohesion: 0.29
Nodes (7): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), insert_staff(), Export supported application tables to atomic CSV snapshots. only: optional…, Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…

### Community 43 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 44 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 49 - "normalize_item_name"
Cohesion: 0.23
Nodes (14): _embedding_to_text(), normalize_item_name(), Rebuild summary counts from inventory_emb. Keeps existing registered_date., Atomically replace the catalog and rebuild unique inventory counts., recalculate_available_quantities(), refresh_main_inventory(), _refresh(), replace_inventory_embeddings() (+6 more)

## Knowledge Gaps
- **73 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+68 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 292 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `embed.py` to `visualize.py`, `PETROSAINS inventory similarity (`test_pg`)`, `pathlib`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `bbox_xyxy()` connect `PETROSAINS inventory similarity (`test_pg`)` to `utils_db/infer.py`, `visualize.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `EpochMetricPrinter`, `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _73 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03884711779448621 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09879032258064516 - nodes in this community are weakly interconnected._