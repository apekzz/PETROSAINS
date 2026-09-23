# Graph Report - hilman_21Sep  (2026-09-23)

## Corpus Check
- 51 files · ~1,375,574 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 489 file(s) not represented in the graph (top: (none) 414, .ipynb 19, .pt 19)

## Summary
- 927 nodes · 1968 edges · 55 communities (49 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 96 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `80c3a4b4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- visualize.py
- pathlib
- sam_tool.py
- dashboard.js
- evaluate_embedding_similarity.py
- main.py
- get_db
- camera_capture_loop
- sam-tool.js
- face.py
- download_dataset.py
- PETROSAINS inventory similarity (`test_pg`)
- detectron2_recipe.py
- eval.py
- tables
- sql.py
- applyFaceStatus
- noise_transfer.py
- analyze_object_areas.py
- _encode_worker_loop
- setup_db.py
- startLocalCamera
- embed.py
- db.py
- post
- run_high_end_boot
- runBrowserFaceLoop
- EarlyStopHook
- fetchStats
- updateTriggerStatus
- PETROSAINS
- V2DatasetMapper
- .__init__
- _clear_session_movements
- ObjectTrainer
- ensure_tables
- EpochMetricPrinter
- dice_loss.py
- MosaicProb
- OneShot Inventory (`inventory_app`)
- utils_db/infer.py
- test_sahi.py
- apply_bce_dice_mask_loss
- Saved PostgreSQL tables
- register_sam_embedding
- _catalog_import_job
- inventory_app_config
- inventory_app_sam_tool
- connect_and_prepare
- export_table_snapshots
- analyzeLocalFrame
- applyMode
- crop_labeled_objects
- yolo_to_coco.py

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `PgConfig` - 19 edges
3. `load_image_and_label()` - 16 edges
4. `connect_and_prepare()` - 15 edges
5. `camera_capture_loop()` - 14 edges
6. `get_image_embedding()` - 14 edges
7. `drive_folder()` - 14 edges
8. `predict_labeled_image()` - 14 edges
9. `import_train_catalog()` - 13 edges
10. `normalize_item_name()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `How to run` --references--> `load_clip_model()`  [INFERRED]
  test_pg/README.md → utils/embed.py
- `3. Evaluate on val / test` --references--> `save_query_objects()`  [INFERRED]
  test_pg/README.md → utils_db/cache.py
- `C. Generate training embeddings with OpenCLIP` --references--> `bbox_xyxy()`  [INFERRED]
  test_pg/README.md → utils/dataset.py
- `main()` --calls--> `drive_folder()`  [EXTRACTED]
  export_train_official.py → utils/gdrive.py
- `main()` --calls--> `build_embedding_df()`  [EXTRACTED]
  test_pg/embed_train_official.py → utils/embed.py

## Import Cycles
- None detected.

## Communities (55 total, 6 thin omitted)

### Community 0 - "visualize.py"
Cohesion: 0.14
Nodes (28): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., math, pil, build_embedding_dataframe(), _class_key() (+20 more)

### Community 1 - "pathlib"
Cohesion: 0.13
Nodes (27): pathlib, pgvector_psycopg, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1)., ensure_container(), fingerprint() (+19 more)

### Community 2 - "sam_tool.py"
Cohesion: 0.15
Nodes (17): base64, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model() (+9 more)

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (48): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+40 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.05
Nodes (54): argparse, collections, csv, cv2, datetime, crop_bgr(), crop_masked_bgr(), load_model() (+46 more)

### Community 5 - "main.py"
Cohesion: 0.08
Nodes (35): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, boot_status(), camera_status(), catalog_compare() (+27 more)

### Community 6 - "get_db"
Cohesion: 0.13
Nodes (28): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+20 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.15
Nodes (29): arm_object_detection(), camera_capture_loop(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state(), ingest_browser_scan() (+21 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "face.py"
Cohesion: 0.12
Nodes (21): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+13 more)

### Community 10 - "download_dataset.py"
Cohesion: 0.09
Nodes (33): google_colab, _bar(), finish(), set_progress(), start(), _width(), re, shutil (+25 more)

### Community 11 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.10
Nodes (20): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, D. Development mode: prediction and evaluation, E. Predict one image (`predict_labeled_image.py`) (+12 more)

### Community 12 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 13 - "eval.py"
Cohesion: 0.16
Nodes (27): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), evaluate_rule(), _global_mean_sim() (+19 more)

### Community 14 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 15 - "sql.py"
Cohesion: 0.13
Nodes (17): contextlib, init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), _embedding_from_text(), ensure_database(), ensure_postgres_running(), fetch_inventory_embeddings() (+9 more)

### Community 16 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 17 - "noise_transfer.py"
Cohesion: 0.09
Nodes (40): dataclasses, choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray (+32 more)

### Community 18 - "analyze_object_areas.py"
Cohesion: 0.32
Nodes (12): _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace, ndarray (+4 more)

