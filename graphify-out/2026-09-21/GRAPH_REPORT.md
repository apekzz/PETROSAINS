# Graph Report - PETROSAINS  (2026-09-21)

## Corpus Check
- 49 files · ~1,370,647 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 486 file(s) not represented in the graph (top: (none) 413, .ipynb 19, .pt 19)

## Summary
- 841 nodes · 1826 edges · 44 communities (40 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 63 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e47fb581`
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
- saved_tables/README.md
- api.py
- sam-tool.js
- db.py
- sql.py
- detectron2_recipe.py
- get
- tables
- download_dataset.py
- dice_loss.py
- sam_tool.py
- post
- run_high_end_boot
- applyFaceStatus
- analyze_object_areas.py
- EarlyStopHook
- setup_db.py
- fetchStats
- runBrowserFaceLoop
- _exit_app
- V2DatasetMapper
- .__init__
- updateTriggerStatus
- ObjectTrainer
- bootstrap_database
- PETROSAINS inventory similarity (`test_pg`)
- EpochMetricPrinter
- analyzeLocalFrame
- setFaceHint
- ensure_tables
- MosaicProb
- applyMode
- test_sahi.py
- apply_bce_dice_mask_loss
- register_sam_embedding

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 27 edges
2. `PgConfig` - 19 edges
3. `load_image_and_label()` - 16 edges
4. `camera_capture_loop()` - 14 edges
5. `run_high_end_boot()` - 14 edges
6. `connect_and_prepare()` - 14 edges
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
- `main()` --calls--> `build_embedding_dataframe()`  [EXTRACTED]
  export_train_official.py → utils/dataset.py
- `main()` --calls--> `drive_folder()`  [EXTRACTED]
  test_pg/embed_train_official.py → utils/gdrive.py

## Import Cycles
- None detected.

## Communities (44 total, 4 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (39): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace, btnImportCatalog (+31 more)

### Community 1 - "face.py"
Cohesion: 0.07
Nodes (32): cv2, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+24 more)

### Community 2 - "evaluate_embedding_similarity.py"
Cohesion: 0.08
Nodes (43): argparse, collections, csv, datetime, json, matplotlib_pyplot, platform, build_samples() (+35 more)

### Community 3 - "main.py"
Cohesion: 0.10
Nodes (28): asyncio, delete, fastapi_middleware_cors, fastapi_responses, _apply_face_embedding(), cosine_similarity(), delete_sam_session(), _encode_image() (+20 more)

### Community 4 - "embed.py"
Cohesion: 0.14
Nodes (27): dataclasses, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights() (+19 more)

### Community 5 - "camera_capture_loop"
Cohesion: 0.13
Nodes (31): arm_object_detection(), boot_status(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active() (+23 more)

### Community 6 - "eval.py"
Cohesion: 0.05
Nodes (94): collections_abc, colorsys, math, matplotlib, matplotlib_patches, numpy, pandas, pathlib (+86 more)

### Community 7 - "PETROSAINS"
Cohesion: 0.18
Nodes (10): Daily use (after first setup), Files, Folders, How to run the inventory app, PETROSAINS, Root layout, Steps, `test_pg/` (similarity pipeline) (+2 more)

### Community 9 - "api.py"
Cohesion: 0.12
Nodes (25): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+17 more)

### Community 10 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 11 - "db.py"
Cohesion: 0.17
Nodes (23): Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), _embedding_from_text(), _embedding_to_text(), fetch_inventory_embeddings(), fetch_item_summary(), fetch_staff_embeddings(), get_db() (+15 more)

### Community 12 - "sql.py"
Cohesion: 0.13
Nodes (20): contextlib, check_db(), close_boot_connection(), connect_and_prepare(), _copy_table_to_file(), ensure_schema_columns(), export_table_snapshots(), _export() (+12 more)

### Community 13 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 14 - "get"
Cohesion: 0.14
Nodes (15): camera_status(), catalog_import_status(), db_status(), detection_preview(), generate_frames(), get_detection_mode(), get_mode(), get_sam_status() (+7 more)

### Community 16 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 17 - "download_dataset.py"
Cohesion: 0.08
Nodes (37): main(), Export the full train image catalog to train_official.parquet (no embeddings)., google_colab, _bar(), fail(), finish(), pulse(), set_progress() (+29 more)

### Community 18 - "dice_loss.py"
Cohesion: 0.15
Nodes (16): Tensor, torch, torch_nn_functional, Label-aware Ultralytics train() kwargs. Aggressive geometry (mosaic, mixup,…, apply_bce_dice_mask_loss(), apply_dice_mask_loss(), bce_dice_single_mask_loss(), dice_single_mask_loss() (+8 more)

### Community 20 - "sam_tool.py"
Cohesion: 0.10
Nodes (29): base64, choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray (+21 more)

### Community 21 - "post"
Cohesion: 0.14
Nodes (20): analyze_face_frame(), api_start_camera(), _cancel_app_exit(), capture_sam_frame(), dashboard_hello(), dashboard_leave(), detection_preview_active(), embed_captured_face() (+12 more)

### Community 22 - "run_high_end_boot"
Cohesion: 0.13
Nodes (19): get_lan_ip(), _catalog_import_job(), _catalog_progress(), images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding() (+11 more)

### Community 24 - "applyFaceStatus"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 26 - "analyze_object_areas.py"
Cohesion: 0.19
Nodes (19): tqdm, _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace (+11 more)

### Community 27 - "EarlyStopHook"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "setup_db.py"
Cohesion: 0.22
Nodes (9): inventory_app_config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), psycopg, sqlite3 (+1 more)

### Community 29 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 31 - "runBrowserFaceLoop"
Cohesion: 0.22
Nodes (10): applyLocalFace(), drawMediaPipeLandmarks(), faceCoverage(), faceReady(), faceSpan(), pointInGate(), runBrowserFaceLoop(), startBrowserFaceLandmarker() (+2 more)

### Community 32 - "_exit_app"
Cohesion: 0.33
Nodes (7): _clear_session_movements(), _exit_app(), _force_close(), shutdown_event(), stop_camera(), clear_sessions(), on_event

### Community 33 - "V2DatasetMapper"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 34 - ".__init__"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 35 - "updateTriggerStatus"
Cohesion: 0.28
Nodes (9): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showFrozenDetectionPreview(), startObjectRecognition() (+1 more)

### Community 37 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 38 - "bootstrap_database"
Cohesion: 0.25
Nodes (8): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), ensure_postgres_running(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only., _run()

### Community 39 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.08
Nodes (23): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, C. Generate training embeddings with OpenCLIP, D. Development mode: prediction and evaluation (+15 more)

### Community 40 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 41 - "analyzeLocalFrame"
Cohesion: 0.33
Nodes (7): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo()

### Community 42 - "setFaceHint"
Cohesion: 0.38
Nodes (7): enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), refreshCameraList(), setFaceHint(), startLocalCamera()

### Community 43 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 44 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 45 - "applyMode"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

### Community 49 - "register_sam_embedding"
Cohesion: 0.18
Nodes (14): BaseModel, create_object_embedding(), FaceModeBody, generate_sam_mask(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), parse_yolo_boxes() (+6 more)

## Knowledge Gaps
- **65 isolated node(s):** `lastIdentifiedNames`, `inventoryItemNames`, `inventoryDisplayToOriginal`, `inventoryOriginalToDisplay`, `knownMovementIds` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 270 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `embed.py` to `eval.py`, `PETROSAINS inventory similarity (`test_pg`)`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `bbox_xyxy()` connect `PETROSAINS inventory similarity (`test_pg`)` to `eval.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `EpochMetricPrinter`, `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `lastIdentifiedNames`, `inventoryItemNames`, `inventoryDisplayToOriginal` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.04440333024976873 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06659619450317125 - nodes in this community are weakly interconnected._