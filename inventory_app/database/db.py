from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from config import DATABASE_URL, LOW_STOCK_THRESHOLD

INVENTORY_ORDER = """
ORDER BY
    CASE WHEN last_seen IS NULL OR last_seen = '' THEN 0 ELSE 1 END DESC,
    last_seen DESC,
    id DESC
"""

SEED_ITEMS = [
    ("Arduino Uno", "Reusable Asset", 5, "Single", "Shelf A1", "Available"),
    ("Paper Cups", "Consumable", 100, "Pack", "Shelf B2", "Available"),
    ("Screwdriver Set", "Reusable Asset", 2, "Single", "Shelf A3", "Checked Out"),
    ("Glue Sticks", "Consumable", 50, "Box", "Shelf C1", "Available"),
]


@contextmanager
def get_db():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def normalize_item_name(name):
    return " ".join(str(name or "").replace("_", " ").split())


def status_for_quantity(quantity, previous_status=None):
    if quantity <= 0:
        return "Checked Out"
    if previous_status and previous_status != "Checked Out":
        return previous_status
    return "Available"


def init_schema(clear_non_inventory=False, seed=True):
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                item_name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                unit_type TEXT,
                location TEXT,
                status TEXT DEFAULT 'Available',
                owner TEXT,
                last_seen TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                item_id INTEGER REFERENCES inventory(id),
                action TEXT,
                acted_by TEXT,
                timestamp TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id SERIAL PRIMARY KEY,
                class_name TEXT,
                count INTEGER,
                confidence DOUBLE PRECISION,
                direction TEXT DEFAULT 'SCAN',
                timestamp TEXT,
                scan_session TEXT,
                operator TEXT DEFAULT 'System'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS object_embeddings (
                id SERIAL PRIMARY KEY,
                object_name TEXT NOT NULL,
                embedding TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_item_name
            ON inventory (LOWER(item_name))
            """
        )

        if clear_non_inventory:
            conn.execute("DELETE FROM detections")
            conn.execute("DELETE FROM transactions")

        conn.execute(
            """
            DELETE FROM inventory a
            USING inventory b
            WHERE a.id > b.id
              AND LOWER(a.item_name) = LOWER(b.item_name)
            """
        )

        count = conn.execute("SELECT COUNT(*) AS n FROM inventory").fetchone()["n"]
        if seed and count == 0:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO inventory
                        (item_name, category, quantity, unit_type, location, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    SEED_ITEMS,
                )


def fetch_inventory(term=""):
    with get_db() as conn:
        needle = (term or "").strip()
        if needle:
            like = f"%{needle}%"
            rows = conn.execute(
                f"""
                SELECT * FROM inventory
                WHERE item_name ILIKE %s
                   OR location ILIKE %s
                   OR status ILIKE %s
                   OR category ILIKE %s
                   OR unit_type ILIKE %s
                {INVENTORY_ORDER}
                """,
                (like, like, like, like, like),
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT * FROM inventory {INVENTORY_ORDER}"
            ).fetchall()
        return [dict(row) for row in rows]


def fetch_item(item_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM inventory WHERE id = %s",
            (item_id,),
        ).fetchone()
        return dict(row) if row else None


def fetch_stats():
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END), 0) AS available,
                COALESCE(SUM(CASE WHEN status = 'Checked Out' THEN 1 ELSE 0 END), 0) AS checked_out,
                COALESCE(SUM(
                    CASE WHEN quantity > 0 AND quantity < %s THEN 1 ELSE 0 END
                ), 0) AS low_stock
            FROM inventory
            """,
            (LOW_STOCK_THRESHOLD,),
        ).fetchone()
        return {
            "total": int(row["total"] or 0),
            "available": int(row["available"] or 0),
            "checked_out": int(row["checked_out"] or 0),
            "low_stock": int(row["low_stock"] or 0),
        }


