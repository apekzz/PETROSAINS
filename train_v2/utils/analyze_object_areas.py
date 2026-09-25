"""Histogram object mask areas (px²) for train / val / test.

YOLO-seg labels are normalized polygons. This script maps them to pixel
coordinates using each image's width/height, then uses the shoelace
formula for polygon area. Boxes (5-number lines) use width*height.

Run from the repo root:

    python train_v2/utils/analyze_object_areas.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
TRAIN_V2 = HERE.parent
DEFAULT_DATASET = TRAIN_V2 / "dataset"
DEFAULT_OUT = TRAIN_V2 / "object_area_histograms.png"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
SPLITS = ("train", "val", "test")


def _shoelace_area(xs: np.ndarray, ys: np.ndarray) -> float:
    return float(0.5 * abs(np.dot(xs, np.roll(ys, 1)) - np.dot(ys, np.roll(xs, 1))))


def _image_size(image_dir: Path, stem: str) -> tuple[int, int] | None:
    for ext in IMAGE_EXTS:
        path = image_dir / f"{stem}{ext}"
        if path.exists():
            with Image.open(path) as im:
                return im.size
    matches = list(image_dir.glob(f"{stem}.*"))
    if not matches:
        return None
    with Image.open(matches[0]) as im:
        return im.size


def _areas_from_label(label_path: Path, width: int, height: int) -> list[float]:
    areas: list[float] = []
    text = label_path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        coords = np.array([float(v) for v in parts[1:]], dtype=np.float64)
        if coords.size == 4:
            _, _, bw, bh = coords
            areas.append(abs(bw * width) * abs(bh * height))
            continue
        if coords.size < 6 or coords.size % 2:
            continue
        xs = coords[0::2] * width
        ys = coords[1::2] * height
        area = _shoelace_area(xs, ys)
        if area > 0:
            areas.append(area)
    return areas


def collect_split_areas(dataset_dir: Path, split: str) -> np.ndarray:
    label_dir = dataset_dir / "labels" / split
    image_dir = dataset_dir / "images" / split
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Missing labels: {label_dir}")

    label_files = sorted(label_dir.glob("*.txt"))
    areas: list[float] = []
    skipped = 0
    for label_path in tqdm(label_files, desc=f"{split} labels", unit="file"):
        size = _image_size(image_dir, label_path.stem)
        if size is None:
            skipped += 1
            continue
        width, height = size
        areas.extend(_areas_from_label(label_path, width, height))

    if skipped:
        print(f"  {split}: skipped {skipped} labels with no matching image")
    return np.asarray(areas, dtype=np.float64)


def summarize(name: str, areas: np.ndarray) -> None:
    if areas.size == 0:
        print(f"{name:5s}  n=0")
        return
    print(
        f"{name:5s}  n={areas.size:5d}  "
        f"min={areas.min():.0f}  "
        f"p25={np.percentile(areas, 25):.0f}  "
        f"median={np.median(areas):.0f}  "
        f"mean={areas.mean():.0f}  "
        f"p75={np.percentile(areas, 75):.0f}  "
        f"max={areas.max():.0f}  px²"
    )


def plot_histograms(
    split_areas: dict[str, np.ndarray],
    out_path: Path,
) -> Path:
    all_pos = np.concatenate([a[a > 0] for a in split_areas.values() if a.size])
    if all_pos.size == 0:
        raise ValueError("No objects with positive area.")

    lo = max(all_pos.min(), 1.0)
    hi = all_pos.max()
    bins = np.logspace(np.log10(lo), np.log10(hi), 40)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharey=True)
    colors = {"train": "#2563eb", "val": "#16a34a", "test": "#dc2626"}

    for ax, split in zip(axes, SPLITS):
        areas = split_areas[split]
        ax.hist(
            areas,
            bins=bins,
            color=colors[split],
            edgecolor="white",
            linewidth=0.4,
        )
        ax.set_xscale("log")
        ax.set_title(f"{split}  (n={areas.size})")
        ax.set_xlabel("object area (px²)")
        ax.grid(True, which="both", axis="x", alpha=0.25)
        if areas.size:
            ax.axvline(
                np.median(areas),
                color="black",
                linestyle="--",
                linewidth=1,
                label=f"median {np.median(areas):.0f}",
            )
            ax.legend(fontsize=8, loc="upper right")

    axes[0].set_ylabel("count")
    fig.suptitle("Segmented object area distribution", fontsize=13)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Histogram YOLO-seg object areas in px².")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = Path(args.dataset)
    print(f"Dataset: {dataset}")
    split_areas = {split: collect_split_areas(dataset, split) for split in SPLITS}

    print()
    print("Object area (px²)")
    for split in SPLITS:
        summarize(split, split_areas[split])

    out = plot_histograms(split_areas, Path(args.out))
    print()
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
