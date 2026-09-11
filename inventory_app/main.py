import os
import sys
import time
import threading
import platform
from collections import defaultdict
from datetime import datetime
from io import BytesIO

import cv2
import numpy as np
import torch
from ultralytics import YOLO

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import router as api_router
import loader
from db import init_schema, record_yolo_capture, normalize_item_name, check_db, save_object_embedding
from config import (
    BASE_DIR, HOST, PORT, CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    TARGET_FPS, JPEG_QUALITY, MODEL_PATH, MODEL_CONFIDENCE, MODEL_IMAGE_SIZE,
    TRIGGER_ENABLED, CHANGE_AREA_PERCENT, SETTLE_FRAMES,
    TRIGGER_COOLDOWN, MOG2_HISTORY, MOG2_VAR_THRESHOLD, MOG2_DETECT_SHADOWS,
    WARMUP_FRAMES, YOLO_PREVIEW_ENABLED, YOLO_PREVIEW_INTERVAL, YOLO_HOLD_SECONDS,
    get_lan_ip,
)


# ============================================================
# APP
# ============================================================

app = FastAPI(title="OneShot Inventory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


# ============================================================
# AI MODEL (loaded during high-end boot, not at import)
# ============================================================

model = None
MODEL_DEVICE = "cpu"

embed_model = None
embed_backend = None
embed_lock = threading.Lock()
EMBEDDING_SIZE = 512


def load_model():
    global model, MODEL_DEVICE
    if model is not None:
        return
    model = YOLO(MODEL_PATH)
    MODEL_DEVICE = 0 if torch.cuda.is_available() else "cpu"


def load_embed_model():
    """CLIP (512-d) with ResNet50 pooled-to-512 fallback."""
    global embed_model, embed_backend
    if embed_model is not None:
        return
    with embed_lock:
        if embed_model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            embed_model = SentenceTransformer("clip-ViT-B-32")
            embed_backend = "clip"
            print("[EMBED] Loaded CLIP clip-ViT-B-32 (512-d)")
            return
        except Exception as exc:
            print("[EMBED] CLIP unavailable, using ResNet50 fallback:", exc)

        from torchvision.models import resnet50, ResNet50_Weights
        backbone = resnet50(weights=ResNet50_Weights.DEFAULT)
        backbone.fc = torch.nn.Identity()
        backbone.eval()
        embed_model = backbone
        embed_backend = "resnet50"
        print("[EMBED] Loaded ResNet50 without final layer (pooled to 512-d)")


def image_to_embedding(image_bytes):
    from PIL import Image

    load_embed_model()
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    if embed_backend == "clip":
        vector = embed_model.encode(image, convert_to_numpy=True)
        vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    else:
        from torchvision import transforms
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])
        tensor = preprocess(image).unsqueeze(0)
        with torch.no_grad():
            features = embed_model(tensor).squeeze().cpu().numpy().astype(np.float32)
        # ResNet50 is 2048-d after dropping fc; pool groups of 4 → 512
        vector = features.reshape(EMBEDDING_SIZE, -1).mean(axis=1)

    if vector.size != EMBEDDING_SIZE:
        raise ValueError(f"Expected {EMBEDDING_SIZE}-d embedding, got {vector.size}")
    return [float(value) for value in vector]



# ============================================================
# CAMERA GLOBAL VARIABLES
# ============================================================

camera = None
camera_lock = threading.Lock()
camera_thread = None
camera_running = False
latest_frame = None
camera_ok = False
camera_error = "Camera has not started."
scan_session = None
SCAN_OPERATOR = "System"

VALID_MODES = {"IN", "OUT", "SCAN"}
detection_mode = "SCAN"
detection_mode_lock = threading.Lock()

trigger_state = "WARMUP"
trigger_state_lock = threading.Lock()
bg_subtractor = None
last_capture = None
last_detections = 0
last_classes = []
cooldown_until = 0.0
inventory_revision = 0
inventory_revision_lock = threading.Lock()

