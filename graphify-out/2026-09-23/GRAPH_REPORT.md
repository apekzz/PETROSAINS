# Graph Report - hilman_21Sep  (2026-09-23)

## Corpus Check
- 51 files · ~1,374,049 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 487 file(s) not represented in the graph (top: (none) 414, .ipynb 19, .pt 19)

## Summary
- 890 nodes · 1905 edges · 51 communities (45 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `18a757f4`
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
- analyze_object_areas.py
- tables
- sql.py
- analyzeLocalFrame
- dataset_importer.py
- backend/infer.py
- embed.py
- setup_db.py
- applyFaceStatus
- eval.py
- db.py
- post
- face_status_payload
- runBrowserFaceLoop
- EarlyStopHook
- fetchStats
- updateTriggerStatus
- PETROSAINS
- V2DatasetMapper
- .__init__
- export_table_snapshots
- ObjectTrainer
- utils_db/infer.py
- EpochMetricPrinter
- run_high_end_boot
- MosaicProb
- OneShot Inventory (`inventory_app`)
- visualize_results.py
- test_sahi.py
- apply_bce_dice_mask_loss
- saved_tables/README.md
- drive_folder
- _catalog_import_job
- inventory_app_config
- inventory_app_sam_tool
- bootstrap_database
- ensure_tables

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
- `main()` --calls--> `drive_folder()`  [EXTRACTED]
  export_train_official.py → utils/gdrive.py
- `run_high_end_boot()` --calls--> `get_lan_ip()`  [INFERRED]
  inventory_app/main.py → inventory_app/backend/config.py

## Import Cycles
- None detected.

## Communities (51 total, 6 thin omitted)

### Community 0 - "visualize.py"
Cohesion: 0.13
Nodes (30): collections_abc, colorsys, main(), Export the full train image catalog to train_official.parquet (no embeddings)., math, pil, build_embedding_dataframe(), _class_key() (+22 more)

### Community 1 - "pathlib"
Cohesion: 0.14
Nodes (26): dataclasses, numpy, pathlib, pgvector_psycopg, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1). (+18 more)

### Community 2 - "sam_tool.py"
Cohesion: 0.14
Nodes (18): base64, collections, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), _get_session() (+10 more)

### Community 3 - "dashboard.js"
Cohesion: 0.04
Nodes (47): applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace (+39 more)

### Community 4 - "evaluate_embedding_similarity.py"
Cohesion: 0.12
Nodes (28): datetime, platform, build_samples(), canonical_name(), classification_metrics(), inventory_name_from_filename(), load_catalog(), main() (+20 more)

### Community 5 - "main.py"
Cohesion: 0.08
Nodes (39): asyncio, delete, fastapi_middleware_cors, fastapi_responses, infer, boot_status(), camera_status(), _cancel_app_exit() (+31 more)

### Community 6 - "get_db"
Cohesion: 0.14
Nodes (25): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_movements(), get_staff_list() (+17 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.14
Nodes (30): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_trigger_state() (+22 more)

### Community 8 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 9 - "face.py"
Cohesion: 0.12
Nodes (21): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+13 more)

### Community 10 - "download_dataset.py"
Cohesion: 0.10
Nodes (25): get_lan_ip(), _bar(), finish(), set_progress(), start(), _width(), json, shutil (+17 more)

### Community 11 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.08
Nodes (23): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, C. Generate training embeddings with OpenCLIP, D. Development mode: prediction and evaluation (+15 more)

### Community 12 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 13 - "analyze_object_areas.py"
Cohesion: 0.17
Nodes (20): argparse, tqdm, _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms() (+12 more)

### Community 14 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 15 - "sql.py"
Cohesion: 0.11
Nodes (23): contextlib, check_db(), close_boot_connection(), connect_and_prepare(), _embedding_from_text(), ensure_postgres_running(), ensure_schema_columns(), fetch_inventory_embeddings() (+15 more)

### Community 16 - "analyzeLocalFrame"
Cohesion: 0.18
Nodes (17): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), blobToBase64(), captureReadyFace(), drawLandmarks(), grabLocalFrame(), grabSegmentedFace() (+9 more)

### Community 17 - "dataset_importer.py"
Cohesion: 0.11
Nodes (34): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+26 more)

