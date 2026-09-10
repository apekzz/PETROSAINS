import os

# App folder (this file's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
LOW_STOCK_THRESHOLD = 10

# Server
HOST = "127.0.0.1"
PORT = 8000

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

# Image-difference trigger (YOLO runs only on capture, not every frame)
TRIGGER_ENABLED = True
DIFF_THRESHOLD = 25          # MOG2 varThreshold
CHANGE_AREA_PERCENT = 5      # % of frame area that must change
SETTLE_FRAMES = 15           # frames to wait after trigger
TRIGGER_COOLDOWN = 5         # seconds between triggers
MOG2_HISTORY = 500
MOG2_VAR_THRESHOLD = DIFF_THRESHOLD
MOG2_DETECT_SHADOWS = False
WARMUP_FRAMES = 30
