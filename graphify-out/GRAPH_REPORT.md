# Graph Report - hilman_21Sep  (2026-09-22)

## Corpus Check
- 50 files · ~1,373,257 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 487 file(s) not represented in the graph (top: (none) 414, .ipynb 19, .pt 19)

## Summary
- 870 nodes · 1854 edges · 45 communities (39 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 93 edges (avg confidence: 0.86)
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
- updateTriggerStatus
- camera_capture_loop
- get_trigger_state
- PETROSAINS
- sam-tool.js
- api.py
- analyzeLocalFrame
- tables
- sql.py
- detectron2_recipe.py
- _encode_worker_loop
- eval.py
- dataset_importer.py
- download_dataset.py
- run_high_end_boot
- sam_tool.py
- embed.py
- post
- db.py
- analyze_object_areas.py
- EarlyStopHook
- setup_db.py
- fetchStats
- _clear_session_movements
- runBrowserFaceLoop
- capture_sam_frame
- V2DatasetMapper
- .__init__
- applyFaceStatus
- ObjectTrainer
- PETROSAINS inventory similarity (`test_pg`)
- EpochMetricPrinter
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
5. `camera_capture_loop()` - 14 edges
6. `get_image_embedding()` - 14 edges
7. `drive_folder()` - 14 edges
8. `predict_labeled_image()` - 14 edges
9. `applyFaceStatus()` - 13 edges
10. `crop_labeled_objects()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `How to run` --references--> `load_clip_model()`  [INFERRED]
  test_pg/README.md → utils/embed.py
- `3. Evaluate on val / test` --references--> `save_query_objects()`  [INFERRED]
  test_pg/README.md → utils_db/cache.py
- `C. Generate training embeddings with OpenCLIP` --references--> `bbox_xyxy()`  [INFERRED]
  test_pg/README.md → utils/dataset.py
- `main()` --calls--> `load_clip_model()`  [EXTRACTED]
  test_pg/predict_labeled_image.py → utils/embed.py
- `_drive_folder()` --calls--> `drive_folder()`  [EXTRACTED]
  train_v2/utils/download_dataset.py → utils/gdrive.py

## Import Cycles
- None detected.

## Communities (45 total, 6 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (47): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+39 more)

### Community 1 - "face.py"
Cohesion: 0.13
Nodes (19): _align_template(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate, _five_from_yunet() (+11 more)

### Community 2 - "evaluate_embedding_similarity.py"
Cohesion: 0.07
Nodes (44): datetime, platform, Tensor, torch, torch_nn_functional, build_samples(), canonical_name(), classification_metrics() (+36 more)

### Community 3 - "main.py"
Cohesion: 0.09
Nodes (34): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, camera_status(), _catalog_import_job(), catalog_import_status() (+26 more)

### Community 4 - "updateTriggerStatus"
Cohesion: 0.24
Nodes (11): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showCaptureAlert() (+3 more)

### Community 5 - "camera_capture_loop"
Cohesion: 0.14
Nodes (26): camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), ingest_scan_frame(), is_object_detection_armed() (+18 more)

### Community 6 - "get_trigger_state"
Cohesion: 0.50
Nodes (4): boot_status(), get_trigger_state(), ingest_browser_scan(), UploadFile

### Community 7 - "PETROSAINS"
Cohesion: 0.18
Nodes (10): Daily use (after first setup), Files, Folders, How to run the inventory app, PETROSAINS, Root layout, Steps, `test_pg/` (similarity pipeline) (+2 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "api.py"
Cohesion: 0.11
Nodes (26): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+18 more)

### Community 10 - "analyzeLocalFrame"
Cohesion: 0.18
Nodes (17): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), drawLandmarks(), grabLocalFrame(), grabSegmentedFace() (+9 more)

### Community 11 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 12 - "sql.py"
Cohesion: 0.10
Nodes (24): contextlib, connect_and_prepare(), _copy_table_to_file(), ensure_postgres_running(), ensure_schema_columns(), ensure_tables(), _apply(), existing_tables() (+16 more)

### Community 13 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 14 - "_encode_worker_loop"
Cohesion: 0.15
Nodes (16): choose_staff_match(), One face at a time, matched against every enrolled staff. Full-threshold hits…, _apply_face_embedding(), cosine_similarity(), embed_captured_face(), _encode_image(), _encode_images(), _encode_worker_loop() (+8 more)

### Community 15 - "eval.py"
Cohesion: 0.05
Nodes (73): argparse, dataclasses, pathlib, pgvector_psycopg, pickle, Series, sys, main() (+65 more)

### Community 16 - "dataset_importer.py"
Cohesion: 0.22
Nodes (15): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+7 more)

### Community 17 - "download_dataset.py"
Cohesion: 0.14
Nodes (21): _bar(), finish(), set_progress(), start(), _width(), shutil, time, _copy_tree() (+13 more)

### Community 19 - "run_high_end_boot"
Cohesion: 0.14
Nodes (18): get_lan_ip(), init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), clear_check_in_out(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only. (+10 more)

### Community 22 - "sam_tool.py"
Cohesion: 0.06
Nodes (44): base64, collections, csv, cv2, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame() (+36 more)

### Community 23 - "embed.py"
Cohesion: 0.05
Nodes (78): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., google_colab, math, matplotlib, matplotlib_patches (+70 more)

### Community 24 - "post"
Cohesion: 0.14
Nodes (19): analyze_face_frame(), api_start_camera(), arm_object_detection(), _cancel_app_exit(), dashboard_hello(), dashboard_leave(), detection_preview_active(), _face_detect_job() (+11 more)

### Community 25 - "db.py"
Cohesion: 0.20
Nodes (17): Compatibility wrappers. All SQL lives in sql.py., check_db(), clear_staff_embeddings(), close_boot_connection(), _embedding_from_text(), export_table_snapshots(), fetch_inventory_embeddings(), fetch_staff_embeddings() (+9 more)

### Community 26 - "analyze_object_areas.py"
Cohesion: 0.19
Nodes (19): tqdm, _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace (+11 more)

### Community 27 - "EarlyStopHook"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "setup_db.py"
Cohesion: 0.25
Nodes (8): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), psycopg, sqlite3

### Community 29 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 30 - "_clear_session_movements"
Cohesion: 0.33
Nodes (7): _clear_session_movements(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event(), stop_camera(), on_event

### Community 31 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 32 - "capture_sam_frame"
Cohesion: 0.18
Nodes (11): BaseModel, sam_status(), capture_sam_frame(), generate_sam_mask(), get_sam_status(), post_face_register(), _register_staff_face(), SamMaskBody (+3 more)

### Community 33 - "V2DatasetMapper"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 34 - ".__init__"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 35 - "applyFaceStatus"
Cohesion: 0.24
Nodes (15): applyFaceStatus(), captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup() (+7 more)

### Community 37 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 39 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.20
Nodes (9): A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, E. Predict one image (`predict_labeled_image.py`), How to run, Input, Output, PETROSAINS inventory similarity (`test_pg`), Share the same Postgres catalog with the team (+1 more)

### Community 40 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 43 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 44 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 49 - "normalize_item_name"
Cohesion: 0.21
Nodes (16): _embedding_to_text(), normalize_item_name(), Rebuild summary counts from inventory_emb. Keeps existing registered_date., Atomically replace the catalog and rebuild unique inventory counts., recalculate_available_quantities(), refresh_main_inventory(), _refresh(), replace_inventory_embeddings() (+8 more)

## Knowledge Gaps
- **72 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 291 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `embed.py` to `PETROSAINS inventory similarity (`test_pg`)`, `eval.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `EpochMetricPrinter`, `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _72 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.039057239057239054 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12615384615384614 - nodes in this community are weakly interconnected._
- **Should `evaluate_embedding_similarity.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06775510204081632 - nodes in this community are weakly interconnected._