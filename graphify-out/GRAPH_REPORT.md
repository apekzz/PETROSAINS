# Graph Report - hilman_21Sep  (2026-09-23)

## Corpus Check
- 51 files · ~1,376,004 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 489 file(s) not represented in the graph (top: (none) 414, .ipynb 19, .pt 19)

## Summary
- 931 nodes · 1979 edges · 53 communities (47 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dc015b90`
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
- visualize_results.py
- _encode_worker_loop
- setup_db.py
- startLocalCamera
- embed.py
- normalize_item_name
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
- fetch_inventory_embeddings
- EpochMetricPrinter
- dice_loss.py
- MosaicProb
- OneShot Inventory (`inventory_app`)
- utils_db/infer.py
- test_sahi.py
- apply_bce_dice_mask_loss
- Saved PostgreSQL tables
- BaseModel
- _catalog_import_job
- inventory_app_config
- inventory_app_sam_tool
- db.py
- replace_inventory_embeddings
- analyzeLocalFrame
- applyMode

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 29 edges
2. `PgConfig` - 19 edges
3. `load_image_and_label()` - 16 edges
4. `connect_and_prepare()` - 15 edges
5. `normalize_item_name()` - 14 edges
6. `camera_capture_loop()` - 14 edges
7. `get_image_embedding()` - 14 edges
8. `drive_folder()` - 14 edges
9. `predict_labeled_image()` - 14 edges
10. `import_train_catalog()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `How to run` --references--> `load_clip_model()`  [INFERRED]
  test_pg/README.md → utils/embed.py
- `3. Evaluate on val / test` --references--> `save_query_objects()`  [INFERRED]
  test_pg/README.md → utils_db/cache.py
- `C. Generate training embeddings with OpenCLIP` --references--> `bbox_xyxy()`  [INFERRED]
  test_pg/README.md → utils/dataset.py
- `main()` --calls--> `drive_folder()`  [EXTRACTED]
  export_train_official.py → utils/gdrive.py
- `run_high_end_boot()` --calls--> `get_lan_ip()`  [INFERRED]
  inventory_app/main.py → inventory_app/backend/config.py

## Import Cycles
- None detected.

## Communities (53 total, 6 thin omitted)

### Community 0 - "visualize.py"
Cohesion: 0.15
Nodes (27): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., math, build_embedding_dataframe(), _class_key(), _class_names_for_image() (+19 more)

### Community 1 - "pathlib"
Cohesion: 0.14
Nodes (26): argparse, pathlib, pgvector_psycopg, sys, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1). (+18 more)

### Community 2 - "sam_tool.py"
Cohesion: 0.15
Nodes (17): base64, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session(), load_sam_model() (+9 more)

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (48): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnCompareCatalogs, btnCompareClose (+40 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.08
Nodes (36): datetime, _bar(), finish(), set_progress(), start(), _width(), json, platform (+28 more)

### Community 5 - "main.py"
Cohesion: 0.08
Nodes (36): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, sam_status(), boot_status(), camera_status() (+28 more)

### Community 6 - "get_db"
Cohesion: 0.13
Nodes (28): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+20 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.14
Nodes (30): arm_object_detection(), camera_capture_loop(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_detection_mode(), get_trigger_state(), ingest_browser_scan() (+22 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "face.py"
Cohesion: 0.06
Nodes (35): cv2, get_lan_ip(), _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model() (+27 more)

### Community 10 - "download_dataset.py"
Cohesion: 0.15
Nodes (23): google_colab, re, _copy_tree(), download_dataset(), _drive_folder(), _iter_files(), _looks_like_dataset(), main() (+15 more)

### Community 11 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.10
Nodes (20): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, D. Development mode: prediction and evaluation, E. Predict one image (`predict_labeled_image.py`) (+12 more)

### Community 12 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 13 - "eval.py"
Cohesion: 0.14
Nodes (29): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), embed_split_crops(), evaluate_rule() (+21 more)

### Community 14 - "tables"
Cohesion: 0.07
Nodes (27): columns, file, rows, exported_at, format, columns, file, columns (+19 more)

### Community 15 - "sql.py"
Cohesion: 0.09
Nodes (28): contextlib, init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), check_db(), close_boot_connection(), connect_and_prepare(), ensure_database() (+20 more)

### Community 16 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 17 - "noise_transfer.py"
Cohesion: 0.07
Nodes (50): dataclasses, choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray (+42 more)

### Community 18 - "visualize_results.py"
Cohesion: 0.14
Nodes (26): collections, csv, matplotlib, matplotlib_pyplot, canonical(), confusion_matrix(), label_bars(), latency_breakdown() (+18 more)

### Community 19 - "_encode_worker_loop"
Cohesion: 0.16
Nodes (14): _apply_face_embedding(), cosine_similarity(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker() (+6 more)

### Community 20 - "setup_db.py"
Cohesion: 0.25
Nodes (8): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), psycopg, sqlite3

### Community 21 - "startLocalCamera"
Cohesion: 0.31
Nodes (10): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), preferLaptopDeviceId(), preferredCameraFacing() (+2 more)

