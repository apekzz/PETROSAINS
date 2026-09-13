# PETROSAINS

Team repo for the Petrosains inventory project: YOLO segmentation, image similarity with OpenCLIP + pgvector, and the inventory dashboard.

Full pgvector / embedding instructions live in **`test_pg/README.md`**.

The app you **run as a product** is **`inventory_app/`**: a FastAPI dashboard with a live camera and YOLO detections. It uses its **own** Postgres database (`oneshot_inventory`), not the `petrosains` pgvector catalog in `test_pg`.

---

## How to run the inventory app

### What you need

- **Python 3.10+**
- **PostgreSQL** running on this machine (or Docker)
- **A webcam** (index `0` by default)
- **YOLO weights** at `inventory_app/models/best.pt` (create the `models` folder and copy your trained `best.pt` there)

This is **not** the same DB as `test_pg` (`petrosains` / password `ai_squad`). The dashboard expects:

- **host:** `127.0.0.1`
- **port:** `5432`
- **database:** `oneshot_inventory`
- **user:** `oneshot`
- **password:** `oneshot`

### Steps

1. **Start PostgreSQL**
   - **Windows:** start the Postgres service, or run a Docker container that listens on `5432`.
   - **Mac:**

     ```bash
     brew services start postgresql@16
     ```

2. **Open a terminal in `inventory_app/`**

   ```bash
   cd inventory_app
   ```

3. **Copy the env file** (once)

   ```bash
   copy .env.example .env
   ```

   On Mac/Linux use `cp .env.example .env`. Edit `.env` only if your Postgres login is different.

4. **Install Python packages** (once)

   ```bash
   python -m pip install -r requirements.txt
   ```

5. **Put the YOLO model in place** (once)

   - Create `inventory_app/models/`
   - Copy **`best.pt`** to `inventory_app/models/best.pt`

6. **Start the app**

   ```bash
   python main.py
   ```

   Boot starts Postgres if needed, creates missing tables, and loads models. Do not run `sql.py` or `setup_db.py`.

7. **Open the dashboard**
   - This PC: **http://127.0.0.1:8000**
   - API docs: **http://127.0.0.1:8000/docs**
   - Camera feed: **http://127.0.0.1:8000/video_feed**
   - Other devices on the same Wi-Fi: use the LAN URL printed in the terminal

### Daily use (after first setup)

```bash
cd inventory_app
python main.py
```

More detail (backup, `psql`, reset tables): **`inventory_app/README`**.

---

## Root layout

### Folders

- **`test_pg/`** — OpenCLIP catalog, pgvector import notebook, eval cache, and one-image prediction. Start here for similarity search. See `test_pg/README.md`.
- **`utils/`** — Shared dataset helpers: Drive paths, YOLO label/crop loading, visualization, OpenCLIP embed functions.
- **`utils_db/`** — Postgres / pgvector helpers: connect, insert, rank, vote rules, confusion matrix, labeled-image inference.
- **`inventory_app/`** — FastAPI + dashboard for live inventory scans. Has its own `inventory_app/README`.
- **`models/`** — Local YOLO weights (for example `yolo11n-seg.pt`).
- **`aiic_model_handoff/`** — Packaged YOLO handoff (`data.yaml` and related files).
- **`ai training/`** — Older segmentation training notebooks (BCE / Dice).
- **`train file/`** — Later training notebooks from `main` (BCE, Dice, single-class YOLO).
- **`train result 1 2/`** — Saved training outputs / run artifacts.
- **`.idea/`** — PyCharm / IDE project files.

### Files

- **`README.md`** — This file: what each top-level item is.
- **`export_train_official.py`** — Builds the train image catalog and writes `test_pg/train_official.parquet`.
- **`evaluation.ipynb`** — Extra evaluation notebook at repo root.
- **`training_bce.ipynb`**, **`training_bce_dice.ipynb`**, **`training_dice.ipynb`** — Training notebooks kept at the root.
- **`test_sahi.py`**, **`test_normal_yolo.py`** — Quick scripts to compare SAHI vs normal YOLO detection.

---

## `test_pg/` (similarity pipeline)

| Item | What it is |
|---|---|
| **`README.md`** | How to export, embed, load Postgres, evaluate rules, and predict one image |
| **`export` is at repo root** | `export_train_official.py` still runs from the repo root |
| **`embed_train_official.py`** | Crops train objects and writes OpenCLIP embeddings |
| **`train_official.parquet`** | Train catalog (no vectors) |
| **`train_embeddings.parquet`** | Shared 512-d catalog to import into pgvector |
| **`setup_pgvector.py`** | Starts Docker Postgres and loads the parquet |
| **`pgvector_import.ipynb`** | Dev notebook: insert vectors, score val, compare vote rules |
| **`predict_labeled_image.py`** | Classify one image + YOLO label (Rule 1) |
| **`val_objects.pkl`** | Cached val embeddings so you can skip re-embed |
| **`embed_failures.txt`** | Log of crops that failed to embed |
| **`L001_test_tubes__…jpg/.txt`** | Sample photo + segmentation label |
| **`overlay.png`** | Sample prediction overlay |

---

## Typical entry points

- **Dashboard / inventory UI:** `inventory_app/`
- **Catalog + similarity + eval:** `test_pg/README.md`
- **Train a detector:** `train file/` or the root `training_*.ipynb` notebooks
