# Graph Report - hilman_21Sep  (2026-09-26)

## Corpus Check
- 84 files · ~1,513,897 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 545 file(s) not represented in the graph (top: (none) 415, .csv 65, .pt 20)

## Summary
- 1067 nodes · 2319 edges · 58 communities (52 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 102 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `05896f39`
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
- backend/infer.py
- applyFaceStatus
- noise_transfer.py
- consultant_model.py
- create_object_embedding
- setup_db.py
- startLocalCamera
- embed.py
- fetch_inventory_embeddings
- post
- run_high_end_boot
- runBrowserFaceLoop
- EarlyStopHook
- fetchStats
- updateTriggerStatus
- PETROSAINS
- V2DatasetMapper
- .__init__
- visualize_results.py
- ObjectTrainer
- evaluate_embedding_mc2_noise.py
- EpochMetricPrinter
- connect_and_prepare
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
- db.py
- ensure_tables
- analyzeLocalFrame
- applyMode
- analyze_object_areas.py
- face_status_payload
- consultant.js
- get
- _encode_worker_loop

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `main()` - 21 edges
3. `PgConfig` - 19 edges
4. `pair_features()` - 16 edges
5. `load_image_and_label()` - 16 edges
6. `advise()` - 15 edges
7. `connect_and_prepare()` - 15 edges
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

## Communities (58 total, 6 thin omitted)

### Community 0 - "visualize.py"
Cohesion: 0.15
Nodes (26): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., math, pil, build_embedding_dataframe(), _class_key() (+18 more)

### Community 1 - "pathlib"
Cohesion: 0.13
Nodes (27): argparse, numpy, pathlib, pgvector_psycopg, sys, main(), parse_args(), Namespace (+19 more)

### Community 2 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): base64, collections, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session() (+10 more)

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (48): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+40 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.08
Nodes (42): datetime, _bar(), finish(), set_progress(), start(), _width(), platform, shutil (+34 more)

### Community 5 - "main.py"
Cohesion: 0.09
Nodes (32): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, _cancel_app_exit(), _clear_session_movements(), dashboard_hello() (+24 more)

### Community 6 - "get_db"
Cohesion: 0.16
Nodes (22): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_staff_list() (+14 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.13
Nodes (31): arm_object_detection(), boot_status(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active() (+23 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "face.py"
Cohesion: 0.12
Nodes (21): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+13 more)

### Community 10 - "download_dataset.py"
Cohesion: 0.15
Nodes (23): google_colab, re, _copy_tree(), download_dataset(), _drive_folder(), _iter_files(), _looks_like_dataset(), main() (+15 more)

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

### Community 15 - "backend/infer.py"
Cohesion: 0.08
Nodes (26): cv2, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon., Run the v2 segmentation model. Same call shape as the notebook. (+18 more)

### Community 16 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 17 - "noise_transfer.py"
Cohesion: 0.09
Nodes (41): dataclasses, choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray (+33 more)

### Community 18 - "consultant_model.py"
Cohesion: 0.07
Nodes (63): get_lan_ip(), advise(), age_bounds(), _blank(), blocking_rule(), _by_setup(), setup(), _check_items() (+55 more)

### Community 19 - "create_object_embedding"
Cohesion: 0.40
Nodes (6): create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), parse_yolo_boxes(), refresh_inventory_catalog_cache()

### Community 20 - "setup_db.py"
Cohesion: 0.20
Nodes (10): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), os, psycopg (+2 more)

### Community 21 - "startLocalCamera"
Cohesion: 0.31
Nodes (10): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferLaptopDeviceId(), preferredCameraFacing() (+2 more)

### Community 22 - "embed.py"
Cohesion: 0.13
Nodes (27): pandas, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights() (+19 more)

### Community 23 - "fetch_inventory_embeddings"
Cohesion: 0.33
Nodes (6): _embedding_from_text(), fetch_inventory_embeddings(), fetch_live_dual_embeddings(), fetch_staff_embeddings(), Fetch one emb table. Default = friend mobileclip2 (abubu)., mobileclip2 + noise catalogs for dual live match (legacy unused).

### Community 24 - "post"
Cohesion: 0.12
Nodes (23): BaseModel, sam_status(), api_noise_capture(), api_start_camera(), capture_sam_frame(), consultant_advise(), consultant_talk(), ConsultantRequest (+15 more)

### Community 25 - "run_high_end_boot"
Cohesion: 0.16
Nodes (16): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), clear_check_in_out(), clear_staff_embeddings(), ensure_database(), Clear transient movement history without touching catalog/staff tables., Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive… (+8 more)

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

