# Graph Report - hilman_21Sep  (2026-09-26)

## Corpus Check
- 84 files · ~1,516,826 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 548 file(s) not represented in the graph (top: (none) 417, .csv 65, .pt 20)

## Summary
- 1117 nodes · 2442 edges · 60 communities (50 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9b41302`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- utils_db/infer.py
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
- dice_loss.py
- applyFaceStatus
- noise_transfer.py
- consultant_model.py
- run_high_end_boot
- setup_db.py
- startLocalCamera
- embed.py
- sql.py
- drive_folder
- bootstrap_database
- runBrowserFaceLoop
- EarlyStopHook
- fetchStats
- updateTriggerStatus
- PETROSAINS
- V2DatasetMapper
- .__init__
- ref_fs
- ObjectTrainer
- evaluate_embedding_mc2_noise.py
- EpochMetricPrinter
- ref_crypto
- MosaicProb
- OneShot Inventory (`inventory_app`)
- yolo_to_coco.py
- test_sahi.py
- apply_bce_dice_mask_loss
- Saved PostgreSQL tables
- analyzeLocalFrame
- _catalog_import_job
- inventory_app_config
- inventory_app_sam_tool
- db.py
- visualize_results.py
- _encode_worker_loop
- visualize.py
- post
- consultant.js
- connect_and_prepare
- ref_path
- register_sam_embedding
- analyze_object_areas.py
- ref_https_cdn_jsdelivr_net_npm_mediapipe_tasks_vision_0_10_14_vision_bundle_mjs

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `main()` - 21 edges
3. `PgConfig` - 19 edges
4. `pair_features()` - 16 edges
5. `advise()` - 16 edges
6. `connect_and_prepare()` - 16 edges
7. `load_image_and_label()` - 16 edges
8. `startLocalCamera()` - 15 edges
9. `normalize_item_name()` - 14 edges
10. `ingest()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `How to run` --references--> `load_clip_model()`  [INFERRED]
  test_pg/README.md → utils/embed.py
- `3. Evaluate on val / test` --references--> `save_query_objects()`  [INFERRED]
  test_pg/README.md → utils_db/cache.py
- `C. Generate training embeddings with OpenCLIP` --references--> `bbox_xyxy()`  [INFERRED]
  test_pg/README.md → utils/dataset.py
- `main()` --calls--> `load_noise_profile_from_capture()`  [INFERRED]
  train_v2/evaluation/evaluate_embedding_mc2_noise.py → inventory_app/backend/noise_transfer.py
- `main()` --calls--> `apply_noise_to_image()`  [INFERRED]
  train_v2/evaluation/evaluate_embedding_mc2_noise.py → inventory_app/backend/noise_transfer.py

## Import Cycles
- None detected.

## Communities (60 total, 10 thin omitted)

### Community 0 - "utils_db/infer.py"
Cohesion: 0.17
Nodes (18): crop_labeled_objects(), load_image_and_label(), Image, Crop each labeled object from ``image`` and attach bbox metadata., Load one image and its YOLO label. Specify the file with ``image_path=``, or an…, embed_split_crops(), pick_query_image(), Embed every labeled crop in ``split``. Reuses a preloaded OpenCLIP model. (+10 more)

### Community 1 - "pathlib"
Cohesion: 0.13
Nodes (27): argparse, dataclasses, numpy, pathlib, pgvector_psycopg, main(), parse_args(), Namespace (+19 more)

### Community 2 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): base64, collections, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session() (+10 more)

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (52): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs (+44 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.18
Nodes (25): build_samples(), canonical_name(), classification_metrics(), inventory_name_from_filename(), load_catalog(), load_prediction_records(), main(), make_masked_crop() (+17 more)

### Community 5 - "main.py"
Cohesion: 0.07
Nodes (45): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, boot_status(), camera_status(), _cancel_app_exit() (+37 more)

### Community 6 - "get_db"
Cohesion: 0.12
Nodes (30): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+22 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.14
Nodes (30): arm_object_detection(), camera_capture_loop(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state(), ingest_browser_scan() (+22 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "face.py"
Cohesion: 0.06
Nodes (34): cv2, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+26 more)

### Community 10 - "download_dataset.py"
Cohesion: 0.14
Nodes (21): _bar(), finish(), set_progress(), start(), _width(), shutil, time, _copy_tree() (+13 more)

### Community 11 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.08
Nodes (23): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, C. Generate training embeddings with OpenCLIP, D. Development mode: prediction and evaluation (+15 more)

### Community 12 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 13 - "eval.py"
Cohesion: 0.16
Nodes (27): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), evaluate_rule(), _global_mean_sim() (+19 more)

### Community 14 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 15 - "dice_loss.py"
Cohesion: 0.15
Nodes (16): torch, torch_nn_functional, Label-aware Ultralytics train() kwargs. Aggressive geometry (mosaic, mixup,…, apply_bce_dice_mask_loss(), apply_dice_mask_loss(), bce_dice_single_mask_loss(), dice_single_mask_loss(), Tensor (+8 more)

### Community 16 - "applyFaceStatus"
Cohesion: 0.23
Nodes (15): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+7 more)

### Community 17 - "noise_transfer.py"
Cohesion: 0.10
Nodes (39): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+31 more)

### Community 18 - "consultant_model.py"
Cohesion: 0.06
Nodes (72): advise(), age_bounds(), _blank(), blocking_rule(), _boundary_reply(), _by_setup(), setup(), _check_items() (+64 more)

### Community 19 - "run_high_end_boot"
Cohesion: 0.17
Nodes (12): ensure_lan_cert(), get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there. (+4 more)

### Community 20 - "setup_db.py"
Cohesion: 0.14
Nodes (13): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), ensure_tables(), _apply() (+5 more)

