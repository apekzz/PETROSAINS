# Graph Report - PETROSAINS  (2026-09-21)

## Corpus Check
- 49 files · ~1,372,237 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 486 file(s) not represented in the graph (top: (none) 413, .ipynb 19, .pt 19)

## Summary
- 864 nodes · 1884 edges · 49 communities (45 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 67 edges (avg confidence: 0.87)
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
- saved_tables/README.md
- api.py
- sam-tool.js
- db.py
- sql.py
- detectron2_recipe.py
- _apply_face_embedding
- pathlib
- tables
- download_dataset.py
- inventory_app/infer.py
- run_high_end_boot
- dataset_importer.py
- post
- sam_tool.py
- visualize.py
- captureReadyFace
- utils_db/infer.py
- analyze_object_areas.py
- EarlyStopHook
- setup_db.py
- fetchStats
- visualize_results.py
- runBrowserFaceLoop
- crop_labeled_objects
- V2DatasetMapper
- .__init__
- applyFaceStatus
- ObjectTrainer
- bootstrap_database
- PETROSAINS inventory similarity (`test_pg`)
- EpochMetricPrinter
- analyzeLocalFrame
- setFaceHint
- ensure_tables
- MosaicProb
- test_sahi.py
- apply_bce_dice_mask_loss
- register_sam_embedding
- drive_folder

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 28 edges
2. `PgConfig` - 19 edges
3. `load_image_and_label()` - 16 edges
4. `connect_and_prepare()` - 15 edges
5. `applyFaceStatus()` - 14 edges
6. `camera_capture_loop()` - 14 edges
7. `run_high_end_boot()` - 14 edges
8. `get_image_embedding()` - 14 edges
9. `drive_folder()` - 14 edges
10. `predict_labeled_image()` - 14 edges

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

## Communities (49 total, 4 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.04
Nodes (44): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace, btnImportCatalog (+36 more)

### Community 1 - "face.py"
Cohesion: 0.11
Nodes (22): _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region(), FaceGate (+14 more)

### Community 2 - "evaluate_embedding_similarity.py"
Cohesion: 0.22
Nodes (18): build_samples(), canonical_name(), classification_metrics(), inventory_name_from_filename(), load_catalog(), main(), make_masked_crop(), polygon_rows() (+10 more)

### Community 3 - "main.py"
Cohesion: 0.08
Nodes (41): asyncio, delete, fastapi_middleware_cors, fastapi_responses, boot_status(), camera_status(), _cancel_app_exit(), catalog_import_status() (+33 more)

### Community 4 - "embed.py"
Cohesion: 0.13
Nodes (29): dataclasses, pandas, main(), Embed every labeled crop from train_official.parquet and save the results., typing, build_embedding_df(), ClipEmbedder, _download_yolo11n_seg() (+21 more)

### Community 5 - "camera_capture_loop"
Cohesion: 0.12
Nodes (34): arm_object_detection(), camera_capture_loop(), catalog_import_active(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), ensure_object_detection_ready(), face_detection_active() (+26 more)

### Community 6 - "eval.py"
Cohesion: 0.16
Nodes (27): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), evaluate_rule(), _global_mean_sim() (+19 more)

### Community 7 - "PETROSAINS"
Cohesion: 0.18
Nodes (10): Daily use (after first setup), Files, Folders, How to run the inventory app, PETROSAINS, Root layout, Steps, `test_pg/` (similarity pipeline) (+2 more)

### Community 9 - "api.py"
Cohesion: 0.14
Nodes (22): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+14 more)

### Community 10 - "sam-tool.js"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 11 - "db.py"
Cohesion: 0.17
Nodes (23): Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), _embedding_from_text(), _embedding_to_text(), fetch_inventory_embeddings(), fetch_item_summary(), fetch_staff_embeddings(), get_db() (+15 more)

### Community 12 - "sql.py"
Cohesion: 0.13
Nodes (20): contextlib, check_db(), close_boot_connection(), connect_and_prepare(), ensure_postgres_running(), ensure_schema_columns(), _lock(), _open_connection() (+12 more)

### Community 13 - "detectron2_recipe.py"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 14 - "_apply_face_embedding"
Cohesion: 0.18
Nodes (13): _apply_face_embedding(), _auto_arm_detection_after_face(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_detect_job(), _face_embed_worker() (+5 more)

### Community 15 - "pathlib"
Cohesion: 0.08
Nodes (45): argparse, datetime, json, numpy, pathlib, pgvector_psycopg, platform, sys (+37 more)

### Community 16 - "tables"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 17 - "download_dataset.py"
Cohesion: 0.29
Nodes (14): _copy_tree(), download_dataset(), _drive_folder(), _iter_files(), _looks_like_dataset(), main(), parse_args(), Namespace (+6 more)

### Community 18 - "inventory_app/infer.py"
Cohesion: 0.08
Nodes (29): cv2, crop_bgr(), crop_masked_bgr(), load_model(), model_device(), parse_detections(), predict_frame(), YOLO11l-seg inference for OneShot inventory. Derived from… (+21 more)

### Community 19 - "run_high_end_boot"
Cohesion: 0.18
Nodes (13): get_lan_ip(), _bar(), fail(), finish(), pulse(), set_progress(), start(), _width() (+5 more)

### Community 20 - "dataset_importer.py"
Cohesion: 0.24
Nodes (14): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+6 more)

