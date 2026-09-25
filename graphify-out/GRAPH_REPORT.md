# Graph Report - main  (2026-09-22)

## Corpus Check
- 12 files · ~234,949 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 25 file(s) not represented in the graph (top: .ipynb 13, (none) 5, .pt 3)

## Summary
- 154 nodes · 287 edges · 15 communities (12 shown, 3 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a9afed3e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dashboard.js
- api.py
- main.py
- config.py
- loader.py
- get
- db.py
- camera_capture_loop
- run_backend_capture
- startup_event
- set_yolo_overlay
- log_yolo_detections
- README.md

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 13 edges
2. `camera_capture_loop()` - 10 edges
3. `run_high_end_boot()` - 10 edges
4. `run_backend_capture()` - 8 edges
5. `fetch_inventory()` - 7 edges
6. `init_schema()` - 6 edges
7. `record_yolo_capture()` - 6 edges
8. `set_yolo_overlay()` - 6 edges
9. `create_object_embedding()` - 6 edges
10. `normalize_item_name()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `run_high_end_boot()` --calls--> `fail()`  [EXTRACTED]
  inventory_app/main.py → inventory_app/boot/loader.py
- `run_high_end_boot()` --calls--> `pulse()`  [EXTRACTED]
  inventory_app/main.py → inventory_app/boot/loader.py
- `run_high_end_boot()` --calls--> `get_lan_ip()`  [EXTRACTED]
  inventory_app/main.py → inventory_app/config.py
- `parse_yolo_boxes()` --calls--> `normalize_item_name()`  [EXTRACTED]
  inventory_app/main.py → inventory_app/database/db.py
- `startup_event()` --calls--> `init_schema()`  [EXTRACTED]
  inventory_app/main.py → inventory_app/database/db.py

## Import Cycles
- None detected.

## Communities (15 total, 3 thin omitted)

### Community 0 - "dashboard.js"
Cohesion: 0.10
Nodes (27): animateValue(), applyMode(), bootFill, bootOverlay, bootPct, bootStage, bootStartedAt, cameraFeed (+19 more)

### Community 1 - "api.py"
Cohesion: 0.14
Nodes (26): fastapi, get_detections(), get_detections_summary(), get_detections_today(), get_inventory(), get_item(), get_stats(), get (+18 more)

### Community 2 - "main.py"
Cohesion: 0.13
Nodes (15): collections, cv2, datetime, fastapi_middleware_cors, fastapi_responses, generate_frames(), make_error_frame(), video_feed() (+7 more)

### Community 3 - "config.py"
Cohesion: 0.40
Nodes (3): get_lan_ip(), os, socket

### Community 4 - "loader.py"
Cohesion: 0.24
Nodes (12): _bar(), fail(), finish(), pulse(), set_progress(), start(), _width(), run_high_end_boot() (+4 more)

### Community 5 - "get"
Cohesion: 0.25
Nodes (9): check_db(), boot_status(), camera_status(), db_status(), get_trigger_state(), get, serve_dashboard(), serve_frontend_file() (+1 more)

### Community 6 - "db.py"
Cohesion: 0.14
Nodes (17): config, contextlib, apply_capture_to_inventory(), _get_item_by_name(), normalize_item_name(), Log YOLO classes and upsert them into inventory. grouped: {class_name:…, record_yolo_capture(), save_object_embedding() (+9 more)

### Community 7 - "camera_capture_loop"
Cohesion: 0.38
Nodes (7): camera_capture_loop(), open_camera(), Rebuild MOG2 after camera open / reconnect., reset_background_subtractor(), set_trigger_state(), significant_change(), start_camera()

### Community 8 - "run_backend_capture"
Cohesion: 0.25
Nodes (9): _box_iou(), maybe_start_yolo_preview(), _nms_detections(), parse_yolo_boxes(), predict_frame(), Keep the highest-confidence box when two overlap (same item)., Run YOLO + DB log without blocking the MJPEG camera thread., run_backend_capture() (+1 more)

### Community 9 - "startup_event"
Cohesion: 0.40
Nodes (5): load_model(), shutdown_event(), startup_event(), stop_camera(), on_event

### Community 10 - "set_yolo_overlay"
Cohesion: 0.50
Nodes (5): detection_labels(), draw_yolo_boxes(), encode_jpeg(), format_confidence(), set_yolo_overlay()

### Community 11 - "log_yolo_detections"
Cohesion: 0.50
Nodes (4): get_detection_mode(), get_mode(), log_yolo_detections(), Insert one detections row per class found in this capture. New classes are…

## Knowledge Gaps
- **9 isolated node(s):** `lastIdentifiedNames`, `cameraFeed`, `cameraStatus`, `bootOverlay`, `bootStage` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 44 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_high_end_boot()` connect `loader.py` to `main.py`, `config.py`, `get`, `camera_capture_loop`, `startup_event`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `create_object_embedding()` connect `db.py` to `main.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `record_yolo_capture()` connect `db.py` to `api.py`, `main.py`, `log_yolo_detections`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `camera_capture_loop()` (e.g. with `run_backend_capture()` and `start_camera()`) actually correct?**
  _`camera_capture_loop()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `lastIdentifiedNames`, `cameraFeed`, `cameraStatus` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dashboard.js` be split into smaller, more focused modules?**
  _Cohesion score 0.10114942528735632 - nodes in this community are weakly interconnected._
- **Should `api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13756613756613756 - nodes in this community are weakly interconnected._