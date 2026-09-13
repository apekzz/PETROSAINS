#!/usr/bin/env python3
"""All inventory_app SQL. main.py calls bootstrap_database() at boot.

Missing tables are created, compatible existing tables are reused, and empty
tables can be restored from saved_tables. Tables are never dropped or replaced.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

import psycopg
from psycopg import sql as pg_sql
from psycopg.rows import dict_row

from config import DATABASE_URL, LOW_STOCK_THRESHOLD

DUPLICATE_WINDOW_SECONDS = int(os.environ.get("DUPLICATE_WINDOW_SECONDS", "8"))

ADMIN_URL = os.environ.get(
    "POSTGRES_ADMIN_URL",
    "postgresql://postgres:ai_squad@127.0.0.1:5432/postgres",
)

REQUIRED_TABLES = {
    "main_inventory": """
        CREATE TABLE main_inventory (
            id SERIAL PRIMARY KEY,
            inventory_name TEXT NOT NULL UNIQUE,
            orig_quantity INTEGER DEFAULT 0,
            available_quantity INTEGER DEFAULT 0,
            registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "check_in_out": """
        CREATE TABLE check_in_out (
            id SERIAL PRIMARY KEY,
            inventory_name TEXT NOT NULL,
            staff_name TEXT,
            out_staff_name TEXT,
            in_staff_name TEXT,
            quantity INTEGER DEFAULT 1,
            out_dt TIMESTAMP,
            in_dt TIMESTAMP
        )
    """,
    "staff": """
        CREATE TABLE staff (
            staff_id TEXT PRIMARY KEY,
            staff_name TEXT NOT NULL,
            facial_embedding TEXT NOT NULL
        )
    """,
    "inventory_emb": """
        CREATE TABLE inventory_emb (
            id SERIAL PRIMARY KEY,
            inventory_name TEXT NOT NULL,
            inventory_embedding TEXT NOT NULL
        )
    """,
}

TABLE_COLUMNS = {
    "inventory_emb": ("id", "inventory_name", "inventory_embedding"),
    "main_inventory": (
        "id",
        "inventory_name",
        "orig_quantity",
        "available_quantity",
        "registered_date",
    ),
    "staff": ("staff_id", "staff_name", "facial_embedding"),
    "check_in_out": (
        "id",
        "inventory_name",
        "staff_name",
        "out_staff_name",
        "in_staff_name",
        "quantity",
        "out_dt",
        "in_dt",
    ),
}
SNAPSHOT_DIR = Path(
    os.environ.get(
        "TABLE_SNAPSHOT_DIR",
        str(Path(__file__).resolve().parent / "saved_tables"),
    )
)
SNAPSHOT_MANIFEST = "manifest.json"


def ensure_schema_columns(conn):
    """Safely migrate existing installations without dropping data."""
    conn.execute(
        """
        ALTER TABLE main_inventory
        ADD COLUMN IF NOT EXISTS available_quantity INTEGER DEFAULT 0
        """
    )
    conn.execute(
        """
        ALTER TABLE check_in_out
        ADD COLUMN IF NOT EXISTS out_staff_name TEXT
        """
    )
    conn.execute(
        """
        ALTER TABLE check_in_out
        ADD COLUMN IF NOT EXISTS in_staff_name TEXT
        """
    )
    conn.execute(
        """
        UPDATE check_in_out
        SET out_staff_name = staff_name
        WHERE out_staff_name IS NULL AND out_dt IS NOT NULL
        """
    )
    conn.execute(
        """
        UPDATE check_in_out
        SET in_staff_name = staff_name
        WHERE in_staff_name IS NULL AND in_dt IS NOT NULL AND out_dt IS NULL
        """
    )


