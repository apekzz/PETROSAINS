"""Interactive Segment Anything service used by the inventory dashboard."""

from __future__ import annotations

import base64
import io
import os
import threading
import uuid
from collections import OrderedDict
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from config import BASE_DIR


MAX_IMAGE_BYTES = 15 * 1024 * 1024
MAX_SESSIONS = 3
SAM_CHECKPOINT = Path(
    os.environ.get(
        "SAM_CHECKPOINT",
        Path(BASE_DIR) / "models" / "sam_b.pt",
    )
)
SAM_MODEL_TYPE = SAM_CHECKPOINT.stem
SAM_DEVICE_REQUEST = os.environ.get("SAM_DEVICE", "auto").strip().lower()

_predictor = None
_device = "not loaded"
_active_session_id = None
_sam_lock = threading.RLock()
_sessions_lock = threading.RLock()
_sessions: OrderedDict[str, dict] = OrderedDict()


def _decode_image_bytes(image_bytes: bytes, mode: str = "RGB") -> np.ndarray:
    if not image_bytes or len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("Image is empty or exceeds 15 MB")
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.load()
            return np.asarray(ImageOps.exif_transpose(image).convert(mode))
    except Exception as exc:
        raise ValueError(f"Could not decode image: {exc}") from exc


def _decode_data_url(data_url: str, mode: str = "L") -> np.ndarray:
    try:
        encoded = str(data_url or "").split(",", 1)[-1]
        return _decode_image_bytes(base64.b64decode(encoded, validate=True), mode)
    except Exception as exc:
        raise ValueError(f"Could not decode mask: {exc}") from exc