### Community 19 - "_encode_worker_loop"
Cohesion: 0.20
Nodes (12): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_embed_worker(), _load_clip_weights() (+4 more)

### Community 20 - "setup_db.py"
Cohesion: 0.20
Nodes (10): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), os, psycopg (+2 more)

### Community 21 - "startLocalCamera"
Cohesion: 0.31
Nodes (10): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferLaptopDeviceId(), preferredCameraFacing() (+2 more)

### Community 22 - "embed.py"
Cohesion: 0.18
Nodes (22): build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights(), get_clip_embedding(), get_image_embedding(), get_yolo_embedding() (+14 more)

### Community 23 - "db.py"
Cohesion: 0.18
Nodes (15): Compatibility wrappers. All SQL lives in sql.py., check_db(), close_boot_connection(), compare_mobileclip2_vs_noise(), insert_check_in_out(), _lock(), mean_name_vectors(), normalize_item_name() (+7 more)

### Community 24 - "post"
Cohesion: 0.13
Nodes (21): sam_status(), analyze_face_frame(), api_noise_capture(), api_start_camera(), capture_sam_frame(), create_object_embedding(), detection_preview_active(), embed_captured_face() (+13 more)

### Community 25 - "run_high_end_boot"
Cohesion: 0.22
Nodes (11): get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API. (+3 more)

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
Cohesion: 0.21
Nodes (12): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), loadCatalogCompare(), maybeToastCapture(), renderMovements(), renderRecognized(), restoreLiveDetectionStream() (+4 more)

### Community 30 - "PETROSAINS"
Cohesion: 0.18
Nodes (10): Daily use (after first setup), Files, Folders, How to run the inventory app, PETROSAINS, Root layout, Steps, `test_pg/` (similarity pipeline) (+2 more)

### Community 31 - "V2DatasetMapper"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 32 - ".__init__"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 33 - "_clear_session_movements"
Cohesion: 0.22
Nodes (10): _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event() (+2 more)

### Community 34 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 35 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 36 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 37 - "dice_loss.py"
Cohesion: 0.15
Nodes (16): Tensor, torch, torch_nn_functional, Label-aware Ultralytics train() kwargs. Aggressive geometry (mosaic, mixup,…, apply_bce_dice_mask_loss(), apply_dice_mask_loss(), bce_dice_single_mask_loss(), dice_single_mask_loss() (+8 more)

### Community 38 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 39 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 40 - "utils_db/infer.py"
Cohesion: 0.20
Nodes (13): matplotlib, matplotlib_patches, pandas, _color_for_name(), draw_predictions(), predict_labeled_image(), DataFrame, Image (+5 more)

### Community 44 - "register_sam_embedding"
Cohesion: 0.16
Nodes (14): BaseModel, FaceModeBody, generate_sam_mask(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), post_face_register(), refresh_inventory_catalog_cache() (+6 more)

### Community 45 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir}., select_and_import_catalog(), _start_catalog_import()

### Community 49 - "connect_and_prepare"
Cohesion: 0.11
Nodes (20): clear_check_in_out(), connect_and_prepare(), ensure_schema_columns(), _open_connection(), Safely migrate existing installations without dropping data., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Reject incompatible existing tables without deleting or replacing them., Tables whose CSV is missing or row-count differs from Postgres. (+12 more)

### Community 50 - "export_table_snapshots"
Cohesion: 0.22
Nodes (10): clear_staff_embeddings(), _copy_table_to_file(), _embedding_to_text(), export_table_snapshots(), _export(), insert_staff(), Export supported application tables to atomic CSV snapshots. only: optional…, Noise train import → replace inventory_emb_noise only (leave friend catalogs). (+2 more)

### Community 51 - "analyzeLocalFrame"
Cohesion: 0.32
Nodes (8): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo(), updateFacePreviews()

### Community 52 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 53 - "crop_labeled_objects"
Cohesion: 0.22
Nodes (9): C. Generate training embeddings with OpenCLIP, bbox_xyxy(), crop_labeled_objects(), Image, Axis-aligned crop box from a YOLO box or polygon label., Crop each labeled object from ``image`` and attach bbox metadata., embed_split_crops(), pick_query_image() (+1 more)

### Community 54 - "yolo_to_coco.py"
Cohesion: 0.57
Nodes (6): convert_dataset(), convert_split(), _image_path(), _polygons_from_label(), Path, Convert train_v2 YOLO-seg labels to COCO JSON for Detectron2.

## Knowledge Gaps
- **82 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+77 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 320 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `pathlib` to `download_dataset.py`, `PETROSAINS inventory similarity (`test_pg`)`, `embed.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `bbox_xyxy()` connect `crop_labeled_objects` to `visualize.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`, `EpochMetricPrinter`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _82 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `visualize.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14408602150537633 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.12903225806451613 - nodes in this community are weakly interconnected._