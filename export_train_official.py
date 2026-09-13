"""Export the full train image catalog to train_official.parquet (no embeddings)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.dataset import build_embedding_dataframe
from utils.gdrive import drive_folder
from utils.visualize import list_images

OUTPUT_PATH = ROOT / "test_pg" / "train_official.parquet"


def main() -> None:
    dataset_dir = drive_folder("dataset")
    image_dir = dataset_dir / "images"
    images = list_images(image_dir)

    catalog = build_embedding_dataframe(
        images,
        dataset_dir=dataset_dir,
        split="train",
        n_per_class=None,
        include_embedding=False,
    )
    catalog.to_parquet(OUTPUT_PATH, index=False)
    print(f"Saved {len(catalog)} train rows to {OUTPUT_PATH}")
    print(catalog.head())


if __name__ == "__main__":
    main()
