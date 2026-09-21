import os
import sys
import time
import queue
import base64
import asyncio
import threading
import platform
import subprocess
import webbrowser
import signal
from collections import defaultdict
from datetime import datetime
from io import BytesIO

import cv2
import numpy as np
import torch
import infer

from fastapi import FastAPI, File, Form, Request, UploadFile
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import router as api_router
import loader
from dataset_importer import choose_folder, import_train_catalog
from db import (
    record_yolo_capture,
    normalize_item_name,
    check_db,
    clear_check_in_out,
    save_object_embedding,
    fetch_staff_embeddings,
    fetch_inventory_embeddings,
    insert_staff,
    replace_inventory_embeddings,
    close_boot_connection,
)
from sql import bootstrap_database
from face import FaceGate, draw_landmarks
from sam_tool import (
    clear_sessions as clear_sam_sessions,
    create_mask as create_sam_mask,
    create_masked_crop,
    create_session as create_sam_session,
    discard_session as discard_sam_session,
    load_sam_model,
    sam_status,
)
from config import (
    BASE_DIR, HOST, PORT, CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    TARGET_FPS, JPEG_QUALITY, MODEL_PATH, OPENCLIP_CHECKPOINT,
    MODEL_CONFIDENCE, MODEL_IMAGE_SIZE,
    TRIGGER_ENABLED, CHANGE_AREA_PERCENT, SETTLE_FRAMES,
    TRIGGER_COOLDOWN, MOG2_HISTORY, MOG2_VAR_THRESHOLD, MOG2_DETECT_SHADOWS,
    WARMUP_FRAMES, YOLO_PREVIEW_ENABLED, YOLO_PREVIEW_INTERVAL, YOLO_HOLD_SECONDS,
    FACE_MATCH_THRESHOLD, FACE_MATCH_STREAK, FACE_EMBED_INTERVAL,
    get_lan_ip,
)


# ====================
# 
# 
# 
# 
# 
# 
# ========================================
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

catalog_import_lock = threading.Lock()
catalog_import_state = {
    "running": False,
    "stage": "idle",
    "percent": 0,
    "processed": 0,
    "total": 0,
    "embedded": 0,
    "current": "",
    "error": "",
    "result": None,
}
inventory_catalog_lock = threading.Lock()
inventory_catalog_cache = None
INVENTORY_MATCH_THRESHOLD = float(
    os.environ.get("INVENTORY_MATCH_THRESHOLD", "0.60")
)


# ============================================================
# AI MODEL (loaded during high-end boot, not at import)
# ============================================================

model = None
MODEL_DEVICE = "cpu"

embed_model = None
embed_backend = None
embed_preprocess = None
embed_device = "cpu"
embed_lock = threading.Lock()
EMBEDDING_SIZE = 512
EMBED_IMAGE_SIZE = 224
_encode_jobs = queue.Queue()
_encode_ready = threading.Event()
_encode_thread = None
ENCODE_TIMEOUT = 8.0


def load_model():
    global model, MODEL_DEVICE
    if model is not None:
        return
    model = infer.load_model()
    MODEL_DEVICE = infer.model_device()


def _load_clip_weights():
    global embed_model, embed_backend, embed_preprocess, embed_device
    if embed_model is not None:
        return
    import open_clip

    if not os.path.isfile(OPENCLIP_CHECKPOINT):
        raise RuntimeError(
            f"OpenCLIP checkpoint not found: {OPENCLIP_CHECKPOINT}"
        )
    embed_device = "cuda" if torch.cuda.is_available() else "cpu"
    embed_model, _, embed_preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32",
        pretrained=OPENCLIP_CHECKPOINT,
    )
    embed_model = embed_model.to(embed_device).eval()
    embed_backend = "openclip-ViT-B-32-laion2b_s34b_b79k"
    print(
        f"[EMBED] Loaded OpenCLIP ViT-B-32 from {OPENCLIP_CHECKPOINT} "
        f"(512-d)  device={embed_device}"
    )


def _prepare_embed_image(image_bytes):
    from PIL import Image

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    if image.size != (EMBED_IMAGE_SIZE, EMBED_IMAGE_SIZE):
        image = image.resize((EMBED_IMAGE_SIZE, EMBED_IMAGE_SIZE), Image.BILINEAR)
    return image


def face_crop_to_embedding(image_bytes):
    """Fast CPU 512-d face vector. No CUDA, no CLIP, no extra threads."""
    image = _prepare_embed_image(image_bytes)
    arr = np.asarray(image, dtype=np.float32) / 255.0
    gray = arr.mean(axis=2)
    grid = gray.reshape(16, 14, 16, 14).mean(axis=(1, 3)).reshape(-1)
    color = arr.reshape(-1, 3)
    hist = np.concatenate([
        np.histogram(color[:, 0], 85, range=(0.0, 1.0))[0],
        np.histogram(color[:, 1], 85, range=(0.0, 1.0))[0],
        np.histogram(color[:, 2], 86, range=(0.0, 1.0))[0],
    ]).astype(np.float32)
    vector = np.concatenate([grid.astype(np.float32), hist])
    norm = float(np.linalg.norm(vector)) or 1.0
    return [float(value) for value in (vector / norm)]


def _encode_images(images):
    tensors = torch.stack([
        embed_preprocess(image.convert("RGB")) for image in images
    ]).to(embed_device)
    with torch.inference_mode():
        vectors = embed_model.encode_image(tensors)
        vectors = vectors / vectors.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    return vectors.detach().float().cpu().numpy().astype(np.float32)


def _encode_image(image):
    return _encode_images([image])[0]


def _encode_worker_loop():
    from PIL import Image

    try:
        _load_clip_weights()
        dummy = Image.new("RGB", (EMBED_IMAGE_SIZE, EMBED_IMAGE_SIZE), (28, 32, 40))
        started = time.perf_counter()
        _encode_image(dummy)
        print(f"[EMBED] Warmup encode {time.perf_counter() - started:.2f}s")
    except Exception as exc:
        print("[EMBED] Worker init failed:", exc)
    _encode_ready.set()

    while True:
        job = _encode_jobs.get()
        if job is None:
            break
        reply = job.get("reply")
        try:
            images = job.get("images")
            if images is None:
                images = [_prepare_embed_image(job["bytes"])]
            started = time.perf_counter()
            vectors = _encode_images(images)
            elapsed = time.perf_counter() - started
            print(
                f"[EMBED] encoded {len(images)} crop(s) in {elapsed:.2f}s "
                f"backend={embed_backend}"
            )
            result = [
                [float(value) for value in vector]
                for vector in vectors
            ]
            if any(len(vector) != EMBEDDING_SIZE for vector in result):
                raise ValueError(f"Expected {EMBEDDING_SIZE}-d embeddings")
            if job.get("mode"):
                _apply_face_embedding(result[0], job["mode"])
            if reply is not None:
                reply.put(result)
        except Exception as exc:
            print("[EMBED] encode error:", exc)
            if reply is not None:
                reply.put(exc)
        finally:
            if job.get("release_pending"):
                global face_embed_pending
                face_embed_pending = False


