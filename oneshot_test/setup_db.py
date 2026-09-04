import sqlite3

conn = sqlite3.connect('inventory.db')
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

# Insert some dummy data for testing (remove later)
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