def _mask_data_url(mask: np.ndarray) -> str:
    output = io.BytesIO()
    Image.fromarray((mask > 0).astype(np.uint8) * 255, "L").save(output, "PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def load_sam_model():
    """Load Ultralytics SAM once during boot and retain its cached predictor."""
    global _predictor, _device
    with _sam_lock:
        if _predictor is not None:
            return _predictor
        if not SAM_CHECKPOINT.exists():
            raise RuntimeError(f"SAM checkpoint not found: {SAM_CHECKPOINT}")
        try:
            import torch
            from ultralytics import SAM
            from ultralytics.models.sam import Predictor
        except ImportError as exc:
            raise RuntimeError(
                "Ultralytics SAM is unavailable. Run: pip install ultralytics"
            ) from exc

        if SAM_DEVICE_REQUEST in {"cpu", "cuda"}:
            requested_device = SAM_DEVICE_REQUEST
        else:
            requested_device = "cuda" if torch.cuda.is_available() else "cpu"

        model = SAM(str(SAM_CHECKPOINT))
        overrides = {
            "model": str(SAM_CHECKPOINT),
            "task": "segment",
            "mode": "predict",
            "imgsz": 1024,
            "device": requested_device,
            "conf": 0.0,
            "verbose": False,
        }
        try:
            predictor = Predictor(overrides=overrides, _callbacks=model.callbacks)
            predictor.setup_model(model=model.model, verbose=False)
            _device = str(predictor.device)
        except RuntimeError as exc:
            if requested_device != "cuda":
                raise
            print(f"[SAM] CUDA load failed ({exc}); falling back to CPU")
            overrides["device"] = "cpu"
            predictor = Predictor(overrides=overrides, _callbacks=model.callbacks)
            predictor.setup_model(model=model.model, verbose=False)
            _device = "cpu"
        _predictor = predictor
        print(
            f"[SAM] Loaded {SAM_MODEL_TYPE} from {SAM_CHECKPOINT.name} "
            f"device={_device}"
        )
        return _predictor


def sam_status():
    return {
        "ready": _predictor is not None,
        "device": _device,
        "model_type": SAM_MODEL_TYPE,
        "checkpoint": str(SAM_CHECKPOINT),
        "checkpoint_exists": SAM_CHECKPOINT.exists(),
    }


def _get_session(session_id: str) -> dict:
    with _sessions_lock:
        current = _sessions.get(session_id)
        if current is None:
            raise KeyError("SAM session not found. Capture the frame again.")
        _sessions.move_to_end(session_id)
        return current


def create_session(image_bytes: bytes) -> dict:
    """Store a frozen frame and compute its SAM image features immediately."""
    global _active_session_id
    image = _decode_image_bytes(image_bytes, "RGB")
    session_id = uuid.uuid4().hex
    current = {"image": image}
    with _sessions_lock:
        _sessions[session_id] = current
        while len(_sessions) > MAX_SESSIONS:
            _sessions.popitem(last=False)
    with _sam_lock:
        predictor = load_sam_model()
        predictor.set_image(image[:, :, ::-1].copy())
        _active_session_id = session_id
    return {
        "session_id": session_id,
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
    }


def create_mask(session_id: str, points, labels) -> dict:
    global _active_session_id
    current = _get_session(session_id)
    coords = np.asarray(points, dtype=np.float32)
    prompt_labels = np.asarray(labels, dtype=np.int32)
    height, width = current["image"].shape[:2]
    if (
        coords.ndim != 2
        or coords.shape != (len(prompt_labels), 2)
        or not len(coords)
    ):
        raise ValueError("Provide one x,y pair and label for every prompt")
    if not np.isin(prompt_labels, [0, 1]).all() or not np.any(prompt_labels == 1):
        raise ValueError("Use at least one foreground point")
    if (
        not np.isfinite(coords).all()
        or (coords[:, 0] < 0).any()
        or (coords[:, 0] >= width).any()
        or (coords[:, 1] < 0).any()
        or (coords[:, 1] >= height).any()
    ):
        raise ValueError("A prompt is outside the frozen image")

    with _sam_lock:
        predictor = load_sam_model()
        if _active_session_id != session_id:
            predictor.set_image(current["image"][:, :, ::-1].copy())
            _active_session_id = session_id
        masks, boxes = predictor.inference_features(
            predictor.features,
            current["image"].shape[:2],
            # Ultralytics interprets (N, 2) as N separate single-point
            # objects. Add a batch dimension so all clicks describe one
            # object: (1, N, 2) points with (1, N) labels.
            points=coords[None, ...],
            labels=prompt_labels[None, ...],
            multimask_output=True,
        )
    if masks is None or not len(masks):
        raise ValueError("Ultralytics SAM returned no masks")
    scores = boxes[:, 4]
    best_index = int(scores.argmax().item())
    mask = masks[best_index].detach().cpu().numpy().astype(bool)
    if not mask.any():
        raise ValueError("Ultralytics SAM returned an empty mask")
    return {
        "mask_data": _mask_data_url(mask),
        "pixels": int(mask.sum()),
        "score": float(scores[best_index].item()),
    }


def create_masked_crop(session_id: str, mask_data: str) -> bytes:
    """Create a tight, black-background crop for the shared OpenCLIP encoder."""
    current = _get_session(session_id)
    mask = _decode_data_url(mask_data, "L") > 127
    image = current["image"]
    if mask.shape != image.shape[:2]:
        raise ValueError("Mask dimensions do not match the frozen frame")
    ys, xs = np.nonzero(mask)
    if not len(xs):
        raise ValueError("The final mask is empty")
    x1 = max(0, int(xs.min()) - 8)
    x2 = min(image.shape[1], int(xs.max()) + 9)
    y1 = max(0, int(ys.min()) - 8)
    y2 = min(image.shape[0], int(ys.max()) + 9)
    crop = np.zeros_like(image[y1:y2, x1:x2])
    local_mask = mask[y1:y2, x1:x2]
    crop[local_mask] = image[y1:y2, x1:x2][local_mask]
    output = io.BytesIO()
    Image.fromarray(crop, "RGB").save(output, "PNG")
    return output.getvalue()


def discard_session(session_id: str):
    global _active_session_id
    with _sessions_lock:
        _sessions.pop(session_id, None)
    with _sam_lock:
        if _active_session_id == session_id:
            _active_session_id = None


def clear_sessions():
    global _active_session_id
    with _sessions_lock:
        _sessions.clear()
    with _sam_lock:
        _active_session_id = None