def fetch_detections(limit=100):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM detections ORDER BY id DESC LIMIT %s",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def fetch_detections_summary():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                class_name,
                SUM(count) AS total_count,
                AVG(confidence) AS avg_confidence,
                COUNT(*) AS frames
            FROM detections
            GROUP BY class_name
            ORDER BY total_count DESC
            """
        ).fetchall()
        return [
            {
                **dict(row),
                "avg_confidence": float(row["avg_confidence"])
                if row["avg_confidence"] is not None
                else None,
            }
            for row in rows
        ]


def fetch_detections_today():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM detections
            WHERE timestamp::date = CURRENT_DATE
            ORDER BY id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def _get_item_by_name(conn, item_name):
    return conn.execute(
        "SELECT * FROM inventory WHERE LOWER(item_name) = LOWER(%s)",
        (item_name,),
    ).fetchone()


def unique_item_name(conn, desired):
    name = normalize_item_name(desired)
    if not name:
        return ""
    if _get_item_by_name(conn, name) is None:
        return name
    index = 2
    while _get_item_by_name(conn, f"{name} {index}") is not None:
        index += 1
    return f"{name} {index}"


def apply_capture_to_inventory(conn, class_name, count, mode, timestamp, operator):
    item_name = normalize_item_name(class_name)
    if not item_name or count <= 0:
        return None

    row = _get_item_by_name(conn, item_name)
    action = {"IN": "check_in", "OUT": "check_out"}.get(mode, "scan")

    if row is None:
        if mode == "OUT":
            print(f"[INVENTORY] OUT refused, unknown item: {item_name}")
            return None
        quantity = count
        status = status_for_quantity(quantity)
        inserted = conn.execute(
            """
            INSERT INTO inventory
                (item_name, category, quantity, unit_type, location, status, last_seen)
            VALUES (%s, 'Detected', %s, 'Single', 'Camera', %s, %s)
            RETURNING id
            """,
            (item_name, quantity, status, timestamp),
        ).fetchone()
        item_id = inserted["id"]
        print(
            f"[INVENTORY] NEW {item_name} | mode={mode} qty={quantity} status={status}"
        )
    else:
        item_id = row["id"]
        quantity = int(row["quantity"] or 0)
        status = row["status"] or "Available"
        last_seen = row["last_seen"]

        if mode == "IN":
            quantity += count
            status = "Available"
            last_seen = timestamp
        elif mode == "OUT":
            quantity = max(0, quantity - count)
            status = status_for_quantity(quantity)
            last_seen = timestamp
        else:
            last_seen = timestamp

        conn.execute(
            """
            UPDATE inventory
            SET quantity = %s, status = %s, last_seen = %s
            WHERE id = %s
            """,
            (quantity, status, last_seen, item_id),
        )
        print(
            f"[INVENTORY] {item_name} | mode={mode} qty={quantity} status={status}"
        )

    conn.execute(
        """
        INSERT INTO transactions (item_id, action, acted_by, timestamp)
        VALUES (%s, %s, %s, %s)
        """,
        (item_id, action, operator, timestamp),
    )
    return item_id


def record_yolo_capture(grouped, mode, timestamp, session_id, operator):
    """
    Log YOLO classes and upsert them into inventory.
    grouped: {class_name: [confidence, ...]}
    """
    with get_db() as conn:
        rows = [
            (
                class_name,
                len(scores),
                sum(scores) / len(scores),
                mode,
                timestamp,
                session_id,
                operator,
            )
            for class_name, scores in grouped.items()
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO detections
                    (class_name, count, confidence, direction, timestamp, scan_session, operator)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
        for class_name, scores in grouped.items():
            apply_capture_to_inventory(
                conn,
                class_name,
                len(scores),
                mode,
                timestamp,
                operator,
            )


def check_db():
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return True, ""
    except Exception as exc:
        return False, str(exc)


def _save_object_embedding_conn(conn, object_name, embedding):
    import json

    conn.execute(
        """
        INSERT INTO object_embeddings (object_name, embedding)
        VALUES (%s, %s)
        """,
        (object_name, json.dumps(embedding)),
    )


def save_object_embedding(object_name, embedding):
    with get_db() as conn:
        _save_object_embedding_conn(conn, object_name, embedding)


def register_added_items(named_embeddings, timestamp, operator="System"):
    """
    Insert each (item_name, embedding) as quantity 1 in inventory.
    Names are made unique if they already exist.
    """
    saved = []
    with get_db() as conn:
        for requested_name, embedding in named_embeddings:
            item_name = unique_item_name(conn, requested_name)
            if not item_name:
                continue
            inserted = conn.execute(
                """
                INSERT INTO inventory
                    (item_name, category, quantity, unit_type, location, status, last_seen)
                VALUES (%s, 'Added', 1, 'Single', 'Camera', 'Available', %s)
                RETURNING id
                """,
                (item_name, timestamp),
            ).fetchone()
            conn.execute(
                """
                INSERT INTO transactions (item_id, action, acted_by, timestamp)
                VALUES (%s, %s, %s, %s)
                """,
                (inserted["id"], "add", operator, timestamp),
            )
            _save_object_embedding_conn(conn, item_name, embedding)
            saved.append({"id": inserted["id"], "item_name": item_name})
            print(f"[INVENTORY] ADDED {item_name} | qty=1")
    return saved