### Community 22 - "embed.py"
Cohesion: 0.13
Nodes (27): pandas, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights() (+19 more)

### Community 23 - "normalize_item_name"
Cohesion: 0.23
Nodes (14): compare_mobileclip2_vs_noise(), mean_name_vectors(), normalize_item_name(), Average embedding per inventory_name (for compare)., Per-name compare: mobileclip2 vs noise (mean vectors). Returns crop counts,…, SAM / one-shot register → mobileclip2 (abubu live primary)., save_inventory_embedding(), save_object_embedding() (+6 more)

### Community 24 - "post"
Cohesion: 0.12
Nodes (23): analyze_face_frame(), api_noise_capture(), api_start_camera(), _cancel_app_exit(), capture_sam_frame(), dashboard_hello(), dashboard_leave(), detection_preview_active() (+15 more)

### Community 25 - "run_high_end_boot"
Cohesion: 0.24
Nodes (10): images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API., run_high_end_boot() (+2 more)

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
Cohesion: 0.40
Nodes (6): _clear_session_movements(), _exit_app(), _force_close(), shutdown_event(), stop_camera(), on_event

### Community 34 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 35 - "fetch_inventory_embeddings"
Cohesion: 0.33
Nodes (6): _embedding_from_text(), fetch_inventory_embeddings(), fetch_live_dual_embeddings(), fetch_staff_embeddings(), Fetch one emb table. Default = friend mobileclip2 (abubu)., mobileclip2 + noise catalogs for dual live match (legacy unused).

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
Cohesion: 0.15
Nodes (18): matplotlib_patches, C. Generate training embeddings with OpenCLIP, bbox_xyxy(), crop_labeled_objects(), Image, Axis-aligned crop box from a YOLO box or polygon label., Crop each labeled object from ``image`` and attach bbox metadata., pick_query_image() (+10 more)

### Community 44 - "BaseModel"
Cohesion: 0.33
Nodes (6): BaseModel, FaceModeBody, post_face_register(), _register_staff_face(), SamRegisterBody, StaffRegisterBody

### Community 45 - "_catalog_import_job"
Cohesion: 0.38
Nodes (7): _catalog_import_job(), _catalog_progress(), import_catalog_paths(), Shared start for picker + path APIs. Caller must own the lock check., Import without folder picker — body: {image_dir, label_dir, noise_capture_dir?}., select_and_import_catalog(), _start_catalog_import()

### Community 49 - "db.py"
Cohesion: 0.17
Nodes (15): Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), insert_check_in_out(), IN / OUT writes check_in_out. SCAN is view-only., Clear transient movement history without touching catalog/staff tables., TRUNCATE listed emb tables and COPY from saved_tables CSVs (vectors as-is)., Restore CSV data only into currently empty supported tables., Rebuild summary from mobileclip2 (abubu rule); fallback legacy inventory_emb. (+7 more)

### Community 50 - "replace_inventory_embeddings"
Cohesion: 0.18
Nodes (12): clear_staff_embeddings(), _copy_table_to_file(), _embedding_to_text(), export_table_snapshots(), _export(), insert_staff(), _mobileclip2_id_skeleton(), Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive… (+4 more)

### Community 51 - "analyzeLocalFrame"
Cohesion: 0.32
Nodes (8): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo(), updateFacePreviews()

### Community 52 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

## Knowledge Gaps
- **82 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+77 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 322 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `bbox_xyxy()` connect `utils_db/infer.py` to `visualize.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `load_clip_model()` connect `embed.py` to `visualize.py`, `pathlib`, `PETROSAINS inventory similarity (`test_pg`)`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`, `EpochMetricPrinter`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _82 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.13763440860215054 - nodes in this community are weakly interconnected._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03634085213032581 - nodes in this community are weakly interconnected._