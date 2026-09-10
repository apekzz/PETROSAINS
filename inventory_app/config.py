import os
import socket

# App folder (this file's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
LOW_STOCK_THRESHOLD = 10

# Server — 0.0.0.0 lets phones/laptops on the same Wi-Fi open the dashboard
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))


def get_lan_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    return None

# Camera
CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))
CAMERA_WIDTH = 640   # Lowered for faster AI processing (fixes black screen lag)
CAMERA_HEIGHT = 480  # Lowered for faster AI processing
TARGET_FPS = 25
JPEG_QUALITY = 85

# AI Model (YOUR ORIGINAL MODEL)
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
MODEL_CONFIDENCE = 0.25
MODEL_IMAGE_SIZE = 640

# Image-difference trigger (YOLO capture stays off the live camera thread)
TRIGGER_ENABLED = True
DIFF_THRESHOLD = 25          # MOG2 varThreshold
CHANGE_AREA_PERCENT = 5      # % of frame area that must change
SETTLE_FRAMES = 15           # frames to wait after trigger
TRIGGER_COOLDOWN = 5         # seconds between triggers
MOG2_HISTORY = 500
MOG2_VAR_THRESHOLD = DIFF_THRESHOLD
MOG2_DETECT_SHADOWS = False
WARMUP_FRAMES = 30

# Live YOLO boxes (preview runs on a background thread so MJPEG stays smooth)
YOLO_PREVIEW_ENABLED = True
YOLO_PREVIEW_INTERVAL = 0.28
YOLO_HOLD_SECONDS = 4