def load_embed_model():
    """Load CLIP once on a dedicated encode thread and keep it there."""
    global _encode_thread
    if embed_model is not None and _encode_ready.is_set():
        return
    if _encode_thread is None or not _encode_thread.is_alive():
        _encode_thread = threading.Thread(
            target=_encode_worker_loop,
            name="ClipEncode",
            daemon=True,
        )
        _encode_thread.start()
    if not _encode_ready.wait(timeout=180):
        raise RuntimeError("CLIP encoder failed to start")


def image_to_embedding(image_bytes, timeout=ENCODE_TIMEOUT):
    load_embed_model()
    reply = queue.Queue()
    _encode_jobs.put({"bytes": image_bytes, "reply": reply})
    try:
        result = reply.get(timeout=timeout)
    except queue.Empty as exc:
        raise TimeoutError("Face embedding timed out") from exc
    if isinstance(result, Exception):
        raise result
    return result[0]


def images_to_embeddings(images, timeout=120.0):
    load_embed_model()
    reply = queue.Queue()
    _encode_jobs.put({"images": images, "reply": reply})
    try:
        result = reply.get(timeout=timeout)
    except queue.Empty as exc:
        raise TimeoutError("OpenCLIP batch embedding timed out") from exc
    if isinstance(result, Exception):
        raise result
    return result


def queue_face_embedding(image_bytes, mode):
    """Encode on the CLIP thread without blocking the API."""
    global face_embed_pending, last_face_embed_at
    load_embed_model()
    face_embed_pending = True
    last_face_embed_at = time.monotonic()
    _encode_jobs.put({
        "bytes": image_bytes,
        "reply": queue.Queue(),
        "mode": mode,
        "release_pending": True,
    })


def load_face_gate():
    global face_gate
    if face_gate is not None:
        return
    engine = FaceGate()
    try:
        engine.load()
    except Exception as exc:
        print("[FACE] Could not load face model:", exc)
    face_gate = engine


def cosine_similarity(left, right):
    a = np.asarray(left, dtype=np.float32).reshape(-1)
    b = np.asarray(right, dtype=np.float32).reshape(-1)
    if a.size == 0 or b.size == 0 or a.size != b.size:
        return -1.0
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-8:
        return -1.0
    return float(np.dot(a, b) / denom)


def match_staff_embedding(embedding):
    best = None
    best_score = -1.0
    for row in fetch_staff_embeddings():
        score = cosine_similarity(embedding, row["facial_embedding"])
        if score > best_score:
            best_score = score
            best = row
    if best is None or best_score < FACE_MATCH_THRESHOLD:
        return None, best_score
    return {
        "staff_id": best["staff_id"],
        "staff_name": best["staff_name"],
        "score": round(best_score, 4),
    }, best_score


def face_detection_active():
    with face_state_lock:
        if face_mode == "register":
            return True
        if face_mode == "recognize" and not recognized_staff:
            return True
        return False


def other_models_allowed():
    return not face_detection_active() and is_object_detection_armed()


def set_face_mode(new_mode):
    global face_mode, face_gate_visible, recognized_staff, pending_face_embedding
    global pending_face_crop, ready_to_register, face_match_streak, face_message
    global face_match_score, SCAN_OPERATOR
    mode = (new_mode or "off").strip().lower()
    if mode not in VALID_FACE_MODES:
        raise ValueError("Invalid face mode")
    set_object_detection_armed(False)
    with face_state_lock:
        face_mode = mode
        pending_face_embedding = None
        pending_face_crop = None
        ready_to_register = False
        face_match_streak = 0
        face_match_score = None
        if mode == "off":
            face_gate_visible = False
            face_message = "Face gate idle"
        elif mode == "register":
            face_gate_visible = True
            face_message = "Place your face in the outline to register"
        else:
            recognized_staff = None
            SCAN_OPERATOR = "System"
            face_gate_visible = True
            face_message = "Place your face in the outline to check out"
    print(f"[FACE] Mode → {mode}")
    return mode


def face_status_payload():
    with face_state_lock:
        staff = dict(recognized_staff) if recognized_staff else None
        return {
            "mode": face_mode,
            "gate_visible": face_gate_visible,
            "detected": face_detected,
            "landmarks_complete": landmarks_complete,
            "in_region": face_in_region,
            "ready_to_register": ready_to_register,
            "embed_pending": face_embed_pending,
            "embed_ready": pending_face_embedding is not None,
            "recognized": staff,
            "match_score": face_match_score,
            "unknown_staff": (
                face_mode == "recognize"
                and face_match_score is not None
                and staff is None
            ),
            "message": face_message,
            "models_paused": face_detection_active(),
            "detection_armed": is_object_detection_armed(),
            "detection_preview_active": detection_preview_active(),
        }


def _apply_face_embedding(embedding, mode):
    global pending_face_embedding, ready_to_register, recognized_staff
    global face_match_streak, face_gate_visible, face_message
    global face_match_score, SCAN_OPERATOR

    with face_state_lock:
        pending_face_embedding = embedding
        if mode == "register":
            ready_to_register = True
            face_message = "Face captured. Enter staff name and ID"
    if mode == "register":
        print("[FACE] Embedding ready for register")
        return

    match, score = match_staff_embedding(embedding)
    with face_state_lock:
        face_match_score = round(score, 4)
        if match:
            face_match_streak = 1
            recognized_staff = match
            SCAN_OPERATOR = match["staff_name"]
            face_gate_visible = False
            face_message = f"Recognized {match['staff_name']}"
            print(
                f"[FACE] Recognized {match['staff_name']} "
                f"({match['staff_id']}) similarity={score:.3f}"
            )
        else:
            face_match_streak = 0
            pending_face_embedding = None
            ready_to_register = False
            if score >= 0:
                face_message = (
                    f"UNKNOWN STAFF · {int(score * 100)}% "
                    f"(requires {int(FACE_MATCH_THRESHOLD * 100)}%)"
                )
            else:
                face_message = "No enrolled staff yet — switch to Register"


def _face_embed_worker(crop_bytes, mode):
    global face_embed_pending
    try:
        _apply_face_embedding(face_crop_to_embedding(crop_bytes), mode)
    except Exception as exc:
        print("[FACE] Embedding error:", exc)
    finally:
        face_embed_pending = False


