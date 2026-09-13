# Saved PostgreSQL tables

These CSV files are generated from the PostgreSQL tables used by the inventory
application. `manifest.json` records their columns, row counts, and export time.

During startup, the application:

1. Creates any missing required tables.
2. Reuses compatible tables that already contain data.
3. Restores a saved CSV only when its matching database table is empty.
4. Resets serial ID sequences and recalculates inventory availability.
5. Exports a fresh snapshot without deleting existing database rows.

Set `TABLE_SNAPSHOT_DIR` to use a different snapshot folder.
