"""Standalone SAM object-registration proof of concept.

Run from the repository root: ``python sam_standalone/app.py``.
This module deliberately does not import or modify inventory_app.
"""

from __future__ import annotations

import base64
import io
import os
import sys
import threading
import uuid
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from PIL import Image, ImageOps
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.embed import CLIP_DIM, get_clip_embedding, load_clip_model
from utils_db.config import PgConfig
from utils_db.store import close_db, connect_db

APP_DIR = Path(__file__).resolve().parent
MAX_BYTES = 15 * 1024 * 1024
sessions: dict[str, dict] = {}
sessions_lock = threading.Lock()
sam_predictor = None
sam_lock = threading.RLock()
clipper = None
clip_lock = threading.Lock()

app = FastAPI(title="PETROSAINS SAM Registration POC")


class Upload(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    image_data: str


class Prompts(BaseModel):
    session_id: str
    points: list[list[float]]
    labels: list[int]


class SaveRequest(BaseModel):
    session_id: str
    object_name: str = Field(min_length=1, max_length=200)
    mask_data: str


def decode_image(data_url: str, mode: str) -> np.ndarray:
    try:
        raw = base64.b64decode(data_url.split(",", 1)[-1], validate=True)
        if not raw or len(raw) > MAX_BYTES:
            raise ValueError("Image is empty or exceeds 15 MB.")
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            return np.asarray(ImageOps.exif_transpose(image).convert(mode))
    except Exception as exc:
        raise ValueError(f"Could not read image: {exc}") from exc


def data_url(mask: np.ndarray) -> str:
    output = io.BytesIO()
    Image.fromarray((mask > 0).astype(np.uint8) * 255, "L").save(output, "PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()


def session(session_id: str) -> dict:
    value = sessions.get(session_id)
    if value is None:
        raise HTTPException(404, "Session not found. Upload the image again.")
    return value


def get_sam():
    global sam_predictor
    with sam_lock:
        if sam_predictor is not None:
            return sam_predictor
        checkpoint = Path(os.environ.get("SAM_CHECKPOINT", ROOT / "models" / "sam_vit_b_01ec64.pth"))
        if not checkpoint.exists():
            raise RuntimeError(f"SAM checkpoint not found: {checkpoint}")
        try:
            import torch
            from segment_anything import SamPredictor, sam_model_registry
        except ImportError as exc:
            raise RuntimeError("Install segment-anything first.") from exc
        model_type = os.environ.get("SAM_MODEL_TYPE", "vit_b")
        model = sam_model_registry[model_type](checkpoint=str(checkpoint))
        model.to("cuda" if torch.cuda.is_available() else "cpu")
        sam_predictor = SamPredictor(model)
        return sam_predictor


def get_clipper():
    global clipper
    with clip_lock:
        if clipper is None:
            clipper = load_clip_model()
        return clipper


@app.get("/", response_class=HTMLResponse)
def page():
    return HTMLResponse((APP_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/app.js")
def javascript():
    return FileResponse(APP_DIR / "app.js", media_type="application/javascript")


@app.get("/style.css")
def stylesheet():
    return FileResponse(APP_DIR / "style.css", media_type="text/css")


@app.post("/api/image")
def upload(payload: Upload):
    try:
        image = decode_image(payload.image_data, "RGB")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    session_id = uuid.uuid4().hex
    sessions[session_id] = {"image": image, "filename": Path(payload.filename).name, "saved": False}
    return {"session_id": session_id, "width": image.shape[1], "height": image.shape[0]}


@app.post("/api/mask")
def create_mask(payload: Prompts):
    current = session(payload.session_id)
    coords = np.asarray(payload.points, dtype=np.float32)
    labels = np.asarray(payload.labels, dtype=np.int32)
    height, width = current["image"].shape[:2]
    if coords.ndim != 2 or coords.shape != (len(labels), 2) or not len(coords):
        raise HTTPException(400, "Provide one x,y pair and label for every prompt.")
    if not np.isin(labels, [0, 1]).all() or not np.any(labels == 1):
        raise HTTPException(400, "Use at least one foreground point; labels are 1 or 0.")
    if not np.isfinite(coords).all() or (coords[:, 0] < 0).any() or (coords[:, 0] >= width).any() or (coords[:, 1] < 0).any() or (coords[:, 1] >= height).any():
        raise HTTPException(400, "A prompt is outside the original image.")
    try:
        with sam_lock:
            predictor = get_sam()
            predictor.set_image(current["image"])
            masks, scores, _ = predictor.predict(point_coords=coords, point_labels=labels, multimask_output=True)
        mask = masks[int(np.argmax(scores))]
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    if not mask.any():
        raise HTTPException(422, "SAM returned an empty mask. Try another foreground point.")
    return {"mask_data": data_url(mask), "pixels": int(mask.sum())}


@app.post("/api/register")
def register(payload: SaveRequest):
    current = session(payload.session_id)
    if current["saved"]:
        raise HTTPException(409, "This upload has already been saved.")
    try:
        mask = decode_image(payload.mask_data, "L") > 127
        image = current["image"]
        if mask.shape != image.shape[:2]:
            raise ValueError("Mask does not match the uploaded image.")
        ys, xs = np.nonzero(mask)
        if not len(xs):
            raise ValueError("Final mask is empty.")
        x1, x2 = max(0, xs.min() - 8), min(image.shape[1], xs.max() + 9)
        y1, y2 = max(0, ys.min() - 8), min(image.shape[0], ys.max() + 9)
        crop = image[y1:y2, x1:x2].copy()
        crop[~mask[y1:y2, x1:x2]] = 255
        embedding = get_clip_embedding(get_clipper(), Image.fromarray(crop))
        if embedding.size != CLIP_DIM or not np.isfinite(embedding).all():
            raise ValueError("OpenCLIP did not produce a valid 512-dimensional embedding.")
        cfg = PgConfig(
            host=os.environ.get("PGHOST", "127.0.0.1"), port=int(os.environ.get("PGPORT", "5432")),
            db=os.environ.get("PGDATABASE", "petrosains"), user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", ""),
        )
        conn = connect_db(cfg)
        try:
            with conn.transaction(), conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO object_embeddings (image_name, class_name, bbox_xyxy, embedding) VALUES (%s, %s, %s, %s) RETURNING id",
                    (current["filename"], payload.object_name.strip(), [int(x1), int(y1), int(x2), int(y2)], embedding),
                )
                row_id = int(cur.fetchone()[0])
        finally:
            close_db(conn)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc
    current["saved"] = True
    return {"ok": True, "id": row_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
