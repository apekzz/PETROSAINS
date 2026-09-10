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

from ultralytics import YOLO

from api import router as api_router
from config import (
    BASE_DIR,
    HOST,
    PORT,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    TARGET_FPS,
    JPEG_QUALITY,
    MODEL_PATH,
    MODEL_CONFIDENCE,
    MODEL_IMAGE_SIZE,
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="OneShot Inventory API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# ============================================================
# AI MODEL
# ============================================================

import torch

print("[MODEL] Loading best model...")
print("[MODEL] Path:", MODEL_PATH)

model = YOLO(MODEL_PATH)

MODEL_DEVICE = 0 if torch.cuda.is_available() else "cpu"

print("[MODEL] Best model loaded successfully.")
print("[MODEL] Classes:", len(model.names))
print("[MODEL] Device:", MODEL_DEVICE)


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
    """
    Open the camera.

    macOS:
        Uses AVFoundation.

    Windows/Linux:
        Uses OpenCV default backend.
    """

    global camera
    global camera_ok
    global camera_error

    # Release previous camera if one exists
    if camera is not None:

        try:
            camera.release()

        except Exception:
            pass

        camera = None

    # --------------------------------------------------------
    # Select correct backend
    # --------------------------------------------------------

    if sys.platform == "darwin":

        backend = cv2.CAP_AVFOUNDATION

    else:

        backend = cv2.CAP_ANY

    print(
        f"[CAMERA] Trying camera index {CAMERA_INDEX}..."
    )

    # --------------------------------------------------------
    # Create VideoCapture
    # --------------------------------------------------------

    try:

        camera = cv2.VideoCapture(
            CAMERA_INDEX,
            backend
        )

    except Exception as exc:

        camera = None

        camera_ok = False

        camera_error = (
            f"Could not create VideoCapture: {exc}"
        )

        print(
            "[CAMERA]",
            camera_error
        )

        return False

    # --------------------------------------------------------
    # Check camera
    # --------------------------------------------------------

    if camera is None or not camera.isOpened():

        camera_error = (
            f"Camera index {CAMERA_INDEX} could not be opened. "
            "Check macOS Camera permission and CAMERA_INDEX."
        )

        camera_ok = False

        print(
            "[CAMERA]",
            camera_error
        )

        if camera is not None:

            try:
                camera.release()

            except Exception:
                pass

            camera = None

        return False

    # --------------------------------------------------------
    # Request camera settings
    # --------------------------------------------------------

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    camera.set(
        cv2.CAP_PROP_FPS,
        TARGET_FPS
    )

    # --------------------------------------------------------
    # Warm up camera
    # --------------------------------------------------------

    print("[CAMERA] Warming up...")

    for _ in range(20):

        ok, frame = camera.read()

        if ok and frame is not None:

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

            camera_ok = True

            camera_error = ""

            print(
                f"[CAMERA] Ready: "
                f"{actual_width} x {actual_height}"
            )

            return True

        time.sleep(0.05)

    # --------------------------------------------------------
    # Failed to read frames
    # --------------------------------------------------------

    camera_error = (
        "Camera opened, but frames could not be read. "
        "Check camera permission or another application "
        "using the camera."
    )

    camera_ok = False

    print(
        "[CAMERA]",
        camera_error
    )

    try:

        camera.release()

    except Exception:
        pass

    camera = None

    return False


# ============================================================
# CAMERA CAPTURE LOOP
# ============================================================

def camera_capture_loop():

    global latest_frame
    global camera_ok
    global camera_error
    global camera_running

    frame_interval = 1.0 / TARGET_FPS

    while camera_running:

        # ----------------------------------------------------
        # Reconnect camera if necessary
        # ----------------------------------------------------

        if camera is None or not camera.isOpened():

            camera_ok = False

            if not open_camera():

                time.sleep(2)

                continue

        # ----------------------------------------------------
        # Read frame
        # ----------------------------------------------------

        start_time = time.monotonic()

        with camera_lock:

            ok, frame = camera.read()

        # ----------------------------------------------------
        # Successful frame
        # ----------------------------------------------------

    if ok and frame is not None:

        # Mirror camera like a normal webcam
        frame = cv2.flip(
            frame,
            1
        )

        # ------------------------------------------------
        # AI INFERENCE
        # ------------------------------------------------

        try:
            results = model.predict(
                source=frame,
                imgsz=MODEL_IMAGE_SIZE,
                conf=MODEL_CONFIDENCE,
                device=MODEL_DEVICE,
                verbose=False
            )

            result = results[0]

            # Draw segmentation mask, bbox,
            # class name and confidence
            frame = result.plot()

        except Exception as exc:

            print(
                "[MODEL] Inference error:",
                exc
            )

        # ------------------------------------------------
        # Encode JPEG
        # ------------------------------------------------

        encode_ok, encoded = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                JPEG_QUALITY
            ]
        )

        if encode_ok:

            with camera_lock:

                latest_frame = encoded.tobytes()

                camera_ok = True

                camera_error = ""

        # ----------------------------------------------------
        # Failed frame
        # ----------------------------------------------------

        else:

            camera_ok = False

            camera_error = (
                "Camera frame read failed."
            )

            time.sleep(0.1)

        # ----------------------------------------------------
        # Maintain 25 FPS
        # ----------------------------------------------------

        elapsed = (
            time.monotonic()
            - start_time
        )

        sleep_time = max(
            0.001,
            frame_interval - elapsed
        )

        time.sleep(
            sleep_time
        )

    camera_ok = False