def handle_face_info(info):
    global face_detected, landmarks_complete, face_in_region, face_message
    global pending_face_embedding, pending_face_crop, ready_to_register, face_match_streak
    global face_embed_pending, last_face_mesh, last_face_points

    with face_draw_lock:
        last_face_mesh = info.get("mesh")
        last_face_points = info.get("points5")

    now = time.monotonic()
    complete = bool(info.get("complete"))
    in_region = bool(info.get("in_region"))
    crop_bytes = info.get("crop_bytes")
    detected = bool(info.get("detected"))

    with face_state_lock:
        face_detected = detected
        landmarks_complete = complete
        face_in_region = in_region
        mode = face_mode

        if not detected:
            face_message = "Looking for a face"
            ready_to_register = False
            pending_face_embedding = None
            pending_face_crop = None
            face_match_streak = 0
            return
        if not in_region:
            face_message = "Move your face into the outline"
            ready_to_register = False
            return
        if crop_bytes:
            pending_face_crop = crop_bytes
        if mode == "register":
            ready_to_register = True
            face_message = "Face in outline — enter staff name and ID"
        elif not complete:
            face_message = "Hold still — facial landmarks are incomplete"

    if (
        crop_bytes
        and in_region
        and mode != "register"
        and not face_embed_pending
        and now - last_face_embed_at >= FACE_EMBED_INTERVAL
    ):
        face_embed_pending = True
        threading.Thread(
            target=_face_embed_worker,
            args=(crop_bytes, mode),
            name="FaceEmbed",
            daemon=True,
        ).start()


def _face_detect_job(frame):
    global face_job_pending
    try:
        if face_gate is None:
            return
        _unused, info = face_gate.process(frame, draw=False)
        handle_face_info(info)
    except Exception as exc:
        print("[FACE] Process error:", exc)
    finally:
        face_job_pending = False


def maybe_start_face_job(frame):
    global face_job_pending
    if not face_detection_active() or face_gate is None:
        return
    if face_job_pending:
        return
    face_job_pending = True
    threading.Thread(
        target=_face_detect_job,
        args=(frame.copy(),),
        name="FaceDetect",
        daemon=True,
    ).start()



# ============================================================
# CAMERA GLOBAL VARIABLES
# ============================================================

camera = None
camera_lock = threading.Lock()
frame_lock = threading.Lock()
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
object_detection_armed = False
object_detection_arm_lock = threading.Lock()

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
boot_done = False

face_gate = None
face_mode = "recognize"
face_gate_visible = True
face_detected = False
landmarks_complete = False
face_in_region = False
face_message = "Place your face in the outline"
recognized_staff = None
pending_face_embedding = None
pending_face_crop = None
ready_to_register = False
face_match_streak = 0
face_match_score = None
last_face_embed_at = 0.0
face_embed_pending = False
face_job_pending = False
last_face_mesh = None
last_face_points = None
face_draw_lock = threading.Lock()
# Status payloads call helpers that also read face state.  A re-entrant lock
# prevents those nested reads from deadlocking FastAPI's worker pool.
face_state_lock = threading.RLock()
VALID_FACE_MODES = {"off", "recognize", "register"}


# ============================================================
# MODE / TRIGGER HELPERS
# ============================================================

def get_detection_mode():
    with detection_mode_lock:
        return detection_mode


def is_object_detection_armed():
    with object_detection_arm_lock:
        return object_detection_armed


def set_object_detection_armed(armed):
    global object_detection_armed
    with object_detection_arm_lock:
        object_detection_armed = bool(armed)
        return object_detection_armed


def detection_preview_active():
    with yolo_overlay_lock:
        return bool(
            annotated_hold_jpeg
            and time.monotonic() < annotated_hold_until
        )


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
    if model is None or catalog_import_active():
        return []
    with model_lock:
        return infer.predict_frame(frame)


def refresh_inventory_catalog_cache():
    global inventory_catalog_cache
    rows = fetch_inventory_embeddings()
    prepared = [
        (
            normalize_item_name(row["inventory_name"]),
            np.asarray(row["inventory_embedding"], dtype=np.float32),
        )
        for row in rows
    ]
    with inventory_catalog_lock:
        inventory_catalog_cache = prepared
    return len(prepared)


def get_inventory_catalog():
    with inventory_catalog_lock:
        cached = inventory_catalog_cache
    if cached is None:
        refresh_inventory_catalog_cache()
        with inventory_catalog_lock:
            cached = inventory_catalog_cache
    return cached or []


def match_inventory_name(crop):
    if crop is None:
        return None, -1.0
    ok, encoded = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        return None, -1.0
    try:
        embedding = image_to_embedding(encoded.tobytes())
    except Exception as exc:
        print("[INFER] Crop embed error:", exc)
        return None, -1.0
    ranking = sorted(
        (
            (cosine_similarity(embedding, vector), name)
            for name, vector in get_inventory_catalog()
        ),
        reverse=True,
    )[:100]
    grouped = defaultdict(list)
    for score, name in ranking:
        grouped[name].append(score)
    supported = [
        (float(np.mean(scores)), name)
        for name, scores in grouped.items()
        if len(scores) >= 3
    ]
    if not supported and ranking:
        supported = [(ranking[0][0], ranking[0][1])]
    if not supported:
        return None, -1.0
    best_score, best_name = max(supported)
    if best_score <= INVENTORY_MATCH_THRESHOLD:
        return None, best_score
    return normalize_item_name(best_name), best_score


def parse_yolo_boxes(results, frame=None):
    detections = infer.parse_detections(results)
    if not detections:
        return []
    frame_height, frame_width = frame.shape[:2] if frame is not None else (1, 1)
    accepted = []
    for item in detections:
        x1, y1, x2, y2 = item["xyxy"]
        item["box_norm"] = (
            max(0.0, min(1.0, x1 / frame_width)),
            max(0.0, min(1.0, y1 / frame_height)),
            max(0.0, min(1.0, x2 / frame_width)),
            max(0.0, min(1.0, y2 / frame_height)),
        )
        crop = infer.crop_masked_bgr(frame, item) if frame is not None else None
        named, identity_score = match_inventory_name(crop)
        if named:
            item["name"] = named
            item["identity_score"] = identity_score
            accepted.append(item)
        else:
            print(
                "[INFER] Detection rejected: "
                f"similarity={identity_score:.3f} "
                f"(required {INVENTORY_MATCH_THRESHOLD:.2f})"
            )
    return accepted


def detection_labels(detections):
    labels = []
    for item in detections:
        confidence = int(item["confidence"] * 100)
        similarity = item.get("identity_score", -1)
        suffix = (
            f" · sim {int(similarity * 100)}%"
            if similarity >= 0
            else ""
        )
        labels.append(f"{item['name']} · det {confidence}%{suffix}")
    return labels


