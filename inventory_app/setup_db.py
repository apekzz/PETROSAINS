import sqlite3

from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create Inventory Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT,
        quantity INTEGER DEFAULT 0,
        unit_type TEXT,  -- 'Single', 'Pack', 'Box'
        location TEXT,
        status TEXT DEFAULT 'Available',  -- 'Available', 'Checked Out', 'Missing'
        owner TEXT,
        last_seen TEXT
    )
''')

# Create Transactions Table (for auditing)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        action TEXT,  -- 'check_in', 'check_out', 'scan'
        user TEXT,
        timestamp TEXT,
        FOREIGN KEY (item_id) REFERENCES inventory(id)
    )
''')

# Create Detections Table (YOLO scan logs)
cursor.execute('''
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
''')

# ALTER existing detections tables that were created before all columns existed
existing_columns = {
    row[1] for row in cursor.execute("PRAGMA table_info(detections)").fetchall()
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
        cursor.execute(f"ALTER TABLE detections ADD COLUMN {column_name} {column_def}")

# Insert dummy inventory only when the table is empty (avoids duplicates on re-run)
if cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
    cursor.executemany('''
        INSERT INTO inventory (item_name, category, quantity, unit_type, location, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        ('Arduino Uno', 'Reusable Asset', 5, 'Single', 'Shelf A1', 'Available'),
        ('Paper Cups', 'Consumable', 100, 'Pack', 'Shelf B2', 'Available'),
        ('Screwdriver Set', 'Reusable Asset', 2, 'Single', 'Shelf A3', 'Checked Out'),
        ('Glue Sticks', 'Consumable', 50, 'Box', 'Shelf C1', 'Available')
    ])

conn.commit()
conn.close()
print("Database created successfully!")
