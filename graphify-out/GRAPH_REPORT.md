# Graph Report - hilman_21Sep  (2026-09-23)

## Corpus Check
- 51 files · ~1,374,501 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 487 file(s) not represented in the graph (top: (none) 414, .ipynb 19, .pt 19)

## Summary
- 900 nodes · 1927 edges · 47 communities (41 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 95 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b9fe2ed9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- eval.py
- utils_db/__init__.py
- sam_tool.py
- dashboard.js
- evaluate_embedding_similarity.py
- main.py
- api.py
- camera_capture_loop
- sam-tool.js
- face.py
- download_dataset.py
- PETROSAINS inventory similarity (`test_pg`)
- detectron2_recipe.py
- visualize_results.py
- tables
- sql.py
- analyzeLocalFrame
- noise_transfer.py
- analyze_object_areas.py
- BaseModel
- setup_db.py
- applyFaceStatus
- _clear_session_movements
- db.py
- post
- _encode_worker_loop
- runBrowserFaceLoop
- EarlyStopHook
- fetchStats
- updateTriggerStatus
- PETROSAINS
- V2DatasetMapper
- .__init__
- run_high_end_boot
- ObjectTrainer
- yolo_to_coco.py
- EpochMetricPrinter
- MosaicProb
- OneShot Inventory (`inventory_app`)
- test_sahi.py
- apply_bce_dice_mask_loss
- saved_tables/README.md
- _catalog_import_job
- inventory_app_config
- inventory_app_sam_tool
- get_db

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 28 edges
2. `PgConfig` - 19 edges
3. `load_image_and_label()` - 16 edges
4. `connect_and_prepare()` - 15 edges
5. `camera_capture_loop()` - 14 edges
6. `get_image_embedding()` - 14 edges
7. `drive_folder()` - 14 edges
8. `predict_labeled_image()` - 14 edges
9. `import_train_catalog()` - 13 edges
10. `applyFaceStatus()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `How to run` --references--> `load_clip_model()`  [INFERRED]
  test_pg/README.md → utils/embed.py
- `3. Evaluate on val / test` --references--> `save_query_objects()`  [INFERRED]
  test_pg/README.md → utils_db/cache.py
- `C. Generate training embeddings with OpenCLIP` --references--> `bbox_xyxy()`  [INFERRED]
  test_pg/README.md → utils/dataset.py
- `run_high_end_boot()` --calls--> `get_lan_ip()`  [INFERRED]
  inventory_app/main.py → inventory_app/backend/config.py
- `main()` --calls--> `load_clip_model()`  [EXTRACTED]
  test_pg/predict_labeled_image.py → utils/embed.py

## Import Cycles
- None detected.

## Communities (47 total, 6 thin omitted)

### Community 0 - "eval.py"
Cohesion: 0.05
Nodes (87): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., google_colab, math, matplotlib, matplotlib_patches (+79 more)

### Community 1 - "utils_db/__init__.py"
Cohesion: 0.07
Nodes (53): argparse, pgvector_psycopg, Series, sys, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1). (+45 more)

### Community 2 - "sam_tool.py"
Cohesion: 0.07
Nodes (30): base64, cv2, get_lan_ip(), crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from… (+22 more)

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (47): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+39 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.06
Nodes (45): datetime, platform, Tensor, torch, torch_nn_functional, build_samples(), canonical_name(), classification_metrics() (+37 more)

### Community 5 - "main.py"
Cohesion: 0.08
Nodes (34): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, sam_status(), boot_status(), camera_status() (+26 more)

### Community 6 - "api.py"
Cohesion: 0.12
Nodes (24): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+16 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.14
Nodes (30): arm_object_detection(), camera_capture_loop(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state() (+22 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "face.py"
Cohesion: 0.12
Nodes (21): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+13 more)

### Community 10 - "download_dataset.py"
Cohesion: 0.14
Nodes (21): _bar(), finish(), set_progress(), start(), _width(), shutil, time, _copy_tree() (+13 more)

### Community 11 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.10
Nodes (20): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, D. Development mode: prediction and evaluation, E. Predict one image (`predict_labeled_image.py`) (+12 more)

### Community 12 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 13 - "visualize_results.py"
Cohesion: 0.27
Nodes (13): collections, csv, matplotlib_pyplot, canonical(), confusion_matrix(), label_bars(), latency_breakdown(), load_predictions() (+5 more)

### Community 14 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 15 - "sql.py"
Cohesion: 0.11
Nodes (24): contextlib, check_db(), close_boot_connection(), connect_and_prepare(), _copy_table_to_file(), ensure_postgres_running(), ensure_schema_columns(), export_table_snapshots() (+16 more)

### Community 16 - "analyzeLocalFrame"
Cohesion: 0.18
Nodes (17): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), drawLandmarks(), grabLocalFrame(), grabSegmentedFace() (+9 more)

### Community 17 - "noise_transfer.py"
Cohesion: 0.10
Nodes (39): dataclasses, choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray (+31 more)

### Community 18 - "analyze_object_areas.py"
Cohesion: 0.32
Nodes (12): _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace, ndarray (+4 more)

### Community 19 - "BaseModel"
Cohesion: 0.22
Nodes (9): BaseModel, FaceModeBody, generate_sam_mask(), post_face_register(), _register_staff_face(), SamMaskBody, SamRegisterBody, StaffRegisterBody (+1 more)

### Community 20 - "setup_db.py"
Cohesion: 0.18
Nodes (11): config, get_stats(), ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), fetch_stats() (+3 more)

### Community 21 - "applyFaceStatus"
Cohesion: 0.24
Nodes (15): applyFaceStatus(), captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup() (+7 more)

### Community 22 - "_clear_session_movements"
Cohesion: 0.25
Nodes (9): _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event() (+1 more)

### Community 23 - "db.py"
Cohesion: 0.18
Nodes (19): Compatibility wrappers. All SQL lives in sql.py., _embedding_to_text(), insert_check_in_out(), insert_staff(), normalize_item_name(), Rebuild summary counts from inventory_emb. Keeps existing registered_date., Atomically replace the catalog and rebuild unique inventory counts., IN / OUT writes check_in_out. SCAN is view-only. (+11 more)

### Community 24 - "post"
Cohesion: 0.16
Nodes (18): analyze_face_frame(), api_noise_capture(), api_start_camera(), capture_sam_frame(), detection_preview_active(), embed_captured_face(), _face_detect_job(), face_status_payload() (+10 more)

### Community 25 - "_encode_worker_loop"
Cohesion: 0.16
Nodes (14): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_embed_worker(), get_inventory_catalog() (+6 more)

### Community 26 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 27 - "EarlyStopHook"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 29 - "updateTriggerStatus"
Cohesion: 0.24
Nodes (11): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showCaptureAlert() (+3 more)

### Community 30 - "PETROSAINS"
Cohesion: 0.18
Nodes (10): Daily use (after first setup), Files, Folders, How to run the inventory app, PETROSAINS, Root layout, Steps, `test_pg/` (similarity pipeline) (+2 more)

### Community 31 - "V2DatasetMapper"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 32 - ".__init__"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 33 - "run_high_end_boot"
Cohesion: 0.13
Nodes (20): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), clear_check_in_out(), clear_staff_embeddings(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only. (+12 more)

### Community 34 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 35 - "yolo_to_coco.py"
Cohesion: 0.57
Nodes (6): convert_dataset(), convert_split(), _image_path(), _polygons_from_label(), Path, Convert train_v2 YOLO-seg labels to COCO JSON for Detectron2.

### Community 36 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 38 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 39 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 45 - "_catalog_import_job"
Cohesion: 0.32
Nodes (8): _catalog_import_job(), _catalog_progress(), images_to_embeddings(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir}., select_and_import_catalog(), _start_catalog_import()

### Community 50 - "get_db"
Cohesion: 0.22
Nodes (10): _embedding_from_text(), ensure_tables(), _apply(), existing_tables(), fetch_inventory_embeddings(), fetch_staff_embeddings(), get_db(), get_staff() (+2 more)

## Knowledge Gaps
- **72 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 302 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `eval.py` to `utils_db/__init__.py`, `PETROSAINS inventory similarity (`test_pg`)`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`, `EpochMetricPrinter`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _72 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `eval.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05240549828178694 - nodes in this community are weakly interconnected._
- **Should `utils_db/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07481005260081823 - nodes in this community are weakly interconnected._
- **Should `sam_tool.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07152496626180836 - nodes in this community are weakly interconnected._