def draw_yolo_boxes(frame, detections):
    vis = frame.copy()
    for item in detections:
        x1, y1, x2, y2 = item["xyxy"]
        identity_score = item.get("identity_score", -1)
        confidence = int(item["confidence"] * 100)
        similarity = (
            f"  SIM {int(identity_score * 100)}%"
            if identity_score >= 0
            else ""
        )
        label = f"{item['name'].upper()}  DET {confidence}%{similarity}"
        polygon = item.get("mask_xy")
        if polygon is not None and len(polygon) >= 3:
            mask_layer = vis.copy()
            cv2.fillPoly(mask_layer, [np.asarray(polygon, dtype=np.int32)], BOX_COLOR)
            vis = cv2.addWeighted(mask_layer, 0.20, vis, 0.80, 0)
            cv2.polylines(
                vis,
                [np.asarray(polygon, dtype=np.int32)],
                True,
                BOX_COLOR,
                2,
                cv2.LINE_AA,
            )
        box_width = max(1, x2 - x1)
        box_height = max(1, y2 - y1)
        corner = max(12, min(34, box_width // 5, box_height // 5))
        for start, end in (
            ((x1, y1), (x1 + corner, y1)),
            ((x1, y1), (x1, y1 + corner)),
            ((x2, y1), (x2 - corner, y1)),
            ((x2, y1), (x2, y1 + corner)),
            ((x1, y2), (x1 + corner, y2)),
            ((x1, y2), (x1, y2 - corner)),
            ((x2, y2), (x2 - corner, y2)),
            ((x2, y2), (x2, y2 - corner)),
        ):
            cv2.line(vis, start, end, BOX_COLOR, 3, cv2.LINE_AA)

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
    global preview_pending, last_capture, last_detections, last_classes
    global cooldown_until
    try:
        if model is None or not is_object_detection_armed():
            return
        detections = parse_yolo_boxes(predict_frame(frame), frame)
        if not is_object_detection_armed():
            return
        logged_count, class_names = log_yolo_detections(detections)
        if logged_count:
            last_capture = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_detections = logged_count
            last_classes = class_names
            cooldown_until = time.monotonic() + TRIGGER_COOLDOWN
            set_trigger_state("COOLDOWN")
            set_yolo_overlay(
                detections,
                hold_frame=frame,
                hold_seconds=YOLO_HOLD_SECONDS,
            )
        else:
            set_yolo_overlay([] if face_detection_active() else detections)
    except Exception as exc:
        print("[YOLO] Preview error:", exc)
    finally:
        preview_pending = False


def maybe_start_yolo_preview(frame, state):
    global preview_pending, last_preview_at
    if not other_models_allowed():
        return
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


scan_warmup_count = 0
scan_settle_count = 0
scan_ingest_lock = threading.Lock()


def ingest_scan_frame(frame):
    """Run motion trigger + YOLO on a browser-captured frame. No OpenCV camera."""
    global scan_warmup_count, scan_settle_count, scan_session, cooldown_until

    if frame is None or not is_object_detection_armed():
        return
    with scan_ingest_lock:
        if bg_subtractor is None:
            reset_background_subtractor()
            scan_warmup_count = 0
            scan_settle_count = 0
        if not scan_session:
            scan_session = datetime.now().strftime("%Y%m%d_%H%M%S")

        now = time.monotonic()
        state = get_trigger_state()
        if TRIGGER_ENABLED and bg_subtractor is not None:
            try:
                mask = bg_subtractor.apply(frame)
                changed, _change_percent = significant_change(mask)

                if state == "WARMUP":
                    scan_warmup_count += 1
                    if scan_warmup_count >= WARMUP_FRAMES:
                        scan_warmup_count = 0
                        set_trigger_state("WAITING")
                        print("[TRIGGER] Warming complete. State = WAITING")

                elif state == "WAITING":
                    if changed:
                        scan_settle_count = 0
                        set_trigger_state("SETTLING")
                        print("[TRIGGER] Change detected → SETTLING")

                elif state == "SETTLING":
                    scan_settle_count += 1
                    if scan_settle_count >= SETTLE_FRAMES:
                        set_trigger_state("CAPTURING")
                        print("[TRIGGER] Object settled → CAPTURING")
                        threading.Thread(
                            target=run_backend_capture,
                            args=(frame.copy(),),
                            name="BackendCapture",
                            daemon=True,
                        ).start()

                elif state == "COOLDOWN":
                    if now >= cooldown_until:
                        scan_settle_count = 0
                        set_trigger_state("WAITING")
                        print("[TRIGGER] Cooldown complete. State = WAITING")
            except Exception as exc:
                print("[TRIGGER] Browser-frame error:", exc)

        maybe_start_yolo_preview(frame, get_trigger_state())


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

    # --------------------------------------------------------
    # RELEASE PREVIOUS CAMERA
    # --------------------------------------------------------

    if camera is not None:
        try:
            camera.release()
        except Exception:
            pass

        camera = None

    # --------------------------------------------------------
    # BACKEND OPTIONS
    # --------------------------------------------------------

    if sys.platform == "darwin":

        backend_options = [
            ("AVFOUNDATION", cv2.CAP_AVFOUNDATION)
        ]

    elif sys.platform.startswith("win"):

        backend_options = [
            ("DSHOW", cv2.CAP_DSHOW),
            ("MSMF", cv2.CAP_MSMF),
            ("ANY", cv2.CAP_ANY),
        ]

    else:

        backend_options = [
            ("ANY", cv2.CAP_ANY)
        ]

    # --------------------------------------------------------
    # TRY EACH BACKEND
    # --------------------------------------------------------

    for backend_name, backend in backend_options:

        print(
            f"[CAMERA] Trying index {CAMERA_INDEX} "
            f"with {backend_name}..."
        )

        try:

            test_camera = cv2.VideoCapture(
                CAMERA_INDEX,
                backend
            )

        except Exception as exc:

            print(
                f"[CAMERA] {backend_name} failed:",
                exc
            )

            continue

        if not test_camera.isOpened():

            print(
                f"[CAMERA] {backend_name} could not open camera."
            )

            test_camera.release()

            continue

        # ----------------------------------------------------
        # WINDOWS — REQUEST MJPG
        # ----------------------------------------------------

        if sys.platform.startswith("win"):

            test_camera.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(
                    "M",
                    "J",
                    "P",
                    "G"
                )
            )

        # ----------------------------------------------------
        # CAMERA SETTINGS
        # ----------------------------------------------------

        test_camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            CAMERA_WIDTH
        )

        test_camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            CAMERA_HEIGHT
        )

        test_camera.set(
            cv2.CAP_PROP_FPS,
            TARGET_FPS
        )

        print(
            f"[CAMERA] Warming up {backend_name}..."
        )

        time.sleep(1.0)

        valid_frame = None

        # ----------------------------------------------------
        # TEST FRAMES
        # ----------------------------------------------------

        for _ in range(30):

            ok, frame = test_camera.read()

            if not ok or frame is None:
                time.sleep(0.1)
                continue

            # ----------------------------------------------
            # BASIC FRAME STATISTICS
            # OpenCV channel order = BGR
            # ----------------------------------------------

            channel_mean = frame.mean(
                axis=(0, 1)
            )

            blue_mean = channel_mean[0]
            green_mean = channel_mean[1]
            red_mean = channel_mean[2]

            frame_std = frame.std()

            print(
                f"[CAMERA DEBUG] "
                f"B={blue_mean:.1f} "
                f"G={green_mean:.1f} "
                f"R={red_mean:.1f} "
                f"STD={frame_std:.1f}"
            )

            # ----------------------------------------------
            # REJECT BLACK / EMPTY FRAME
            # ----------------------------------------------

            if frame.mean() < 5.0:
                continue

            # ----------------------------------------------
            # REJECT SOLID / CORRUPTED GREEN FRAME
            # ----------------------------------------------

            green_corrupt = (
                green_mean
                > blue_mean * 2.5
                and
                green_mean
                > red_mean * 2.5
                and
                frame_std < 70
            )

            if green_corrupt:

                print(
                    "[CAMERA] Corrupted green frame detected."
                )

                continue

            valid_frame = frame
            break

        # ----------------------------------------------------
        # BACKEND SUCCESS
        # ----------------------------------------------------

        if valid_frame is not None:

            camera = test_camera

            camera_ok = True
            camera_error = ""

            actual_width = int(
                camera.get(
                    cv2.CAP_PROP_FRAME_WIDTH
                )
            )

            actual_height = int(
                camera.get(
                    cv2.CAP_PROP_FRAME_HEIGHT
                )
            )

            print(
                f"[CAMERA] SUCCESS using {backend_name}"
            )

            print(
                f"[CAMERA] Ready: "
                f"{actual_width} x "
                f"{actual_height}"
            )

            reset_background_subtractor()
            try:
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass

            return True

        # ----------------------------------------------------
        # BACKEND PRODUCED INVALID FRAMES
        # ----------------------------------------------------

        print(
            f"[CAMERA] {backend_name} produced invalid frames."
        )

        test_camera.release()

    # --------------------------------------------------------
    # ALL BACKENDS FAILED
    # --------------------------------------------------------

    camera = None
    camera_ok = False

    camera_error = (
        "No camera backend produced a valid frame."
    )

    print(
        "[CAMERA]",
        camera_error
    )

    return False


