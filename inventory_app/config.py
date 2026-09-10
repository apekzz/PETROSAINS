import os

# App folder (this file's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
LOW_STOCK_THRESHOLD = 10

# Server
HOST = "127.0.0.1"
PORT = 8000

# Camera — change CAMERA_INDEX if the wrong webcam opens
CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
TARGET_FPS = 25
JPEG_QUALITY = 85

# AI Model
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
MODEL_CONFIDENCE = 0.25
MODEL_IMAGE_SIZE = 640