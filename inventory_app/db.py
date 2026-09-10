import sqlite3

from config import DB_PATH, LOW_STOCK_THRESHOLD

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


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def normalize_item_name(name):
    return " ".join(str(name or "").replace("_", " ").split())


def status_for_quantity(quantity, previous_status=None):
    if quantity <= 0:
        return "Checked Out"
    if previous_status and previous_status != "Checked Out":
        return previous_status
    return "Available"


def init_schema(clear_non_inventory=False):
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                action TEXT,
                user TEXT,
                timestamp TEXT,
                FOREIGN KEY (item_id) REFERENCES inventory(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT,
                count INTEGER,
                confidence REAL,
                direction TEXT DEFAULT 'SCAN',
                timestamp TEXT,
                scan_session TEXT,
                operator TEXT DEFAULT 'System'
            )
            """
        )

        existing_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(detections)").fetchall()
        }
        required_columns = {
            "class_name": "TEXT",
            "count": "INTEGER",
            "confidence": "REAL",
            "direction": "TEXT DEFAULT 'SCAN'",
            "timestamp": "TEXT",
            "scan_session": "TEXT",
            "operator": "TEXT DEFAULT 'System'",
        }
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                conn.execute(
                    f"ALTER TABLE detections ADD COLUMN {column_name} {column_def}"
                )

        if clear_non_inventory:
            conn.execute("DELETE FROM detections")
            conn.execute("DELETE FROM transactions")

        conn.execute(
            """
            DELETE FROM inventory
            WHERE id NOT IN (
                SELECT MIN(id) FROM inventory GROUP BY item_name COLLATE NOCASE
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_item_name
            ON inventory(item_name COLLATE NOCASE)
            """
        )

        if conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO inventory
                    (item_name, category, quantity, unit_type, location, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                SEED_ITEMS,
            )

        conn.commit()
    finally:
        conn.close()


def fetch_inventory(term=""):
    conn = get_db()
    try:
        needle = (term or "").strip()
        if needle:
            like = f"%{needle}%"
            rows = conn.execute(
                f"""
                SELECT * FROM inventory
                WHERE item_name LIKE ? COLLATE NOCASE
                   OR location LIKE ? COLLATE NOCASE
                   OR status LIKE ? COLLATE NOCASE
                   OR category LIKE ? COLLATE NOCASE
                   OR unit_type LIKE ? COLLATE NOCASE
                {INVENTORY_ORDER}
                """,
                (like, like, like, like, like),
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT * FROM inventory {INVENTORY_ORDER}"
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_item(item_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM inventory WHERE id = ?",
            (item_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def fetch_stats():
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END), 0) AS available,
                COALESCE(SUM(CASE WHEN status = 'Checked Out' THEN 1 ELSE 0 END), 0) AS checked_out,
                COALESCE(SUM(
                    CASE WHEN quantity > 0 AND quantity < ? THEN 1 ELSE 0 END
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
    finally:
        conn.close()


def fetch_detections(limit=100):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM detections ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_detections_summary():
    conn = get_db()
    try:
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
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_detections_today():
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT * FROM detections
            WHERE date(timestamp) = date('now', 'localtime')
            ORDER BY id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _get_item_by_name(conn, item_name):
    return conn.execute(
        "SELECT * FROM inventory WHERE item_name = ? COLLATE NOCASE",
        (item_name,),
    ).fetchone()


def apply_capture_to_inventory(conn, class_name, count, mode, timestamp, operator):
    item_name = normalize_item_name(class_name)
    if not item_name or count <= 0:
        return None

    row = _get_item_by_name(conn, item_name)
    action = {"IN": "check_in", "OUT": "check_out"}.get(mode, "scan")

    if row is None:
        if mode == "OUT":
            quantity = 0
        else:
            quantity = count
        status = status_for_quantity(quantity)
        cursor = conn.execute(
            """
            INSERT INTO inventory
                (item_name, category, quantity, unit_type, location, status, last_seen)
            VALUES (?, 'Detected', ?, 'Single', 'Camera', ?, ?)
            """,
            (item_name, quantity, status, timestamp),
        )
        item_id = cursor.lastrowid
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
            SET quantity = ?, status = ?, last_seen = ?
            WHERE id = ?
            """,
            (quantity, status, last_seen, item_id),
        )
        print(
            f"[INVENTORY] {item_name} | mode={mode} qty={quantity} status={status}"
        )

    conn.execute(
        """
        INSERT INTO transactions (item_id, action, user, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (item_id, action, operator, timestamp),
    )
    return item_id


def record_yolo_capture(grouped, mode, timestamp, session_id, operator):
    """
    Log YOLO classes and upsert them into inventory.
    grouped: {class_name: [confidence, ...]}
    """
    conn = get_db()
    try:
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
        conn.executemany(
            """
            INSERT INTO detections
                (class_name, count, confidence, direction, timestamp, scan_session, operator)
            VALUES (?, ?, ?, ?, ?, ?, ?)
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
        conn.commit()
    finally:
        conn.close()
