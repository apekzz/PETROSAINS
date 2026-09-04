import cv2
import sqlite3
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/inventory")
def get_inventory():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM inventory").fetchall()
    conn.close()
    return [dict(item) for item in items]

@app.get("/api/search?q={query}")
def search_inventory(query: str):
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM inventory WHERE item_name LIKE ?", (f"%{query}%",)).fetchall()
    conn.close()
    return [dict(item) for item in items]

# Using 0 will select your MacBook's FaceTime HD camera
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    with open("dashboard.html", "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    # Changed from 0.0.0.0 to 127.0.0.1 for local Mac testing
    uvicorn.run(app, host="127.0.0.1", port=8000)