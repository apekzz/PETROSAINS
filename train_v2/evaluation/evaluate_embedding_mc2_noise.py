#!/usr/bin/env python3
"""MobileCLIP2 classification eval: mc2 vs noise catalogs on val+test.

Protocols:
  clean   — GT mask crops as-is vs both catalogs
  stamped — FaceTime-noise stamped crops vs both catalogs

Ranking matches live inventory_app.match_inventory_name:
  per-name mean of top-3 cosine scores, reject if score <= threshold (0.60).

Example:
  /opt/miniconda3/bin/python train_v2/evaluation/evaluate_embedding_mc2_noise.py
  /opt/miniconda3/bin/python train_v2/evaluation/evaluate_embedding_mc2_noise.py --limit 20
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = Path("/Users/user/Downloads/BACHELOR AI/Dataset/yolo_eval")
DEFAULT_MC2 = (
    ROOT / "inventory_app" / "database" / "saved_tables" / "inventory_emb_mobileclip2.csv"
)
DEFAULT_NOISE = (
    ROOT / "inventory_app" / "database" / "saved_tables" / "inventory_emb_noise.csv"
)
DEFAULT_NOISE_CAPTURE = (
    ROOT / "inventory_app" / "noise_captures" / "laptop_20260923_115322"
)
DEFAULT_OUTPUT = ROOT / "train_v2" / "evaluation" / "results" / "embedding_mc2_noise"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CATALOGS = ("mc2", "noise")
PROTOCOLS = ("clean", "stamped")
SPLITS = ("val", "test", "merged")

sys.path.insert(0, str(ROOT / "inventory_app" / "backend"))


def inventory_name_from_filename(path: Path) -> str:
    key = path.stem.split("__", 1)[0]
    raw = key.split("_", 1)[1] if "_" in key else key
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", raw)
    return " ".join(spaced.replace("_", " ").split())


def canonical_name(name: str) -> str:
    return " ".join(str(name or "").replace("_", " ").lower().split())


def pick_device(requested: str | None) -> str:
    if requested:
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def polygon_rows(label_path: Path) -> list[list[float]]:
    rows = []
    for raw in label_path.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split()
        if not parts:
            continue
        values = [float(value) for value in parts[1:]]
        if len(values) >= 6 and len(values) % 2 == 0:
            rows.append(values)
    return rows


def make_masked_crop(image: Image.Image, values: list[float]) -> Image.Image | None:
    width, height = image.size
    points = [
        (
            max(0, min(width - 1, round(values[index] * width))),
            max(0, min(height - 1, round(values[index + 1] * height))),
        )
        for index in range(0, len(values), 2)
    ]
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    bbox = mask.getbbox()
    if bbox is None or bbox[2] - bbox[0] < 4 or bbox[3] - bbox[1] < 4:
        return None
    cutout = Image.composite(image, Image.new("RGB", image.size), mask)
    crop = cutout.crop(bbox)
    crop.thumbnail((512, 512), Image.Resampling.LANCZOS)
    return crop


def build_samples(dataset: Path, limit: int | None = None) -> tuple[list[dict], dict]:
    samples = []
    split_counts = {}
    missing_labels = 0
    invalid_polygons = 0
    for split in ("val", "test"):
        image_dir = dataset / "images" / split
        if not image_dir.is_dir():
            split_counts[split] = 0
            continue
        images = sorted(
            path
            for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
        split_counts[split] = len(images)
        for image_path in images:
            label_path = dataset / "labels" / split / f"{image_path.stem}.txt"
            if not label_path.is_file():
                missing_labels += 1
                continue
            rows = polygon_rows(label_path)
            if not rows:
                invalid_polygons += 1
            for polygon_index, values in enumerate(rows):
                samples.append(
                    {
                        "split": split,
                        "image": image_path,
                        "polygon_index": polygon_index,
                        "true_name": inventory_name_from_filename(image_path),
                        "polygon": values,
                    }
                )
                if limit is not None and len(samples) >= limit:
                    diagnostics = {
                        "val_images": split_counts.get("val", 0),
                        "test_images": split_counts.get("test", 0),
                        "missing_labels": missing_labels,
                        "images_without_valid_polygons": invalid_polygons,
                        "limit": limit,
                    }
                    return samples, diagnostics
    diagnostics = {
        "val_images": split_counts.get("val", 0),
        "test_images": split_counts.get("test", 0),
        "missing_labels": missing_labels,
        "images_without_valid_polygons": invalid_polygons,
        "limit": limit,
    }
    return samples, diagnostics


def load_catalog(path: Path) -> tuple[list[str], np.ndarray]:
    names = []
    vectors = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            vector = np.asarray(
                json.loads(row["inventory_embedding"]),
                dtype=np.float32,
            )
            if vector.ndim != 1 or vector.size == 0:
                continue
            norm = float(np.linalg.norm(vector))
            if norm <= 0:
                continue
            names.append(" ".join(row["inventory_name"].split()))
            vectors.append(vector / norm)
    if not vectors:
        raise RuntimeError(f"No valid embeddings found in {path}")
    dimensions = {vector.size for vector in vectors}
    if len(dimensions) != 1:
        raise RuntimeError(f"Catalog contains mixed dimensions: {sorted(dimensions)}")
    return names, np.stack(vectors)


def rank_like_live(
    query: np.ndarray,
    catalog_names: list[str],
    catalog_matrix: np.ndarray,
) -> list[tuple[float, str, str]]:
    """Per-name mean of top-3 cosines (live match_inventory_name)."""
    scores = catalog_matrix @ query
    grouped: dict[str, list[float]] = defaultdict(list)
    display_names: dict[str, str] = {}
    for index, name in enumerate(catalog_names):
        key = canonical_name(name)
        grouped[key].append(float(scores[int(index)]))
        display_names.setdefault(key, name)
    ranked = [
        (
            float(np.mean(sorted(class_scores, reverse=True)[:3])),
            display_names[key],
            key,
        )
        for key, class_scores in grouped.items()
    ]
    ranked.sort(reverse=True)
    return ranked


def classification_metrics(records: list[dict], true_classes: list[str]) -> dict:
    total = len(records)
    accepted_records = [record for record in records if record["accepted"]]
    correct = sum(record["correct"] for record in records)
    accepted_correct = sum(record["correct"] for record in accepted_records)
    per_class = []
    for class_name in true_classes:
        support = sum(record["true_key"] == class_name for record in records)
        tp = sum(
            record["true_key"] == class_name
            and record["pred_key"] == class_name
            and record["accepted"]
            for record in records
        )
        fp = sum(
            record["true_key"] != class_name
            and record["pred_key"] == class_name
            and record["accepted"]
            for record in records
        )
        fn = support - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (
            2.0 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        per_class.append(
            {
                "class": class_name,
                "support": support,
                "true_positive": tp,
                "false_positive": fp,
                "false_negative": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )
    macro_precision = float(np.mean([row["precision"] for row in per_class])) if per_class else 0.0
    macro_recall = float(np.mean([row["recall"] for row in per_class])) if per_class else 0.0
    macro_f1 = float(np.mean([row["f1"] for row in per_class])) if per_class else 0.0
    weighted_f1 = (
        sum(row["f1"] * row["support"] for row in per_class) / total if total else 0.0
    )
    micro_precision = (
        accepted_correct / len(accepted_records) if accepted_records else 0.0
    )
    micro_recall = correct / total if total else 0.0
    micro_f1 = (
        2.0 * micro_precision * micro_recall / (micro_precision + micro_recall)
        if micro_precision + micro_recall
        else 0.0
    )
    return {
        "samples": total,
        "accepted": len(accepted_records),
        "rejected": total - len(accepted_records),
        "coverage": len(accepted_records) / total if total else 0.0,
        "top1_accuracy_with_rejections": correct / total if total else 0.0,
        "accepted_accuracy": (
            accepted_correct / len(accepted_records) if accepted_records else 0.0
        ),
        "top5_accuracy": (
            sum(record["top5_correct"] for record in records) / total if total else 0.0
        ),
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": micro_f1,
        "per_class": per_class,
    }


def score_queries(
    queries: np.ndarray,
    sample_meta: list[dict],
    catalog_names: list[str],
    catalog_matrix: np.ndarray,
    threshold: float,
    catalog_tag: str,
    protocol: str,
) -> list[dict]:
    records = []
    for index, meta in enumerate(sample_meta):
        ranked = rank_like_live(queries[index], catalog_names, catalog_matrix)
        best_score, best_name, best_key = ranked[0] if ranked else (-1.0, "", "")
        second = ranked[1][0] if len(ranked) > 1 else 0.0
        accepted = best_score > threshold
        true_key = canonical_name(meta["true_name"])
        pred_key = best_key if accepted else "unknown"
        top5_keys = {key for _score, _name, key in ranked[:5]}
        records.append(
            {
                "protocol": protocol,
                "catalog": catalog_tag,
                "split": meta["split"],
                "image": meta["image"].name,
                "polygon_index": meta["polygon_index"],
                "true_name": meta["true_name"],
                "true_key": true_key,
                "predicted_name": best_name if accepted else "UNKNOWN",
                "pred_key": pred_key,
                "similarity": best_score,
                "second_similarity": second,
                "margin": best_score - second,
                "accepted": accepted,
                "correct": bool(accepted and best_key == true_key),
                "top5_correct": true_key in top5_keys,
            }
        )
    return records


def filter_split(records: list[dict], split: str) -> list[dict]:
    if split == "merged":
        return records
    return [record for record in records if record["split"] == split]


def load_mobileclip2(device: str):
    import open_clip
    from timm.utils.model import reparameterize_model

    model, _, preprocess = open_clip.create_model_and_transforms(
        "MobileCLIP2-S2",
        pretrained="dfndr2b",
    )
    model = model.eval()
    try:
        model = reparameterize_model(model, inplace=True)
    except Exception as exc:  # pragma: no cover - optional fuse
        print(f"Reparameterization skipped: {exc}", flush=True)
    model = model.to(device)
    return model, preprocess


def encode_batches(
    model,
    preprocess,
    images: list[Image.Image],
    device: str,
    batch_size: int,
) -> np.ndarray:
    vectors = []
    with torch.inference_mode():
        for start in range(0, len(images), batch_size):
            batch = images[start : start + batch_size]
            tensors = torch.stack(
                [preprocess(image.convert("RGB")) for image in batch]
            ).to(device)
            encoded = model.encode_image(tensors)
            encoded = encoded / encoded.norm(dim=-1, keepdim=True).clamp_min(1e-8)
            vectors.append(encoded.detach().float().cpu().numpy().astype(np.float32))
            if device == "mps":
                torch.mps.synchronize()
            elif device.startswith("cuda"):
                torch.cuda.synchronize()
            done = min(start + batch_size, len(images))
            if done == len(images) or done % max(batch_size * 4, 1) == 0:
                print(f"  encoded {done}/{len(images)}", flush=True)
    return np.concatenate(vectors, axis=0)


def write_records(path: Path, records: list[dict]) -> None:
    columns = [
        "protocol",
        "catalog",
        "split",
        "image",
        "polygon_index",
        "true_name",
        "predicted_name",
        "similarity",
        "second_similarity",
        "margin",
        "accepted",
        "correct",
        "top5_correct",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record in records:
            writer.writerow({column: record[column] for column in columns})


def write_class_metrics(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pretty(name: str) -> str:
    return " ".join(str(name or "").replace("_", " ").split()).title()


def chart_side_by_side(summary: dict, charts: Path) -> Path:
    """E1: Top-1 / Top-5 / Macro-F1 bars — mc2 vs noise × protocol × split."""
    metrics = [
        ("top1_accuracy_with_rejections", "Top-1"),
        ("top5_accuracy", "Top-5"),
        ("macro_f1", "Macro-F1"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharey=True)
    fig.suptitle(
        "MobileCLIP2 Classification — mc2 vs noise",
        fontsize=16,
        weight="bold",
    )
    x = np.arange(len(SPLITS))
    width = 0.35
    for row, protocol in enumerate(PROTOCOLS):
        for col, (key, label) in enumerate(metrics):
            axis = axes[row, col]
            mc2 = [
                summary[protocol]["mc2"][split]["quality"][key] * 100 for split in SPLITS
            ]
            noise = [
                summary[protocol]["noise"][split]["quality"][key] * 100
                for split in SPLITS
            ]
            bars_a = axis.bar(x - width / 2, mc2, width, label="mc2", color="#1f77b4")
            bars_b = axis.bar(x + width / 2, noise, width, label="noise", color="#ff7f0e")
            axis.set_title(f"{protocol} · {label}")
            axis.set_xticks(x)
            axis.set_xticklabels(SPLITS)
            axis.set_ylim(0, 105)
            axis.grid(axis="y", alpha=0.25)
            if col == 0:
                axis.set_ylabel("%")
            if row == 0 and col == 2:
                axis.legend(loc="lower right")
            for bars in (bars_a, bars_b):
                for bar in bars:
                    axis.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        f"{bar.get_height():.0f}",
                        ha="center",
                        fontsize=7,
                    )
    fig.tight_layout()
    path = charts / "e1_side_by_side_metrics.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_coverage(summary: dict, charts: Path) -> Path:
    """E2: Coverage + accepted-only accuracy."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Coverage & Accepted Accuracy", fontsize=15, weight="bold")
    x = np.arange(len(SPLITS))
    width = 0.2
    for axis, key, title in zip(
        axes,
        ("coverage", "accepted_accuracy"),
        ("Coverage (accepted / all)", "Accepted-only accuracy"),
    ):
        offsets = [-1.5, -0.5, 0.5, 1.5]
        labels = []
        for protocol, catalog, color, offset in (
            ("clean", "mc2", "#1f77b4", offsets[0]),
            ("clean", "noise", "#ff7f0e", offsets[1]),
            ("stamped", "mc2", "#2ca02c", offsets[2]),
            ("stamped", "noise", "#d62728", offsets[3]),
        ):
            values = [
                summary[protocol][catalog][split]["quality"][key] * 100
                for split in SPLITS
            ]
            label = f"{protocol}/{catalog}"
            labels.append(label)
            axis.bar(x + offset * width, values, width, label=label, color=color)
        axis.set_title(title)
        axis.set_xticks(x)
        axis.set_xticklabels(SPLITS)
        axis.set_ylim(0, 105)
        axis.set_ylabel("%")
        axis.grid(axis="y", alpha=0.25)
        axis.legend(fontsize=8)
    fig.tight_layout()
    path = charts / "e2_coverage_accepted.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_top_confusions(records: list[dict], charts: Path, tag: str) -> Path | None:
    """E3: top-10 true→pred confusions."""
    errors = Counter()
    for row in records:
        if row["true_key"] == row["pred_key"]:
            continue
        errors[(pretty(row["true_name"]), pretty(row["predicted_name"]))] += 1
    top = errors.most_common(10)
    if not top:
        return None
    labels = [f"{true} → {predicted}" for (true, predicted), _ in top][::-1]
    counts = [count for _pair, count in top][::-1]
    fig, axis = plt.subplots(figsize=(11, 6))
    bars = axis.barh(labels, counts, color="#c0392b")
    axis.set_title(f"Top confusions — {tag}", fontsize=14, weight="bold")
    axis.set_xlabel("Count")
    for bar, count in zip(bars, counts):
        axis.text(
            count + 0.15,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=9,
        )
    fig.tight_layout()
    safe = tag.replace("/", "_").replace(" ", "_")
    path = charts / f"e3_top_confusions_{safe}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_confusion_matrix(records: list[dict], charts: Path, tag: str) -> Path:
    """E4: full normalized confusion matrix (109 classes — dense labels)."""
    true_classes = sorted({pretty(row["true_name"]) for row in records})
    predicted_classes = true_classes + ["Unknown"]
    true_index = {name: index for index, name in enumerate(true_classes)}
    pred_index = {name: index for index, name in enumerate(predicted_classes)}
    matrix = np.zeros((len(true_classes), len(predicted_classes)), dtype=np.int32)
    for row in records:
        true_name = pretty(row["true_name"])
        predicted_name = pretty(row["predicted_name"])
        if predicted_name not in pred_index:
            predicted_name = "Unknown"
        matrix[true_index[true_name], pred_index[predicted_name]] += 1
    totals = matrix.sum(axis=1, keepdims=True)
    normalized = np.divide(
        matrix,
        totals,
        out=np.zeros_like(matrix, dtype=np.float64),
        where=totals > 0,
    )
    fig, axis = plt.subplots(figsize=(24, 21))
    image = axis.imshow(normalized, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    axis.set_title(f"Normalized confusion — {tag}", fontsize=15, weight="bold")
    axis.set_xlabel("Predicted")
    axis.set_ylabel("True")
    axis.set_xticks(range(len(predicted_classes)))
    axis.set_xticklabels(predicted_classes, rotation=90, fontsize=4)
    axis.set_yticks(range(len(true_classes)))
    axis.set_yticklabels(true_classes, fontsize=4)
    fig.colorbar(image, ax=axis, fraction=0.022, pad=0.02)
    fig.tight_layout()
    safe = tag.replace("/", "_").replace(" ", "_")
    path = charts / f"e4_confusion_{safe}.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def write_lecturer_report(path: Path, summary: dict, meta: dict) -> None:
    lines = [
        "MOBILECLIP2 CLASSIFICATION EVAL — mc2 vs noise",
        "=" * 52,
        f"Generated: {meta['generated_at']}",
        f"Device: {meta['device']}",
        f"Dataset: {meta['dataset']}",
        f"Noise capture: {meta['noise_capture']}",
        f"Ranking: live top-3 mean per name · threshold > {meta['threshold']:.2f}",
        f"Samples evaluated (clean): {meta['clean_samples']}",
        f"Samples stamped: {meta['stamped_samples']} (failed stamp: {meta['stamp_failures']})",
        "",
    ]
    for protocol in PROTOCOLS:
        lines.append(f"PROTOCOL: {protocol.upper()}")
        lines.append("-" * 40)
        for catalog in CATALOGS:
            lines.append(f"  Catalog: {catalog}")
            for split in SPLITS:
                quality = summary[protocol][catalog][split]["quality"]
                lines.append(
                    f"    {split:7s}  top1={quality['top1_accuracy_with_rejections']:.4f}  "
                    f"top5={quality['top5_accuracy']:.4f}  "
                    f"macroF1={quality['macro_f1']:.4f}  "
                    f"cov={quality['coverage']:.4f}  "
                    f"acc_acc={quality['accepted_accuracy']:.4f}"
                )
            lines.append("")
        lines.append("")
    lines.extend(
        [
            "NOTES",
            "- clean: GT mask crops, fair same-query compare.",
            "- stamped: FaceTime residual grain on crops (domain-matched for noise catalog).",
            "- Catalog-vs-catalog cosine/L2 already in compare_metrics_for_lecturer.txt;",
            "  this report is held-out classification accuracy.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def self_check_rank() -> None:
    """ponytail: smallest assert that live top-3 ranking stays correct."""
    names = ["A", "A", "A", "A", "B", "B", "B"]
    matrix = np.asarray(
        [
            [1.0, 0.0],
            [0.9, 0.0],
            [0.8, 0.0],
            [0.1, 0.0],
            [0.0, 1.0],
            [0.0, 0.5],
            [0.0, 0.4],
        ],
        dtype=np.float32,
    )
    # normalize rows
    matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True).clip(min=1e-8)
    query = np.asarray([1.0, 0.0], dtype=np.float32)
    query = query / np.linalg.norm(query)
    ranked = rank_like_live(query, names, matrix)
    assert ranked[0][2] == "a"
    # mean of top-3 for A ≈ mean of three highest A scores
    a_scores = sorted(
        float(matrix[i] @ query) for i, name in enumerate(names) if name == "A"
    )[::-1][:3]
    assert abs(ranked[0][0] - float(np.mean(a_scores))) < 1e-5
    print("self_check_rank: OK", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate MobileCLIP2 mc2 vs noise on val+test masks."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--mc2-catalog", type=Path, default=DEFAULT_MC2)
    parser.add_argument("--noise-catalog", type=Path, default=DEFAULT_NOISE)
    parser.add_argument("--noise-capture", type=Path, default=DEFAULT_NOISE_CAPTURE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--threshold", type=float, default=0.60)
    parser.add_argument("--device", default=None)
    parser.add_argument("--limit", type=int, default=None, help="Max mask crops (debug)")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--charts-only", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        self_check_rank()
        return

    output = args.output.resolve()
    charts = output / "charts"
    output.mkdir(parents=True, exist_ok=True)
    charts.mkdir(parents=True, exist_ok=True)

    if args.charts_only:
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        all_records = []
        with (output / "predictions.csv").open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                row["accepted"] = row["accepted"] in ("True", "true", "1")
                row["correct"] = row["correct"] in ("True", "true", "1")
                row["top5_correct"] = row["top5_correct"] in ("True", "true", "1")
                row["true_key"] = canonical_name(row["true_name"])
                row["pred_key"] = (
                    canonical_name(row["predicted_name"])
                    if row["accepted"]
                    else "unknown"
                )
                all_records.append(row)
        paths = [
            chart_side_by_side(summary, charts),
            chart_coverage(summary, charts),
        ]
        for protocol in PROTOCOLS:
            for catalog in CATALOGS:
                subset = [
                    row
                    for row in all_records
                    if row["protocol"] == protocol and row["catalog"] == catalog
                ]
                merged = filter_split(subset, "merged")
                tag = f"{protocol}/{catalog}/merged"
                path = chart_top_confusions(merged, charts, tag)
                if path:
                    paths.append(path)
                paths.append(chart_confusion_matrix(merged, charts, tag))
        for path in paths:
            print(path)
        return

    dataset = args.dataset.resolve()
    device = pick_device(args.device)
    if not args.mc2_catalog.is_file():
        raise FileNotFoundError(args.mc2_catalog)
    if not args.noise_catalog.is_file():
        raise FileNotFoundError(args.noise_catalog)
    if not args.noise_capture.is_dir():
        raise FileNotFoundError(args.noise_capture)

    print("Indexing val/test samples...", flush=True)
    samples, diagnostics = build_samples(dataset, limit=args.limit)
    if not samples:
        raise RuntimeError(f"No samples under {dataset}")
    print(
        f"Indexed {len(samples)} crops "
        f"(val_images={diagnostics['val_images']} "
        f"test_images={diagnostics['test_images']})",
        flush=True,
    )

    print("Loading catalogs...", flush=True)
    catalogs = {
        "mc2": load_catalog(args.mc2_catalog.resolve()),
        "noise": load_catalog(args.noise_catalog.resolve()),
    }
    for tag, (names, matrix) in catalogs.items():
        print(f"  {tag}: {len(names)} vectors · dim={matrix.shape[1]}", flush=True)

    from noise_transfer import apply_noise_to_image, load_noise_profile_from_capture

    noise_profile = load_noise_profile_from_capture(args.noise_capture.resolve())
    print(
        f"Noise profile avg={noise_profile.avg_noise:.3f} "
        f"from {args.noise_capture}",
        flush=True,
    )

    print(f"Loading MobileCLIP2-S2 on {device}...", flush=True)
    load_started = time.perf_counter()
    model, preprocess = load_mobileclip2(device)
    model_load_seconds = time.perf_counter() - load_started
    print(f"Model ready in {model_load_seconds:.1f}s", flush=True)

    print("Building clean crops...", flush=True)
    clean_images: list[Image.Image] = []
    sample_meta: list[dict] = []
    skipped = 0
    image_cache: dict[Path, Image.Image] = {}
    crop_started = time.perf_counter()
    for sample in samples:
        image_path = sample["image"]
        if image_path not in image_cache:
            image_cache[image_path] = Image.open(image_path).convert("RGB")
        crop = make_masked_crop(image_cache[image_path], sample["polygon"])
        if crop is None:
            skipped += 1
            continue
        clean_images.append(crop)
        sample_meta.append(sample)
    image_cache.clear()
    crop_seconds = time.perf_counter() - crop_started
    print(
        f"Crops ready: {len(clean_images)} (skipped invalid {skipped}) "
        f"in {crop_seconds:.1f}s",
        flush=True,
    )
    if not clean_images:
        raise RuntimeError("No valid crops")

    print("Encoding clean queries...", flush=True)
    encode_started = time.perf_counter()
    clean_vectors = encode_batches(
        model, preprocess, clean_images, device, args.batch
    )
    clean_encode_seconds = time.perf_counter() - encode_started

    print("Stamping noise onto crops...", flush=True)
    stamped_images: list[Image.Image] = []
    stamped_meta: list[dict] = []
    stamp_failures = 0
    for crop, meta in zip(clean_images, sample_meta):
        try:
            stamped_images.append(apply_noise_to_image(crop, noise_profile))
            stamped_meta.append(meta)
        except Exception:
            stamp_failures += 1
    print(
        f"Stamped {len(stamped_images)} / {len(clean_images)} "
        f"(failures={stamp_failures})",
        flush=True,
    )

    stamped_vectors = None
    stamped_encode_seconds = 0.0
    if stamped_images:
        print("Encoding stamped queries...", flush=True)
        encode_started = time.perf_counter()
        stamped_vectors = encode_batches(
            model, preprocess, stamped_images, device, args.batch
        )
        stamped_encode_seconds = time.perf_counter() - encode_started

    # free model memory before metrics/charts
    del model
    if device == "mps":
        torch.mps.empty_cache()

    all_records: list[dict] = []
    summary: dict = {}
    true_classes_all = sorted({canonical_name(meta["true_name"]) for meta in sample_meta})

    for protocol, vectors, meta_list in (
        ("clean", clean_vectors, sample_meta),
        ("stamped", stamped_vectors, stamped_meta),
    ):
        if vectors is None or not meta_list:
            continue
        summary[protocol] = {}
        for catalog_tag, (names, matrix) in catalogs.items():
            print(f"Scoring {protocol}/{catalog_tag}...", flush=True)
            records = score_queries(
                vectors,
                meta_list,
                names,
                matrix,
                args.threshold,
                catalog_tag,
                protocol,
            )
            all_records.extend(records)
            summary[protocol][catalog_tag] = {}
            for split in SPLITS:
                subset = filter_split(records, split)
                classes = sorted({row["true_key"] for row in subset}) or true_classes_all
                quality = classification_metrics(subset, classes)
                summary[protocol][catalog_tag][split] = {
                    "quality": {
                        key: value
                        for key, value in quality.items()
                        if key != "per_class"
                    },
                }
                out_dir = output / protocol / catalog_tag / split
                write_records(out_dir / "predictions.csv", subset)
                write_class_metrics(out_dir / "per_class_metrics.csv", quality["per_class"])
                (out_dir / "metrics.json").write_text(
                    json.dumps(quality, indent=2),
                    encoding="utf-8",
                )

    write_records(output / "predictions.csv", all_records)
    meta = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "dataset": str(dataset),
        "mc2_catalog": str(args.mc2_catalog.resolve()),
        "noise_catalog": str(args.noise_catalog.resolve()),
        "noise_capture": str(args.noise_capture.resolve()),
        "device": device,
        "torch": torch.__version__,
        "python": platform.python_version(),
        "threshold": args.threshold,
        "batch_size": args.batch,
        "ranking": "live_top3_mean",
        "diagnostics": diagnostics,
        "clean_samples": len(sample_meta),
        "stamped_samples": len(stamped_meta),
        "stamp_failures": stamp_failures,
        "skipped_invalid_crops": skipped,
        "efficiency": {
            "model_load_seconds": model_load_seconds,
            "crop_seconds": crop_seconds,
            "clean_encode_seconds": clean_encode_seconds,
            "stamped_encode_seconds": stamped_encode_seconds,
        },
    }
    payload = {"meta": meta, **summary}
    (output / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_lecturer_report(output / "report_for_lecturer.txt", summary, meta)

    print("Writing charts...", flush=True)
    chart_paths = [
        chart_side_by_side(summary, charts),
        chart_coverage(summary, charts),
    ]
    for protocol in PROTOCOLS:
        if protocol not in summary:
            continue
        for catalog in CATALOGS:
            subset = [
                row
                for row in all_records
                if row["protocol"] == protocol and row["catalog"] == catalog
            ]
            merged = filter_split(subset, "merged")
            tag = f"{protocol}/{catalog}/merged"
            path = chart_top_confusions(merged, charts, tag)
            if path:
                chart_paths.append(path)
            chart_paths.append(chart_confusion_matrix(merged, charts, tag))

    print(f"\nDone → {output}", flush=True)
    print(f"Lecturer report: {output / 'report_for_lecturer.txt'}", flush=True)
    for path in chart_paths:
        print(f"  chart: {path}", flush=True)


if __name__ == "__main__":
    main()
