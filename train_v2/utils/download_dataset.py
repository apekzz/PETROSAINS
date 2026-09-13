"""Copy the existing Drive YOLO dataset into train_v2/dataset.

Finds the same Shared Drive folder as the rest of the repo
(``utils.gdrive.drive_folder("dataset")``), copies images + labels locally
with a tqdm progress bar, remaps every class id to ``0`` (single ``object``
class), and writes a matching ``data.yaml``.

Run from the repo root (PowerShell):

    python train_v2/utils/download_dataset.py

Optional flags:

    python train_v2/utils/download_dataset.py --force
    python train_v2/utils/download_dataset.py --source "G:\\path\\to\\dataset"
    python train_v2/utils/download_dataset.py --dest train_v2/dataset
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from tqdm import tqdm

HERE = Path(__file__).resolve().parent
TRAIN_V2 = HERE.parent
REPO = TRAIN_V2.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _drive_folder(name: str = "dataset") -> Path:
    from utils.gdrive import drive_folder

    return drive_folder(name)

SKIP_DIR_NAMES = {"__pycache__", ".ipynb_checkpoints", ".git"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
DEFAULT_DEST = TRAIN_V2 / "dataset"


def _iter_files(src: Path) -> list[Path]:
    files: list[Path] = []
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
    return files


def _copy_tree(src: Path, dest: Path) -> int:
    files = _iter_files(src)
    if not files:
        raise FileNotFoundError(f"No files found under {src}")

    total_bytes = sum(path.stat().st_size for path in files)
    dest.mkdir(parents=True, exist_ok=True)

    copied = 0
    with tqdm(
        total=total_bytes,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc="Copying dataset",
    ) as pbar:
        for src_file in files:
            rel = src_file.relative_to(src)
            dest_file = dest / rel
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_file)
            pbar.update(src_file.stat().st_size)
            copied += 1
    return copied


def _remap_label_file(path: Path) -> int:
    """Rewrite every YOLO class id to 0. Keep polygon / box coordinates."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return 0

    rewritten: list[str] = []
    n_objects = 0
    for line in lines:
        parts = line.split()
        if len(parts) < 5:
            continue
        parts[0] = "0"
        rewritten.append(" ".join(parts))
        n_objects += 1

    path.write_text("\n".join(rewritten) + ("\n" if rewritten else ""), encoding="utf-8")
    return n_objects


def remap_labels_to_single_class(dataset_dir: Path) -> tuple[int, int]:
    label_files = sorted((dataset_dir / "labels").rglob("*.txt"))
    n_objects = 0
    for path in tqdm(label_files, desc="Remapping classes → 0", unit="file"):
        n_objects += _remap_label_file(path)
    return len(label_files), n_objects


def write_single_class_yaml(dataset_dir: Path) -> Path:
    yaml_path = dataset_dir / "data.yaml"
    # Ultralytics resolves train/val/test relative to `path`.
    yaml_path.write_text(
        "\n".join(
            [
                f"path: {dataset_dir.resolve().as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "nc: 1",
                "names:",
                "  0: object",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return yaml_path


def _looks_like_dataset(path: Path) -> bool:
    return (path / "images").is_dir() and (path / "labels").is_dir()


def download_dataset(
    source: Path | None = None,
    dest: Path = DEFAULT_DEST,
    *,
    force: bool = False,
) -> Path:
    src = Path(source) if source is not None else _drive_folder("dataset")
    dest = Path(dest)

    if not _looks_like_dataset(src):
        raise FileNotFoundError(
            f"Source does not look like a YOLO dataset (need images/ and labels/): {src}"
        )

    already_there = dest.exists() and any(dest.rglob("*"))
    if already_there and not force:
        print(f"Destination already has files: {dest}")
        print("Skipping copy. Pass --force to recopy from Drive.")
    else:
        if already_there and force:
            print(f"Removing existing {dest} (--force)")
            shutil.rmtree(dest)
        print(f"Source : {src}")
        print(f"Dest   : {dest}")
        n_files = _copy_tree(src, dest)
        print(f"Copied {n_files} files")

    n_files, n_objects = remap_labels_to_single_class(dest)
    yaml_path = write_single_class_yaml(dest)
    n_images = sum(1 for p in (dest / "images").rglob("*") if p.suffix.lower() in IMAGE_EXTS)

    print()
    print(f"Images          : {n_images}")
    print(f"Label files     : {n_files}")
    print(f"Objects remapped: {n_objects}  (all class ids → 0 / object)")
    print(f"data.yaml       : {yaml_path}")
    return dest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the Drive YOLO dataset into train_v2/dataset as a single-class set."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Override the Drive dataset folder. Default: drive_folder('dataset').",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help=f"Local destination. Default: {DEFAULT_DEST}",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete the destination and recopy from source.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    download_dataset(source=args.source, dest=args.dest, force=args.force)


if __name__ == "__main__":
    main()
