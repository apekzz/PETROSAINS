"""PostgreSQL / pgvector connection settings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PgConfig:
    host: str = "127.0.0.1"
    port: int = 5432
    db: str = "petrosains"
    user: str = "postgres"
    password: str = "postgres"
    table: str = "object_embeddings"
    vector_dim: int = 512
    parquet_path: Path = Path("train_embeddings.parquet")
    connect_timeout: int = 5

    def conninfo(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.db} "
            f"user={self.user} password={self.password} "
            f"connect_timeout={self.connect_timeout}"
        )