model_lock = threading.Lock()
yolo_overlay_lock = threading.Lock()
yolo_boxes = []
yolo_labels = []
annotated_hold_jpeg = None
annotated_hold_until = 0.0
preview_pending = False
last_preview_at = 0.0

BOX_COLOR = (200, 212, 0)
LABEL_BG = (12, 21, 16)
TEXT_COLOR = (246, 240, 232)

boot_ready = False
boot_stage = "standby"
boot_percent = 0


# ============================================================
# MODE / TRIGGER HELPERS
# ============================================================

def get_detection_mode():
    with detection_mode_lock:
        return detection_mode


def set_trigger_state(new_state):
    global trigger_state
    with trigger_state_lock:
        trigger_state = new_state


def get_trigger_state():
    with trigger_state_lock:
        return trigger_state


def reset_background_subtractor():
    """Rebuild MOG2 after camera open / reconnect."""
    global bg_subtractor
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=MOG2_HISTORY,
        varThreshold=MOG2_VAR_THRESHOLD,
        detectShadows=MOG2_DETECT_SHADOWS,
    )
    set_trigger_state("WARMUP")
    print("[TRIGGER] Background subtractor reset. State = WARMUP")


def encode_jpeg(frame):
    encode_ok, encoded = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY],
    )
    if encode_ok:
        return encoded.tobytes()
    return None


def predict_frame(frame):
    with model_lock:
        return model.predict(
            source=frame,
            imgsz=MODEL_IMAGE_SIZE,
            conf=MODEL_CONFIDENCE,
            device=MODEL_DEVICE,
            verbose=False,
        )


def parse_yolo_boxes(results):
    if not results:
        return []
    result = results[0]
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return []

    xyxy = boxes.xyxy.cpu().numpy()
    confidences = boxes.conf.cpu().numpy()
    class_ids = boxes.cls.cpu().numpy()
    names = result.names if getattr(result, "names", None) else model.names

    detections = []
    for box, confidence, class_id in zip(xyxy, confidences, class_ids):
        x1, y1, x2, y2 = [int(value) for value in box]
        detections.append({
            "xyxy": (x1, y1, x2, y2),
            "confidence": float(confidence),
            "name": normalize_item_name(names[int(class_id)]),
        })
    return detections


def detection_labels(detections):
    return [
        f"{item['name']} {int(item['confidence'] * 100)}%"
        for item in detections
    ]


