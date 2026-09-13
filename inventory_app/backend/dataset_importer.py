"""Import YOLO-seg train crops into the inventory embedding catalog."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def choose_folder(title: str, initial_dir: str | Path) -> str:
    """Open a native Windows folder picker and return the selected directory."""
    initial = str(Path(initial_dir).resolve()).replace("'", "''")
    caption = str(title).replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$d = New-Object System.Windows.Forms.FolderBrowserDialog; "
        f"$d.Description = '{caption}'; "
        f"$d.SelectedPath = '{initial}'; "
        "$d.ShowNewFolderButton = $false; "
        "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) "
        "{ [Console]::WriteLine($d.SelectedPath) }"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-STA", "-Command", script],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def validate_train_folders(
    image_dir: str | Path,
    label_dir: str | Path,
) -> tuple[Path, Path]:
    images = Path(image_dir).resolve()
    labels = Path(label_dir).resolve()
    if not images.is_dir() or not labels.is_dir():
        raise ValueError("Both selected folders must exist.")
    if images.name.lower() != "train" or images.parent.name.lower() != "images":
        raise ValueError("Select the dataset images/train folder.")
    if labels.name.lower() != "train" or labels.parent.name.lower() != "labels":
        raise ValueError("Select the dataset labels/train folder.")
    if images.parent.parent != labels.parent.parent:
        raise ValueError("Image and label folders must belong to the same dataset.")
    return images, labels


def inventory_name_from_filename(path: Path) -> str:
    """Convert T015_Caliper__IMG_7300.jpg to Caliper."""
    key = path.stem.split("__", 1)[0]
    raw = key.split("_", 1)[1] if "_" in key else key
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", raw)
    return " ".join(spaced.replace("_", " ").split())


def _polygon_rows(label_path: Path) -> list[list[float]]:
    polygons: list[list[float]] = []
    for raw in label_path.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split()
        if not parts:
            continue
        values = [float(value) for value in parts[1:]]
        if len(values) < 6 or len(values) % 2:
            continue
        polygons.append(values)
    return polygons


def masked_crops(image: Image.Image, label_path: Path) -> list[Image.Image]:
    """Return tight RGB crops whose non-object pixels are black."""
    width, height = image.size
    crops: list[Image.Image] = []
    for values in _polygon_rows(label_path):
        points = [
            (
                max(0, min(width - 1, round(values[i] * width))),
                max(0, min(height - 1, round(values[i + 1] * height))),
            )
            for i in range(0, len(values), 2)
        ]
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).polygon(points, fill=255)
        bbox = mask.getbbox()
        if bbox is None or bbox[2] - bbox[0] < 4 or bbox[3] - bbox[1] < 4:
            continue
        cutout = Image.composite(image, Image.new("RGB", image.size), mask)
        crop = cutout.crop(bbox)
        crop.thumbnail((512, 512), Image.Resampling.LANCZOS)
        crops.append(crop)
    return crops


def import_train_catalog(
    image_dir: str | Path,
    label_dir: str | Path,
    encode_batch: Callable[[list[Image.Image]], list[np.ndarray]],
    replace_rows: Callable[[list[tuple[str, list[float]]]], None],
    update: Callable[..., None],
    batch_size: int = 8,
) -> dict:
    """Mask-crop, OpenCLIP-encode, and atomically replace catalog rows."""
    images_dir, labels_dir = validate_train_folders(image_dir, label_dir)
    image_paths = sorted(
        path for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not image_paths:
        raise ValueError("No supported images found in images/train.")

    update(stage="cropping", total=len(image_paths), processed=0, embedded=0)
    missing_labels = 0
    total_crops = 0
    for index, image_path in enumerate(image_paths, 1):
        label_path = labels_dir / f"{image_path.stem}.txt"
        if not label_path.is_file():
            missing_labels += 1
        else:
            total_crops += len(_polygon_rows(label_path))
        update(
            stage="cropping",
            total=len(image_paths),
            processed=index,
            embedded=0,
            current=image_path.name,
        )

    if not total_crops:
        raise ValueError("No segmentation polygons could be cropped.")

    rows: list[tuple[str, list[float]]] = []
    pending: list[tuple[str, Image.Image]] = []
    update(stage="embedding", total=total_crops, processed=0, embedded=0)
    for image_path in image_paths:
        label_path = labels_dir / f"{image_path.stem}.txt"
        if not label_path.is_file():
            continue
        with Image.open(image_path) as source:
            image = source.convert("RGB")
            name = inventory_name_from_filename(image_path)
            pending.extend((name, crop) for crop in masked_crops(image, label_path))
        while len(pending) >= batch_size:
            batch, pending = pending[:batch_size], pending[batch_size:]
            vectors = encode_batch([crop for _name, crop in batch])
            if len(vectors) != len(batch):
                raise RuntimeError("OpenCLIP returned an unexpected batch size.")
            rows.extend(
                (name, [float(value) for value in vector])
                for (name, _crop), vector in zip(batch, vectors)
            )
            update(
                stage="embedding",
                total=total_crops,
                processed=len(rows),
                embedded=len(rows),
                current=image_path.name,
            )

    if pending:
        vectors = encode_batch([crop for _name, crop in pending])
        if len(vectors) != len(pending):
            raise RuntimeError("OpenCLIP returned an unexpected batch size.")
        rows.extend(
            (name, [float(value) for value in vector])
            for (name, _crop), vector in zip(pending, vectors)
        )
        update(
            stage="embedding",
            total=total_crops,
            processed=len(rows),
            embedded=len(rows),
            current=pending[-1][0],
        )

    update(
        stage="database",
        total=total_crops,
        processed=total_crops,
        embedded=len(rows),
    )
    replace_rows(rows)
    unique_items = len({name for name, _vector in rows})
    return {
        "images": len(image_paths),
        "embeddings": len(rows),
        "unique_items": unique_items,
        "missing_labels": missing_labels,
        "image_dir": str(images_dir),
        "label_dir": str(labels_dir),
    }
