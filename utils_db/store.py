"""Load, insert, and query object embeddings in pgvector."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from pgvector.psycopg import register_vector
from tqdm import tqdm

from .config import PgConfig


def load_embeddings_parquet(path: str | Path, vector_dim: int) -> pd.DataFrame:
    df = pd.read_parquet(path)
    dims = df["embedding"].map(len)
    print(f"rows: {len(df)}")
    print(f"embedding dim min/max: {dims.min()} / {dims.max()}")
    if dims.nunique() != 1:
        raise ValueError("All embeddings must have the same length")
    if int(dims.iloc[0]) != vector_dim:
        raise ValueError(f"Expected dim {vector_dim}, got {int(dims.iloc[0])}")
    return df


def connect_db(cfg: PgConfig):
    print(f"Connecting to {cfg.host}:{cfg.port}/{cfg.db} ...")
    conn = psycopg.connect(cfg.conninfo(), autocommit=True)
    register_vector(conn)
    print("Connected.")
    return conn


def create_object_table(conn, cfg: PgConfig, *, drop: bool = True) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        if drop:
            cur.execute(f"DROP TABLE IF EXISTS {cfg.table};")
        cur.execute(
            f"""
            CREATE TABLE {cfg.table} (
                id            BIGSERIAL PRIMARY KEY,
                image_name    TEXT NOT NULL,
                class_name    TEXT NOT NULL,
                bbox_xyxy     INTEGER[4] NOT NULL,
                embedding     vector({cfg.vector_dim}) NOT NULL
            );
            """
        )
    print(f"Ready: {cfg.table} (vector({cfg.vector_dim}))")


def insert_embeddings(conn, df: pd.DataFrame, cfg: PgConfig, *, batch_size: int = 200) -> int:
    rows = []
    for rec in df.itertuples(index=False):
        bbox = [int(v) for v in rec.bbox_xyxy]
        vec = np.asarray(rec.embedding, dtype=np.float32)
        rows.append((rec.image_name, rec.class_name, bbox, vec))

    sql = f"""
        INSERT INTO {cfg.table} (image_name, class_name, bbox_xyxy, embedding)
        VALUES (%s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        for start in tqdm(
            range(0, len(rows), batch_size),
            desc="Inserting into pgvector",
            unit="batch",
            dynamic_ncols=True,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        ):
            cur.executemany(sql, rows[start : start + batch_size])
        cur.execute(f"SELECT COUNT(*) FROM {cfg.table};")
        count = int(cur.fetchone()[0])
    print("inserted:", count)
    return count


def create_hnsw_index(conn, cfg: PgConfig) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {cfg.table}_embedding_hnsw
            ON {cfg.table}
            USING hnsw (embedding vector_cosine_ops);
            """
        )
        cur.execute(f"ANALYZE {cfg.table};")
    print("HNSW cosine index ready")


def close_db(conn) -> None:
    conn.close()
    print("Connection closed.")