def draw_yolo_boxes(frame, detections):
    vis = frame.copy()
    for item in detections:
        x1, y1, x2, y2 = item["xyxy"]
        label = f"{item['name']} {int(item['confidence'] * 100)}%"
        cv2.rectangle(vis, (x1, y1), (x2, y2), BOX_COLOR, 2)

        (text_w, text_h), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        label_y = max(0, y1 - text_h - 8)
        cv2.rectangle(
            vis,
            (x1, label_y),
            (x1 + text_w + 10, label_y + text_h + baseline + 8),
            LABEL_BG,
            -1,
        )
        cv2.rectangle(
            vis,
            (x1, label_y),
            (x1 + text_w + 10, label_y + text_h + baseline + 8),
            BOX_COLOR,
            1,
        )
        cv2.putText(
            vis,
            label,
            (x1 + 5, label_y + text_h + 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            TEXT_COLOR,
            1,
            cv2.LINE_AA,
        )
    return vis


def set_yolo_overlay(detections, hold_frame=None, hold_seconds=0):
    global yolo_boxes, yolo_labels, annotated_hold_jpeg, annotated_hold_until
    labels = detection_labels(detections)
    hold_jpeg = None
    hold_until = 0.0
    if hold_frame is not None and detections and hold_seconds > 0:
        hold_jpeg = encode_jpeg(draw_yolo_boxes(hold_frame, detections))
        hold_until = time.monotonic() + hold_seconds
    with yolo_overlay_lock:
        yolo_boxes = detections
        yolo_labels = labels
        if hold_jpeg is not None:
            annotated_hold_jpeg = hold_jpeg
            annotated_hold_until = hold_until


def run_yolo_preview(frame):
    global preview_pending
    try:
        if model is None:
            return
        detections = parse_yolo_boxes(predict_frame(frame))
        set_yolo_overlay(detections)
    except Exception as exc:
        print("[YOLO] Preview error:", exc)
    finally:
        preview_pending = False


def maybe_start_yolo_preview(frame, state):
    global preview_pending, last_preview_at
    if not YOLO_PREVIEW_ENABLED or model is None:
        return
    if state in {"CAPTURING", "WARMUP"}:
        return
    with yolo_overlay_lock:
        holding = annotated_hold_jpeg and time.monotonic() < annotated_hold_until
    if holding:
        return
    now = time.monotonic()
    if now - last_preview_at < YOLO_PREVIEW_INTERVAL:
        return
    if preview_pending:
        return
    preview_pending = True
    last_preview_at = now
    threading.Thread(
        target=run_yolo_preview,
        args=(frame.copy(),),
        name="YoloPreview",
        daemon=True,
    ).start()


def significant_change(mask):
    total_pixels = mask.shape[0] * mask.shape[1]
    if total_pixels == 0:
        return False, 0.0
    non_zero_pixels = cv2.countNonZero(mask)
    change_percent = (non_zero_pixels / total_pixels) * 100.0
    return change_percent > CHANGE_AREA_PERCENT, change_percent


# ============================================================
# OPEN CAMERA
# ============================================================

def open_camera():
    global camera, camera_ok, camera_error

    if camera is not None:
        try:
            camera.release()
        except Exception:
            pass
        camera = None

    backend = cv2.CAP_AVFOUNDATION if sys.platform == "darwin" else cv2.CAP_ANY
    print(f"[CAMERA] Trying camera index {CAMERA_INDEX}...")

    try:
        camera = cv2.VideoCapture(CAMERA_INDEX, backend)
    except Exception as exc:
        camera = None
        camera_ok = False
        camera_error = f"Could not create VideoCapture: {exc}"
        print("[CAMERA]", camera_error)
        return False

    if camera is None or not camera.isOpened():
        camera_error = f"Camera index {CAMERA_INDEX} could not be opened."
        camera_ok = False
        print("[CAMERA]", camera_error)
        if camera is not None:
            try:
                camera.release()
            except Exception:
                pass
            camera = None
        return False

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, TARGET_FPS)

    print("[CAMERA] Warming up...")
    time.sleep(1.0)

    for _ in range(20):
        ok, frame = camera.read()
        if ok and frame is not None:
            if np.mean(frame) < 5.0:
                print("[CAMERA] WARNING: Frames are black. Check FaceTime/Zoom/Teams!")
            else:
                print("[CAMERA] Camera feed is live!")

            camera_ok = True
            camera_error = ""
            print(
                f"[CAMERA] Ready: "
                f"{int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))} x "
                f"{int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))}"
            )
            reset_background_subtractor()
            return True
        time.sleep(0.1)

    camera_error = "Camera opened, but frames could not be read."
    camera_ok = False
    print("[CAMERA]", camera_error)
    try:
        camera.release()
    except Exception:
        pass
    camera = None
    return False


# ============================================================
# YOLO DETECTION LOGGING + INVENTORY UPDATES
# ============================================================

