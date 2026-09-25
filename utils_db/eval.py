"""Val/test query helpers: load splits, embed a crop, rank against pgvector."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from tqdm import tqdm

from utils.dataset import crop_labeled_objects, load_image_and_label
from utils.embed import get_image_embedding
from utils.gdrive import drive_folder
from utils.visualize import _class_color, list_images, load_class_names

from .config import PgConfig


def load_val_test_splits(dataset_name: str = "dataset") -> dict:
    dataset_dir = drive_folder(dataset_name)
    val_image_dir = dataset_dir / "images" / "val"
    test_image_dir = dataset_dir / "images" / "test"
    val_label_dir = dataset_dir / "labels" / "val"
    test_label_dir = dataset_dir / "labels" / "test"

    val_images = list_images(val_image_dir)
    test_images = list_images(test_image_dir)

    print("Val images :", val_image_dir, len(val_images))
    print("Val labels :", val_label_dir, "exists" if val_label_dir.exists() else "missing")
    print("Test images:", test_image_dir, len(test_images))
    print("Test labels:", test_label_dir, "exists" if test_label_dir.exists() else "missing")
    print("example val :", val_images[0].name if val_images else None)
    print("example test:", test_images[0].name if test_images else None)

    return {
        "dataset_dir": dataset_dir,
        "val_images": val_images,
        "test_images": test_images,
        "val_label_dir": val_label_dir,
        "test_label_dir": test_label_dir,
    }


def pick_query_image(
    splits: dict,
    *,
    split: str = "val",
    index: int = 0,
    show: bool = True,
) -> dict:
    split_images = splits["val_images"] if split == "val" else splits["test_images"]
    query_path = split_images[index]
    image, labels = load_image_and_label(
        image_path=query_path,
        dataset_dir=splits["dataset_dir"],
    )
    crops = crop_labeled_objects(image, labels)

    print("split:", split)
    print("image:", query_path)
    print("labels:", len(labels), "crops:", len(crops))
    for item in crops:
        print(f"  [{item['instance_id']}] {item['class_name']}  bbox={item['bbox_xyxy']}")

    if show:
        fig, ax = plt.subplots()
        ax.imshow(np.asarray(image))
        for item in crops:
            x1, y1, x2, y2 = item["bbox_xyxy"]
            color = _class_color(item["class_id"])
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
            ax.text(
                x1,
                max(0, y1 - 8),
                f"[{item['instance_id']}] {item['class_name']}",
                color="white",
                fontsize=8,
                va="bottom",
                ha="left",
                bbox={"facecolor": color, "edgecolor": "none", "pad": 2, "alpha": 0.9},
            )
        ax.axis("off")
        ax.set_title(f"{split}/{query_path.name}  ({len(crops)} objects)")
        plt.show()

    return {
        "split": split,
        "path": query_path,
        "image": image,
        "labels": labels,
        "crops": crops,
    }


def embed_query_crops(query: dict, model) -> list[dict]:
    """Embed labeled crops with a preloaded OpenCLIP model (does not load weights)."""
    if model is None:
        raise ValueError("Pass a preloaded OpenCLIP model from load_clip_model().")

    objects: list[dict] = []
    for item in query["crops"]:
        embedding = get_image_embedding(model, item["crop"])
        objects.append(
            {
                "instance_id": item["instance_id"],
                "class_name": item["class_name"],
                "bbox_xyxy": list(item["bbox_xyxy"]),
                "embedding": embedding,
            }
        )
        print(f"embedded [{item['instance_id']}] {item['class_name']}  dim={embedding.shape[0]}")
    return objects


def _rank_one(conn, query_vec, cfg: PgConfig, *, limit: int | None = None) -> pd.DataFrame:
    vec = np.asarray(query_vec, dtype=np.float32)
    sql = f"""
        SELECT image_name, class_name, bbox_xyxy,
               1 - (embedding <=> %s) AS cosine_sim
        FROM {cfg.table}
        ORDER BY embedding <=> %s
    """
    params: tuple = (vec, vec)
    if limit is not None:
        sql += " LIMIT %s"
        params = (vec, vec, int(limit))
    with conn.cursor() as cur:
        cur.execute(sql, params)
        hits = cur.fetchall()
    table = pd.DataFrame(
        hits, columns=["image_name", "class_name", "bbox_xyxy", "cosine_sim"]
    )
    table.insert(0, "rank", range(1, len(table) + 1))
    return table


def rank_against_database(conn, query_objects: list[dict], cfg: PgConfig) -> pd.DataFrame:
    if not query_objects:
        print("No labeled crops on this image.")
        return pd.DataFrame(
            columns=["query_class", "rank", "image_name", "class_name", "bbox_xyxy", "cosine_sim"]
        )

    tables = []
    for obj in query_objects:
        print(f"\nQuery [{obj['instance_id']}] {obj['class_name']}  bbox={obj['bbox_xyxy']}")
        table = _rank_one(conn, obj["embedding"], cfg)
        table.insert(0, "query_class", obj["class_name"])
        tables.append(table)
        print(f"full ranking rows: {len(table)}")

    similarity_df = pd.concat(tables, ignore_index=True)
    print(f"\nTotal ranking rows: {len(similarity_df)}")
    return similarity_df


def average_top_n(similarity_df: pd.DataFrame, top_n: int = 100) -> pd.DataFrame:
    top_df = similarity_df[similarity_df["rank"] <= top_n]
    class_sim = (
        top_df.groupby("class_name", as_index=False)
        .agg(
            avg_cosine_sim=("cosine_sim", "mean"),
            n=("cosine_sim", "size"),
        )
        .sort_values("avg_cosine_sim", ascending=False)
    )
    print(f"Averaged over top {top_n} ranking rows ({len(top_df)} rows used)")
    return class_sim


def soft_vote_top_n(similarity_df: pd.DataFrame, top_n: int = 100) -> pd.DataFrame:
    """Cumulative similarity / soft vote over the top ``top_n`` ranks.

    ``total_score = sum(sim) = avg_cosine_sim * n``. Highest score wins.
    """
    top_df = similarity_df[similarity_df["rank"] <= top_n]
    voted = (
        top_df.groupby("class_name", as_index=False)
        .agg(
            avg_cosine_sim=("cosine_sim", "mean"),
            n=("cosine_sim", "size"),
            total_score=("cosine_sim", "sum"),
        )
        .sort_values("total_score", ascending=False)
        .reset_index(drop=True)
    )
    return voted


def embed_split_crops(splits: dict, model, *, split: str = "val") -> list[dict]:
    """Embed every labeled crop in ``split``. Reuses a preloaded OpenCLIP model."""
    if model is None:
        raise ValueError("Pass a preloaded OpenCLIP model from load_clip_model().")

    images = splits["val_images"] if split == "val" else splits["test_images"]
    objects: list[dict] = []
    n_failed = 0
    for path in tqdm(images, desc=f"Embedding {split} crops", unit="img"):
        try:
            image, labels = load_image_and_label(
                image_path=path,
                dataset_dir=splits["dataset_dir"],
            )
            crops = crop_labeled_objects(image, labels)
        except Exception as exc:
            n_failed += 1
            tqdm.write(f"Skip {path.name}: {exc}")
            continue
        for item in crops:
            objects.append(
                {
                    "image_name": path.name,
                    "path": path,
                    "instance_id": item["instance_id"],
                    "class_name": item["class_name"],
                    "bbox_xyxy": list(item["bbox_xyxy"]),
                    "embedding": get_image_embedding(model, item["crop"]),
                }
            )
    print(
        f"{split}: {len(objects)} crops from "
        f"{len(images) - n_failed}/{len(images)} images"
    )
    return objects


VOTE_RULES = ("support", "log", "soft", "bayes")


def collect_split_votes(
    conn,
    query_objects: list[dict],
    cfg: PgConfig,
    *,
    top_n: int = 100,
) -> pd.DataFrame:
    """Rank each crop once. Returns per-class top-n stats for applying vote rules."""
    parts: list[pd.DataFrame] = []
    for obj in tqdm(query_objects, desc="Ranking vs database", unit="crop"):
        ranking = _rank_one(conn, obj["embedding"], cfg, limit=top_n)
        voted = soft_vote_top_n(ranking, top_n=top_n)
        if voted.empty:
            voted = pd.DataFrame(
                [
                    {
                        "class_name": None,
                        "avg_cosine_sim": np.nan,
                        "n": 0,
                        "total_score": np.nan,
                    }
                ]
            )
        voted = voted.copy()
        voted.insert(0, "true_class", obj["class_name"])
        voted.insert(0, "instance_id", obj["instance_id"])
        voted.insert(0, "image_name", obj["image_name"])
        parts.append(voted)
    vote_df = pd.concat(parts, ignore_index=True)
    n_queries = vote_df[["image_name", "instance_id"]].drop_duplicates().shape[0]
    print(f"Collected class votes for {n_queries} crops  ({len(vote_df)} class rows)")
    return vote_df


def _global_mean_sim(vote_df: pd.DataFrame, default: float = 0.60) -> float:
    weights = vote_df["n"].astype(float)
    total_n = float(weights.sum())
    if total_n <= 0:
        return default
    return float(vote_df["total_score"].fillna(0.0).sum() / total_n)


def _score_candidates(
    group: pd.DataFrame,
    *,
    rule: str,
    min_n: int,
    m: float,
    mu0: float,
) -> pd.DataFrame:
    g = group.dropna(subset=["class_name"]).copy()
    if g.empty:
        return g
    g["n"] = g["n"].astype(int)
    if rule == "support":
        g = g[g["n"] >= min_n]
        if g.empty:
            return g
        g["score"] = g["avg_cosine_sim"]
    elif rule == "log":
        g["score"] = g["avg_cosine_sim"] * np.log1p(g["n"].astype(float))
    elif rule == "soft":
        g["score"] = g["total_score"]
    elif rule == "bayes":
        n = g["n"].astype(float)
        g["score"] = (n * g["avg_cosine_sim"] + m * mu0) / (n + m)
    else:
        raise ValueError(f"Unknown rule {rule!r}. Use one of {VOTE_RULES}.")
    return g.sort_values("score", ascending=False)


def apply_vote_rule(
    vote_df: pd.DataFrame,
    *,
    rule: str = "soft",
    min_n: int = 3,
    m: float = 3.0,
    mu0: float | None = None,
) -> pd.DataFrame:
    """Pick one class per crop using a vote rule.

    ``support``: keep ``n >= min_n``, then argmax ``avg_cosine_sim``.
    ``log``: argmax ``avg_cosine_sim * ln(1 + n)``.
    ``soft``: argmax ``sum(sim) = avg_cosine_sim * n``.
    ``bayes``: argmax ``(n * avg + m * mu0) / (n + m)``.
    """
    rule = rule.lower().strip()
    if rule not in VOTE_RULES:
        raise ValueError(f"Unknown rule {rule!r}. Use one of {VOTE_RULES}.")
    prior = _global_mean_sim(vote_df) if mu0 is None else float(mu0)

    rows: list[dict] = []
    keys = ["image_name", "instance_id"]
    for (image_name, instance_id), group in vote_df.groupby(keys, sort=False):
        true_class = group["true_class"].iloc[0]
        ranked = _score_candidates(
            group, rule=rule, min_n=min_n, m=m, mu0=prior
        )
        if ranked.empty:
            pred_class = None
            score = np.nan
            avg_cosine_sim = np.nan
            n_hits = 0
        else:
            winner = ranked.iloc[0]
            pred_class = winner["class_name"]
            score = float(winner["score"])
            avg_cosine_sim = float(winner["avg_cosine_sim"])
            n_hits = int(winner["n"])
        rows.append(
            {
                "image_name": image_name,
                "instance_id": instance_id,
                "true_class": true_class,
                "pred_class": pred_class,
                "correct": true_class == pred_class,
                "rule": rule,
                "score": score,
                "avg_cosine_sim": avg_cosine_sim,
                "n": n_hits,
            }
        )

    pred_df = pd.DataFrame(rows)
    metrics = classification_metrics(pred_df)
    extra = f"  min_n={min_n}" if rule == "support" else ""
    if rule == "bayes":
        extra = f"  m={m}  mu0={prior:.3f}"
    print(
        f"Rule={rule}{extra}  n={int(metrics['n'])}  "
        f"acc={metrics['accuracy']:.3f}  "
        f"P_macro={metrics['precision_macro']:.3f}  "
        f"R_macro={metrics['recall_macro']:.3f}"
    )
    return pred_df


def predict_split(
    conn,
    query_objects: list[dict],
    cfg: PgConfig,
    *,
    top_n: int = 100,
    rule: str = "soft",
    min_n: int = 3,
    m: float = 3.0,
    mu0: float | None = None,
) -> pd.DataFrame:
    """Rank each crop vs the DB, then apply a vote rule. Prefer ``collect_split_votes`` + ``apply_vote_rule``."""
    vote_df = collect_split_votes(conn, query_objects, cfg, top_n=top_n)
    return apply_vote_rule(vote_df, rule=rule, min_n=min_n, m=m, mu0=mu0)


def classification_metrics(pred_df: pd.DataFrame) -> pd.Series:
    """Overall accuracy plus macro / weighted precision and recall."""
    true = pred_df["true_class"].astype(str)
    pred = pred_df["pred_class"].where(pred_df["pred_class"].notna(), "__none__").astype(str)
    labels = sorted(true.unique())
    n = len(pred_df)
    acc = float((true == pred).mean()) if n else 0.0

    precs: list[float] = []
    recs: list[float] = []
    supports: list[int] = []
    for cls in labels:
        tp = int(((true == cls) & (pred == cls)).sum())
        fp = int(((true != cls) & (pred == cls)).sum())
        support = int((true == cls).sum())
        precs.append(tp / (tp + fp) if (tp + fp) else 0.0)
        recs.append(tp / support if support else 0.0)
        supports.append(support)

    total = float(sum(supports))
    metrics = pd.Series(
        {
            "n": n,
            "accuracy": acc,
            "precision_macro": float(np.mean(precs)) if precs else 0.0,
            "recall_macro": float(np.mean(recs)) if recs else 0.0,
            "precision_weighted": (
                float(np.dot(precs, supports) / total) if total else 0.0
            ),
            "recall_weighted": (
                float(np.dot(recs, supports) / total) if total else 0.0
            ),
        }
    )
    return metrics


def evaluate_rule(
    vote_df: pd.DataFrame,
    *,
    splits: dict | None = None,
    rule: str = "soft",
    min_n: int = 3,
    m: float = 3.0,
    mu0: float | None = None,
    show: bool = True,
    title: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply one vote rule and draw its confusion matrix."""
    pred_df = apply_vote_rule(vote_df, rule=rule, min_n=min_n, m=m, mu0=mu0)
    cm = plot_confusion_matrix(
        pred_df,
        splits=splits,
        show=show,
        title=title,
    )
    return pred_df, cm


