"""Convert train_v2 YOLO-seg labels to COCO JSON for Detectron2."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
TRAIN_V2 = HERE.parent
DEFAULT_DATASET = TRAIN_V2 / "dataset"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
SPLITS = ("train", "val", "test")


def _image_path(image_dir: Path, stem: str) -> Path | None:
    for ext in IMAGE_EXTS:
        path = image_dir / f"{stem}{ext}"
        if path.exists():
            return path
    matches = list(image_dir.glob(f"{stem}.*"))
    return matches[0] if matches else None


def _polygons_from_label(label_path: Path, width: int, height: int) -> list[dict]:
    objects: list[dict] = []
    text = label_path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        coords = np.array([float(v) for v in parts[1:]], dtype=np.float64)
        if coords.size == 4:
            cx, cy, bw, bh = coords
            x1 = (cx - bw / 2) * width
            y1 = (cy - bh / 2) * height
            w = abs(bw) * width
            h = abs(bh) * height
            poly = [x1, y1, x1 + w, y1, x1 + w, y1 + h, x1, y1 + h]
        elif coords.size >= 6 and coords.size % 2 == 0:
            xs = coords[0::2] * width
            ys = coords[1::2] * height
            poly = np.stack([xs, ys], axis=1).reshape(-1).tolist()
            x1, y1 = float(xs.min()), float(ys.min())
            w, h = float(xs.max() - xs.min()), float(ys.max() - ys.min())
        else:
            continue
        area = abs(w * h)
        if area <= 0 or len(poly) < 6:
            continue
        objects.append(
            {
                "bbox": [float(x1), float(y1), float(w), float(h)],
                "segmentation": [poly],
                "area": float(area),
            }
        )
    return objects


def convert_split(dataset_dir: Path, split: str, out_path: Path) -> Path:
    image_dir = dataset_dir / "images" / split
    label_dir = dataset_dir / "labels" / split
    if not label_dir.is_dir():
        raise FileNotFoundError(label_dir)

    images = []
    annotations = []
    ann_id = 1
    label_files = sorted(label_dir.glob("*.txt"))
    for image_id, label_path in enumerate(tqdm(label_files, desc=f"COCO {split}", unit="file"), start=1):
        image_path = _image_path(image_dir, label_path.stem)
        if image_path is None:
            continue
        with Image.open(image_path) as im:
            width, height = im.size
        images.append(
            {
                "id": image_id,
                "file_name": image_path.name,
                "width": width,
                "height": height,
            }
        )
        for obj in _polygons_from_label(label_path, width, height):
            annotations.append(
                {
                    "id": ann_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "iscrowd": 0,
                    **obj,
                }
            )
            ann_id += 1

    coco = {
        "info": {"description": "train_v2 single-class object (YOLO-seg → COCO)"},
        "licenses": [],
        "categories": [{"id": 1, "name": "object", "supercategory": "object"}],
        "images": images,
        "annotations": annotations,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(coco), encoding="utf-8")
    print(f"{split}: {len(images)} images, {len(annotations)} objects → {out_path}")
    return out_path


def convert_dataset(dataset_dir: Path = DEFAULT_DATASET) -> dict[str, Path]:
    dataset_dir = Path(dataset_dir)
    coco_dir = dataset_dir / "coco"
    written = {}
    for split in SPLITS:
        written[split] = convert_split(dataset_dir, split, coco_dir / f"{split}.json")
    return written


if __name__ == "__main__":
    convert_dataset()