def log_yolo_detections(results):
    """
    Insert one detections row per class found in this capture.
    New classes are added to inventory; IN / OUT update stock.
    Newest captured items stay at the top of the list.
    Never crash the camera.
    Returns (logged_count, class_names).
    """
    global inventory_revision
    try:
        if not results:
            return 0, []

        result = results[0]
        boxes = getattr(result, "boxes", None)
        if boxes is None or len(boxes) == 0:
            return 0, []

        class_ids = boxes.cls.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()
        names = result.names if getattr(result, "names", None) else model.names

        grouped = defaultdict(list)
        for class_id, confidence in zip(class_ids, confidences):
            class_name = names[int(class_id)]
            grouped[class_name].append(float(confidence))

        if not grouped:
            return 0, []

        mode = get_detection_mode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_id = scan_session or datetime.now().strftime("%Y%m%d_%H%M%S")
        class_names = list(grouped.keys())

        record_yolo_capture(
            grouped,
            mode,
            timestamp,
            session_id,
            SCAN_OPERATOR,
        )
        with inventory_revision_lock:
            inventory_revision += 1

        print(
            f"[DETECTION] Mode={mode} | Logged {len(class_names)} classes at {timestamp}"
        )
        return len(class_names), class_names

    except Exception as exc:
        print("[DB] Detection log error:", exc)
        return 0, []


# ============================================================
# BACKEND CAPTURE (YOLO off the live stream)
# ============================================================

def run_backend_capture(frame):
    """Run YOLO + DB log without blocking the MJPEG camera thread."""
    global last_capture, last_detections, last_classes, cooldown_until

    try:
        results = predict_frame(frame)
        detections = parse_yolo_boxes(results)
        logged_count, class_names = log_yolo_detections(results)
        last_capture = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_detections = logged_count
        last_classes = class_names
        set_yolo_overlay(detections)
    except Exception as exc:
        print("[MODEL] Inference error:", exc)
        last_capture = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_detections = 0
        last_classes = []
        set_yolo_overlay([])
    finally:
        cooldown_until = time.monotonic() + TRIGGER_COOLDOWN
        set_trigger_state("COOLDOWN")
        print("[TRIGGER] Capture done → COOLDOWN")

def camera_capture_loop():
    global latest_frame, camera_ok, camera_error, camera_running
    global last_capture, last_detections, last_classes, bg_subtractor, cooldown_until

    frame_interval = 1.0 / TARGET_FPS
    warmup_count = 0
    settle_count = 0

    while camera_running:
        if camera is None or not camera.isOpened():
            camera_ok = False
            warmup_count = 0
            settle_count = 0
            if not open_camera():
                time.sleep(2)
                continue

        start_time = time.monotonic()
        with camera_lock:
            ok, frame = camera.read()

        if not ok or frame is None:
            camera_ok = False
            camera_error = "Camera frame read failed."
            time.sleep(0.1)
            elapsed = time.monotonic() - start_time
            time.sleep(max(0.001, frame_interval - elapsed))
            continue

        live_frame = cv2.flip(frame, 1)
        now = time.monotonic()
        state = get_trigger_state()

        if TRIGGER_ENABLED and bg_subtractor is not None:
            try:
                mask = bg_subtractor.apply(live_frame)
                changed, _change_percent = significant_change(mask)

                if state == "WARMUP":
                    warmup_count += 1
                    if warmup_count >= WARMUP_FRAMES:
                        warmup_count = 0
                        set_trigger_state("WAITING")
                        print("[TRIGGER] Warming complete. State = WAITING")

                elif state == "WAITING":
                    if changed:
                        settle_count = 0
                        set_trigger_state("SETTLING")
                        print("[TRIGGER] Change detected → SETTLING")

                elif state == "SETTLING":
                    settle_count += 1
                    if settle_count >= SETTLE_FRAMES:
                        capture_frame = live_frame.copy()
                        set_trigger_state("CAPTURING")
                        print("[TRIGGER] Object settled → CAPTURING")
                        threading.Thread(
                            target=run_backend_capture,
                            args=(capture_frame,),
                            name="BackendCapture",
                            daemon=True,
                        ).start()

                elif state == "CAPTURING":
                    pass

                elif state == "COOLDOWN":
                    if now >= cooldown_until:
                        settle_count = 0
                        set_trigger_state("WAITING")
                        print("[TRIGGER] Cooldown complete. State = WAITING")

            except Exception as exc:
                print("[TRIGGER] State machine error:", exc)

        maybe_start_yolo_preview(live_frame, state)

        display_frame = live_frame
        with yolo_overlay_lock:
            hold_jpeg = annotated_hold_jpeg
            hold_until = annotated_hold_until
            boxes = list(yolo_boxes)

        now = time.monotonic()
        if hold_jpeg and now < hold_until:
            encoded = hold_jpeg
        else:
            if boxes:
                display_frame = draw_yolo_boxes(live_frame, boxes)
            encoded = encode_jpeg(display_frame)
        if encoded is not None:
            with camera_lock:
                latest_frame = encoded
                camera_ok = True
                camera_error = ""
        else:
            camera_ok = False
            camera_error = "JPEG encoding failed."

        elapsed = time.monotonic() - start_time
        time.sleep(max(0.001, frame_interval - elapsed))

    camera_ok = False