### Community 21 - "post"
Cohesion: 0.13
Nodes (23): BaseModel, analyze_face_frame(), api_start_camera(), capture_sam_frame(), detection_preview_active(), embed_captured_face(), face_status_payload(), FaceModeBody (+15 more)

### Community 22 - "sam_tool.py"
Cohesion: 0.15
Nodes (19): base64, collections, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), discard_session() (+11 more)

### Community 23 - "visualize.py"
Cohesion: 0.18
Nodes (23): collections_abc, colorsys, math, build_embedding_dataframe(), _class_key(), _class_names_for_image(), load_image_and_label(), DataFrame (+15 more)

### Community 24 - "captureReadyFace"
Cohesion: 0.33
Nodes (9): blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), sendSegmentedEmbed(), setRegisterProgress(), showRegisterModal(), submitFaceRegister() (+1 more)

### Community 25 - "utils_db/infer.py"
Cohesion: 0.18
Nodes (14): matplotlib, matplotlib_patches, pil, pick_query_image(), _color_for_name(), draw_predictions(), predict_labeled_image(), DataFrame (+6 more)

### Community 26 - "analyze_object_areas.py"
Cohesion: 0.32
Nodes (12): _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace, ndarray (+4 more)

### Community 27 - "EarlyStopHook"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "setup_db.py"
Cohesion: 0.15
Nodes (13): get_stats(), inventory_app_config, ensure_database(), ensure_postgres_running(), migrate_sqlite_inventory(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run() (+5 more)

### Community 29 - "fetchStats"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 30 - "visualize_results.py"
Cohesion: 0.31
Nodes (12): csv, matplotlib_pyplot, canonical(), confusion_matrix(), label_bars(), latency_breakdown(), load_predictions(), main() (+4 more)

### Community 31 - "runBrowserFaceLoop"
Cohesion: 0.20
Nodes (12): applyLocalFace(), drawMediaPipeLandmarks(), faceCenteredInGate(), faceCentroid(), faceCoverage(), faceReady(), faceSpan(), pointInGate() (+4 more)

### Community 32 - "crop_labeled_objects"
Cohesion: 0.25
Nodes (8): C. Generate training embeddings with OpenCLIP, bbox_xyxy(), crop_labeled_objects(), Image, Axis-aligned crop box from a YOLO box or polygon label., Crop each labeled object from ``image`` and attach bbox metadata., embed_split_crops(), Embed every labeled crop in ``split``. Reuses a preloaded OpenCLIP model.

### Community 33 - "V2DatasetMapper"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 34 - ".__init__"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 35 - "applyFaceStatus"
Cohesion: 0.20
Nodes (14): applyFaceStatus(), applyMode(), applyObjectRecognitionState(), ensureObjectRecognitionArmed(), escapeHtml(), fetchInventory(), loadCurrentMode(), pollFaceStatus() (+6 more)

### Community 37 - "ObjectTrainer"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 38 - "bootstrap_database"
Cohesion: 0.14
Nodes (14): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., startup_event(), bootstrap_database(), clear_staff_embeddings(), _copy_table_to_file(), ensure_database(), export_table_snapshots() (+6 more)

### Community 39 - "PETROSAINS inventory similarity (`test_pg`)"
Cohesion: 0.10
Nodes (20): pickle, 1. Start Postgres with Docker, 2. Load catalog vectors into pgvector, 3. Evaluate on val / test, A. Dataset and Google Drive, B. Extract inventory as a catalog parquet, D. Development mode: prediction and evaluation, E. Predict one image (`predict_labeled_image.py`) (+12 more)

### Community 40 - "EpochMetricPrinter"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 41 - "analyzeLocalFrame"
Cohesion: 0.24
Nodes (10): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), showCaptureAlert(), sizeOverlayToVideo() (+2 more)

### Community 42 - "setFaceHint"
Cohesion: 0.26
Nodes (12): captureButtonLabel(), enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), openNativeCamera(), openRegisterPopup(), preferredCameraFacing() (+4 more)

### Community 43 - "ensure_tables"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 44 - "MosaicProb"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 49 - "register_sam_embedding"
Cohesion: 0.16
Nodes (16): _catalog_import_job(), _catalog_progress(), cosine_similarity(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), images_to_embeddings(), load_embed_model() (+8 more)

### Community 50 - "drive_folder"
Cohesion: 0.20
Nodes (13): main(), Export the full train image catalog to train_official.parquet (no embeddings)., google_colab, re, drive_folder(), _looks_like_dataset(), Path, Google Drive path helpers for local Drive Desktop and Colab. (+5 more)

## Knowledge Gaps
- **70 isolated node(s):** `lastIdentifiedNames`, `inventoryItemNames`, `inventoryDisplayToOriginal`, `inventoryOriginalToDisplay`, `knownMovementIds` (+65 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 279 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load_clip_model()` connect `embed.py` to `PETROSAINS inventory similarity (`test_pg`)`, `pathlib`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `bbox_xyxy()` connect `crop_labeled_objects` to `visualize.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `ObjectTrainer` connect `ObjectTrainer` to `EpochMetricPrinter`, `.__init__`, `EarlyStopHook`, `detectron2_recipe.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `lastIdentifiedNames`, `inventoryItemNames`, `inventoryDisplayToOriginal` to the rest of the system?**
  _70 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03996983408748114 - nodes in this community are weakly interconnected._
- **Should `face.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11083743842364532 - nodes in this community are weakly interconnected._