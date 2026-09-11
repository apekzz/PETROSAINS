# PETROSAINS inventory similarity

This repo finds **which catalog SKU** a cropped object is, using **OpenCLIP ViT-B-32** embeddings and **pgvector** nearest-neighbor search.

The usual path is:

1. Put the YOLO dataset on **Google Drive** and sync it locally.
2. Export the **train catalog** to parquet.
3. Embed every train crop with **OpenCLIP**.
4. Load those vectors into **Postgres / pgvector** and evaluate rules in the notebook.
5. Classify a new image + label file with `predict_labeled_image.py`.

---

## A. Dataset and Google Drive

You need the official dataset on your Drive, then a **local sync** so Python can read the files.

- **Place the dataset in Google Drive.** It must contain `images/`, `labels/`, and `data.yaml`.
- **Install Google Drive for Desktop** and sign in with the same account.
- **Sync / stream the folder to this PC.** On Windows it should appear under `G:\My Drive`.
- **If the dataset is in Shared with me**, create a shortcut into **My Drive** (Drive Desktop often shows that shortcut as `dataset.lnk`).
- **Keep Drive running** while you export, embed, or evaluate. The helpers in `utils/gdrive.py` look for `G:\My Drive\dataset` or that shortcut.

---

## B. Extract inventory as a catalog parquet

This step walks the **train** split and writes one row per image (name, path, class names). **No embeddings yet.** That catalog is what we later crop and embed before the database.

- **Open a terminal** in this repo folder.
- **Run:**

```bash
python export_train_official.py
```

- **Output:** `train_official.parquet`
- **What it contains:** `image_name`, `path`, `class_name` for every train image.

---

## C. Generate training embeddings with OpenCLIP

Each **labeled object** in each catalog image is cropped from its bbox / mask, then encoded with **OpenCLIP ViT-B-32** (`laion2b_s34b_b79k`). One image can produce several rows.

- **Install the encoder once:** `pip install open-clip-torch`
- **Run:**

```bash
python embed_train_official.py
```

- **The model is loaded once**, then every crop is embedded (do not reload weights per image).
- **Output:** `train_embeddings.parquet`
  - Columns: `image_name`, `class_name`, `bbox_xyxy`, `embedding` (**512-d**, L2-normalized)
- **Failures** (if any) are appended to `embed_failures.txt`.

You now have vectors ready for pgvector.

---

## Share the same Postgres catalog with the team

Do **not** copy the Docker volume or dump live Postgres. The file that must match is **`train_embeddings.parquet`** (~14 MB). That is the exact OpenCLIP catalog.

- **One person embeds** (`embed_train_official.py`) and keeps that parquet.
- **Everyone else uses that same file.** Do not re-run embedding unless you mean to replace the catalog.
- **Put `train_embeddings.parquet` next to the repo** (Drive / OneDrive / zip). It is not required to live in git.
- **Each teammate imports it into their own empty Docker DB:**

```bash
docker start petrosains-pg
python setup_pgvector.py
```

- **First time only**, if the container does not exist, `setup_pgvector.py` creates `petrosains-pg` (password `ai_squad`).
- **The script prints a fingerprint** (`rows`, `dim`, `classes`, `vec_mean`, `vec_std`). Compare it with your teammate. **Same numbers = same catalog.**
- Optional val cache: share **`val_objects.pkl`** too if you want the notebook eval without re-embedding val.

---

## D. Development mode: prediction and evaluation

This is `pgvector_import.ipynb`. It **loads the parquet into Postgres**, then scores **val** crops against the catalog and compares filtration rules.

### 1. Start Postgres with Docker

Without Docker (or a running pgvector container), the notebook **cannot connect**.

- **Install Docker Desktop** and start it.
- **First time only**, create the container:

```bash
docker run -d --name petrosains-pg -e POSTGRES_PASSWORD=ai_squad -e POSTGRES_DB=petrosains -p 5432:5432 pgvector/pgvector:pg16
```

- **Later sessions**, just start it:

```bash
docker start petrosains-pg
```

- **Connection used in the notebook:** host `127.0.0.1`, port `5432`, database `petrosains`, user `postgres`, password `ai_squad`.
- Use **`127.0.0.1`**, not `localhost`, on Windows.

