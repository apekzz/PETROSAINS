from fastapi import APIRouter, HTTPException, Query
import sqlite3

from config import DB_PATH, LOW_STOCK_THRESHOLD

# Create an API Router with a prefix so all URLs start with /api
router = APIRouter(prefix="/api", tags=["Inventory API"])

# Helper to connect to database
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# API 1: Get all inventory items
@router.get("/inventory")
def get_inventory():
    conn = get_db()
    items = conn.execute("SELECT * FROM inventory").fetchall()
    conn.close()
    return [dict(item) for item in items]

# API 2: Get Stats (Total, Available, Checked Out, Low Stock) in ONE call
@router.get("/stats")
def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    available = conn.execute("SELECT COUNT(*) FROM inventory WHERE status='Available'").fetchone()[0]
    checked_out = conn.execute("SELECT COUNT(*) FROM inventory WHERE status='Checked Out'").fetchone()[0]
    low_stock = conn.execute(
        "SELECT COUNT(*) FROM inventory WHERE quantity < ?",
        (LOW_STOCK_THRESHOLD,),
    ).fetchone()[0]
    conn.close()
    return {
        "total": total,
        "available": available,
        "checked_out": checked_out,
        "low_stock": low_stock
    }

# API 3: Search items by name, location, status, and related fields
@router.get("/search")
def search_inventory(
    q: str = Query("", alias="q"),
    query: str = Query("", alias="query"),
):
    conn = get_db()
    term = f"%{(q or query).strip()}%"
    items = conn.execute(
        """
        SELECT * FROM inventory
        WHERE item_name LIKE ? COLLATE NOCASE
           OR location LIKE ? COLLATE NOCASE
           OR status LIKE ? COLLATE NOCASE
           OR category LIKE ? COLLATE NOCASE
           OR unit_type LIKE ? COLLATE NOCASE
        """,
        (term, term, term, term, term),
    ).fetchall()
    conn.close()
    return [dict(item) for item in items]

# API 4: Get a specific item by ID
@router.get("/items/{item_id}")
def get_item(item_id: int):
    conn = get_db()
    item = conn.execute("SELECT * FROM inventory WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(item)