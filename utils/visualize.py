"""Preview dataset images with YOLO box or segmentation labels drawn on top."""

from __future__ import annotations

import colorsys
import math
import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from PIL import Image

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff", ".gif"}


def list_images(
    image_dir: Path,
    image_exts: set[str] | None = None,
) -> list[Path]:
    """Collect image files under ``image_dir`` (includes train/val/test)."""
    exts = {e.lower() for e in (image_exts or IMAGE_EXTS)}
    return sorted(
        p for p in Path(image_dir).rglob("*") if p.is_file() and p.suffix.lower() in exts
    )


def load_class_names(yaml_path: Path | None) -> dict[int, str]:
    if yaml_path is None or not Path(yaml_path).exists():
        return {}

    names: dict[int, str] = {}
    in_names = False
    for raw in Path(yaml_path).read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.strip().startswith("names:"):
            in_names = True
            continue
        if not in_names:
            continue
        if line and not line[:1].isspace():
            break
        match = re.match(r"\s*(\d+)\s*:\s*[\"']?(.*?)[\"']?\s*$", line)
        if match:
            names[int(match.group(1))] = match.group(2).strip()
    return names


def summarize_images(images: Sequence[Path], dataset_dir: Path | None = None) -> None:
    images = [Path(p) for p in images]
    splits = Counter(p.parent.name for p in images)
    print(f"Found {len(images)} images")
    print("By folder:", dict(splits))
    root = Path(dataset_dir) if dataset_dir is not None else None
    for path in images[:10]:
        shown = path.relative_to(root) if root is not None else path.name
        print(" -", shown)


def view_labeled_images(
    images: Sequence[Path],
    *,
    dataset_dir: Path | None = None,
    label_dir: Path | None = None,
    yaml_path: Path | None = None,
    index: int = 0,
    n: int = 1,
    figsize: tuple[float, float] = (8, 8),
) -> None:
    """Show one or more images from ``images`` with labels overlaid."""
    images = [Path(p) for p in images]
    if not images:
        print("No images to view.")
        return

    if dataset_dir is None:
        dataset_dir = _infer_dataset_dir(images[0])
    if label_dir is None and dataset_dir is not None:
        label_dir = Path(dataset_dir) / "labels"
    if yaml_path is None and dataset_dir is not None:
        yaml_path = Path(dataset_dir) / "data.yaml"

    names = load_class_names(yaml_path)
    start = max(0, index)
    end = min(len(images), start + max(1, n))
    batch = images[start:end]
    cols = min(len(batch), 2)
    rows = math.ceil(len(batch) / cols)
    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(figsize[0] * cols, figsize[1] * rows),
        squeeze=False,
    )
    axes_list = [axes[r, c] for r in range(rows) for c in range(cols)]

    for ax, image_path in zip(axes_list, batch):
        _draw_one(ax, image_path, label_dir, names, dataset_dir)

    for ax in axes_list[len(batch) :]:
        ax.axis("off")

    fig.tight_layout()
    plt.show()


def _infer_dataset_dir(image_path: Path) -> Path | None:
    for parent in Path(image_path).parents:
        if (parent / "data.yaml").exists() and (parent / "labels").is_dir():
            return parent
    return None


def _label_path(image_path: Path, label_dir: Path | None) -> Path:
    image_path = Path(image_path)
    if label_dir is not None:
        return Path(label_dir) / image_path.parent.name / f"{image_path.stem}.txt"
    text = str(image_path)
    for token in ("\\images\\", "/images/"):
        if token in text:
            return Path(text.replace(token, token.replace("images", "labels"))).with_suffix(".txt")
    return image_path.with_suffix(".txt")


def _class_color(cls_id: int) -> tuple[float, float, float]:
    hue = (cls_id * 0.61803398875) % 1.0
    return colorsys.hsv_to_rgb(hue, 0.75, 0.95)


def _parse_objects(label_path: Path, width: int, height: int) -> list[tuple[int, str, list[tuple[float, float]]]]:
    objects: list[tuple[int, str, list[tuple[float, float]]]] = []
    if not label_path.exists():
        return objects

    for raw in label_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [float(x) for x in line.split()]
        cls_id = int(parts[0])
        coords = parts[1:]
        if len(coords) == 4:
            cx, cy, bw, bh = coords
            x1 = (cx - bw / 2) * width
            y1 = (cy - bh / 2) * height
            x2 = (cx + bw / 2) * width
            y2 = (cy + bh / 2) * height
            objects.append((cls_id, "box", [(x1, y1), (x2, y2)]))
        elif len(coords) >= 6:
            points = [
                (coords[i] * width, coords[i + 1] * height)
                for i in range(0, len(coords) - 1, 2)
            ]
            objects.append((cls_id, "poly", points))
    return objects


def _draw_one(
    ax,
    image_path: Path,
    label_dir: Path | None,
    names: dict[int, str],
    dataset_dir: Path | None,
) -> None:
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    label_path = _label_path(image_path, label_dir)
    objects = _parse_objects(label_path, width, height)

    ax.imshow(np.asarray(image))
    for cls_id, kind, points in objects:
        color = _class_color(cls_id)
        name = names.get(cls_id, str(cls_id))
        if kind == "box":
            (x1, y1), (x2, y2) = points
            ax.add_patch(
                Rectangle(
                    (x1, y1),
                    x2 - x1,
                    y2 - y1,
                    fill=False,
                    linewidth=2,
                    edgecolor=color,
                )
            )
            text_xy = (x1, max(0, y1 - 8))
        else:
            ax.add_patch(
                Polygon(
                    points,
                    closed=True,
                    fill=True,
                    alpha=0.25,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=2,
                )
            )
            text_xy = points[0]
        ax.text(
            text_xy[0],
            text_xy[1],
            name,
            color="white",
            fontsize=8,
            va="bottom",
            ha="left",
            bbox={"facecolor": color, "edgecolor": "none", "pad": 2, "alpha": 0.9},
        )

    title = (
        str(image_path.relative_to(dataset_dir))
        if dataset_dir is not None
        else image_path.name
    )
    missing = "" if label_path.exists() else "  [no label]"
    ax.set_title(f"{title}{missing}  ({len(objects)} objects)")
    ax.axis("off")
