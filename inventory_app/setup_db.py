#!/usr/bin/env python3
"""Create the Postgres role/database, tables, and optional SQLite import."""

import os
import sqlite3
import subprocess
import sys

import psycopg

from config import BASE_DIR, DATABASE_URL, SQLITE_PATH
from db import fetch_inventory, fetch_stats, init_schema

ADMIN_URL = os.environ.get("POSTGRES_ADMIN_URL", "postgresql:///postgres")


def _run(cmd):
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def ensure_postgres_running():
    result = _run(["pg_isready"])
    if result.returncode == 0:
        return
    _run(["brew", "services", "start", "postgresql@16"])
    _run(["brew", "services", "start", "postgresql"])
    result = _run(["pg_isready"])
    if result.returncode != 0:
        print("PostgreSQL is not running.")
        print("Install and start it with:")
        print("  brew install postgresql@16")
        print("  brew services start postgresql@16")
        sys.exit(1)


def ensure_database():
    """Create role + database if this machine can admin Postgres locally."""
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute("SELECT 1")
        return
    except Exception:
        pass

    try:
        admin = psycopg.connect(ADMIN_URL, autocommit=True)
    except Exception as exc:
        print("Could not connect to PostgreSQL as admin.")
        print("Tried:", ADMIN_URL)
        print("App URL:", DATABASE_URL)
        print(exc)
        sys.exit(1)

    with admin:
        roles = {
            row[0]
            for row in admin.execute("SELECT rolname FROM pg_roles").fetchall()
        }
        if "oneshot" not in roles:
            admin.execute("CREATE ROLE oneshot LOGIN PASSWORD 'oneshot'")
            print("Created role: oneshot")

        databases = {
            row[0]
            for row in admin.execute("SELECT datname FROM pg_database").fetchall()
        }
        if "oneshot_inventory" not in databases:
            admin.execute("CREATE DATABASE oneshot_inventory OWNER oneshot")
            print("Created database: oneshot_inventory")
        admin.execute("GRANT ALL PRIVILEGES ON DATABASE oneshot_inventory TO oneshot")

    with psycopg.connect("postgresql:///oneshot_inventory", autocommit=True) as inventory_admin:
        inventory_admin.execute("GRANT ALL ON SCHEMA public TO oneshot")
        inventory_admin.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO oneshot")
        inventory_admin.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO oneshot")
        inventory_admin.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO oneshot"
        )
        inventory_admin.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO oneshot"
        )


def migrate_sqlite_inventory():
    if not os.path.isfile(SQLITE_PATH):
        return 0
    current = fetch_inventory()
    if current:
        return 0

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    try:
        rows = sqlite_conn.execute(
            """
            SELECT item_name, category, quantity, unit_type, location, status, owner, last_seen
            FROM inventory
            """
        ).fetchall()
    except sqlite3.Error:
        return 0
    finally:
        sqlite_conn.close()

    if not rows:
        return 0

    from db import get_db

    seen = set()
    copied = 0
    with get_db() as conn:
        for row in rows:
            name = (row["item_name"] or "").strip()
            key = name.lower()
            if not name or key in seen:
                continue
            seen.add(key)
            exists = conn.execute(
                "SELECT id FROM inventory WHERE LOWER(item_name) = LOWER(%s)",
                (name,),
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """
                INSERT INTO inventory
                    (item_name, category, quantity, unit_type, location, status, owner, last_seen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    row["category"],
                    row["quantity"],
                    row["unit_type"],
                    row["location"],
                    row["status"],
                    row["owner"],
                    row["last_seen"],
                ),
            )
            copied += 1
    return copied


if __name__ == "__main__":
    ensure_postgres_running()
    ensure_database()
    init_schema(seed=False)
    copied = migrate_sqlite_inventory()
    init_schema()
    stats = fetch_stats()
    print("PostgreSQL is ready.")
    print("URL:", DATABASE_URL)
    if copied:
        print(f"Copied {copied} unique items from the old SQLite file.")
    print("Inventory stats:", stats)
    from db import get_db
    with get_db() as conn:
        embed_count = conn.execute(
            "SELECT COUNT(*) AS n FROM object_embeddings"
        ).fetchone()["n"]
    print("object_embeddings rows:", embed_count)
    print("Project folder:", BASE_DIR)