# ============================================================
# YOLO DETECTION LOGGING + INVENTORY UPDATES
# ============================================================

def log_yolo_detections(detections):
    """
    Insert one check_in_out row per named object found in this capture.
    Newest captured items stay at the top of the list.
    Never crash the camera.
    Returns (logged_count, class_names).
    """
    global inventory_revision
    try:
        if not detections or not is_object_detection_armed():
            return 0, []

        grouped = defaultdict(list)
        for item in detections:
            grouped[item["name"]].append(float(item["confidence"]))

        if not grouped:
            return 0, []

        mode = get_detection_mode()
        if mode in {"IN", "OUT"}:
            with face_state_lock:
                staff = recognized_staff
            if not staff:
                print(f"[FACE] {mode} blocked — no recognized staff")
                return 0, []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_id = scan_session or datetime.now().strftime("%Y%m%d_%H%M%S")
        class_names = list(grouped.keys())

        inserted_names = record_yolo_capture(
            grouped,
            mode,
            timestamp,
            session_id,
            staff["staff_name"] if mode in {"IN", "OUT"} else SCAN_OPERATOR,
        )
        if not inserted_names:
            return 0, []
        with inventory_revision_lock:
            inventory_revision += 1

        print(
            f"[DETECTION] Mode={mode} | Logged {len(inserted_names)} "
            f"classes at {timestamp}"
        )
        set_object_detection_armed(False)
        set_trigger_state("WAITING")
        print("[DETECTION] Movement saved — object recognition disarmed")
        return len(inserted_names), inserted_names

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
        detections = parse_yolo_boxes(results, frame)
        logged_count, class_names = log_yolo_detections(detections)
        last_capture = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_detections = logged_count
        last_classes = class_names
        if logged_count:
            set_yolo_overlay(
                detections,
                hold_frame=frame,
                hold_seconds=YOLO_HOLD_SECONDS,
            )
        else:
            set_yolo_overlay([] if face_detection_active() else detections)
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
      try:
        if camera is None or not camera.isOpened():
            camera_ok = False
            warmup_count = 0
            settle_count = 0
            if not open_camera():
                time.sleep(2)
                continue

        start_time = time.monotonic()
        try:
            with camera_lock:
                ok, frame = camera.read()
        except Exception as exc:
            print("[CAMERA] Read error:", exc)
            time.sleep(0.05)
            continue

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
        face_active = face_detection_active()
        if face_active:
            maybe_start_face_job(live_frame)

        detection_armed = is_object_detection_armed()
        if (
            TRIGGER_ENABLED
            and bg_subtractor is not None
            and not face_active
            and detection_armed
        ):
            try:
                mask = bg_subtractor.apply(live_frame)
                changed, _change_percent = significant_change(mask)
                state = get_trigger_state()

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

        if not face_active and detection_armed:
            maybe_start_yolo_preview(live_frame, state)

        display_frame = live_frame
        hold_jpeg = None
        hold_until = 0.0
        boxes = []
        if face_active:
            with face_draw_lock:
                mesh = last_face_mesh
                points5 = last_face_points
            if mesh or points5:
                display_frame = draw_landmarks(live_frame, mesh or [], points5 or [])
        else:
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
            with frame_lock:
                latest_frame = encoded
            camera_ok = True
            camera_error = ""
        else:
            camera_ok = False
            camera_error = "JPEG encoding failed."

        elapsed = time.monotonic() - start_time
        time.sleep(max(0.001, frame_interval - elapsed))
      except Exception as exc:
        print("[CAMERA] Loop error:", exc)
        time.sleep(0.05)

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
        camera_thread.join(timeout=0.2)
    with camera_lock:
        if camera is not None:
            try:
                camera.release()
            except Exception:
                pass
            camera = None
    with frame_lock:
        latest_frame = None
    print("[CAMERA] Stopped.")


@app.on_event("startup")
def startup_event():
    global boot_ready, boot_done
    if boot_done:
        return
    bootstrap_database()
    clear_check_in_out()
    if model is None:
        load_model()
    load_embed_model()
    load_sam_model()
    load_face_gate()
    set_face_mode("recognize")
    boot_ready = True
    boot_done = True


@app.on_event("shutdown")
def shutdown_event():
    stop_camera()
    clear_sam_sessions()
    if face_gate is not None:
        face_gate.close()
    _clear_session_movements()
    close_boot_connection()


dashboard_clients = 0
dashboard_clients_lock = threading.Lock()
_exit_timer = None
_last_heartbeat = 0.0
_watchdog_started = False
HEARTBEAT_TIMEOUT = 60.0
_session_clear_lock = threading.Lock()
_session_movements_cleared = False


def _clear_session_movements():
    global _session_movements_cleared
    with _session_clear_lock:
        if _session_movements_cleared:
            return
        try:
            clear_check_in_out()
            _session_movements_cleared = True
        except Exception as exc:
            print("[SQL] Could not clear check_in_out during shutdown:", exc)


