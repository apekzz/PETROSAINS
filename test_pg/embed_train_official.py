"""Embed every labeled crop from train_official.parquet and save the results."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from utils.embed import build_embedding_df, load_clip_model
from utils.gdrive import drive_folder

CATALOG_PATH = HERE / "train_official.parquet"
OUTPUT_PATH = HERE / "train_embeddings.parquet"
FAIL_LOG_PATH = HERE / "embed_failures.txt"


def main() -> None:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CATALOG_PATH}. Run export_train_official.py from the repo root first."
        )

    catalog = pd.read_parquet(CATALOG_PATH)
    print(f"Loaded {len(catalog)} rows from {CATALOG_PATH}")

    dataset_dir = drive_folder("dataset")
    model = load_clip_model()  # OpenCLIP ViT-B-32, loaded once
    embedding_df = build_embedding_df(
        model,
        catalog,
        dataset_dir=dataset_dir,
        fail_log_path=FAIL_LOG_PATH,
    )

    save_df = embedding_df.copy()
    if len(save_df):
        save_df["embedding"] = save_df["embedding"].apply(
            lambda x: x.tolist() if hasattr(x, "tolist") else x
        )
    save_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"Saved {len(save_df)} crop embeddings to {OUTPUT_PATH}")
    print(f"Failure log: {FAIL_LOG_PATH}")


if __name__ == "__main__":
    main()
