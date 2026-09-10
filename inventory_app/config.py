import os

# App folder (this file's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
LOW_STOCK_THRESHOLD = 10

# Server
HOST = "127.0.0.1"
PORT = 8000

# Camera — Lower resolution = faster AI processing & no stream lag
CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TARGET_FPS = 25
JPEG_QUALITY = 85

# AI Model
# If you have your own trained model (best.pt), change this to:
# MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
MODEL_PATH = "yolov8n.pt"   # Auto-downloads if missing
MODEL_CONFIDENCE = 0.25
MODEL_IMAGE_SIZE = 640