# ============================================================
# START / STOP CAMERA
# ============================================================

def start_camera():
    global camera_thread, camera_running, scan_session
    if camera_running:
        return
    print("[CAMERA] Starting camera...")
    camera_running = True
    scan_session = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("[CAMERA] Scan session:", scan_session)
    open_camera()
    camera_thread = threading.Thread(
        target=camera_capture_loop,
        name="CameraCapture",
        daemon=True,
    )
    camera_thread.start()


def stop_camera():
    global camera_running, camera, latest_frame
    camera_running = False
    if camera_thread is not None and camera_thread.is_alive():
        camera_thread.join(timeout=2)
    with camera_lock:
        if camera is not None:
            try:
                camera.release()
            except Exception:
                pass
            camera = None
        latest_frame = None
    print("[CAMERA] Stopped.")


@app.on_event("startup")
def startup_event():
    init_schema()
    if model is None:
        load_model()
    if not camera_running:
        start_camera()


@app.on_event("shutdown")
def shutdown_event():
    stop_camera()


# ============================================================
# CAMERA STATUS API
# ============================================================

@app.get("/camera_status")
def camera_status():
    if camera is not None and camera.isOpened():
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
        width = 0
        height = 0
    return JSONResponse({
        "ok": camera_ok,
        "camera_index": CAMERA_INDEX,
        "platform": platform.system(),
        "width": width,
        "height": height,
        "error": camera_error,
    })


# ============================================================
# DETECTION MODE API
# ============================================================

@app.get("/api/mode")
def get_mode():
    return JSONResponse({"mode": get_detection_mode()})


@app.post("/api/mode/{new_mode}")
def set_mode(new_mode: str):
    global detection_mode
    mode = new_mode.strip().upper()
    if mode not in VALID_MODES:
        return JSONResponse(
            {"detail": "Invalid mode. Use IN, OUT, or SCAN."},
            status_code=400,
        )
    with detection_mode_lock:
        detection_mode = mode
    print(f"[MODE] Changed to: {mode}")
    return JSONResponse({"mode": mode, "status": "changed"})


# ============================================================
# TRIGGER STATUS API
# ============================================================

@app.get("/api/trigger_status")
def trigger_status():
    with yolo_overlay_lock:
        labels = list(yolo_labels)
    with inventory_revision_lock:
        revision = inventory_revision
    return JSONResponse({
        "state": get_trigger_state(),
        "last_capture": last_capture,
        "last_detections": last_detections,
        "last_classes": last_classes,
        "yolo_labels": labels,
        "inventory_revision": revision,
    })


@app.get("/api/boot_status")
def boot_status():
    return JSONResponse({
        "ready": boot_ready,
        "stage": boot_stage,
        "percent": boot_percent,
        "camera_ok": camera_ok,
        "trigger_state": get_trigger_state(),
    })


