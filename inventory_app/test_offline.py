#!/usr/bin/env python3
"""Check that OneShot Inventory can load models and the database offline."""

import os
import sys

_BASE = os.path.dirname(os.path.abspath(__file__))
os.environ["HF_HOME"] = os.path.join(_BASE, "models", "hf_cache")
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["YOLO_OFFLINE"] = "1"

sys.path.insert(0, _BASE)


def report(ok, label, detail=""):
    mark = "✅" if ok else "❌"
    extra = f"  {detail}" if detail else ""
    print(f"{mark}  {label}{extra}")
    return ok


def main():
    passed = []

    env_ok = (
        os.environ.get("HF_HUB_OFFLINE") == "1"
        and os.environ.get("TRANSFORMERS_OFFLINE") == "1"
    )
    passed.append(report(
        env_ok,
        "HF_HUB_OFFLINE and TRANSFORMERS_OFFLINE are 1",
        "" if env_ok else f"got HF_HUB_OFFLINE={os.environ.get('HF_HUB_OFFLINE')!r} TRANSFORMERS_OFFLINE={os.environ.get('TRANSFORMERS_OFFLINE')!r}",
    ))

    try:
        from ultralytics import YOLO
        from config import MODEL_PATH
        YOLO(MODEL_PATH)
        passed.append(report(True, "YOLO model loaded", MODEL_PATH))
    except Exception as exc:
        passed.append(report(False, "YOLO model loaded", str(exc)))

    try:
        from sentence_transformers import SentenceTransformer
        SentenceTransformer("clip-ViT-B-32")
        passed.append(report(True, "CLIP embedding model loaded"))
    except Exception as exc:
        passed.append(report(False, "CLIP embedding model loaded", str(exc)))

    try:
        from database.db import check_db
        ok, err = check_db()
        passed.append(report(bool(ok), "PostgreSQL connected", "" if ok else str(err)))
    except Exception as exc:
        passed.append(report(False, "PostgreSQL connected", str(exc)))

    all_ok = all(passed)
    print()
    print("summary:", f"{sum(passed)}/{len(passed)} passed")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