def validate_required_schema(conn):
    """Reject incompatible existing tables without deleting or replacing them."""
    rows = conn.execute(
        """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = ANY(%s)
        """,
        (list(TABLE_COLUMNS),),
    ).fetchall()
    present = {}
    for row in rows:
        present.setdefault(row["table_name"], set()).add(row["column_name"])
    missing = {
        table: [column for column in columns if column not in present.get(table, set())]
        for table, columns in TABLE_COLUMNS.items()
    }
    missing = {table: columns for table, columns in missing.items() if columns}
    if missing:
        details = "; ".join(
            f"{table}: {', '.join(columns)}"
            for table, columns in missing.items()
        )
        raise RuntimeError(f"Incompatible PostgreSQL schema; missing columns: {details}")


def _copy_table_to_file(conn, table, columns, destination):
    statement = pg_sql.SQL(
        "COPY {} ({}) TO STDOUT WITH (FORMAT CSV, HEADER TRUE)"
    ).format(
        pg_sql.Identifier(table),
        pg_sql.SQL(", ").join(map(pg_sql.Identifier, columns)),
    )
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with temporary.open("wb") as output:
        with conn.cursor().copy(statement) as copy:
            for chunk in copy:
                output.write(bytes(chunk))
    temporary.replace(destination)


def export_table_snapshots(conn=None):
    """Export supported application tables to atomic CSV snapshots."""

    def _export(cur):
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        manifest = {
            "format": 1,
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "tables": {},
        }
        for table, columns in TABLE_COLUMNS.items():
            count = int(
                cur.execute(
                    pg_sql.SQL("SELECT COUNT(*) AS count FROM {}").format(
                        pg_sql.Identifier(table)
                    )
                ).fetchone()["count"]
            )
            filename = f"{table}.csv"
            _copy_table_to_file(
                cur,
                table,
                columns,
                SNAPSHOT_DIR / filename,
            )
            manifest["tables"][table] = {
                "file": filename,
                "columns": list(columns),
                "rows": count,
            }

        manifest_path = SNAPSHOT_DIR / SNAPSHOT_MANIFEST
        temporary = manifest_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        temporary.replace(manifest_path)
        return {
            table: details["rows"]
            for table, details in manifest["tables"].items()
        }

    if conn is not None:
        return _export(conn)
    with get_db() as owned:
        return _export(owned)


def _reset_serial_sequence(conn, table):
    if "id" not in TABLE_COLUMNS[table]:
        return
    conn.execute(
        pg_sql.SQL(
            """
            SELECT setval(
                pg_get_serial_sequence(%s, 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL
            )
            FROM {}
            """
        ).format(pg_sql.Identifier(table)),
        (table,),
    )


def restore_empty_tables_from_snapshots(conn):
    """Restore CSV data only into currently empty supported tables."""
    manifest_path = SNAPSHOT_DIR / SNAPSHOT_MANIFEST
    if not manifest_path.is_file():
        return {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read table snapshot manifest: {exc}") from exc

    restored = {}
    saved_tables = manifest.get("tables", {})
    for table in TABLE_COLUMNS:
        details = saved_tables.get(table)
        if not isinstance(details, dict):
            continue
        current_count = int(
            conn.execute(
                pg_sql.SQL("SELECT COUNT(*) AS count FROM {}").format(
                    pg_sql.Identifier(table)
                )
            ).fetchone()["count"]
        )
        if current_count:
            continue

        columns = tuple(details.get("columns") or ())
        allowed_columns = set(TABLE_COLUMNS[table])
        if (
            not columns
            or len(columns) != len(set(columns))
            or any(column not in allowed_columns for column in columns)
        ):
            raise RuntimeError(f"Invalid snapshot columns for table {table}")
        source = SNAPSHOT_DIR / str(details.get("file") or f"{table}.csv")
        if not source.is_file():
            continue

        statement = pg_sql.SQL(
            "COPY {} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
        ).format(
            pg_sql.Identifier(table),
            pg_sql.SQL(", ").join(map(pg_sql.Identifier, columns)),
        )
        with source.open("rb") as input_file:
            with conn.cursor().copy(statement) as copy:
                while chunk := input_file.read(1024 * 1024):
                    copy.write(chunk)
        _reset_serial_sequence(conn, table)
        restored[table] = int(
            conn.execute(
                pg_sql.SQL("SELECT COUNT(*) AS count FROM {}").format(
                    pg_sql.Identifier(table)
                )
            ).fetchone()["count"]
        )
    return restored

_boot_conn = None
_boot_lock = None


def _lock():
    global _boot_lock
    if _boot_lock is None:
        import threading

        _boot_lock = threading.Lock()
    return _boot_lock


def normalize_item_name(name):
    return " ".join(str(name or "").replace("_", " ").split())


def _embedding_to_text(embedding):
    return json.dumps([float(value) for value in embedding])


def _embedding_from_text(raw):
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [float(value) for value in raw]
    return [float(value) for value in json.loads(raw)]


def _open_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=8)


