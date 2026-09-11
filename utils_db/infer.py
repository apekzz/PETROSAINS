"""Predict classes for objects in one labeled image using pgvector + Rule 1."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from PIL import Image

from utils.dataset import crop_labeled_objects, load_image_and_label
from utils.embed import get_image_embedding
from utils.visualize import _class_color, load_class_names

from .config import PgConfig
from .eval import apply_vote_rule, collect_split_votes


def _color_for_name(name: str) -> tuple[float, float, float]:
    return _class_color(sum(ord(ch) for ch in str(name)) % 109)


def predict_labeled_image(
    image_path: str | Path,
    label_path: str | Path,
    conn,
    model,
    cfg: PgConfig,
    *,
    yaml_path: str | Path | None = None,
    top_n: int = 100,
    min_n: int = 3,
    show: bool = True,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Crop each labeled object, embed it, apply Rule 1, and draw the result.

    Object order is ``instance_id`` (label line order) so each prediction
    maps back to the same box / mask.
    """
    image_path = Path(image_path)
    label_path = Path(label_path)
    image, labels = load_image_and_label(
        image_path=image_path,
        label_path=label_path,
        yaml_path=Path(yaml_path) if yaml_path else None,
    )
    crops = crop_labeled_objects(image, labels)
    if not crops:
        print(f"No labeled objects in {label_path}")
        return pd.DataFrame()

    query_objects = []
    for item in crops:
        query_objects.append(
            {
                "image_name": image_path.name,
                "instance_id": item["instance_id"],
                "class_name": item["class_name"],
                "bbox_xyxy": list(item["bbox_xyxy"]),
                "kind": item["kind"],
                "points": item["points"],
                "embedding": get_image_embedding(model, item["crop"]),
            }
        )
        print(
            f"embedded [{item['instance_id']}] "
            f"label={item['class_name']}  bbox={item['bbox_xyxy']}"
        )

    vote_df = collect_split_votes(conn, query_objects, cfg, top_n=top_n)
    pred_df = apply_vote_rule(vote_df, rule="support", min_n=min_n)

    by_id = {int(row.instance_id): row for row in pred_df.itertuples(index=False)}
    rows = []
    for item in query_objects:
        pred = by_id.get(int(item["instance_id"]))
        pred_class = pred.pred_class if pred is not None else None
        rows.append(
            {
                "instance_id": item["instance_id"],
                "label_class": item["class_name"],
                "pred_class": pred_class,
                "score": float(pred.score) if pred is not None else np.nan,
                "avg_cosine_sim": float(pred.avg_cosine_sim) if pred is not None else np.nan,
                "n": int(pred.n) if pred is not None else 0,
                "bbox_xyxy": item["bbox_xyxy"],
                "kind": item["kind"],
                "points": item["points"],
            }
        )
        print(
            f"  [{item['instance_id']}] {item['class_name']} -> "
            f"{pred_class}  n={int(pred.n) if pred is not None else 0}  "
            f"score={float(pred.score) if pred is not None else float('nan'):.3f}"
        )

    result = pd.DataFrame(rows)
    draw_predictions(image, result, show=show, output_path=output_path, title=image_path.name)
    return result


def draw_predictions(
    image: Image.Image,
    result: pd.DataFrame,
    *,
    show: bool = True,
    output_path: str | Path | None = None,
    title: str = "",
) -> None:
    """Draw bbox + segmentation mask + predicted class on the input image."""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(np.asarray(image))
    for rec in result.itertuples(index=False):
        name = rec.pred_class or "unknown"
        color = _color_for_name(name)
        if rec.kind == "box":
            (x1, y1), (x2, y2) = rec.points
            ax.add_patch(
                Rectangle(
                    (x1, y1),
                    x2 - x1,
                    y2 - y1,
                    fill=False,
                    linewidth=2,
                    edgecolor=color,
                )
            )
            text_xy = (x1, max(0, y1 - 8))
        else:
            ax.add_patch(
                Polygon(
                    rec.points,
                    closed=True,
                    fill=True,
                    alpha=0.28,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=2,
                )
            )
            x1, y1, x2, y2 = rec.bbox_xyxy
            ax.add_patch(
                Rectangle(
                    (x1, y1),
                    x2 - x1,
                    y2 - y1,
                    fill=False,
                    linewidth=1.5,
                    linestyle="--",
                    edgecolor=color,
                )
            )
            text_xy = rec.points[0]
        label = f"[{rec.instance_id}] {name}"
        if pd.notna(rec.score):
            label += f"  n={rec.n}  {rec.score:.3f}"
        ax.text(
            text_xy[0],
            text_xy[1],
            label,
            color="white",
            fontsize=8,
            va="bottom",
            ha="left",
            bbox={"facecolor": color, "edgecolor": "none", "pad": 2, "alpha": 0.9},
        )
    ax.axis("off")
    ax.set_title(title or "Predicted inventory classes")
    fig.tight_layout()
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"saved overlay to {output_path}")
    if show:
        plt.show()
    else:
        plt.close(fig)