def _touch_heartbeat():
    global _last_heartbeat
    if _last_heartbeat > 0:
        _last_heartbeat = time.monotonic()


def _cancel_app_exit():
    global _exit_timer
    if _exit_timer is not None:
        _exit_timer.cancel()
        _exit_timer = None


def _exit_app(reason="dashboard closed"):
    print(f"[APP] Force close ({reason})")
    try:
        stop_camera()
    except Exception:
        pass
    try:
        if face_gate is not None:
            face_gate.close()
    except Exception:
        pass
    clear_sam_sessions()
    _clear_session_movements()
    try:
        close_boot_connection()
    except Exception:
        pass
    print("[APP] Terminal exiting.")
    os._exit(0)


def _maybe_exit_after_leave():
    with dashboard_clients_lock:
        if dashboard_clients > 0:
            return
    _exit_app("dashboard leave")


@app.post("/api/client/hello")
def dashboard_hello():
    global dashboard_clients, _last_heartbeat
    _cancel_app_exit()
    with dashboard_clients_lock:
        dashboard_clients = 1
    _last_heartbeat = time.monotonic()
    return JSONResponse({"ok": True, "clients": dashboard_clients})


@app.post("/api/client/leave")
def dashboard_leave():
    global dashboard_clients, _exit_timer, _last_heartbeat
    with dashboard_clients_lock:
        dashboard_clients = 0
    _last_heartbeat = 0.0
    _cancel_app_exit()
    timer = threading.Timer(3.0, _maybe_exit_after_leave)
    timer.daemon = True
    _exit_timer = timer
    timer.start()
    return JSONResponse({"ok": True, "clients": 0})


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
    if mode == "OUT":
        with face_state_lock:
            already = recognized_staff is not None
        if not already:
            set_face_mode("recognize")
    return JSONResponse({"mode": mode, "status": "changed"})


class FaceModeBody(BaseModel):
    mode: str


class StaffRegisterBody(BaseModel):
    staff_id: str
    staff_name: str
    image_b64: str = ""


class SamMaskBody(BaseModel):
    session_id: str
    points: list[list[float]]
    labels: list[int]


class SamRegisterBody(BaseModel):
    session_id: str
    object_name: str
    mask_data: str


@app.get("/api/sam/status")
def get_sam_status():
    return JSONResponse(sam_status())


@app.post("/api/sam/capture")
async def capture_sam_frame(file: UploadFile = File(...)):
    image_bytes = await file.read()
    if not image_bytes:
        return JSONResponse({"detail": "Captured frame is empty"}, status_code=400)
    _touch_heartbeat()
    try:
        result = await asyncio.to_thread(create_sam_session, image_bytes)
    except ValueError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=400)
    except Exception as exc:
        print("[SAM] Capture error:", exc)
        return JSONResponse({"detail": str(exc)}, status_code=503)
    _touch_heartbeat()
    return JSONResponse({"ok": True, **result, **sam_status()})


@app.post("/api/sam/mask")
async def generate_sam_mask(body: SamMaskBody):
    _touch_heartbeat()
    try:
        result = await asyncio.to_thread(
            create_sam_mask,
            body.session_id,
            body.points,
            body.labels,
        )
    except KeyError as exc:
        return JSONResponse({"detail": exc.args[0]}, status_code=404)
    except ValueError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=400)
    except Exception as exc:
        print("[SAM] Mask error:", exc)
        return JSONResponse({"detail": str(exc)}, status_code=503)
    _touch_heartbeat()
    return JSONResponse({"ok": True, **result})


@app.post("/api/sam/register")
async def register_sam_embedding(body: SamRegisterBody):
    object_name = normalize_item_name(body.object_name)
    if not object_name:
        return JSONResponse({"detail": "Object name is required"}, status_code=400)
    _touch_heartbeat()
    try:
        crop_bytes = await asyncio.to_thread(
            create_masked_crop,
            body.session_id,
            body.mask_data,
        )
        embedding = await asyncio.to_thread(image_to_embedding, crop_bytes, 30.0)
        saved_name = await asyncio.to_thread(
            save_object_embedding,
            object_name,
            embedding,
        )
        refresh_inventory_catalog_cache()
        discard_sam_session(body.session_id)
    except KeyError as exc:
        return JSONResponse({"detail": exc.args[0]}, status_code=404)
    except ValueError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=400)
    except Exception as exc:
        print("[SAM] Register error:", exc)
        return JSONResponse({"detail": str(exc)}, status_code=500)
    _touch_heartbeat()
    print(f"[SAM] Registered inventory embedding: {saved_name}")
    return JSONResponse({
        "ok": True,
        "object_name": saved_name,
        "embedding_dim": len(embedding),
    })


@app.delete("/api/sam/session/{session_id}")
def delete_sam_session(session_id: str):
    discard_sam_session(session_id)
    return JSONResponse({"ok": True})


@app.get("/api/face/status")
def get_face_status():
    return JSONResponse(face_status_payload())


@app.post("/api/face/mode")
def post_face_mode(body: FaceModeBody):
    try:
        mode = set_face_mode(body.mode)
    except ValueError:
        return JSONResponse(
            {"detail": "Invalid face mode. Use off, recognize, or register."},
            status_code=400,
        )
    return JSONResponse(face_status_payload() | {"status": "changed", "mode": mode})


def _register_staff_face(staff_id, staff_name, crop_bytes=None):
    global pending_face_embedding, pending_face_crop, ready_to_register, face_message
    staff_id = (staff_id or "").strip()
    staff_name = " ".join((staff_name or "").split())
    if not staff_id or not staff_name:
        return JSONResponse(
            {"detail": "staff_id and staff_name are required"},
            status_code=400,
        )
    print(f"[FACE] Register start {staff_id} / {staff_name}")
    with face_state_lock:
        embedding = list(pending_face_embedding) if pending_face_embedding else None
        crop = crop_bytes or pending_face_crop
    if embedding is None and crop:
        print("[FACE] Encoding captured crop on CPU")
        try:
            embedding = face_crop_to_embedding(crop)
        except Exception as exc:
            print("[FACE] Register embed error:", exc)
            embedding = None
    if embedding is None:
        return JSONResponse(
            {
                "detail": "Face crop was not captured. Put your face in the outline again.",
            },
            status_code=400,
        )
    print("[FACE] Inserting staff row")
    try:
        saved = insert_staff(staff_id, staff_name, embedding)
    except ValueError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=409)
    except Exception as exc:
        print("[FACE] Register error:", exc)
        return JSONResponse(
            {"detail": f"Could not save staff face: {exc}"},
            status_code=500,
        )
    with face_state_lock:
        pending_face_embedding = None
        pending_face_crop = None
        ready_to_register = False
        face_message = f"Registered {saved['staff_name']}"
    print(f"[FACE] Registered {saved['staff_name']} ({saved['staff_id']})")
    return JSONResponse({"status": "saved", **saved})


