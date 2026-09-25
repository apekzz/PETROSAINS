# OneShot Inventory (`inventory_app`)

## Layout

```
inventory_app/
  main.py              # FastAPI entry (run from here)
  requirements.txt
  frontend/            # Dashboard UI (HTML/CSS/JS + logos)
  backend/             # Vision/API helpers (face, YOLO, SAM, config)
  database/            # SQL layer + inventory.db + saved_tables/
  boot/                # Boot progress loader
  models/              # Weights (.pt / .onnx / OpenCLIP)
  graphify-out/        # Code graph (local)
```

## Run

```bash
cd inventory_app
python main.py
```

Open http://127.0.0.1:8000
