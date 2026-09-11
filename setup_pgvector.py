"""Create the Docker Postgres DB (if needed) and load train_embeddings.parquet."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils_db import (
    PgConfig,
    close_db,
    connect_db,
    create_hnsw_index,
    create_object_table,
    insert_embeddings,
    load_embeddings_parquet,
)

CONTAINER = "petrosains-pg"
IMAGE = "pgvector/pgvector:pg16"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import train_embeddings.parquet into a local pgvector database."
    )
    parser.add_argument(
        "--parquet",
        default="train_embeddings.parquet",
        help="Shared catalog file (default: train_embeddings.parquet)",
    )
    parser.add_argument("--password", default="ai_squad")
    parser.add_argument("--skip-docker", action="store_true")
    return parser.parse_args()


def ensure_container(password: str) -> None:
    started = subprocess.run(
        ["docker", "start", CONTAINER],
        capture_output=True,
        text=True,
    )
    if started.returncode == 0:
        print(f"Started existing container {CONTAINER}")
        return

    print(f"Creating {CONTAINER} from {IMAGE} ...")
    created = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER,
            "-e",
            f"POSTGRES_PASSWORD={password}",
            "-e",
            "POSTGRES_DB=petrosains",
            "-p",
            "5432:5432",
            IMAGE,
        ],
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        raise RuntimeError(
            "Could not start Docker Postgres.\n"
            f"{created.stderr or started.stderr}\n"
            "Install Docker Desktop, then retry."
        )
    print(f"Created {CONTAINER}")


def fingerprint(df) -> dict:
    vecs = np.stack([np.asarray(v, dtype=np.float32) for v in df["embedding"]])
    return {
        "rows": int(len(df)),
        "dim": int(vecs.shape[1]),
        "classes": int(df["class_name"].nunique()),
        "vec_mean": float(vecs.mean()),
        "vec_std": float(vecs.std()),
    }


def main() -> None:
    args = parse_args()
    parquet_path = Path(args.parquet)
    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Missing {parquet_path}. Ask the team for the shared "
            "train_embeddings.parquet (do not re-embed unless you intend to)."
        )

    if not args.skip_docker:
        ensure_container(args.password)

    cfg = PgConfig(
        host="127.0.0.1",
        port=5432,
        db="petrosains",
        user="postgres",
        password=args.password,
        table="object_embeddings",
        vector_dim=512,
        parquet_path=parquet_path,
    )
    df = load_embeddings_parquet(cfg.parquet_path, cfg.vector_dim)
    stats = fingerprint(df)
    print("parquet fingerprint:", stats)

    conn = connect_db(cfg)
    try:
        create_object_table(conn, cfg, drop=True)
        insert_embeddings(conn, df, cfg)
        create_hnsw_index(conn, cfg)
    finally:
        close_db(conn)

    print("Database now matches this parquet file.")
    print("Compare fingerprint with your teammate. Same numbers = same catalog.")


if __name__ == "__main__":
    main()
