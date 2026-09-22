# Graph Report - PETROSAINS  (2026-09-21)

## Corpus Check
- 50 files · ~1,373,004 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 486 file(s) not represented in the graph (top: (none) 413, .ipynb 19, .pt 19)

## Summary
- 867 nodes · 1844 edges · 53 communities (47 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 93 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `36121c0c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- face.py
- evaluate_embedding_similarity.py
- main.py
- embed.py
- camera_capture_loop
- eval.py
- PETROSAINS
- sam-tool.js
- db.py
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
- connect_and_prepare
- post
- sam_tool.py
- visualize.py
- capture_sam_frame
- predict_labeled_image
- analyze_object_areas.py
- EarlyStopHook
- setup_db.py
- fetchStats
- visualize_results.py
- runBrowserFaceLoop
- updateTriggerStatus
- V2DatasetMapper
- .__init__
- enableCaptureFallback
- clear_check_in_out
- ObjectTrainer
- _clear_session_movements
- PETROSAINS inventory similarity (`test_pg`)
- EpochMetricPrinter
- bootstrap_database
- export_table_snapshots
- OneShot Inventory (`inventory_app`)
- MosaicProb
- saved_tables/README.md
- test_sahi.py
- apply_bce_dice_mask_loss
- inventory_app_config
- normalize_item_name
- drive_folder
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
- `main()` --calls--> `build_embedding_dataframe()`  [EXTRACTED]
  export_train_official.py → utils/dataset.py
- `run_high_end_boot()` --calls--> `get_lan_ip()`  [INFERRED]
  inventory_app/main.py → inventory_app/backend/config.py

## Import Cycles
- None detected.

## Communities (53 total, 6 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (47): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+39 more)

### Community 1 - "face.py"
Cohesion: 0.06
Nodes (33): cv2, get_lan_ip(), _align_template(), choose_staff_match(), crop_from_box(), encode_crop(), ensure_face_model(), face_in_region() (+25 more)

### Community 2 - "evaluate_embedding_similarity.py"
Cohesion: 0.09
Nodes (36): datetime, json, platform, tqdm, build_samples(), canonical_name(), classification_metrics(), inventory_name_from_filename() (+28 more)

### Community 3 - "main.py"
Cohesion: 0.09
Nodes (32): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, boot_status(), camera_status(), catalog_import_status() (+24 more)

### Community 4 - "embed.py"
Cohesion: 0.14
Nodes (28): dataclasses, pandas, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe() (+20 more)

### Community 5 - "camera_capture_loop"
Cohesion: 0.12
Nodes (30): draw_landmarks(), arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active() (+22 more)

### Community 6 - "eval.py"
Cohesion: 0.15
Nodes (28): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), evaluate_rule(), _global_mean_sim() (+20 more)

### Community 7 - "PETROSAINS"
Cohesion: 0.18
Nodes (10): Daily use (after first setup), Files, Folders, How to run the inventory app, PETROSAINS, Root layout, Steps, `test_pg/` (similarity pipeline) (+2 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "db.py"
Cohesion: 0.14
Nodes (29): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+21 more)

### Community 10 - "applyFaceStatus"
Cohesion: 0.15
Nodes (25): analyzeLocalFrame(), applyCapturedPhoto(), applyFaceStatus(), applyLocalFace(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), drawLandmarks() (+17 more)

### Community 11 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 12 - "sql.py"
Cohesion: 0.16
Nodes (14): contextlib, check_db(), close_boot_connection(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_staff_embeddings(), _lock() (+6 more)

### Community 13 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 14 - "_encode_worker_loop"
Cohesion: 0.20
Nodes (12): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_embed_worker(), _load_clip_weights() (+4 more)

### Community 15 - "pathlib"
Cohesion: 0.14
Nodes (26): argparse, numpy, pathlib, pgvector_psycopg, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1). (+18 more)

### Community 16 - "dataset_importer.py"
Cohesion: 0.22
Nodes (15): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+7 more)

### Community 17 - "download_dataset.py"
Cohesion: 0.14
Nodes (21): _bar(), finish(), set_progress(), start(), _width(), shutil, time, _copy_tree() (+13 more)

### Community 18 - "dice_loss.py"
Cohesion: 0.15
Nodes (16): Tensor, torch, torch_nn_functional, Label-aware Ultralytics train() kwargs. Aggressive geometry (mosaic, mixup,…, apply_bce_dice_mask_loss(), apply_dice_mask_loss(), bce_dice_single_mask_loss(), dice_single_mask_loss() (+8 more)

### Community 19 - "run_high_end_boot"
Cohesion: 0.19
Nodes (13): _catalog_import_job(), _catalog_progress(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load CLIP once on a dedicated encode thread and keep it there. (+5 more)

### Community 20 - "connect_and_prepare"
Cohesion: 0.17
Nodes (12): connect_and_prepare(), ensure_schema_columns(), ensure_tables(), _apply(), _open_connection(), Safely migrate existing installations without dropping data., Reject incompatible existing tables without deleting or replacing them., Tables whose CSV is missing or row-count differs from Postgres. (+4 more)

### Community 21 - "post"
Cohesion: 0.18
Nodes (16): analyze_face_frame(), api_start_camera(), detection_preview_active(), embed_captured_face(), _face_detect_job(), face_status_payload(), get_face_status(), handle_face_info() (+8 more)

### Community 22 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): base64, collections, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session() (+10 more)

### Community 23 - "visualize.py"
Cohesion: 0.14
Nodes (29): collections_abc, colorsys, math, matplotlib, matplotlib_patches, pil, build_embedding_dataframe(), _class_key() (+21 more)

### Community 24 - "capture_sam_frame"
Cohesion: 0.18
Nodes (11): BaseModel, sam_status(), capture_sam_frame(), FaceModeBody, generate_sam_mask(), get_sam_status(), post_face_register(), SamMaskBody (+3 more)

### Community 25 - "predict_labeled_image"
Cohesion: 0.20
Nodes (12): crop_labeled_objects(), Image, Crop each labeled object from ``image`` and attach bbox metadata., embed_split_crops(), Embed every labeled crop in ``split``. Reuses a preloaded OpenCLIP model., draw_predictions(), predict_labeled_image(), DataFrame (+4 more)

### Community 26 - "analyze_object_areas.py"
Cohesion: 0.32
Nodes (12): _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace, ndarray (+4 more)

### Community 27 - "EarlyStopHook"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "setup_db.py"
Cohesion: 0.17
Nodes (11): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), existing_tables(), table_status() (+3 more)

### Community 29 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 30 - "visualize_results.py"
Cohesion: 0.31
Nodes (12): csv, matplotlib_pyplot, canonical(), confusion_matrix(), label_bars(), latency_breakdown(), load_predictions(), main() (+4 more)

### Community 31 - "runBrowserFaceLoop"
Cohesion: 0.22
Nodes (10): drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate(), runBrowserFaceLoop() (+2 more)

### Community 32 - "updateTriggerStatus"
Cohesion: 0.24
Nodes (11): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showCaptureAlert() (+3 more)

### Community 33 - "V2DatasetMapper"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 34 - ".__init__"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 35 - "enableCaptureFallback"
Cohesion: 0.29
Nodes (8): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferredCameraFacing(), refreshCameraList()

### Community 36 - "clear_check_in_out"
Cohesion: 0.29
Nodes (7): clear_check_in_out(), insert_check_in_out(), IN / OUT writes check_in_out. SCAN is view-only., Clear transient movement history without touching catalog/staff tables., recalculate_available_quantities(), record_yolo_capture(), _refresh()

### Community 37 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 38 - "_clear_session_movements"
Cohesion: 0.22
Nodes (10): _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event() (+2 more)

### Community 39 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.08
Nodes (23): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, C. Generate training embeddings with OpenCLIP, D. Development mode: prediction and evaluation (+15 more)

### Community 40 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 41 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 42 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Export supported application tables to atomic CSV snapshots. only: optional…, Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…

### Community 43 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 44 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 49 - "normalize_item_name"
Cohesion: 0.22
Nodes (15): _embedding_to_text(), insert_staff(), normalize_item_name(), Rebuild summary counts from inventory_emb. Keeps existing registered_date., Atomically replace the catalog and rebuild unique inventory counts., refresh_main_inventory(), replace_inventory_embeddings(), save_inventory_embedding() (+7 more)

### Community 50 - "drive_folder"
Cohesion: 0.18
Nodes (14): main(), Export the full train image catalog to train_official.parquet (no embeddings)., google_colab, re, sys, drive_folder(), _looks_like_dataset(), Path (+6 more)

## Knowledge Gaps
- **72 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 290 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `embed.py` to `PETROSAINS inventory similarity (`test_pg`)`, `pathlib`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `bbox_xyxy()` connect `PETROSAINS inventory similarity (`test_pg`)` to `predict_labeled_image`, `visualize.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `EpochMetricPrinter`, `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _72 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.039057239057239054 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0647342995169082 - nodes in this community are weakly interconnected._