@app.post("/api/face/register")
def post_face_register(body: StaffRegisterBody):
    crop_bytes = None
    if body.image_b64:
        try:
            crop_bytes = base64.b64decode(body.image_b64)
        except Exception:
            crop_bytes = None
    return _register_staff_face(body.staff_id, body.staff_name, crop_bytes)


@app.post("/api/face/embed")
async def embed_captured_face(file: UploadFile = File(...), mode: str = Form("")):
    """Store the captured face crop and compute a CPU embedding before Save."""
    image_bytes = await file.read()
    if not image_bytes:
        return JSONResponse({"detail": "Empty face crop"}, status_code=400)
    requested = (mode or "").strip().lower()
    with face_state_lock:
        pending_face_crop = image_bytes
        use_mode = requested if requested in VALID_FACE_MODES else face_mode
    print(f"[FACE] Crop captured ({len(image_bytes)} bytes) — encoding")
    try:
        embedding = face_crop_to_embedding(image_bytes)
    except Exception as exc:
        print("[FACE] Capture embed error:", exc)
        return JSONResponse({"detail": f"Could not embed captured face: {exc}"}, status_code=500)
    _apply_face_embedding(embedding, use_mode)
    print(f"[FACE] Crop embedding ready ({len(embedding)}-d)")
    return JSONResponse(face_status_payload() | {
        "ok": True,
        "embed_ready": True,
        "mode": use_mode,
        "dim": len(embedding),
    })


@app.post("/api/face/analyze")
async def analyze_face_frame(file: UploadFile = File(...)):
    if face_gate is None:
        return JSONResponse({"detail": "Face model is not loaded"}, status_code=503)
    image_bytes = await file.read()
    if not image_bytes:
        return JSONResponse({"detail": "Empty frame"}, status_code=400)
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        return JSONResponse({"detail": "Could not decode frame"}, status_code=400)
    _unused, info = face_gate.process(frame, draw=False)
    handle_face_info(info)
    print(
        f"[FACE] analyze detected={info.get('detected')} "
        f"in_region={info.get('in_region')} complete={info.get('complete')}"
    )
    payload = face_status_payload()
    in_region = bool(info.get("in_region"))
    payload["detected"] = bool(info.get("detected"))
    payload["in_region"] = in_region
    if in_region:
        payload["points"] = [
            {"x": float(x), "y": float(y)} for x, y in (info.get("points5") or [])
        ]
        payload["mesh"] = [
            {"x": float(x), "y": float(y)} for x, y in (info.get("mesh") or [])
        ]
        crop_bytes = info.get("crop_bytes")
        payload["face_preview_b64"] = (
            base64.b64encode(crop_bytes).decode("ascii") if crop_bytes else ""
        )
    else:
        payload["points"] = []
        payload["mesh"] = []
        payload["face_preview_b64"] = ""
    return JSONResponse(payload)


@app.post("/api/camera/start")
def api_start_camera():
    return JSONResponse({"ok": True, "camera_ok": True, "preview": "browser"})


@app.post("/api/detection/arm")
def arm_object_detection():
    global scan_warmup_count, scan_settle_count, scan_session
    with face_state_lock:
        staff = dict(recognized_staff) if recognized_staff else None
    if not staff:
        return JSONResponse(
            {"detail": "Recognize a staff member before starting object recognition."},
            status_code=409,
        )

    set_object_detection_armed(True)
    scan_warmup_count = 0
    scan_settle_count = 0
    scan_session = datetime.now().strftime("%Y%m%d_%H%M%S")
    reset_background_subtractor()
    set_yolo_overlay([])
    set_trigger_state("WARMUP")
    print(f"[DETECTION] Armed by {staff['staff_name']}")
    return JSONResponse({
        "ok": True,
        "detection_armed": True,
        "state": get_trigger_state(),
    })


@app.post("/api/scan/frame")
async def ingest_browser_scan(file: UploadFile = File(...)):
    if not is_object_detection_armed():
        return JSONResponse({"ok": True, "skipped": "not_armed"})
    if face_detection_active():
        return JSONResponse({"ok": True, "skipped": "face"})
    image_bytes = await file.read()
    if not image_bytes:
        return JSONResponse({"detail": "Empty frame"}, status_code=400)
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        return JSONResponse({"detail": "Could not decode frame"}, status_code=400)
    ingest_scan_frame(cv2.flip(frame, 1))
    return JSONResponse({"ok": True, "state": get_trigger_state()})


@app.post("/api/face/clear")
def post_face_clear():
    global recognized_staff, SCAN_OPERATOR
    set_face_mode("off")
    with face_state_lock:
        recognized_staff = None
        SCAN_OPERATOR = "System"
    return JSONResponse(face_status_payload())


def catalog_import_active():
    with catalog_import_lock:
        return bool(catalog_import_state["running"])


def _catalog_progress(**changes):
    with catalog_import_lock:
        catalog_import_state.update(changes)
        stage = catalog_import_state["stage"]
        processed = int(catalog_import_state.get("processed") or 0)
        total = max(1, int(catalog_import_state.get("total") or 1))
        ratio = min(1.0, processed / total)
        if stage == "selecting":
            percent = 2
        elif stage == "cropping":
            percent = 5 + round(ratio * 20)
        elif stage == "embedding":
            percent = 25 + round(ratio * 68)
        elif stage == "database":
            percent = 96
        elif stage == "complete":
            percent = 100
        elif stage == "failed":
            percent = catalog_import_state.get("percent", 0)
        else:
            percent = 0
        catalog_import_state["percent"] = percent


def _catalog_import_job(image_dir, label_dir):
    try:
        result = import_train_catalog(
            image_dir,
            label_dir,
            images_to_embeddings,
            replace_inventory_embeddings,
            _catalog_progress,
        )
        refresh_inventory_catalog_cache()
        _catalog_progress(
            running=False,
            stage="complete",
            result=result,
            error="",
            current="",
        )
        print(
            "[CATALOG] Complete: "
            f"{result['embeddings']} embeddings, "
            f"{result['unique_items']} unique items"
        )
    except Exception as exc:
        print("[CATALOG] Import failed:", exc)
        _catalog_progress(running=False, stage="failed", error=str(exc))


@app.get("/api/catalog/import/status")
def catalog_import_status():
    with catalog_import_lock:
        return JSONResponse(dict(catalog_import_state))


