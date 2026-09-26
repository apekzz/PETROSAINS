# Graph Report - hilman_21Sep  (2026-09-26)

## Corpus Check
- 84 files · ~1,514,949 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 547 file(s) not represented in the graph (top: (none) 417, .csv 65, .pt 20)

## Summary
- 1088 nodes · 2365 edges · 61 communities (51 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 104 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3f30865`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- visualize.py
- pathlib
- pil
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
- eval.py
- tables
- dice_loss.py
- applyFaceStatus
- noise_transfer.py
- consultant_model.py
- run_high_end_boot
- get_db
- startLocalCamera
- embed.py
- sql.py
- BaseModel
- export_table_snapshots
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
- utils_db/infer.py
- test_sahi.py
- apply_bce_dice_mask_loss
- Saved PostgreSQL tables
- fetch_inventory_embeddings
- _catalog_import_job
- inventory_app_config
- inventory_app_sam_tool
- db.py
- visualize_results.py
- _encode_worker_loop
- applyMode
- close_boot_connection
- post
- consultant.js
- refresh_main_inventory
- ref_path
- register_sam_embedding
- backend/infer.py
- ref_https_cdn_jsdelivr_net_npm_mediapipe_tasks_vision_0_10_14_vision_bundle_mjs

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `main()` - 21 edges
3. `PgConfig` - 19 edges
4. `pair_features()` - 16 edges
5. `connect_and_prepare()` - 16 edges
6. `load_image_and_label()` - 16 edges
7. `advise()` - 15 edges
8. `normalize_item_name()` - 14 edges
9. `camera_capture_loop()` - 14 edges
10. `get_image_embedding()` - 14 edges

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

## Communities (61 total, 10 thin omitted)

### Community 0 - "visualize.py"
Cohesion: 0.15
Nodes (27): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., sys, build_embedding_dataframe(), _class_key(), _class_names_for_image() (+19 more)

### Community 1 - "pathlib"
Cohesion: 0.13
Nodes (27): numpy, pathlib, pgvector_psycopg, psycopg, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1). (+19 more)

### Community 2 - "pil"
Cohesion: 0.46
Nodes (7): pil, convert_dataset(), convert_split(), _image_path(), _polygons_from_label(), Path, Convert train_v2 YOLO-seg labels to COCO JSON for Detectron2.

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (49): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+41 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.11
Nodes (36): datetime, json, platform, build_samples(), canonical_name(), classification_metrics(), inventory_name_from_filename(), load_catalog() (+28 more)

### Community 5 - "main.py"
Cohesion: 0.08
Nodes (38): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, sam_status(), boot_status(), camera_status() (+30 more)

### Community 6 - "api.py"
Cohesion: 0.14
Nodes (21): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_movements(), get_staff_list() (+13 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.12
Nodes (33): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode() (+25 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "face.py"
Cohesion: 0.06
Nodes (39): base64, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+31 more)

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
Cohesion: 0.14
Nodes (30): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), embed_split_crops(), evaluate_rule() (+22 more)

### Community 14 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 15 - "dice_loss.py"
Cohesion: 0.15
Nodes (16): torch, torch_nn_functional, Label-aware Ultralytics train() kwargs. Aggressive geometry (mosaic, mixup,…, apply_bce_dice_mask_loss(), apply_dice_mask_loss(), bce_dice_single_mask_loss(), dice_single_mask_loss(), Tensor (+8 more)

### Community 16 - "applyFaceStatus"
Cohesion: 0.23
Nodes (15): analyzeLocalFrame(), applyFaceStatus(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), grabLocalFrame(), grabSegmentedFace(), hasCapturedRegisterFace() (+7 more)

### Community 17 - "noise_transfer.py"
Cohesion: 0.09
Nodes (41): dataclasses, choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray (+33 more)

### Community 18 - "consultant_model.py"
Cohesion: 0.07
Nodes (63): advise(), age_bounds(), _blank(), blocking_rule(), _boundary_reply(), _by_setup(), setup(), _check_items() (+55 more)

### Community 19 - "run_high_end_boot"
Cohesion: 0.18
Nodes (13): ensure_lan_cert(), get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there. (+5 more)

### Community 20 - "get_db"
Cohesion: 0.16
Nodes (16): config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), ensure_tables() (+8 more)

### Community 21 - "startLocalCamera"
Cohesion: 0.21
Nodes (16): applyCapturedPhoto(), captureButtonLabel(), enableCaptureFallback(), hideRemoteCameraPicker(), ingestScanFrame(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback() (+8 more)

### Community 22 - "embed.py"
Cohesion: 0.10
Nodes (36): google_colab, pandas, re, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg() (+28 more)

### Community 23 - "sql.py"
Cohesion: 0.11
Nodes (25): contextlib, _app_db_up(), bootstrap_database(), check_db(), connect_and_prepare(), _drop_stale_postmaster_pid(), ensure_database(), ensure_postgres_running() (+17 more)

### Community 24 - "BaseModel"
Cohesion: 0.18
Nodes (11): BaseModel, consultant_advise(), consultant_talk(), ConsultantRequest, FaceModeBody, post_face_register(), _register_staff_face(), SamRegisterBody (+3 more)

### Community 25 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…, Export supported application tables to atomic CSV snapshots. only: optional…

### Community 26 - "runBrowserFaceLoop"
Cohesion: 0.16
Nodes (14): applyLocalFace(), drawLandmarks(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan() (+6 more)

### Community 27 - "EarlyStopHook"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "fetchStats"
Cohesion: 0.14
Nodes (16): animateValue(), escapeHtml(), fetchInventory(), fetchSelectedItemStats(), fetchStats(), loadCatalogCompare(), loadItemOptions(), pollCatalogImport() (+8 more)

### Community 29 - "updateTriggerStatus"
Cohesion: 0.38
Nodes (7): applyObjectRecognitionState(), maybeToastCapture(), restoreLiveDetectionStream(), showCaptureAlert(), showFrozenDetectionPreview(), startObjectRecognition(), updateTriggerStatus()

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
Cohesion: 0.13
Nodes (33): build_samples(), canonical_name(), chart_confusion_matrix(), chart_coverage(), chart_side_by_side(), chart_top_confusions(), classification_metrics(), encode_batches() (+25 more)

### Community 36 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 38 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 39 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 40 - "utils_db/infer.py"
Cohesion: 0.17
Nodes (15): matplotlib, matplotlib_patches, crop_labeled_objects(), Image, Crop each labeled object from ``image`` and attach bbox metadata., _color_for_name(), draw_predictions(), predict_labeled_image() (+7 more)

### Community 44 - "fetch_inventory_embeddings"
Cohesion: 0.25
Nodes (8): _embedding_from_text(), fetch_inventory_embeddings(), fetch_live_dual_embeddings(), fetch_staff_embeddings(), Fetch one emb table. Default = friend mobileclip2 (abubu)., mobileclip2 + noise catalogs for dual live match (legacy unused)., cosine_similarity(), match_staff_embedding()

### Community 45 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir, noise_capture_dir?}., select_and_import_catalog(), _start_catalog_import()

### Community 49 - "db.py"
Cohesion: 0.11
Nodes (25): get_item_summary(), init_schema(), Compatibility wrappers. All SQL lives in sql.py., Boot helper — create missing tables only. Never seeds or overwrites., clear_check_in_out(), compare_mobileclip2_vs_noise(), _embedding_to_text(), fetch_item_summary() (+17 more)

### Community 50 - "visualize_results.py"
Cohesion: 0.23
Nodes (18): collections, csv, matplotlib_pyplot, build_confusion(), canonical(), confusion_matrix(), draw_confusion(), label_bars() (+10 more)

### Community 51 - "_encode_worker_loop"
Cohesion: 0.20
Nodes (12): _apply_face_embedding(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker(), handle_face_info() (+4 more)

### Community 52 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 53 - "close_boot_connection"
Cohesion: 0.43
Nodes (7): close_boot_connection(), _clear_session_movements(), _exit_app(), _force_close(), shutdown_event(), stop_camera(), on_event

### Community 54 - "post"
Cohesion: 0.15
Nodes (19): analyze_face_frame(), api_noise_capture(), api_start_camera(), _cancel_app_exit(), dashboard_hello(), dashboard_leave(), detection_preview_active(), embed_captured_face() (+11 more)

### Community 55 - "consultant.js"
Cohesion: 0.20
Nodes (23): advise(), ageFrom(), askNext(), block(), boundaryText(), decline(), foldFacts(), followUp() (+15 more)

### Community 56 - "refresh_main_inventory"
Cohesion: 0.20
Nodes (10): apply_saved_stock_totals(), TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Restore CSV data only into currently empty supported tables., Copy official orig_quantity from the main_inventory snapshot onto matching…, Add inventory names from photo rows. Do not replace official stock totals., refresh_main_inventory(), _refresh(), reload_embedding_snapshots_from_csv() (+2 more)

### Community 58 - "register_sam_embedding"
Cohesion: 0.31
Nodes (9): create_masked_crop(), Create a tight, black-background crop for the shared OpenCLIP encoder., save_object_embedding(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), refresh_inventory_catalog_cache() (+1 more)

### Community 68 - "backend/infer.py"
Cohesion: 0.11
Nodes (23): argparse, cv2, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon. (+15 more)

## Knowledge Gaps
- **83 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 339 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_noise_profile_from_capture()` connect `noise_transfer.py` to `evaluate_embedding_mc2_noise.py`, `_catalog_import_job`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`, `EpochMetricPrinter`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `EpochMetricPrinter` connect `EpochMetricPrinter` to `detectron2_recipe.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `apply_noise_to_image()` and `load_noise_profile_from_capture()`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `visualize.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14942528735632185 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.12903225806451613 - nodes in this community are weakly interconnected._