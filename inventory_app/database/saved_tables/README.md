# Saved PostgreSQL tables

CSV snapshots of inventory app tables. `manifest.json` records columns, row counts, and export time.

## Embedding catalogs (3)

| Table / CSV | Role |
|---|---|
| `inventory_emb` | Legacy (from abubu). **Unused for live match.** |
| `inventory_emb_mobileclip2` | Friend MobileCLIP2 catalog (abubu). Live dual A. |
| `inventory_emb_noise` | Hilman FaceTime-noise catalog. Live dual B. |

Live matching scores **both** mobileclip2 and noise. Compare UI: `/api/catalog/compare`.

During startup the app:

1. Creates any missing required tables.
2. Reuses compatible tables that already contain data.
3. Restores a saved CSV only when its matching database table is empty.
4. Resets serial ID sequences and recalculates inventory availability.
5. Exports a fresh snapshot without deleting existing database rows (emb CSVs skipped on boot).

Set `TABLE_SNAPSHOT_DIR` to use a different snapshot folder.