### Community 33 - "visualize_results.py"
Cohesion: 0.25
Nodes (17): csv, matplotlib_pyplot, build_confusion(), canonical(), confusion_matrix(), draw_confusion(), label_bars(), latency_breakdown() (+9 more)

### Community 34 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 35 - "evaluate_embedding_mc2_noise.py"
Cohesion: 0.13
Nodes (33): build_samples(), canonical_name(), chart_confusion_matrix(), chart_coverage(), chart_side_by_side(), chart_top_confusions(), classification_metrics(), encode_batches() (+25 more)

### Community 36 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 37 - "connect_and_prepare"
Cohesion: 0.12
Nodes (18): connect_and_prepare(), ensure_schema_columns(), _open_connection(), Safely migrate existing installations without dropping data., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Reject incompatible existing tables without deleting or replacing them., Tables whose CSV is missing or row-count differs from Postgres., Restore CSV data only into currently empty supported tables. (+10 more)

### Community 38 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 39 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 40 - "utils_db/infer.py"
Cohesion: 0.15
Nodes (20): matplotlib, matplotlib_patches, crop_labeled_objects(), load_image_and_label(), Image, Crop each labeled object from ``image`` and attach bbox metadata., Load one image and its YOLO label. Specify the file with ``image_path=``, or an…, embed_split_crops() (+12 more)

### Community 44 - "sql.py"
Cohesion: 0.15
Nodes (17): contextlib, get_movements(), _app_db_up(), check_db(), close_boot_connection(), _drop_stale_postmaster_pid(), ensure_postgres_running(), fetch_movements() (+9 more)

### Community 45 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir, noise_capture_dir?}., select_and_import_catalog(), _start_catalog_import()

### Community 49 - "db.py"
Cohesion: 0.13
Nodes (23): Compatibility wrappers. All SQL lives in sql.py., compare_mobileclip2_vs_noise(), _copy_table_to_file(), _embedding_to_text(), export_table_snapshots(), _export(), get_staff(), insert_check_in_out() (+15 more)

### Community 50 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 51 - "analyzeLocalFrame"
Cohesion: 0.32
Nodes (8): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo(), updateFacePreviews()

### Community 52 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 53 - "analyze_object_areas.py"
Cohesion: 0.19
Nodes (19): tqdm, _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace (+11 more)

### Community 54 - "face_status_payload"
Cohesion: 0.15
Nodes (16): analyze_face_frame(), _apply_face_embedding(), cosine_similarity(), detection_preview_active(), embed_captured_face(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker() (+8 more)

### Community 55 - "consultant.js"
Cohesion: 0.24
Nodes (14): advise(), ageFrom(), askNext(), block(), clearTime(), hasAudience(), ingest(), payload() (+6 more)

### Community 56 - "get"
Cohesion: 0.17
Nodes (13): camera_status(), catalog_compare(), catalog_import_status(), db_status(), detection_preview(), get_detection_mode(), get_mode(), get (+5 more)

### Community 57 - "_encode_worker_loop"
Cohesion: 0.22
Nodes (10): _encode_image(), _encode_images(), _encode_worker_loop(), images_to_embeddings(), _load_clip_weights(), load_embed_model(), _prepare_inventory_model_image(), queue_face_embedding() (+2 more)

## Knowledge Gaps
- **82 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+77 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 334 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ModernAMPTrainer` connect `.__init__` to `ObjectTrainer`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`, `EpochMetricPrinter`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `MosaicProb` connect `MosaicProb` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `apply_noise_to_image()` and `load_noise_profile_from_capture()`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _82 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.13306451612903225 - nodes in this community are weakly interconnected._
- **Should `sam_tool.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._