@app.get("/db_status")
def db_status():
    connected, error = check_db()
    if connected:
        return JSONResponse({"connected": True})
    return JSONResponse({"connected": False, "error": error})


@app.post("/api/objects/embedding")
async def create_object_embedding(
    file: UploadFile = File(...),
    object_name: str = Form(...),
):
    name = normalize_item_name(object_name)
    if not name:
        return JSONResponse(
            {"detail": "object_name is required"},
            status_code=400,
        )
    image_bytes = await file.read()
    if not image_bytes:
        return JSONResponse(
            {"detail": "Image file is empty"},
            status_code=400,
        )
    try:
        embedding = image_to_embedding(image_bytes)
        save_object_embedding(name, embedding)
    except Exception as exc:
        print("[EMBED] Error:", exc)
        return JSONResponse(
            {"detail": f"Could not create embedding: {exc}"},
            status_code=500,
        )
    return JSONResponse({
        "status": "saved",
        "object_name": name,
        "embedding_size": len(embedding),
    })


# ============================================================
# ERROR FRAME
# ============================================================

def make_error_frame(text):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(
        frame, "ONESHOT CAMERA", (145, 190),
        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA,
    )
    cv2.putText(
        frame, text, (65, 250),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2, cv2.LINE_AA,
    )
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    return encoded.tobytes() if ok else b""


# ============================================================
# MJPEG FRAME GENERATOR (FIXED HEADER - NO BLACK SCREEN)
# ============================================================

def generate_frames():
    last_frame = None
    while True:
        with camera_lock:
            frame_bytes = latest_frame

        if frame_bytes is None:
            frame_bytes = make_error_frame(
                "Waiting for camera..." if camera_running else "Camera is stopped."
            )

        if frame_bytes != last_frame:
            last_frame = frame_bytes

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )
        time.sleep(0.04)


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    dashboard_path = os.path.join(BASE_DIR, "dashboard.html")
    if not os.path.exists(dashboard_path):
        return HTMLResponse("<h1>dashboard.html not found</h1>", status_code=500)
    with open(dashboard_path, "r", encoding="utf-8") as file:
        html = file.read()
    return HTMLResponse(content=html)


FRONTEND_FILES = {
    "theme.css": "text/css",
    "dashboard.css": "text/css",
    "config.js": "application/javascript",
    "dashboard.js": "application/javascript",
    "petronas-logo.svg": "image/svg+xml",
}


@app.get("/{filename}")
def serve_frontend_file(filename: str):
    media_type = FRONTEND_FILES.get(filename)
    if media_type is None:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse({"detail": f"{filename} not found"}, status_code=404)
    return FileResponse(file_path, media_type=media_type)


# ============================================================
# RUN SERVER
# ============================================================

def set_boot(percent, stage):
    global boot_percent, boot_stage
    boot_percent = percent
    boot_stage = stage
    loader.set_progress(percent, stage)


def run_high_end_boot():
    global boot_ready
    loader.start()
    try:
        set_boot(8, "booting core systems")
        loader.pulse(0.25)

        set_boot(22, "loading neon UI kernel")
        loader.pulse(0.2)

        set_boot(40, "loading YOLOv8 weights")
        load_model()
        loader.pulse(0.15)

        set_boot(68, "opening camera pipeline")
        start_camera()

        set_boot(86, "calibrating motion sensors")
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if camera_ok and get_trigger_state() != "WARMUP":
                break
            loader.pulse(0.12)

        set_boot(100, "systems online")
        boot_ready = True
        lan_ip = get_lan_ip()
        local_url = f"http://127.0.0.1:{PORT}"
        lan_url = f"http://{lan_ip}:{PORT}" if lan_ip else None
        loader.finish(local_url, lan_url)
    except Exception as exc:
        boot_ready = True
        loader.fail(str(exc))


if __name__ == "__main__":
    run_high_end_boot()
    uvicorn.run(app, host=HOST, port=PORT, reload=False, log_level="warning")
