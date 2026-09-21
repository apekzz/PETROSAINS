import os
import socket

# Project root (folder that contains main.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Database (PostgreSQL). Override with a .env file or DATABASE_URL.
def _load_dotenv():
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


_load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://oneshot:oneshot@127.0.0.1:5432/oneshot_inventory",
)
SQLITE_PATH = os.path.join(DATABASE_DIR, "inventory.db")
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

# AI Model — YOLO11l-seg v2 (BCE + Dice) from train_v2
MODEL_PATH = os.path.join(BASE_DIR, "models", "yolo11l_seg_object_bce_dice.pt")
MODEL_FALLBACK_PATH = os.path.join(BASE_DIR, "models", "best.pt")
OPENCLIP_CHECKPOINT = os.environ.get(
    "OPENCLIP_CHECKPOINT",
    os.path.join(BASE_DIR, "models", "open_clip_pytorch_model.bin"),
)
MODEL_CONFIDENCE = 0.25
MODEL_IMAGE_SIZE = 640

# Image-difference trigger (YOLO capture stays off the live camera thread)
TRIGGER_ENABLED = True
DIFF_THRESHOLD = 25          # MOG2 varThreshold
CHANGE_AREA_PERCENT = 5      # % of frame area that must change
SETTLE_FRAMES = 6            # frames to wait after trigger
TRIGGER_COOLDOWN = 3         # seconds between triggers
MOG2_HISTORY = 500
MOG2_VAR_THRESHOLD = DIFF_THRESHOLD
MOG2_DETECT_SHADOWS = False
WARMUP_FRAMES = 12

# Live YOLO boxes (preview runs on a background thread so MJPEG stays smooth)
YOLO_PREVIEW_ENABLED = True
YOLO_PREVIEW_INTERVAL = 0.12
YOLO_HOLD_SECONDS = 1.5

# Face gate (register / recognize)
# Histogram embeds (restored staff.csv). Margin+streak cut wrong flips.
FACE_MATCH_THRESHOLD = float(os.environ.get("FACE_MATCH_THRESHOLD", "0.90"))
FACE_MATCH_MARGIN = float(os.environ.get("FACE_MATCH_MARGIN", "0.025"))
FACE_MATCH_STREAK = int(os.environ.get("FACE_MATCH_STREAK", "3"))
FACE_EMBED_INTERVAL = 0.28