### 2. Load catalog vectors into pgvector

From a terminal you can load the shared parquet in one step: `python setup_pgvector.py`.

Or in `pgvector_import.ipynb`, run **sections 1–7**:

- **Load** `train_embeddings.parquet` (`vector_dim=512`).
- **Connect** to Postgres.
- **Create** the `object_embeddings` table (this **drops** the old table).
- **Insert** every crop row.
- **Build** the HNSW cosine index.

Skip recreate/insert only if that table is already filled with the current 512-d OpenCLIP vectors.

### 3. Evaluate on val / test

Then run **sections 8–16**:

- **Load** val and test image lists from the Drive dataset.
- **Load OpenCLIP once** (same weights as `embed_train_official.py`).
- **Embed all val crops** (first time) and **save** them with `save_query_objects()`, or **load** `val_objects.pkl` next time.
- **Rank** each crop against every database row (top 100).
- **Compare filtration rules** and look at accuracy / macro precision / macro recall:

| Rule | Idea |
|---|---|
| **Rule 3 — soft vote** | `total_score = avg_cosine_sim × n` |
| **Rule 1 — support threshold** | keep classes with `n >= min_n` (default **3**), then argmax average cosine |
| **Rule 2 — log-frequency** | `avg_cosine_sim × ln(1 + n)` |
| **Rule 4 — Bayesian shrink** | `(n · avg + m · μ0) / (n + m)` |

**Rule 1 (support threshold) currently gives the best result** on this val set. Use that rule for the standalone prediction script.

- **Close the connection last** (section 16).

---

## E. Predict one image (`predict_labeled_image.py`)

Use this after the embedding table is **already in Postgres**. It does **not** train anything.

### What it does

1. Reads **your image** and a **YOLO label** (bbox and/or polygon mask).
2. Crops each object **in label-line order** (`instance_id` 0, 1, 2, …).
3. Embeds each crop with **OpenCLIP ViT-B-32**.
4. Searches pgvector and applies **Rule 1**: `n >= min_n`, then highest **average cosine**.
5. Draws the **predicted class**, **bbox**, and **segmentation mask** back on the input image.

Sequence is preserved: crop `i` is the same box/mask as prediction `i`.

### Input

| Argument | Required | Meaning |
|---|---|---|
| **`--image`** | yes | Photo to classify |
| **`--label`** | yes | YOLO `.txt` next to that photo (class id + box **or** polygon) |
| **`--yaml`** | no | `data.yaml` so printed label names match the dataset |
| **`--output`** | no | Overlay image path (default `prediction_overlay.png`) |
| **`--min-n`** | no | Rule 1 threshold (default **3**) |
| **`--top-n`** | no | Ranking depth (default **100**) |
| **`--password`** | no | Postgres password (default `ai_squad`) |
| **`--no-show`** | no | Save the overlay without opening a window |

Label format is standard YOLO:

- **Box:** `class_id cx cy w h` (normalized)
- **Mask:** `class_id x1 y1 x2 y2 ...` (normalized polygon)

### Output

- **Console table:** `instance_id`, label class (from the file), **predicted class**, support `n`, score
- **Overlay image:** input photo with mask fill, dashed/solid box, and the predicted SKU name on each object
- **Return value** (if you import the function): a pandas DataFrame, one row per object

### How to run

From the repo folder, with Docker already running and the catalog imported:

```bash
python predict_labeled_image.py --image L001_test_tubes__L001_TEST_TUBE_L001_04.jpg --label L001_test_tubes__L001_TEST_TUBE_L001_04.txt --output overlay.png
```

- **`--image`** / **`--label`:** sample photo and YOLO label already in this repo
- **`--output`:** writes `overlay.png` with predicted class, bbox, and mask

If Postgres is not up yet:

```bash
docker start petrosains-pg
```

Optional extra flags:

```bash
python predict_labeled_image.py --image L001_test_tubes__L001_TEST_TUBE_L001_04.jpg --label L001_test_tubes__L001_TEST_TUBE_L001_04.txt --yaml path/to/data.yaml --min-n 3 --no-show
```

**Requirements:** Docker container running, `train_embeddings.parquet` already inserted (notebook sections 1–7), and OpenCLIP weights (downloaded on first `load_clip_model()`).