# ============================================================
# START CAMERA
# ============================================================

def start_camera():

    global camera_thread
    global camera_running

    if camera_running:

        return

    print(
        "[CAMERA] Starting camera..."
    )

    camera_running = True

    # Try to open camera immediately
    open_camera()

    # Start background capture
    camera_thread = threading.Thread(
        target=camera_capture_loop,
        name="CameraCapture",
        daemon=True
    )

    camera_thread.start()


# ============================================================
# STOP CAMERA
# ============================================================

def stop_camera():

    global camera_running
    global camera
    global latest_frame

    camera_running = False

    # Wait for camera thread
    if (
        camera_thread is not None
        and camera_thread.is_alive()
    ):

        camera_thread.join(
            timeout=2
        )

    with camera_lock:

        if camera is not None:

            try:

                camera.release()

            except Exception:
                pass

            camera = None

        latest_frame = None

    print(
        "[CAMERA] Stopped."
    )


# ============================================================
# FASTAPI STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    start_camera()


# ============================================================
# FASTAPI SHUTDOWN
# ============================================================

@app.on_event("shutdown")
def shutdown_event():

    stop_camera()


# ============================================================
# CAMERA STATUS API
# ============================================================

@app.get("/camera_status")
def camera_status():

    if (
        camera is not None
        and camera.isOpened()
    ):

        width = int(
            camera.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        height = int(
            camera.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

    else:

        width = 0

        height = 0

    return JSONResponse(
        {
            "ok": camera_ok,

            "camera_index":
                CAMERA_INDEX,

            "platform":
                platform.system(),

            "width":
                width,

            "height":
                height,

            "error":
                camera_error
        }
    )


# ============================================================
# ERROR FRAME
# ============================================================

def make_error_frame(text):

    frame = np.zeros(
        (
            480,
            640,
            3
        ),
        dtype=np.uint8
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    cv2.putText(
        frame,
        "ONESHOT CAMERA",
        (145, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    # --------------------------------------------------------
    # Error message
    # --------------------------------------------------------

    cv2.putText(
        frame,
        text,
        (65, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )

    # --------------------------------------------------------
    # Encode
    # --------------------------------------------------------

    ok, encoded = cv2.imencode(
        ".jpg",
        frame,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            JPEG_QUALITY
        ]
    )

    if ok:

        return encoded.tobytes()

    return b""


# ============================================================
# MJPEG FRAME GENERATOR
# ============================================================

def generate_frames():

    last_frame = None

    while True:

        # ----------------------------------------------------
        # Get latest frame
        # ----------------------------------------------------

        with camera_lock:

            frame_bytes = latest_frame

        # ----------------------------------------------------
        # Camera not ready
        # ----------------------------------------------------

        if frame_bytes is None:

            if camera_running:

                frame_bytes = make_error_frame(
                    "Waiting for camera..."
                )

            else:

                frame_bytes = make_error_frame(
                    "Camera is stopped."
                )

        # ----------------------------------------------------
        # Prevent excessive CPU usage
        # ----------------------------------------------------

        if frame_bytes == last_frame:

            time.sleep(
                0.01
            )

        else:

            last_frame = frame_bytes

        # ----------------------------------------------------
        # MJPEG response
        # ----------------------------------------------------

        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n"

            b"Cache-Control: no-cache\r\n"

            b"Pragma: no-cache\r\n"

            b"Content-Length: "
            + str(
                len(frame_bytes)
            ).encode()
            + b"\r\n\r\n"

            + frame_bytes

            + b"\r\n"
        )


# ============================================================
# VIDEO FEED
# ============================================================

@app.get("/video_feed")
def video_feed():

    return StreamingResponse(

        generate_frames(),

        media_type=(
            "multipart/"
            "x-mixed-replace;"
            " boundary=frame"
        ),

        headers={
            "Cache-Control":
                "no-cache, no-store, "
                "must-revalidate",

            "Pragma":
                "no-cache",

            "Expires":
                "0"
        }
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def serve_dashboard():

    dashboard_path = os.path.join(
        BASE_DIR,
        "dashboard.html"
    )

    # --------------------------------------------------------
    # Check dashboard
    # --------------------------------------------------------

    if not os.path.exists(
        dashboard_path
    ):

        return HTMLResponse(
            "<h1>dashboard.html not found</h1>",
            status_code=500
        )

    # --------------------------------------------------------
    # Read dashboard
    # --------------------------------------------------------

    with open(
        dashboard_path,
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    return HTMLResponse(
        content=html
    )


FRONTEND_FILES = {
    "theme.css": "text/css",
    "dashboard.css": "text/css",
    "config.js": "application/javascript",
    "dashboard.js": "application/javascript",
}


@app.get("/{filename}")
def serve_frontend_file(filename: str):
    media_type = FRONTEND_FILES.get(filename)

    if media_type is None:
        return JSONResponse(
            {"detail": "Not found"},
            status_code=404
        )

    file_path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(file_path):
        return JSONResponse(
            {"detail": f"{filename} not found"},
            status_code=404
        )

    return FileResponse(
        file_path,
        media_type=media_type
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        " OneShot Inventory"
    )

    print(
        "=========================================="
    )

    print(
        f" Dashboard: http://{HOST}:{PORT}"
    )

    print(
        f" Camera:    http://{HOST}:{PORT}/video_feed"
    )

    print(
        f" Status:    http://{HOST}:{PORT}/camera_status"
    )

    print(
        "=========================================="
    )

    print()

    uvicorn.run(

        app,

        host=HOST,

        port=PORT,

        reload=False
    )