@app.post("/api/catalog/import/select")
async def select_and_import_catalog():
    with catalog_import_lock:
        if catalog_import_state["running"]:
            return JSONResponse(
                {"detail": "A catalog import is already running."},
                status_code=409,
            )
    _catalog_progress(
        running=True,
        stage="selecting",
        percent=2,
        processed=0,
        total=0,
        embedded=0,
        current="",
        error="",
        result=None,
    )
    dataset_root = os.path.normpath(
        os.path.join(BASE_DIR, "..", "train_v2", "dataset")
    )
    image_dir = await asyncio.to_thread(
        choose_folder,
        "Select train image folder (images/train)",
        os.path.join(dataset_root, "images", "train"),
    )
    if not image_dir:
        _catalog_progress(running=False, stage="idle", error="Folder selection cancelled.")
        return JSONResponse({"detail": "Image folder selection cancelled."}, status_code=400)
    label_dir = await asyncio.to_thread(
        choose_folder,
        "Select train label folder (labels/train)",
        os.path.join(dataset_root, "labels", "train"),
    )
    if not label_dir:
        _catalog_progress(running=False, stage="idle", error="Folder selection cancelled.")
        return JSONResponse({"detail": "Label folder selection cancelled."}, status_code=400)

    threading.Thread(
        target=_catalog_import_job,
        args=(image_dir, label_dir),
        name="CatalogImport",
        daemon=True,
    ).start()
    with catalog_import_lock:
        return JSONResponse(dict(catalog_import_state))


# ============================================================
# TRIGGER STATUS API
# ============================================================

@app.get("/api/trigger_status")
def trigger_status():
    with yolo_overlay_lock:
        preview_remaining = max(0.0, annotated_hold_until - time.monotonic())
        preview_active = bool(annotated_hold_jpeg and preview_remaining > 0)
        labels = list(yolo_labels)
        boxes = [
            {
                "name": item.get("name") or "object",
                "confidence": round(float(item.get("confidence", 0.0)), 4),
                "similarity": (
                    round(float(item["identity_score"]), 4)
                    if item.get("identity_score", -1) >= 0
                    else None
                ),
                "box": [round(float(value), 5) for value in item.get("box_norm", ())],
            }
            for item in yolo_boxes
            if len(item.get("box_norm", ())) == 4
        ]
    with inventory_revision_lock:
        revision = inventory_revision
    with face_state_lock:
        can_arm_detection = recognized_staff is not None
    detection_armed = is_object_detection_armed()
    if face_detection_active():
        state = "FACE"
    elif preview_active:
        state = "PREVIEW"
    elif can_arm_detection and not detection_armed:
        state = "READY"
    else:
        state = get_trigger_state()
    return JSONResponse({
        "state": state,
        "detection_armed": detection_armed,
        "can_arm_detection": can_arm_detection,
        "preview_active": preview_active,
        "preview_remaining_ms": round(preview_remaining * 1000),
        "last_capture": last_capture,
        "last_detections": last_detections,
        "last_classes": last_classes,
        "yolo_labels": labels,
        "yolo_boxes": boxes,
        "inventory_revision": revision,
    })


@app.get("/api/detection/preview")
def detection_preview():
    with yolo_overlay_lock:
        active = bool(
            annotated_hold_jpeg
            and time.monotonic() < annotated_hold_until
        )
        frame_bytes = annotated_hold_jpeg if active else None
    if frame_bytes is None:
        return JSONResponse({"detail": "No detection preview is active."}, status_code=404)
    return Response(
        content=frame_bytes,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )


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
        refresh_inventory_catalog_cache()
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
        with frame_lock:
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
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )


@app.get("/video_frame")
def video_frame():
    with frame_lock:
        frame_bytes = latest_frame
    if frame_bytes is None:
        frame_bytes = make_error_frame(
            "Waiting for camera..." if camera_running else "Camera is stopped."
        )
    return Response(
        content=frame_bytes,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        },
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
    "sam-tool.css": "text/css",
    "config.js": "application/javascript",
    "dashboard.js": "application/javascript",
    "sam-tool.js": "application/javascript",
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
    global boot_ready, boot_done
    loader.start()
    try:
        set_boot(6, "connecting to database")
        bootstrap_database()
        clear_check_in_out()
        loader.pulse(0.15)

        set_boot(18, "preparing inventory tables")
        loader.pulse(0.1)

        set_boot(32, "loading YOLO weights")
        load_model()
        loader.pulse(0.12)

        set_boot(50, "loading embedding encoder")
        load_embed_model()
        loader.pulse(0.08)
        set_boot(58, "warming embedding encoder")
        loader.pulse(0.08)

        set_boot(64, "loading Segment Anything")
        load_sam_model()
        loader.pulse(0.12)

        set_boot(78, "loading face recognition")
        load_face_gate()
        loader.pulse(0.12)

        set_boot(88, "arming face gate")
        set_face_mode("recognize")
        loader.pulse(0.1)

        set_boot(100, "systems online")
        boot_ready = True
        boot_done = True
        lan_ip = get_lan_ip()
        local_url = f"http://127.0.0.1:{PORT}"
        lan_url = f"http://{lan_ip}:{PORT}" if lan_ip else None
        loader.finish(local_url, lan_url)
    except Exception as exc:
        boot_ready = True
        loader.fail(str(exc))


def open_chrome(url):
    candidates = [
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            subprocess.Popen([path, "--new-window", url])
            print("[APP] Opened Chrome:", url)
            return
    try:
        subprocess.Popen(["cmd", "/c", "start", "", "chrome", url], shell=False)
        print("[APP] Opened Chrome via PATH:", url)
        return
    except Exception:
        pass
    webbrowser.open(url)
    print("[APP] Opened default browser:", url)


def open_chrome_when_ready(url):
    import urllib.request
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=0.5)
            break
        except Exception:
            time.sleep(0.25)
    open_chrome(url)


def free_port(port):
    """Kill whatever is still bound to this app's port so a restart can bind."""
    if sys.platform != "win32":
        return
    try:
        output = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            errors="ignore",
        )
    except Exception:
        return
    pids = set()
    needle = f":{port}"
    for line in output.splitlines():
        if "LISTENING" not in line.upper() or needle not in line:
            continue
        pid = line.strip().split()[-1]
        if pid.isdigit() and int(pid) not in {0, os.getpid()}:
            pids.add(int(pid))
    for pid in pids:
        try:
            subprocess.check_call(
                ["taskkill", "/PID", str(pid), "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[APP] Freed port {port} by stopping PID {pid}")
        except Exception:
            pass


if __name__ == "__main__":
    free_port(PORT)
    run_high_end_boot()
    dashboard_url = f"http://127.0.0.1:{PORT}"
    def _force_close(*_args):
        print("\n[APP] Interrupt — force close")
        _clear_session_movements()
        close_boot_connection()
        os._exit(0)

    signal.signal(signal.SIGINT, _force_close)
    signal.signal(signal.SIGTERM, _force_close)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, _force_close)

    threading.Thread(
        target=open_chrome_when_ready,
        args=(dashboard_url,),
        name="OpenChrome",
        daemon=True,
    ).start()
    uvicorn.run(app, host=HOST, port=PORT, reload=False, log_level="warning")