@contextmanager
def get_db():
    conn = _open_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def existing_tables(conn=None):
    def _read(cur):
        rows = cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        ).fetchall()
        return {row["table_name"] for row in rows}

    if conn is not None:
        return _read(conn)
    with get_db() as owned:
        return _read(owned)


def ensure_tables(conn=None):
    """Create only required tables that are not already in the database."""
    def _apply(cur):
        present = existing_tables(cur)
        created = []
        skipped = []
        for name, ddl in REQUIRED_TABLES.items():
            if name in present:
                skipped.append(name)
                continue
            cur.execute(ddl)
            created.append(name)
        return created, skipped

    if conn is not None:
        return _apply(conn)
    with get_db() as owned:
        return _apply(owned)


def _run(cmd):
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def ensure_postgres_running():
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        pass

    print("[SQL] Starting Docker Postgres (petrosains-pg)...")
    _run(["docker", "start", "petrosains-pg"])
    for _ in range(20):
        try:
            with psycopg.connect(ADMIN_URL, connect_timeout=2) as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            time.sleep(1)

    _run(["pg_isready"])
    try:
        with psycopg.connect(ADMIN_URL, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as exc:
        raise RuntimeError(
            "PostgreSQL is not running. Start it with: docker start petrosains-pg"
        ) from exc


def ensure_database():
    """Create the oneshot role and oneshot_inventory database if they are missing."""
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
            conn.execute("SELECT 1")
        return
    except Exception:
        pass

    admin = psycopg.connect(ADMIN_URL, autocommit=True, connect_timeout=8)
    with admin:
        roles = {row[0] for row in admin.execute("SELECT rolname FROM pg_roles").fetchall()}
        if "oneshot" not in roles:
            admin.execute("CREATE ROLE oneshot LOGIN PASSWORD 'oneshot'")
            print("[SQL] Created role: oneshot")
        databases = {
            row[0] for row in admin.execute("SELECT datname FROM pg_database").fetchall()
        }
        if "oneshot_inventory" not in databases:
            admin.execute("CREATE DATABASE oneshot_inventory OWNER oneshot")
            print("[SQL] Created database: oneshot_inventory")
        admin.execute("GRANT ALL PRIVILEGES ON DATABASE oneshot_inventory TO oneshot")

    with psycopg.connect(
        "postgresql://postgres:ai_squad@127.0.0.1:5432/oneshot_inventory",
        autocommit=True,
        connect_timeout=8,
    ) as inventory_admin:
        inventory_admin.execute("GRANT ALL ON SCHEMA public TO oneshot")
        inventory_admin.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO oneshot")
        inventory_admin.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO oneshot")


def bootstrap_database():
    """Called from main.py boot. Starts Postgres, creates missing DB/tables only."""
    ensure_postgres_running()
    ensure_database()
    return connect_and_prepare()


def connect_and_prepare():
    """Open the database at boot, keep a live connection, create missing tables."""
    global _boot_conn
    with _lock():
        if _boot_conn is not None and not _boot_conn.closed:
            try:
                _boot_conn.execute("SELECT 1")
                ensure_tables(_boot_conn)
                ensure_schema_columns(_boot_conn)
                validate_required_schema(_boot_conn)
                recalculate_available_quantities(_boot_conn)
                _boot_conn.commit()
                return _boot_conn
            except Exception:
                try:
                    _boot_conn.close()
                except Exception:
                    pass
                _boot_conn = None

        _boot_conn = _open_connection()
        _boot_conn.execute("SELECT 1")
        created, skipped = ensure_tables(_boot_conn)
        ensure_schema_columns(_boot_conn)
        validate_required_schema(_boot_conn)
        restored = restore_empty_tables_from_snapshots(_boot_conn)
        if "main_inventory" in restored or restored.get("inventory_emb"):
            refresh_main_inventory(_boot_conn)
        recalculate_available_quantities(_boot_conn)
        _boot_conn.commit()
        if created:
            print("[SQL] Created tables:", ", ".join(created))
        if skipped:
            print("[SQL] Already present:", ", ".join(skipped))
        if restored:
            summary = ", ".join(
                f"{table}={count}" for table, count in restored.items()
            )
            print("[SQL] Restored empty tables from snapshots:", summary)
        try:
            exported = export_table_snapshots(_boot_conn)
            summary = ", ".join(
                f"{table}={count}" for table, count in exported.items()
            )
            print(f"[SQL] Saved table snapshots: {SNAPSHOT_DIR} ({summary})")
        except Exception as exc:
            print("[SQL] Could not export table snapshots:", exc)
        print("[SQL] Database connection established")
        return _boot_conn


def close_boot_connection():
    global _boot_conn
    with _lock():
        if _boot_conn is not None:
            try:
                _boot_conn.close()
            except Exception:
                pass
            _boot_conn = None


def check_db():
    try:
        with _lock():
            if _boot_conn is not None and not _boot_conn.closed:
                _boot_conn.execute("SELECT 1")
                return True, ""
        with get_db() as conn:
            conn.execute("SELECT 1")
        return True, ""
    except Exception as exc:
        return False, str(exc)


def _open_checkout_qty(conn, inventory_name):
    row = conn.execute(
        """
        SELECT COALESCE(SUM(quantity), 0) AS qty
        FROM check_in_out
        WHERE inventory_name = %s
          AND out_dt IS NOT NULL
          AND in_dt IS NULL
        """,
        (inventory_name,),
    ).fetchone()
    return int(row["qty"] or 0)


def _inventory_status(orig_quantity, open_qty):
    available = max(0, int(orig_quantity or 0) - int(open_qty or 0))
    if available <= 0:
        return "Checked Out", available
    return "Available", available


def _format_dt(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _row_to_inventory(conn, row):
    available = int(row.get("available_quantity") or 0)
    status = "Available" if available > 0 else "Checked Out"
    registered = _format_dt(row.get("registered_date"))
    return {
        "id": row["id"],
        "item_name": row["inventory_name"],
        "inventory_name": row["inventory_name"],
        "quantity": int(row["orig_quantity"] or 0),
        "available": available,
        "orig_quantity": int(row["orig_quantity"] or 0),
        "unit_type": "item",
        "location": registered,
        "status": status,
        "owner": "",
        "last_seen": registered,
        "registered_date": registered,
    }


def fetch_inventory(term=""):
    with get_db() as conn:
        needle = (term or "").strip()
        if needle:
            like = f"%{needle}%"
            rows = conn.execute(
                """
                SELECT * FROM main_inventory
                WHERE inventory_name ILIKE %s
                ORDER BY registered_date DESC NULLS LAST, id DESC
                """,
                (like,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM main_inventory
                ORDER BY registered_date DESC NULLS LAST, id DESC
                """
            ).fetchall()
        return [_row_to_inventory(conn, row) for row in rows]


def fetch_item(item_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM main_inventory WHERE id = %s",
            (item_id,),
        ).fetchone()
        return _row_to_inventory(conn, row) if row else None


def fetch_stats():
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM main_inventory) AS unique_items,
                (SELECT COUNT(*) FROM staff) AS staff_registered,
                (
                    SELECT COUNT(*) FROM check_in_out
                    WHERE out_dt IS NOT NULL AND in_dt IS NULL
                ) AS checkout_sessions,
                (
                    SELECT COUNT(*) FROM main_inventory
                    WHERE available_quantity > 0
                      AND available_quantity < %s
                ) AS low_stock
            """,
            (LOW_STOCK_THRESHOLD,),
        ).fetchone()
        return {
            "total": int(row["unique_items"] or 0),
            "available": int(row["staff_registered"] or 0),
            "checked_out": int(row["checkout_sessions"] or 0),
            "low_stock": int(row["low_stock"] or 0),
        }


def refresh_main_inventory(conn=None):
    """Rebuild summary counts from inventory_emb. Keeps existing registered_date."""

    def _refresh(cur):
        cur.execute(
            """
            INSERT INTO main_inventory
                (inventory_name, orig_quantity, available_quantity, registered_date)
            SELECT inventory_name, COUNT(*)::int, COUNT(*)::int, CURRENT_TIMESTAMP
            FROM inventory_emb
            GROUP BY inventory_name
            ON CONFLICT (inventory_name) DO UPDATE
            SET orig_quantity = EXCLUDED.orig_quantity
            """
        )
        cur.execute(
            """
            DELETE FROM main_inventory AS m
            WHERE NOT EXISTS (
                SELECT 1
                FROM inventory_emb AS e
                WHERE e.inventory_name = m.inventory_name
            )
            """
        )
        recalculate_available_quantities(cur)

    if conn is not None:
        _refresh(conn)
        return
    with get_db() as owned:
        _refresh(owned)


def recalculate_available_quantities(conn, inventory_name=None):
    params = []
    where = ""
    if inventory_name:
        where = "WHERE m.inventory_name = %s"
        params.append(normalize_item_name(inventory_name))
    conn.execute(
        f"""
        UPDATE main_inventory AS m
        SET available_quantity = GREATEST(
            0,
            m.orig_quantity - COALESCE((
                SELECT SUM(c.quantity)
                FROM check_in_out AS c
                WHERE c.inventory_name = m.inventory_name
                  AND c.out_dt IS NOT NULL
                  AND c.in_dt IS NULL
            ), 0)
        )
        {where}
        """,
        params,
    )


def save_inventory_embedding(inventory_name, embedding):
    name = normalize_item_name(inventory_name)
    if not name:
        raise ValueError("inventory_name is required")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO inventory_emb (inventory_name, inventory_embedding)
            VALUES (%s, %s)
            """,
            (name, _embedding_to_text(embedding)),
        )
        refresh_main_inventory(conn)
    return name


def save_object_embedding(object_name, embedding):
    return save_inventory_embedding(object_name, embedding)


def replace_inventory_embeddings(rows):
    """Atomically replace the catalog and rebuild unique inventory counts."""
    prepared = [
        (normalize_item_name(name), _embedding_to_text(embedding))
        for name, embedding in rows
        if normalize_item_name(name)
    ]
    if not prepared:
        raise ValueError("No inventory embeddings to save")
    with get_db() as conn:
        conn.execute("DELETE FROM inventory_emb")
        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO inventory_emb (inventory_name, inventory_embedding)
                VALUES (%s, %s)
                """,
                prepared,
            )
        refresh_main_inventory(conn)
    return len(prepared)


def insert_check_in_out(inventory_name, staff_name, quantity, direction):
    name = normalize_item_name(inventory_name)
    staff = " ".join(str(staff_name or "Unknown").split())
    qty = max(1, int(quantity or 1))
    now = datetime.now()
    cutoff = now - timedelta(seconds=max(1, DUPLICATE_WINDOW_SECONDS))
    with get_db() as conn:
        inventory = conn.execute(
            """
            SELECT orig_quantity, available_quantity
            FROM main_inventory
            WHERE inventory_name = %s
            FOR UPDATE
            """,
            (name,),
        ).fetchone()
        if not inventory:
            print(f"[SQL] Movement excluded: {name} is not in main_inventory")
            return None

        stamp_column = "in_dt" if direction == "IN" else "out_dt"
        actor_column = "in_staff_name" if direction == "IN" else "out_staff_name"
        duplicate = conn.execute(
            f"""
            SELECT id FROM check_in_out
            WHERE inventory_name = %s
              AND {actor_column} = %s
              AND {stamp_column} IS NOT NULL
              AND {stamp_column} >= %s
            ORDER BY {stamp_column} DESC
            LIMIT 1
            """,
            (name, staff, cutoff),
        ).fetchone()
        if duplicate:
            print(
                f"[SQL] Duplicate suppressed: {direction} "
                f"{name} / {staff} within {DUPLICATE_WINDOW_SECONDS}s"
            )
            return None

        if direction == "IN":
            opened_rows = conn.execute(
                """
                SELECT id, quantity, out_dt, out_staff_name
                FROM check_in_out
                WHERE inventory_name = %s
                  AND out_staff_name = %s
                  AND out_dt IS NOT NULL
                  AND in_dt IS NULL
                ORDER BY out_dt ASC
                FOR UPDATE
                """,
                (name, staff),
            ).fetchall()
            outstanding = sum(int(row["quantity"] or 0) for row in opened_rows)
            return_qty = min(qty, outstanding)
            if return_qty <= 0:
                print(
                    f"[SQL] Check-in excluded: {staff} has no outstanding {name}"
                )
                return None

            remaining = return_qty
            movement_id = None
            for opened in opened_rows:
                if remaining <= 0:
                    break
                open_qty = int(opened["quantity"] or 0)
                if remaining >= open_qty:
                    conn.execute(
                        """
                        UPDATE check_in_out
                        SET in_dt = %s, in_staff_name = %s
                        WHERE id = %s
                        """,
                        (now, staff, opened["id"]),
                    )
                    movement_id = opened["id"]
                    remaining -= open_qty
                else:
                    conn.execute(
                        "UPDATE check_in_out SET quantity = %s WHERE id = %s",
                        (open_qty - remaining, opened["id"]),
                    )
                    completed = conn.execute(
                        """
                        INSERT INTO check_in_out (
                            inventory_name, staff_name,
                            out_staff_name, in_staff_name,
                            quantity, out_dt, in_dt
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            name,
                            opened["out_staff_name"],
                            opened["out_staff_name"],
                            staff,
                            remaining,
                            opened["out_dt"],
                            now,
                        ),
                    ).fetchone()
                    movement_id = completed["id"]
                    remaining = 0
            recalculate_available_quantities(conn, name)
            return movement_id

        available = int(inventory["available_quantity"] or 0)
        checkout_qty = min(qty, available)
        if checkout_qty <= 0:
            print(f"[SQL] Checkout excluded: no available stock for {name}")
            return None
        row = conn.execute(
            """
            INSERT INTO check_in_out (
                inventory_name, staff_name, out_staff_name,
                quantity, out_dt, in_dt
            )
            VALUES (%s, %s, %s, %s, %s, NULL)
            RETURNING id
            """,
            (name, staff, staff, checkout_qty, now),
        ).fetchone()
        recalculate_available_quantities(conn, name)
        return row["id"]


def record_yolo_capture(grouped, mode, timestamp, session_id, operator):
    """IN / OUT writes check_in_out. SCAN is view-only."""
    if mode not in {"IN", "OUT"}:
        return []
    staff_name = operator or "Unknown"
    inserted = []
    for class_name, scores in grouped.items():
        row_id = insert_check_in_out(
            class_name,
            staff_name,
            len(scores),
            mode,
        )
        if row_id is not None:
            inserted.append(class_name)
    return inserted


def clear_check_in_out():
    """Clear transient movement history without touching catalog/staff tables."""
    with get_db() as conn:
        conn.execute("DELETE FROM check_in_out")
        recalculate_available_quantities(conn)
    print("[SQL] Cleared check_in_out")


def fetch_movements(limit=200, staff_name=""):
    staff = " ".join(str(staff_name or "").split())
    if not staff:
        return []
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                id, inventory_name, staff_name,
                out_staff_name, in_staff_name,
                quantity, out_dt, in_dt
            FROM check_in_out
            WHERE out_staff_name = %s OR in_staff_name = %s
            ORDER BY id DESC
            LIMIT %s
            """,
            (staff, staff, limit),
        ).fetchall()
        return [_row_to_movement(row) for row in rows]


def _row_to_movement(row):
    return {
        "id": row["id"],
        "inventory_name": row["inventory_name"],
        "staff_name": row.get("staff_name"),
        "out_staff_name": row.get("out_staff_name") or row.get("staff_name"),
        "in_staff_name": row.get("in_staff_name"),
        "quantity": int(row["quantity"] or 0),
        "out_dt": _format_dt(row.get("out_dt")),
        "in_dt": _format_dt(row.get("in_dt")),
    }


def fetch_item_summary(inventory_name):
    name = normalize_item_name(inventory_name)
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT
                m.inventory_name,
                m.orig_quantity,
                m.available_quantity,
                (
                    SELECT COUNT(*)
                    FROM check_in_out AS c
                    WHERE c.inventory_name = m.inventory_name
                      AND c.out_dt IS NOT NULL
                ) AS checkout_frequency
            FROM main_inventory AS m
            WHERE m.inventory_name = %s
            """,
            (name,),
        ).fetchone()
        if not row:
            return None
        return {
            "inventory_name": row["inventory_name"],
            "original_stock": int(row["orig_quantity"] or 0),
            "available_stock": int(row["available_quantity"] or 0),
            "checkout_frequency": int(row["checkout_frequency"] or 0),
        }


def fetch_detections(limit=100):
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM check_in_out
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()
        return [_checkout_as_detection(row) for row in rows]


def fetch_detections_summary():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                inventory_name AS class_name,
                SUM(quantity) AS total_count,
                NULL AS avg_confidence,
                COUNT(*) AS frames
            FROM check_in_out
            GROUP BY inventory_name
            ORDER BY total_count DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def fetch_detections_today():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM check_in_out
            WHERE (out_dt::date = CURRENT_DATE OR in_dt::date = CURRENT_DATE)
            ORDER BY id DESC
            """
        ).fetchall()
        return [_checkout_as_detection(row) for row in rows]


def _checkout_as_detection(row):
    out_dt = row.get("out_dt")
    in_dt = row.get("in_dt")
    direction = "IN" if in_dt and not out_dt else "OUT" if out_dt and not in_dt else "IN"
    stamp = in_dt or out_dt
    return {
        "id": row["id"],
        "class_name": row["inventory_name"],
        "count": int(row["quantity"] or 0),
        "confidence": None,
        "direction": direction,
        "timestamp": _format_dt(stamp),
        "scan_session": "",
        "operator": row.get("staff_name") or "",
    }


def fetch_staff():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT staff_id, staff_name FROM staff ORDER BY staff_name"
        ).fetchall()
        return [dict(row) for row in rows]


