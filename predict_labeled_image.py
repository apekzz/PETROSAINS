"""Classify labeled objects in one image against the pgvector catalog (Rule 1)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.embed import load_clip_model
from utils_db import PgConfig, close_db, connect_db, predict_labeled_image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Crop objects from an image + YOLO label, embed them with OpenCLIP, "
            "and classify each box with Rule 1 (support threshold) against pgvector."
        )
    )
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--label", required=True, help="Path to the YOLO box/mask .txt label")
    parser.add_argument("--yaml", default=None, help="Optional data.yaml for label class names")
    parser.add_argument("--output", default="prediction_overlay.png", help="Where to save the overlay")
    parser.add_argument("--min-n", type=int, default=3, help="Rule 1 support threshold (default: 3)")
    parser.add_argument("--top-n", type=int, default=100, help="Top ranking rows used for voting")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--db", default="petrosains")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--password", default="ai_squad")
    parser.add_argument("--table", default="object_embeddings")
    parser.add_argument("--no-show", action="store_true", help="Do not open a matplotlib window")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = PgConfig(
        host=args.host,
        port=args.port,
        db=args.db,
        user=args.user,
        password=args.password,
        table=args.table,
        vector_dim=512,
    )
    conn = connect_db(cfg)
    try:
        model = load_clip_model()
        result = predict_labeled_image(
            args.image,
            args.label,
            conn,
            model,
            cfg,
            yaml_path=args.yaml,
            top_n=args.top_n,
            min_n=args.min_n,
            show=not args.no_show,
            output_path=args.output,
        )
        if len(result):
            print(result[["instance_id", "label_class", "pred_class", "n", "score"]])
    finally:
        close_db(conn)


if __name__ == "__main__":
    main()
