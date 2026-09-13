#!/usr/bin/env python3
"""Create the Postgres role/database, tables, and optional SQLite import."""

import os
import sqlite3
import subprocess
import sys

_APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _sub in ("backend", "database", "boot"):
    _path = os.path.join(_APP_ROOT, _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import psycopg

from config import BASE_DIR, DATABASE_URL, SQLITE_PATH
from sql import connect_and_prepare, fetch_inventory, fetch_stats, table_status

ADMIN_URL = os.environ.get(
    "POSTGRES_ADMIN_URL",
    "postgresql://postgres:ai_squad@127.0.0.1:5432/postgres",
)


def _run(cmd):
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def ensure_postgres_running():
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
        return
    except Exception:
        pass

    _run(["docker", "start", "petrosains-pg"])
    for _ in range(20):
        try:
            with psycopg.connect(
                "postgresql://postgres:ai_squad@127.0.0.1:5432/postgres",
                connect_timeout=2,
            ) as conn:
                conn.execute("SELECT 1")
            return
        except Exception:
            import time

            time.sleep(1)

    result = _run(["pg_isready"])
    if result.returncode == 0:
        return
    _run(["brew", "services", "start", "postgresql@16"])
    _run(["brew", "services", "start", "postgresql"])
    result = _run(["pg_isready"])
    if result.returncode != 0:
        print("PostgreSQL is not running.")
        print("Start the Docker DB used by this repo:")
        print("  docker start petrosains-pg")
        print("Or install Postgres and start the service, then retry.")
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

    with psycopg.connect(
        "postgresql://postgres:ai_squad@127.0.0.1:5432/oneshot_inventory",
        autocommit=True,
    ) as inventory_admin:
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

    from sql import get_db

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
                """
                SELECT id FROM main_inventory
                WHERE LOWER(inventory_name) = LOWER(%s)
                """,
                (name,),
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """
                INSERT INTO main_inventory
                    (inventory_name, orig_quantity, registered_date)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                """,
                (name, row["quantity"] or 0),
            )
            copied += 1
    return copied


if __name__ == "__main__":
    ensure_postgres_running()
    ensure_database()
    connect_and_prepare()
    copied = migrate_sqlite_inventory()
    stats = fetch_stats()
    print("PostgreSQL is ready.")
    print("URL:", DATABASE_URL)
    print("Required tables:", table_status())
    if copied:
        print(f"Copied {copied} unique items from the old SQLite file.")
    print("Inventory stats:", stats)
    from sql import get_db
    with get_db() as conn:
        present = {
            row["table_name"]
            for row in conn.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            ).fetchall()
        }
        emb_count = 0
        if "inventory_emb" in present:
            emb_count = conn.execute(
                "SELECT COUNT(*) AS n FROM inventory_emb"
            ).fetchone()["n"]
    print("inventory_emb rows:", emb_count)
    print("Project folder:", BASE_DIR)
