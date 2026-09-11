"""Load dataset images/labels and build a catalog dataframe."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

from .visualize import _infer_dataset_dir, _label_path, _parse_objects, load_class_names


def load_image_and_label(
    source: str | Path | int | None = None,
    images: Sequence[Path] | None = None,
    *,
    image_path: str | Path | None = None,
    index: int | None = None,
    dataset_dir: Path | None = None,
    label_dir: Path | None = None,
    yaml_path: Path | None = None,
    label_path: str | Path | None = None,
) -> tuple[Image.Image, list[dict]]:
    """Load one image and its YOLO label.

    Specify the file with ``image_path=``, or an ``index=`` into ``images``.
    ``source`` still accepts a path or integer index.

    Returns ``(image, labels)`` where each label is a dict with
    ``class_id``, ``class_name``, ``kind``, and ``points``.
    """
    if image_path is not None:
        resolved = Path(image_path)
    elif index is not None:
        if not images:
            raise ValueError("Pass images= when loading by index.")
        resolved = Path(images[index])
    elif source is None:
        raise ValueError("Pass image_path=, index=, or a path/index as the first argument.")
    elif isinstance(source, int):
        if not images:
            raise ValueError("Pass images= when loading by index.")
        resolved = Path(images[source])
    else:
        resolved = Path(source)

    if not resolved.exists():
        raise FileNotFoundError(resolved)

    if dataset_dir is None:
        dataset_dir = _infer_dataset_dir(resolved)
    if label_dir is None and dataset_dir is not None:
        label_dir = Path(dataset_dir) / "labels"
    if yaml_path is None and dataset_dir is not None:
        yaml_path = Path(dataset_dir) / "data.yaml"

    image = Image.open(resolved).convert("RGB")
    names = load_class_names(yaml_path)
    if label_path is not None:
        lbl_path = Path(label_path)
        if not lbl_path.exists():
            raise FileNotFoundError(lbl_path)
    else:
        lbl_path = _label_path(resolved, label_dir)
    objects = _parse_objects(lbl_path, image.size[0], image.size[1])

    labels = [
        {
            "class_id": cls_id,
            "class_name": names.get(cls_id, str(cls_id)),
            "kind": kind,
            "points": points,
            "label_path": lbl_path,
            "image_path": resolved,
        }
        for cls_id, kind, points in objects
    ]
    return image, labels


def _class_names_for_image(
    image_path: Path,
    label_dir: Path | None,
    names: dict[int, str],
) -> str:
    label_path = _label_path(image_path, label_dir)
    if not label_path.exists():
        return ""

    class_ids: list[int] = []
    for raw in label_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        class_ids.append(int(float(line.split()[0])))

    unique_names = []
    seen: set[str] = set()
    for cls_id in class_ids:
        name = names.get(cls_id, str(cls_id))
        if name not in seen:
            seen.add(name)
            unique_names.append(name)
    return ", ".join(unique_names)


def bbox_xyxy(
    label: dict,
    image_size: tuple[int, int],
    pad: int = 8,
) -> tuple[int, int, int, int] | None:
    """Axis-aligned crop box from a YOLO box or polygon label."""
    width, height = image_size
    points = label["points"]
    if label.get("kind") == "box":
        (x1, y1), (x2, y2) = points
    else:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)

    x1 = max(0, int(x1) - pad)
    y1 = max(0, int(y1) - pad)
    x2 = min(width, int(x2) + pad)
    y2 = min(height, int(y2) + pad)
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def crop_labeled_objects(
    image: Image.Image,
    labels: list[dict],
    *,
    pad: int = 8,
) -> list[dict]:
    """Crop each labeled object from ``image`` and attach bbox metadata."""
    crops: list[dict] = []
    for instance_id, label in enumerate(labels):
        bbox = bbox_xyxy(label, image.size, pad=pad)
        if bbox is None:
            continue
        crop = image.crop(bbox)
        crops.append(
            {
                "instance_id": instance_id,
                "class_id": label["class_id"],
                "class_name": label["class_name"],
                "kind": label["kind"],
                "points": label["points"],
                "bbox_xyxy": bbox,
                "crop": crop,
                "crop_width": crop.size[0],
                "crop_height": crop.size[1],
            }
        )
    return crops


def _class_key(image_path: Path) -> str:
    return image_path.stem.split("__", 1)[0]


def _sample_per_class(images: Sequence[Path], n_per_class: int) -> list[Path]:
    grouped: dict[str, list[Path]] = {}
    selected: list[Path] = []
    for path in images:
        key = _class_key(path)
        bucket = grouped.setdefault(key, [])
        if len(bucket) < n_per_class:
            bucket.append(path)
            selected.append(path)
    return selected


def build_embedding_dataframe(
    images: Sequence[Path],
    *,
    dataset_dir: Path | None = None,
    label_dir: Path | None = None,
    yaml_path: Path | None = None,
    split: str = "train",
    n_per_class: int | None = 10,
    include_embedding: bool = True,
) -> pd.DataFrame:
    """Build a catalog with image name, path, class name, and empty embeddings.

    Defaults to the train split and ``n_per_class=10`` images per class.
    Set ``n_per_class=None`` to keep every image in the split.
    Set ``include_embedding=False`` to omit the embedding column.
    """
    images = [Path(p) for p in images]
    if split:
        images = [p for p in images if p.parent.name.lower() == split.lower()]
    if n_per_class is not None:
        images = _sample_per_class(images, n_per_class)
    if not images:
        columns = ["image_name", "path", "class_name"]
        if include_embedding:
            columns.append("embedding")
        return pd.DataFrame(columns=columns)

    if dataset_dir is None:
        dataset_dir = _infer_dataset_dir(images[0])
    if label_dir is None and dataset_dir is not None:
        label_dir = Path(dataset_dir) / "labels"
    if yaml_path is None and dataset_dir is not None:
        yaml_path = Path(dataset_dir) / "data.yaml"

    names = load_class_names(yaml_path)
    desc = f"Building {split or 'all'} catalog"
    if n_per_class is not None:
        desc += f" ({n_per_class}/class)"
    rows = []
    for path in tqdm(
        images,
        desc=desc,
        unit="img",
        dynamic_ncols=True,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
    ):
        rows.append(
            {
                "image_name": path.name,
                "path": str(path),
                "class_name": _class_names_for_image(path, label_dir, names),
            }
        )
    df = pd.DataFrame(rows, columns=["image_name", "path", "class_name"])
    if include_embedding:
        df["embedding"] = pd.Series([None] * len(df), dtype="object")
    return df
