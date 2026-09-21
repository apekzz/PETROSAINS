# Graph Report - PETROSAINS  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 813 nodes · 1798 edges · 49 communities (46 shown, 3 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 60 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0b0e430f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 27 edges
2. `PgConfig` - 19 edges
3. `load_image_and_label()` - 16 edges
4. `connect_and_prepare()` - 14 edges
5. `predict_labeled_image()` - 14 edges
6. `drive_folder()` - 14 edges
7. `run_high_end_boot()` - 14 edges
8. `get_image_embedding()` - 14 edges
9. `camera_capture_loop()` - 14 edges
10. `crop_labeled_objects()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `embed_split_crops()` --calls--> `get_image_embedding()`  [EXTRACTED]
  utils_db/eval.py → utils/embed.py
- `main()` --calls--> `predict_labeled_image()`  [EXTRACTED]
  test_pg/predict_labeled_image.py → utils_db/infer.py
- `predict_labeled_image()` --calls--> `get_image_embedding()`  [EXTRACTED]
  utils_db/infer.py → utils/embed.py
- `main()` --calls--> `build_embedding_dataframe()`  [EXTRACTED]
  export_train_official.py → utils/dataset.py
- `main()` --calls--> `drive_folder()`  [EXTRACTED]
  test_pg/embed_train_official.py → utils/gdrive.py

## Import Cycles
- None detected.

## Communities (49 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (39): bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, btnCatalogClose, btnHeaderRegisterFace, btnImportCatalog (+31 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (34): cv2, _align_template(), choose_staff_match(), crop_from_box(), draw_landmarks(), encode_crop(), ensure_face_model(), face_in_region() (+26 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (35): datetime, json, platform, build_samples(), canonical_name(), classification_metrics(), inventory_name_from_filename(), load_catalog() (+27 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (33): asyncio, delete, fastapi_middleware_cors, fastapi_responses, boot_status(), camera_status(), catalog_import_active(), catalog_import_status() (+25 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (27): pandas, main(), Embed every labeled crop from train_official.parquet and save the results., build_embedding_df(), ClipEmbedder, _download_yolo11n_seg(), embed_from_dataframe(), _find_weights() (+19 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (29): arm_object_detection(), camera_capture_loop(), detection_labels(), draw_yolo_boxes(), encode_jpeg(), face_detection_active(), get_trigger_state(), ingest_browser_scan() (+21 more)

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (27): Series, apply_vote_rule(), average_top_n(), classification_metrics(), collect_split_votes(), embed_query_crops(), evaluate_rule(), _global_mean_sim() (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (24): argparse, pgvector_psycopg, sys, main(), parse_args(), Namespace, Classify labeled objects in one image against the pgvector catalog (Rule 1)., ensure_container() (+16 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (26): collections_abc, colorsys, math, numpy, pil, tqdm, bbox_xyxy(), build_embedding_dataframe() (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (25): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_item_summary(), get_movements() (+17 more)

### Community 10 - "Community 10"
Cohesion: 0.19
Nodes (21): calculateTransform(), captureFrozenFrame(), endStroke(), exportMask(), generateMask(), loadSourceCanvas(), maskBytes(), normalizeMask() (+13 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (23): Compatibility wrappers. All SQL lives in sql.py., clear_check_in_out(), _embedding_from_text(), _embedding_to_text(), fetch_inventory_embeddings(), fetch_item_summary(), fetch_staff_embeddings(), get_db() (+15 more)

### Community 12 - "Community 12"
Cohesion: 0.13
Nodes (20): contextlib, check_db(), close_boot_connection(), connect_and_prepare(), _copy_table_to_file(), ensure_schema_columns(), export_table_snapshots(), _export() (+12 more)

### Community 13 - "Community 13"
Cohesion: 0.10
Nodes (19): copy, detectron2, detectron2_config, detectron2_data, detectron2_data_datasets, detectron2_engine, detectron2_engine_hooks, detectron2_engine_train_loop (+11 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (20): matplotlib, matplotlib_patches, crop_labeled_objects(), load_image_and_label(), Image, Crop each labeled object from ``image`` and attach bbox metadata., Load one image and its YOLO label. Specify the file with ``image_path=``, or an…, embed_split_crops() (+12 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (19): base64, collections, create_mask(), create_masked_crop(), create_session(), _decode_data_url(), _decode_image_bytes(), discard_session() (+11 more)

### Community 16 - "Community 16"
Cohesion: 0.10
Nodes (19): columns, file, rows, exported_at, format, columns, file, rows (+11 more)

### Community 17 - "Community 17"
Cohesion: 0.15
Nodes (16): dataclasses, main(), Export the full train image catalog to train_official.parquet (no embeddings)., google_colab, pathlib, re, PostgreSQL / pgvector connection settings., drive_folder() (+8 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (16): Tensor, torch, torch_nn_functional, Label-aware Ultralytics train() kwargs. Aggressive geometry (mosaic, mixup,…, apply_bce_dice_mask_loss(), apply_dice_mask_loss(), bce_dice_single_mask_loss(), dice_single_mask_loss() (+8 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (13): get_lan_ip(), _bar(), fail(), finish(), pulse(), set_progress(), start(), _width() (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.22
Nodes (15): choose_folder(), import_train_catalog(), inventory_name_from_filename(), masked_crops(), _polygon_rows(), Image, ndarray, Path (+7 more)

### Community 21 - "Community 21"
Cohesion: 0.18
Nodes (16): analyze_face_frame(), api_start_camera(), capture_sam_frame(), detection_preview_active(), embed_captured_face(), _face_detect_job(), face_status_payload(), get_face_status() (+8 more)

### Community 22 - "Community 22"
Cohesion: 0.16
Nodes (15): _catalog_import_job(), _catalog_progress(), cosine_similarity(), create_object_embedding(), get_inventory_catalog(), image_to_embedding(), images_to_embeddings(), load_embed_model() (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.29
Nodes (14): _copy_tree(), download_dataset(), _drive_folder(), _iter_files(), _looks_like_dataset(), main(), parse_args(), Namespace (+6 more)

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (14): applyFaceStatus(), blobToBase64(), captureReadyFace(), grabSegmentedFace(), hasCapturedRegisterFace(), openRegisterPopup(), pollFaceStatus(), sendSegmentedEmbed() (+6 more)

### Community 25 - "Community 25"
Cohesion: 0.31
Nodes (12): csv, matplotlib_pyplot, canonical(), confusion_matrix(), label_bars(), latency_breakdown(), load_predictions(), main() (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.32
Nodes (12): _areas_from_label(), collect_split_areas(), _image_size(), main(), parse_args(), plot_histograms(), Namespace, ndarray (+4 more)

### Community 27 - "Community 27"
Cohesion: 0.22
Nodes (5): HookBase, CloseMosaicHook, EarlyStopHook, MLflowHook, YOLO-style patience on val mask AP50 (one eval = one epoch).

### Community 28 - "Community 28"
Cohesion: 0.20
Nodes (10): inventory_app_config, ensure_database(), ensure_postgres_running(), Create the Postgres role/database, tables, and optional SQLite import., Create role + database if this machine can admin Postgres locally., _run(), os, psycopg (+2 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (11): animateValue(), fetchSelectedItemStats(), fetchStats(), loadItemOptions(), pollCatalogImport(), renderCatalogImport(), renderItemOptions(), selectInventoryItem() (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (10): BaseModel, FaceModeBody, generate_sam_mask(), post_face_register(), register_sam_embedding(), _register_staff_face(), SamMaskBody, SamRegisterBody (+2 more)

### Community 31 - "Community 31"
Cohesion: 0.22
Nodes (10): applyLocalFace(), drawMediaPipeLandmarks(), faceCoverage(), faceReady(), faceSpan(), pointInGate(), runBrowserFaceLoop(), startBrowserFaceLandmarker() (+2 more)

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (10): _cancel_app_exit(), _clear_session_movements(), dashboard_hello(), dashboard_leave(), _exit_app(), _force_close(), _maybe_exit_after_leave(), shutdown_event() (+2 more)

### Community 33 - "Community 33"
Cohesion: 0.29
Nodes (7): _ensure_bbox_mode(), _hsv_jitter(), ndarray, YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4., _resize_record(), _shift_annos(), V2DatasetMapper

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (5): AMPTrainer, ClsGainWrapper, ModernAMPTrainer, Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every…, Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking…

### Community 35 - "Community 35"
Cohesion: 0.28
Nodes (9): applyObjectRecognitionState(), escapeHtml(), fetchInventory(), renderMovements(), renderRecognized(), restoreLiveDetectionStream(), showFrozenDetectionPreview(), startObjectRecognition() (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.28
Nodes (9): _apply_face_embedding(), _encode_image(), _encode_images(), _encode_worker_loop(), face_crop_to_embedding(), _face_embed_worker(), _load_clip_weights(), _prepare_embed_image() (+1 more)

### Community 37 - "Community 37"
Cohesion: 0.25
Nodes (3): DefaultTrainer, ObjectTrainer, Same Detectron2 loop, plus YOLO-style patience.

### Community 38 - "Community 38"
Cohesion: 0.25
Nodes (8): init_schema(), Boot helper — create missing tables only. Never seeds or overwrites., bootstrap_database(), ensure_database(), ensure_postgres_running(), Create the oneshot role and oneshot_inventory database if they are missing., Called from main.py boot. Starts Postgres, creates missing DB/tables only., _run()

### Community 39 - "Community 39"
Cohesion: 0.29
Nodes (7): pickle, load_query_objects(), Path, Save and reload cropped-object embeddings (val cache, etc.)., Write ``objects`` to a pickle using a temp file so a crash cannot leave 0 bytes., Load objects previously written by ``save_query_objects``., save_query_objects()

### Community 40 - "Community 40"
Cohesion: 0.29
Nodes (3): CommonMetricPrinter, EpochMetricPrinter, Detectron2 is iter-based; print the matching YOLO-style epoch next to iter.

### Community 41 - "Community 41"
Cohesion: 0.33
Nodes (7): analyzeLocalFrame(), applyCapturedPhoto(), base64JpegToBlob(), drawLandmarks(), grabLocalFrame(), ingestScanFrame(), sizeOverlayToVideo()

### Community 42 - "Community 42"
Cohesion: 0.38
Nodes (7): enableCaptureFallback(), isLoopbackHost(), isPhoneDevice(), needsCaptureFallback(), refreshCameraList(), setFaceHint(), startLocalCamera()

### Community 43 - "Community 43"
Cohesion: 0.33
Nodes (5): ensure_tables(), _apply(), existing_tables(), Create only required tables that are not already in the database., table_status()

### Community 44 - "Community 44"
Cohesion: 0.33
Nodes (3): setter, MosaicProb, Process-shared mosaic probability so close_mosaic works with DataLoader workers.

### Community 45 - "Community 45"
Cohesion: 0.67
Nodes (3): applyMode(), loadCurrentMode(), setMode()

## Knowledge Gaps
- **49 isolated node(s):** `bootFill`, `bootOverlay`, `bootPct`, `bootStage`, `bootStartedAt` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 251 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ObjectTrainer` connect `Community 37` to `Community 40`, `Community 34`, `Community 27`, `Community 13`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `EpochMetricPrinter` connect `Community 40` to `Community 13`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `MosaicProb` connect `Community 44` to `Community 34`, `Community 27`, `Community 13`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PgConfig` (e.g. with `collect_split_votes()` and `predict_split()`) actually correct?**
  _`PgConfig` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `bootFill`, `bootOverlay`, `bootPct` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.04440333024976873 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06765327695560254 - nodes in this community are weakly interconnected._