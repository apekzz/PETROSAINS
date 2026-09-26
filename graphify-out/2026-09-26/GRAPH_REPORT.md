# Graph Report - hilman_21Sep  (2026-09-26)

## Corpus Check
- 84 files · ~1,514,880 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 547 file(s) not represented in the graph (top: (none) 417, .csv 65, .pt 20)

## Summary
- 1086 nodes · 2357 edges · 61 communities (51 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 104 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3f30865`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- visualize.py
- pathlib
- sam_tool.py
- dashboard.js
- evaluate_embedding_similarity.py
- main.py
- db.py
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
- connect_and_prepare
- register_sam_embedding
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
- sql.py
- _catalog_import_job
- inventory_app_config
- inventory_app_sam_tool
- normalize_item_name
- bootstrap_database
- _encode_worker_loop
- applyMode
- close_boot_connection
- post
- consultant.js
- clear_check_in_out
- ref_path
- backend/infer.py
- evaluate_segmentation.py
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
Nodes (27): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., math, build_embedding_dataframe(), _class_key(), _class_names_for_image() (+19 more)

### Community 1 - "pathlib"
Cohesion: 0.14
Nodes (26): numpy, pathlib, pgvector_psycopg, sys, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1). (+18 more)

### Community 2 - "sam_tool.py"
Cohesion: 0.08
Nodes (37): base64, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model() (+29 more)

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (49): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+41 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.16
Nodes (27): datetime, platform, build_samples(), canonical_name(), classification_metrics(), inventory_name_from_filename(), load_catalog(), load_prediction_records() (+19 more)

### Community 5 - "main.py"
Cohesion: 0.09
Nodes (32): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, boot_status(), camera_status(), catalog_compare() (+24 more)

### Community 6 - "db.py"
Cohesion: 0.15
Nodes (26): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+18 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.12
Nodes (33): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode() (+25 more)

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
Cohesion: 0.06
Nodes (66): advise(), age_bounds(), _blank(), blocking_rule(), _boundary_reply(), _by_setup(), setup(), _check_items() (+58 more)

### Community 19 - "run_high_end_boot"
Cohesion: 0.18
Nodes (13): ensure_lan_cert(), get_lan_ip(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there. (+5 more)

### Community 20 - "setup_db.py"
Cohesion: 0.14
Nodes (13): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), ensure_tables(), _apply() (+5 more)

### Community 21 - "startLocalCamera"
Cohesion: 0.21
Nodes (16): applyCapturedPhoto(), captureButtonLabel(), enableCaptureFallback(), hideRemoteCameraPicker(), ingestScanFrame(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback() (+8 more)

### Community 22 - "embed.py"
Cohesion: 0.10
Nodes (36): google_colab, pandas, re, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg() (+28 more)

### Community 23 - "connect_and_prepare"
Cohesion: 0.10
Nodes (22): apply_saved_stock_totals(), check_db(), connect_and_prepare(), ensure_schema_columns(), _lock(), _open_connection(), Safely migrate existing installations without dropping data., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is). (+14 more)

### Community 24 - "register_sam_embedding"
Cohesion: 0.15
Nodes (17): BaseModel, save_object_embedding(), consultant_advise(), consultant_talk(), ConsultantRequest, create_object_embedding(), generate_sam_mask(), get_inventory_catalog() (+9 more)

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
Cohesion: 0.08
Nodes (51): collections, csv, matplotlib_pyplot, build_samples(), canonical_name(), chart_confusion_matrix(), chart_coverage(), chart_side_by_side() (+43 more)

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

### Community 44 - "sql.py"
Cohesion: 0.14
Nodes (18): contextlib, _app_db_up(), _checkout_as_detection(), _drop_stale_postmaster_pid(), _embedding_from_text(), ensure_postgres_running(), fetch_inventory_embeddings(), fetch_live_dual_embeddings() (+10 more)

### Community 45 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir, noise_capture_dir?}., select_and_import_catalog(), _start_catalog_import()

### Community 49 - "normalize_item_name"
Cohesion: 0.19
Nodes (13): compare_mobileclip2_vs_noise(), _embedding_to_text(), insert_staff(), mean_name_vectors(), _mobileclip2_id_skeleton(), normalize_item_name(), Average embedding per inventory_name (for compare)., Per-name compare: mobileclip2 vs noise (mean vectors). Returns crop counts,… (+5 more)

### Community 50 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 51 - "_encode_worker_loop"
Cohesion: 0.13
Nodes (17): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker() (+9 more)

### Community 52 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 53 - "close_boot_connection"
Cohesion: 0.36
Nodes (8): close_boot_connection(), _clear_session_movements(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event(), stop_camera(), on_event

### Community 54 - "post"
Cohesion: 0.13
Nodes (22): sam_status(), analyze_face_frame(), api_noise_capture(), api_start_camera(), _cancel_app_exit(), capture_sam_frame(), dashboard_hello(), dashboard_leave() (+14 more)

### Community 55 - "consultant.js"
Cohesion: 0.20
Nodes (21): advise(), ageFrom(), askNext(), block(), boundaryText(), decline(), foldFacts(), followUp() (+13 more)

### Community 56 - "clear_check_in_out"
Cohesion: 0.33
Nodes (6): clear_check_in_out(), insert_check_in_out(), IN / OUT writes check_in_out. SCAN is view-only., Clear transient movement history without touching catalog/staff tables., recalculate_available_quantities(), record_yolo_capture()

### Community 68 - "backend/infer.py"
Cohesion: 0.16
Nodes (11): argparse, cv2, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon. (+3 more)

### Community 77 - "evaluate_segmentation.py"
Cohesion: 0.33
Nodes (8): count_instances(), main(), metric_value(), Path, Evaluate YOLO11 segmentation on the merged validation and test splits., split_images(), write_text_report(), yaml

## Knowledge Gaps
- **83 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 339 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MosaicProb` connect `MosaicProb` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `EarlyStopHook` connect `EarlyStopHook` to `detectron2_recipe.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `load_noise_profile_from_capture()` connect `noise_transfer.py` to `evaluate_embedding_mc2_noise.py`, `_catalog_import_job`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `apply_noise_to_image()` and `load_noise_profile_from_capture()`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `visualize.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14942528735632185 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.13763440860215054 - nodes in this community are weakly interconnected._