### Community 18 - "backend/infer.py"
Cohesion: 0.08
Nodes (26): cv2, crop_bgr(), crop_masked_bgr(), load_model(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from…, Tight object cutout using the predicted segmentation polygon., Run the v2 segmentation model. Same call shape as the notebook. (+18 more)

### Community 19 - "embed.py"
Cohesion: 0.14
Nodes (27): pandas, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights() (+19 more)

### Community 20 - "setup_db.py"
Cohesion: 0.20
Nodes (10): config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), os, psycopg (+2 more)

### Community 21 - "applyFaceStatus"
Cohesion: 0.24
Nodes (15): applyFaceStatus(), captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup() (+7 more)

### Community 22 - "eval.py"
Cohesion: 0.14
Nodes (29): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), embed_split_crops(), evaluate_rule() (+21 more)

### Community 23 - "db.py"
Cohesion: 0.16
Nodes (20): get_item_summary(), Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), _embedding_to_text(), fetch_item_summary(), get_staff(), insert_check_in_out(), insert_staff() (+12 more)

### Community 24 - "post"
Cohesion: 0.15
Nodes (19): BaseModel, sam_status(), api_start_camera(), capture_sam_frame(), FaceModeBody, generate_sam_mask(), get_sam_status(), post_face_clear() (+11 more)

### Community 25 - "face_status_payload"
Cohesion: 0.11
Nodes (22): analyze_face_frame(), _apply_face_embedding(), cosine_similarity(), detection_preview_active(), embed_captured_face(), _encode_image(), _encode_images(), _encode_worker_loop() (+14 more)

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

### Community 33 - "export_table_snapshots"
Cohesion: 0.33
Nodes (6): clear_staff_embeddings(), _copy_table_to_file(), export_table_snapshots(), _export(), Export supported application tables to atomic CSV snapshots. only: optional…, Wipe enrolled faces every boot. Also clear staff.csv so restore cannot revive…

### Community 34 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 35 - "utils_db/infer.py"
Cohesion: 0.18
Nodes (14): matplotlib, matplotlib_patches, crop_labeled_objects(), Image, Crop each labeled object from ``image`` and attach bbox metadata., _color_for_name(), draw_predictions(), predict_labeled_image() (+6 more)

### Community 36 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 37 - "run_high_end_boot"
Cohesion: 0.22
Nodes (11): images_to_embeddings(), load_embed_model(), load_face_gate(), load_model(), queue_face_embedding(), Load MobileCLIP2 once on a dedicated encode thread and keep it there., Encode on the CLIP thread without blocking the API., run_high_end_boot() (+3 more)

### Community 38 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 39 - "OneShot Inventory (`inventory_app`)"
Cohesion: 0.50
Nodes (3): Layout, OneShot Inventory (`inventory_app`), Run

### Community 40 - "visualize_results.py"
Cohesion: 0.31
Nodes (12): csv, matplotlib_pyplot, canonical(), confusion_matrix(), label_bars(), latency_breakdown(), load_predictions(), main() (+4 more)

### Community 44 - "drive_folder"
Cohesion: 0.29
Nodes (9): google_colab, re, drive_folder(), _looks_like_dataset(), Path, Google Drive path helpers for local Drive Desktop and Colab., Resolve a Windows .lnk (Google Drive shortcuts show up this way)., Find a Drive folder, including Shared-with-me shortcuts saved as .lnk. (+1 more)

### Community 45 - "_catalog_import_job"
Cohesion: 0.28
Nodes (9): _catalog_import_job(), _catalog_progress(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), match_inventory_name(), parse_yolo_boxes(), refresh_inventory_catalog_cache() (+1 more)

### Community 49 - "bootstrap_database"
Cohesion: 0.33
Nodes (6): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only.

### Community 50 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

## Knowledge Gaps
- **72 isolated node(s):** `format`, `exported_at`, `file`, `columns`, `rows` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 298 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `embed.py` to `pathlib`, `PETROSAINS inventory similarity (`test_pg`)`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `bbox_xyxy()` connect `PETROSAINS inventory similarity (`test_pg`)` to `visualize.py`, `utils_db/infer.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`, `EpochMetricPrinter`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `format`, `exported_at`, `file` to the rest of the system?**
  _72 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `visualize.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13446969696969696 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.13548387096774195 - nodes in this community are weakly interconnected._