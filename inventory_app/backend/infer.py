"""YOLO11l-seg inference for OneShot inventory.

Derived from train_v2/train_rtdetr_l_v2.ipynb section 7 (sanity-check predict).
The trained class is a single `object` mask. Item names are resolved later
by matching a crop embedding against `inventory_emb`.
"""

from __future__ import annotations

import os

import cv2
import numpy as np
import torch
from ultralytics import YOLO

from config import (
    BASE_DIR,
    MODEL_CONFIDENCE,
    MODEL_IMAGE_SIZE,
    MODEL_IOU,
    MODEL_MAX_DET,
    NESTED_PART_CONTAIN,
    NESTED_PART_MAX_AREA_RATIO,
)

WEIGHT_NAME = "yolo11l_seg_object_bce_dice.pt"
WEIGHT_PATH = os.path.join(BASE_DIR, "models", WEIGHT_NAME)
FALLBACK_BEST = os.path.join(BASE_DIR, "models", "best.pt")
SOURCE_WEIGHTS = os.path.normpath(
    os.path.join(
        BASE_DIR,
        "..",
        "train_v2",
        "runs",
        "v2",
        "yolo11l_seg_object_bce_dice",
        "weights",
        "best.pt",
    )
)

_model = None
_device = "cpu"


def resolve_weights():
    for path in (WEIGHT_PATH, FALLBACK_BEST, SOURCE_WEIGHTS):
        if path and os.path.isfile(path) and os.path.getsize(path) > 1_000_000:
            return path
    return None


def load_model():
    global _model, _device
    if _model is not None:
        return _model
    path = resolve_weights()
    if path is None:
        print("[INFER] YOLO11l-seg weights not found — detection paused")
        return None
    _model = YOLO(path)
    _device = 0 if torch.cuda.is_available() else "cpu"
    print(f"[INFER] Loaded YOLO11l-seg from {path}  device={_device}")
    return _model


def predict_frame(frame, conf=None, imgsz=None, iou=None, max_det=None, retina_masks=True):
    """Run the v2 segmentation model. Same call shape as the notebook."""
    engine = load_model()
    if engine is None or frame is None:
        return []
    return engine.predict(
        source=frame,
        imgsz=imgsz or MODEL_IMAGE_SIZE,
        conf=conf if conf is not None else MODEL_CONFIDENCE,
        iou=iou if iou is not None else MODEL_IOU,
        max_det=max_det if max_det is not None else MODEL_MAX_DET,
        device=_device,
        verbose=False,
        retina_masks=retina_masks,
    )


def parse_detections(results, default_name="object"):
    if not results:
        return []
    result = results[0]
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return []
    xyxy = boxes.xyxy.cpu().numpy()
    confidences = boxes.conf.cpu().numpy()
    classes = boxes.cls.cpu().numpy() if getattr(boxes, "cls", None) is not None else None
    names = getattr(result, "names", None) or {}
    masks = getattr(result, "masks", None)
    polygons = list(getattr(masks, "xy", []) or [])
    detections = []
    for index, (box, confidence) in enumerate(zip(xyxy, confidences)):
        x1, y1, x2, y2 = [int(value) for value in box]
        polygon = polygons[index] if index < len(polygons) else None
        class_id = int(classes[index]) if classes is not None else None
        label = default_name
        if class_id is not None:
            if isinstance(names, dict):
                label = str(names.get(class_id, default_name))
            elif isinstance(names, (list, tuple)) and 0 <= class_id < len(names):
                label = str(names[class_id])
        detections.append({
            "xyxy": (x1, y1, x2, y2),
            "confidence": float(confidence),
            "name": label,
            "mask_xy": (
                np.asarray(polygon, dtype=np.int32)
                if polygon is not None and len(polygon) >= 3
                else None
            ),
            "hidden": False,
            "nested": False,
        })
    return detections


def _detection_area(detection):
    polygon = detection.get("mask_xy")
    if polygon is not None and len(polygon) >= 3:
        area = float(cv2.contourArea(np.asarray(polygon, dtype=np.int32)))
        if area > 0:
            return area
    x1, y1, x2, y2 = detection["xyxy"]
    return float(max(1, (x2 - x1) * (y2 - y1)))


def _bbox_containment(inner, outer):
    ix1, iy1, ix2, iy2 = inner["xyxy"]
    ox1, oy1, ox2, oy2 = outer["xyxy"]
    x1 = max(ix1, ox1)
    y1 = max(iy1, oy1)
    x2 = min(ix2, ox2)
    y2 = min(iy2, oy2)
    if x2 <= x1 or y2 <= y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    inner_area = max(1, (ix2 - ix1) * (iy2 - iy1))
    return inter / inner_area