### Community 21 - "startLocalCamera"
Cohesion: 0.27
Nodes (10): cameraChoiceSaved(), hideRemoteCameraPicker(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), preferLaptopDeviceId(), readCameraPermission(), refreshCameraList() (+2 more)

### Community 22 - "embed.py"
Cohesion: 0.15
Nodes (26): main(), typing, build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights(), get_clip_embedding() (+18 more)

### Community 23 - "sql.py"
Cohesion: 0.16
Nodes (15): contextlib, _app_db_up(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_live_dual_embeddings(), fetch_staff_embeddings() (+7 more)

### Community 24 - "drive_folder"
Cohesion: 0.16
Nodes (16): main(), Export the full train image catalog to train_official.parquet (no embeddings)., google_colab, pandas, re, sys, Embed every labeled crop from train_official.parquet and save the results., drive_folder() (+8 more)

### Community 25 - "bootstrap_database"
Cohesion: 0.14
Nodes (14): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), clear_staff_embeddings(), _copy_table_to_file(), ensure_database(), export_table_snapshots(), _export() (+6 more)

### Community 26 - "runBrowserFaceLoop"
Cohesion: 0.22
Nodes (11): applyLocalFace(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate(), runBrowserFaceLoop() (+3 more)

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

### Community 34 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 35 - "evaluate_embedding_mc2_noise.py"
Cohesion: 0.09
Nodes (44): datetime, json, platform, build_samples(), canonical_name(), chart_confusion_matrix(), chart_coverage(), chart_side_by_side() (+36 more)

### Community 36 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 38 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 39 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 40 - "yolo_to_coco.py"
Cohesion: 0.46
Nodes (7): tqdm, convert_dataset(), convert_split(), _image_path(), _polygons_from_label(), Path, Convert train_v2 YOLO-seg labels to COCO JSON for Detectron2.

### Community 44 - "analyzeLocalFrame"
Cohesion: 0.21
Nodes (13): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), captureButtonLabel(), drawLandmarks(), drawMediaPipeLandmarks(), enableCaptureFallback(), grabLocalFrame() (+5 more)

### Community 45 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir, noise_capture_dir?}., select_and_import_catalog(), _start_catalog_import()

### Community 49 - "db.py"
Cohesion: 0.14
Nodes (21): Compatibility wrappers. All SQL lives in sql.py., check_db(), close_boot_connection(), compare_mobileclip2_vs_noise(), _embedding_to_text(), insert_check_in_out(), insert_staff(), _lock() (+13 more)

### Community 50 - "visualize_results.py"
Cohesion: 0.25
Nodes (17): csv, matplotlib_pyplot, build_confusion(), canonical(), confusion_matrix(), draw_confusion(), label_bars(), latency_breakdown() (+9 more)

### Community 51 - "_encode_worker_loop"
Cohesion: 0.20
Nodes (12): _apply_face_embedding(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker(), handle_face_info() (+4 more)

### Community 52 - "visualize.py"
Cohesion: 0.17
Nodes (23): collections_abc, colorsys, math, matplotlib_patches, pil, build_embedding_dataframe(), _class_key(), _class_names_for_image() (+15 more)

### Community 54 - "post"
Cohesion: 0.09
Nodes (31): BaseModel, sam_status(), analyze_face_frame(), api_noise_capture(), api_start_camera(), capture_sam_frame(), consultant_advise(), consultant_talk() (+23 more)

### Community 55 - "consultant.js"
Cohesion: 0.13
Nodes (36): advise(), ageForLevel(), ageFrom(), askNext(), blankChat(), block(), boundaryText(), clearSide() (+28 more)

### Community 56 - "connect_and_prepare"
Cohesion: 0.10
Nodes (22): apply_saved_stock_totals(), clear_check_in_out(), connect_and_prepare(), ensure_schema_columns(), _open_connection(), Clear transient movement history without touching catalog/staff tables., Safely migrate existing installations without dropping data., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is). (+14 more)

### Community 58 - "register_sam_embedding"
Cohesion: 0.28
Nodes (9): cosine_similarity(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), match_staff_embedding(), refresh_inventory_catalog_cache(), register_sam_embedding() (+1 more)

### Community 68 - "analyze_object_areas.py"
Cohesion: 0.29
Nodes (13): matplotlib, _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace (+5 more)

## Knowledge Gaps
- **83 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 342 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EpochMetricPrinter` connect `EpochMetricPrinter` to `detectron2_recipe.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `MosaicProb` connect `MosaicProb` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `bbox_xyxy()` connect `PETROSAINS inventory similarity (`test_pg`)` to `utils_db/infer.py`, `visualize.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `apply_noise_to_image()` and `load_noise_profile_from_capture()`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.1310483870967742 - nodes in this community are weakly interconnected._
- **Should `sam_tool.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._