def _matrix_labels(pred_df: pd.DataFrame, splits: dict | None = None) -> list[str]:
    """Val-set true classes (yaml order), plus any predicted class not in val."""
    true_classes = set(pred_df["true_class"].dropna().astype(str))
    pred_classes = set(pred_df["pred_class"].dropna().astype(str))
    yaml_order: list[str] = []
    if splits is not None:
        names = load_class_names(splits["dataset_dir"] / "data.yaml")
        yaml_order = [names[i] for i in sorted(names)]
    ordered_true = [name for name in yaml_order if name in true_classes]
    if not ordered_true:
        ordered_true = sorted(true_classes)
    extra_pred = sorted(pred_classes - set(ordered_true))
    return ordered_true + extra_pred


def plot_confusion_matrix(
    pred_df: pd.DataFrame,
    *,
    splits: dict | None = None,
    show: bool = True,
    title: str | None = None,
) -> pd.DataFrame:
    """Confusion matrix over every class that appears in the validation set."""
    true = pred_df["true_class"].astype(str)
    pred = pred_df["pred_class"].where(pred_df["pred_class"].notna(), "__none__").astype(str)
    labels = _matrix_labels(pred_df, splits)
    if "__none__" in set(pred) and "__none__" not in labels:
        labels = labels + ["__none__"]
    cm = pd.crosstab(true, pred).reindex(index=labels, columns=labels, fill_value=0)

    metrics = classification_metrics(pred_df)
    print(
        f"Confusion matrix {cm.shape[0]} x {cm.shape[1]}  n={int(metrics['n'])}\n"
        f"  accuracy           {metrics['accuracy']:.3f}\n"
        f"  precision_macro    {metrics['precision_macro']:.3f}\n"
        f"  recall_macro       {metrics['recall_macro']:.3f}\n"
        f"  precision_weighted {metrics['precision_weighted']:.3f}\n"
        f"  recall_weighted    {metrics['recall_weighted']:.3f}"
    )

    if show and labels:
        size = min(28, max(8, 0.28 * len(labels)))
        fig, ax = plt.subplots(figsize=(size, size))
        im = ax.imshow(cm.values, cmap="Blues")
        fontsize = 8 if len(labels) <= 40 else 5
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=fontsize)
        ax.set_yticklabels(labels, fontsize=fontsize)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        heading = title or "Val confusion matrix"
        ax.set_title(
            f"{heading}\n"
            f"acc={metrics['accuracy']:.3f}  "
            f"P={metrics['precision_macro']:.3f}  "
            f"R={metrics['recall_macro']:.3f}  "
            f"(n={int(metrics['n'])})"
        )
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        if len(labels) <= 25:
            vmax = float(cm.values.max()) if cm.size else 1.0
            for i in range(len(labels)):
                for j in range(len(labels)):
                    val = int(cm.values[i, j])
                    if val == 0:
                        continue
                    color = "white" if val > vmax / 2 else "black"
                    ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=7)
        fig.tight_layout()
        plt.show()
    return cm