def _mask_containment(inner, outer):
    """Fraction of the inner mask that lies inside the outer mask."""
    inner_poly = inner.get("mask_xy")
    outer_poly = outer.get("mask_xy")
    if (
        inner_poly is None
        or outer_poly is None
        or len(inner_poly) < 3
        or len(outer_poly) < 3
    ):
        return _bbox_containment(inner, outer)

    ix1, iy1, ix2, iy2 = inner["xyxy"]
    width = max(1, ix2 - ix1)
    height = max(1, iy2 - iy1)
    scale = 1.0
    max_side = 160
    if max(width, height) > max_side:
        scale = max_side / max(width, height)
    raster_w = max(1, int(round(width * scale)))
    raster_h = max(1, int(round(height * scale)))

    def _shift(polygon):
        points = np.asarray(polygon, dtype=np.float32)
        points[:, 0] = (points[:, 0] - ix1) * scale
        points[:, 1] = (points[:, 1] - iy1) * scale
        return points.astype(np.int32)

    inner_mask = np.zeros((raster_h, raster_w), dtype=np.uint8)
    outer_mask = np.zeros((raster_h, raster_w), dtype=np.uint8)
    cv2.fillPoly(inner_mask, [_shift(inner_poly)], 1)
    cv2.fillPoly(outer_mask, [_shift(outer_poly)], 1)
    inner_count = int(inner_mask.sum())
    if inner_count == 0:
        return _bbox_containment(inner, outer)
    return float(np.logical_and(inner_mask, outer_mask).sum()) / inner_count


def mark_nested_parts(
    detections,
    contain_frac=None,
    max_area_ratio=None,
):
    """Flag small detections that sit inside a larger object's mask.

    YOLO still keeps the box. Callers hide flagged items from the UI / log
    so a phone camera is not shown or named as a ring.
    """
    if len(detections) < 2:
        for item in detections:
            item["nested"] = False
            item["hidden"] = False
        return detections

    contain_frac = NESTED_PART_CONTAIN if contain_frac is None else contain_frac
    max_area_ratio = (
        NESTED_PART_MAX_AREA_RATIO if max_area_ratio is None else max_area_ratio
    )
    areas = [_detection_area(item) for item in detections]
    nested = [False] * len(detections)
    for i, inner in enumerate(detections):
        for j, outer in enumerate(detections):
            if i == j or areas[j] <= 0:
                continue
            if areas[i] >= areas[j] * max_area_ratio:
                continue
            if _bbox_containment(inner, outer) < contain_frac:
                continue
            if _mask_containment(inner, outer) >= contain_frac:
                nested[i] = True
                break
    hidden_count = 0
    for item, is_nested in zip(detections, nested):
        item["nested"] = is_nested
        item["hidden"] = is_nested
        hidden_count += int(is_nested)
    if hidden_count:
        print(f"[YOLO] Hid {hidden_count} nested part(s) inside a larger object")
    return detections


def visible_detections(detections):
    return [item for item in detections if not item.get("hidden")]


def crop_bgr(frame, xyxy, pad=6):
    if frame is None:
        return None
    height, width = frame.shape[:2]
    x1, y1, x2, y2 = xyxy
    x1 = max(0, x1 - pad)
    y1 = max(0, y1 - pad)
    x2 = min(width, x2 + pad)
    y2 = min(height, y2 + pad)
    if x2 - x1 < 8 or y2 - y1 < 8:
        return None
    return frame[y1:y2, x1:x2].copy()


def crop_masked_bgr(frame, detection, pad=2):
    """Tight object cutout using the predicted segmentation polygon."""
    if frame is None:
        return None
    polygon = detection.get("mask_xy")
    if polygon is None or len(polygon) < 3:
        return crop_bgr(frame, detection["xyxy"], pad=pad)
    height, width = frame.shape[:2]
    polygon = np.asarray(polygon, dtype=np.int32)
    polygon[:, 0] = np.clip(polygon[:, 0], 0, width - 1)
    polygon[:, 1] = np.clip(polygon[:, 1], 0, height - 1)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    x, y, w, h = cv2.boundingRect(polygon)
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(width, x + w + pad)
    y2 = min(height, y + h + pad)
    if x2 - x1 < 8 or y2 - y1 < 8:
        return None
    cutout = np.zeros_like(frame)
    cutout[mask > 0] = frame[mask > 0]
    return cutout[y1:y2, x1:x2]


def model_device():
    return _device


if __name__ == "__main__":
    import argparse
    import cv2

    parser = argparse.ArgumentParser(description="YOLO11l-seg v2 inference")
    parser.add_argument("source", help="Image or folder to predict")
    parser.add_argument("--conf", type=float, default=MODEL_CONFIDENCE)
    parser.add_argument("--out", default="", help="Optional annotated image path")
    args = parser.parse_args()

    engine = load_model()
    if engine is None:
        raise SystemExit("Weights not found")
    results = engine.predict(
        source=args.source,
        imgsz=MODEL_IMAGE_SIZE,
        conf=args.conf,
        device=_device,
        verbose=True,
    )
    result = results[0]
    count = 0 if result.boxes is None else len(result.boxes)
    print(f"detections: {count}  (class ignored — all are object)")
    if args.out:
        result.save(filename=args.out)
        print("Wrote", args.out)
    elif hasattr(result, "plot"):
        vis = result.plot()
        preview = os.path.join(BASE_DIR, "preview_seg_v2.jpg")
        cv2.imwrite(preview, vis)
        print("Wrote", preview)
