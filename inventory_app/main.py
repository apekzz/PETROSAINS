import os
import sys
import time
import threading
import platform

import cv2
import numpy as np

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Safe import for the AI model
try:
    from ultralytics import YOLO
    import torch
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False
    print("[MODEL] Ultralytics or Torch not installed. AI detection is disabled.")

from api import router as api_router
from config import (
    BASE_DIR, HOST, PORT, CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    TARGET_FPS, JPEG_QUALITY, MODEL_PATH, MODEL_CONFIDENCE, MODEL_IMAGE_SIZE,
)

app = FastAPI(title="OneShot Inventory API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(api_router)

# ============================================================
# AI MODEL
# ============================================================
model = None
MODEL_DEVICE = "cpu"

if AI_ENABLED:
    print("[MODEL] Loading model...")
    try:
        model = YOLO(MODEL_PATH)
        MODEL_DEVICE = 0 if torch.cuda.is_available() else "cpu"
        print("[MODEL] Model loaded successfully.")
        print(f"[MODEL] Classes: {len(model.names)} | Device: {MODEL_DEVICE}")
    except Exception as e:
        print(f"[MODEL] Failed to load model: {e}")
        model = None

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

# ============================================================
# OPEN CAMERA
# ============================================================
def open_camera():
    global camera, camera_ok, camera_error
    if camera is not None:
        try: camera.release()
        except Exception: pass
        camera = None

    backend = cv2.CAP_AVFOUNDATION if sys.platform == "darwin" else cv2.CAP_ANY
    print(f"[CAMERA] Trying camera index {CAMERA_INDEX}...")
    try:
        camera = cv2.VideoCapture(CAMERA_INDEX, backend)
    except Exception as exc:
        camera = None; camera_ok = False; camera_error = f"Could not create VideoCapture: {exc}"
        print("[CAMERA]", camera_error); return False

    if camera is None or not camera.isOpened():
        camera_error = f"Camera index {CAMERA_INDEX} could not be opened."
        camera_ok = False; print("[CAMERA]", camera_error)
        if camera is not None:
            try: camera.release()
            except Exception: pass
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
                print("[CAMERA] WARNING: Frames are black. Check FaceTime/Zoom!")
            else:
                print("[CAMERA] Camera feed is live!")
            camera_ok = True; camera_error = ""
            print(f"[CAMERA] Ready: {int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))} x {int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            return True
        time.sleep(0.1)

    camera_error = "Camera opened, but frames could not be read."
    camera_ok = False; print("[CAMERA]", camera_error)
    try: camera.release()
    except Exception: pass
    camera = None; return False

# ============================================================
# CAMERA CAPTURE LOOP (FIXED INDENTATION)
# ============================================================
def camera_capture_loop():
    global latest_frame, camera_ok, camera_error, camera_running
    frame_interval = 1.0 / TARGET_FPS

    while camera_running:
        if camera is None or not camera.isOpened():
            camera_ok = False
            if not open_camera():
                time.sleep(2); continue

        start_time = time.monotonic()
        with camera_lock:
            ok, frame = camera.read()

        # FIXED: This block is now INSIDE the while loop
        if ok and frame is not None:
            frame = cv2.flip(frame, 1)
            if model is not None:
                try:
                    results = model.predict(source=frame, imgsz=MODEL_IMAGE_SIZE, conf=MODEL_CONFIDENCE, device=MODEL_DEVICE, verbose=False)
                    frame = results[0].plot()
                except Exception as exc:
                    print("[MODEL] Inference error:", exc)

            encode_ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if encode_ok:
                with camera_lock:
                    latest_frame = encoded.tobytes()
                    camera_ok = True; camera_error = ""
            else:
                camera_ok = False; camera_error = "JPEG encoding failed."
        else:
            camera_ok = False; camera_error = "Camera frame read failed."
            time.sleep(0.1)

        elapsed = time.monotonic() - start_time
        time.sleep(max(0.001, frame_interval - elapsed))

    camera_ok = False

# ============================================================
# START / STOP CAMERA
# ============================================================
def start_camera():
    global camera_thread, camera_running
    if camera_running: return
    print("[CAMERA] Starting camera...")
    camera_running = True
    open_camera()
    camera_thread = threading.Thread(target=camera_capture_loop, name="CameraCapture", daemon=True)
    camera_thread.start()

def stop_camera():
    global camera_running, camera, latest_frame
    camera_running = False
    if camera_thread is not None and camera_thread.is_alive():
        camera_thread.join(timeout=2)
    with camera_lock:
        if camera is not None:
            try: camera.release()
            except Exception: pass
            camera = None
        latest_frame = None
    print("[CAMERA] Stopped.")

@app.on_event("startup")
def startup_event(): start_camera()

@app.on_event("shutdown")
def shutdown_event(): stop_camera()

# ============================================================
# CAMERA STATUS API
# ============================================================
@app.get("/camera_status")
def camera_status():
    if camera is not None and camera.isOpened():
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
        width = 0; height = 0
    return JSONResponse({"ok": camera_ok, "camera_index": CAMERA_INDEX, "platform": platform.system(), "width": width, "height": height, "error": camera_error})

# ============================================================
# ERROR FRAME
# ============================================================
def make_error_frame(text):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, "ONESHOT CAMERA", (145, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, text, (65, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2, cv2.LINE_AA)
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    return encoded.tobytes() if ok else b""

# ============================================================
# MJPEG FRAME GENERATOR (FIXED HEADER FOR BROWSER)
# ============================================================
def generate_frames():
    while True:
        with camera_lock:
            frame_bytes = latest_frame
        if frame_bytes is None:
            frame_bytes = make_error_frame("Waiting for camera..." if camera_running else "Camera is stopped.")

        # Standard MJPEG format. No custom Content-Length headers.
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        time.sleep(0.04)

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    dashboard_path = os.path.join(BASE_DIR, "dashboard.html")
    if not os.path.exists(dashboard_path):
        return HTMLResponse("<h1>dashboard.html not found</h1>", status_code=500)
    with open(dashboard_path, "r", encoding="utf-8") as file:
        html = file.read()
    return HTMLResponse(content=html)

FRONTEND_FILES = {"theme.css": "text/css", "dashboard.css": "text/css", "config.js": "application/javascript", "dashboard.js": "application/javascript"}

@app.get("/{filename}")
def serve_frontend_file(filename: str):
    media_type = FRONTEND_FILES.get(filename)
    if media_type is None: return JSONResponse({"detail": "Not found"}, status_code=404)
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path): return JSONResponse({"detail": f"{filename} not found"}, status_code=404)
    return FileResponse(file_path, media_type=media_type)

# ============================================================
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    print("\n==========================================")
    print(" OneShot Inventory")
    print("==========================================")
    print(f" Dashboard: http://{HOST}:{PORT}")
    print(f" Camera:    http://{HOST}:{PORT}/video_feed")
    print("==========================================\n")
    uvicorn.run(app, host=HOST, port=PORT, reload=False)