def fetch_inventory_embeddings():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT inventory_name, inventory_embedding FROM inventory_emb"
        ).fetchall()
        return [
            {
                "inventory_name": row["inventory_name"],
                "inventory_embedding": _embedding_from_text(row["inventory_embedding"]),
            }
            for row in rows
        ]


def fetch_staff_embeddings():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT staff_id, staff_name, facial_embedding FROM staff"
        ).fetchall()
        return [
            {
                "staff_id": row["staff_id"],
                "staff_name": row["staff_name"],
                "facial_embedding": _embedding_from_text(row["facial_embedding"]),
            }
            for row in rows
        ]


def get_staff(staff_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT staff_id, staff_name FROM staff WHERE staff_id = %s",
            (str(staff_id).strip(),),
        ).fetchone()
        return dict(row) if row else None


def insert_staff(staff_id, staff_name, embedding):
    sid = str(staff_id or "").strip()
    name = " ".join(str(staff_name or "").split())
    if not sid or not name:
        raise ValueError("staff_id and staff_name are required")
    if get_staff(sid):
        raise ValueError(f"staff_id '{sid}' already exists")
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO staff (staff_id, staff_name, facial_embedding)
            VALUES (%s, %s, %s)
            """,
            (sid, name, _embedding_to_text(embedding)),
        )
    return {"staff_id": sid, "staff_name": name}


def table_status():
    present = existing_tables()
    return {
        name: ("present" if name in present else "missing")
        for name in REQUIRED_TABLES
    }


