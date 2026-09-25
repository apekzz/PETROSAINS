#!/usr/bin/env python3
"""Create report-ready PNG charts from saved evaluation results."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "train_v2" / "evaluation" / "results"
OUTPUT = RESULTS / "visualizations"


def canonical(name: str) -> str:
    return " ".join(str(name or "").replace("_", " ").split()).title()


def label_bars(axis, bars, suffix="%", horizontal=False):
    for bar in bars:
        if horizontal:
            value = bar.get_width()
            axis.text(
                value + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.1f}{suffix}",
                va="center",
                fontsize=9,
            )
        else:
            value = bar.get_height()
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                value + 1,
                f"{value:.1f}{suffix}",
                ha="center",
                fontsize=9,
            )


def performance_summary(segmentation: dict, embedding: dict) -> Path:
    seg = segmentation["quality"]
    emb = embedding["quality"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("AI Inventory System — Predictive Performance", fontsize=16, weight="bold")

    seg_names = ["Precision", "Recall", "F1", "mAP50–95"]
    seg_values = [
        seg["mask_precision"] * 100,
        seg["mask_recall"] * 100,
        seg["mask_f1"] * 100,
        seg["mask_map50_95"] * 100,
    ]
    bars = axes[0].bar(seg_names, seg_values, color="#087f8c")
    axes[0].set_title("YOLO11l Segmentation")
    axes[0].set_ylabel("Score (%)")
    axes[0].set_ylim(0, 105)
    axes[0].grid(axis="y", alpha=0.25)
    label_bars(axes[0], bars)

    emb_names = ["Top-1", "Top-5", "Macro F1", "Coverage"]
    emb_values = [
        emb["top1_accuracy_with_rejections"] * 100,
        emb["top5_accuracy"] * 100,
        emb["macro_f1"] * 100,
        emb["coverage"] * 100,
    ]
    bars = axes[1].bar(emb_names, emb_values, color="#6c5ce7")
    axes[1].set_title("OpenCLIP Item Identification")
    axes[1].set_ylabel("Score (%)")
    axes[1].set_ylim(0, 105)
    axes[1].grid(axis="y", alpha=0.25)
    label_bars(axes[1], bars)

    fig.text(
        0.5,
        0.01,
        "Merged validation + test data · 817 images · 109 inventory classes",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    path = OUTPUT / "performance_summary.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def latency_breakdown(segmentation: dict, embedding: dict) -> Path:
    seg = segmentation["efficiency"]
    emb = embedding["efficiency"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Average Processing Latency", fontsize=16, weight="bold")

    seg_names = ["Preprocess", "Model inference", "Postprocess"]
    seg_values = [
        seg["preprocess_ms_per_image"],
        seg["inference_ms_per_image"],
        seg["postprocess_ms_per_image"],
    ]
    bars = axes[0].barh(seg_names, seg_values, color="#087f8c")
    axes[0].set_title("YOLO11l per Image")
    axes[0].set_xlabel("Latency (milliseconds)")
    axes[0].grid(axis="x", alpha=0.25)
    label_bars(axes[0], bars, " ms", horizontal=True)

    emb_names = ["Mask crop", "Preprocess", "OpenCLIP", "Similarity search"]
    emb_values = [
        emb["crop_ms_per_sample"],
        emb["preprocess_ms_per_sample"],
        emb["embedding_ms_per_sample"],
        emb["matching_ms_per_sample"],
    ]
    bars = axes[1].barh(emb_names, emb_values, color="#6c5ce7")
    axes[1].set_title("Item Identification per Crop")
    axes[1].set_xlabel("Latency (milliseconds)")
    axes[1].grid(axis="x", alpha=0.25)
    label_bars(axes[1], bars, " ms", horizontal=True)

    fig.text(
        0.5,
        0.01,
        "RTX 4050 Laptop GPU · mask-crop timing includes full-resolution OneDrive I/O",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    path = OUTPUT / "latency_breakdown.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def load_predictions() -> list[dict]:
    path = RESULTS / "embedding" / "predictions.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def prediction_label(name: str) -> str:
    label = canonical(name)
    return "Unknown" if label.lower() == "unknown" else label


def build_confusion(records: list[dict]) -> tuple[list[str], list[str], np.ndarray]:
    true_classes = sorted({canonical(row["true_name"]) for row in records})
    predicted_names = [prediction_label(row["predicted_name"]) for row in records]
    extra = sorted(
        {
            name
            for name in predicted_names
            if name not in true_classes and name != "Unknown"
        }
    )
    predicted_classes = true_classes + extra
    if any(name == "Unknown" for name in predicted_names):
        predicted_classes.append("Unknown")
    true_index = {name: index for index, name in enumerate(true_classes)}
    pred_index = {name: index for index, name in enumerate(predicted_classes)}
    matrix = np.zeros((len(true_classes), len(predicted_classes)), dtype=np.int32)
    for true_name, predicted_name in zip(
        (canonical(row["true_name"]) for row in records),
        predicted_names,
    ):
        matrix[true_index[true_name], pred_index[predicted_name]] += 1
    return true_classes, predicted_classes, matrix


def write_matrix_csv(path: Path, rows: list[str], columns: list[str], values: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["true_class", *columns])
        for name, row in zip(rows, values):
            writer.writerow([name, *row])


def draw_confusion(
    true_classes: list[str],
    predicted_classes: list[str],
    values: np.ndarray,
    path: Path,
    *,
    title: str,
    colorbar_label: str,
    cmap: str,
    vmin: float,
    vmax: float,
) -> Path:
    fig, axis = plt.subplots(figsize=(24, 21))
    image = axis.imshow(values, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    axis.set_title(title, fontsize=16, weight="bold", pad=16)
    axis.set_xlabel("Predicted class", fontsize=12)
    axis.set_ylabel("True class", fontsize=12)
    axis.set_xticks(range(len(predicted_classes)))
    axis.set_xticklabels(predicted_classes, rotation=90, fontsize=4.5)
    axis.set_yticks(range(len(true_classes)))
    axis.set_yticklabels(true_classes, fontsize=4.5)
    colorbar = fig.colorbar(image, ax=axis, fraction=0.022, pad=0.02)
    colorbar.set_label(colorbar_label, rotation=270, labelpad=18)
    fig.text(
        0.5,
        0.005,
        "Merged validation + test · one cell per mask object · score at or below 60% is Unknown",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def confusion_matrix(records: list[dict]) -> list[Path]:
    true_classes, predicted_classes, matrix = build_confusion(records)
    row_totals = matrix.sum(axis=1, keepdims=True)
    normalized = np.divide(
        matrix,
        row_totals,
        out=np.zeros_like(matrix, dtype=np.float64),
        where=row_totals > 0,
    )
    embedding_dir = RESULTS / "embedding"
    embedding_dir.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    count_csv = embedding_dir / "confusion_matrix.csv"
    normalized_csv = embedding_dir / "confusion_matrix_normalized.csv"
    write_matrix_csv(count_csv, true_classes, predicted_classes, matrix.tolist())
    write_matrix_csv(
        normalized_csv,
        true_classes,
        predicted_classes,
        np.round(normalized, 4).tolist(),
    )

    count_png = embedding_dir / "confusion_matrix.png"
    normalized_png = embedding_dir / "confusion_matrix_normalized.png"
    draw_confusion(
        true_classes,
        predicted_classes,
        matrix,
        count_png,
        title=f"Confusion Matrix — {len(true_classes)} Classes (counts)",
        colorbar_label="Number of objects",
        cmap="Blues",
        vmin=0,
        vmax=float(matrix.max()) if matrix.size else 1,
    )
    draw_confusion(
        true_classes,
        predicted_classes,
        normalized,
        normalized_png,
        title=f"Normalized Confusion Matrix — {len(true_classes)} Classes",
        colorbar_label="Share of each true class",
        cmap="Blues",
        vmin=0,
        vmax=1,
    )
    # Keep the older chart path in sync with the normalized matrix.
    draw_confusion(
        true_classes,
        predicted_classes,
        normalized,
        OUTPUT / "embedding_confusion_matrix.png",
        title=f"Normalized Confusion Matrix — {len(true_classes)} Classes",
        colorbar_label="Share of each true class",
        cmap="Blues",
        vmin=0,
        vmax=1,
    )
    return [count_png, normalized_png, count_csv, normalized_csv]


def top_confusions(records: list[dict]) -> Path:
    errors = Counter()
    for row in records:
        true_name = canonical(row["true_name"])
        predicted_name = canonical(row["predicted_name"])
        if true_name != predicted_name:
            errors[(true_name, predicted_name)] += 1
    top = errors.most_common(15)
    labels = [f"{true} → {predicted}" for (true, predicted), _count in top][::-1]
    counts = [count for _pair, count in top][::-1]

    fig, axis = plt.subplots(figsize=(12, 7.5))
    bars = axis.barh(labels, counts, color="#c0392b")
    axis.set_title(
        "Most Frequent OpenCLIP Misclassifications",
        fontsize=15,
        weight="bold",
    )
    axis.set_xlabel("Number of object crops")
    axis.set_ylabel("True class → predicted class")
    axis.grid(axis="x", alpha=0.25)
    for bar, count in zip(bars, counts):
        axis.text(
            count + 0.2,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=9,
        )
    fig.text(
        0.5,
        0.01,
        "UNKNOWN indicates rejection below the 60% similarity threshold",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    path = OUTPUT / "top_embedding_confusions.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    segmentation = json.loads(
        (RESULTS / "segmentation" / "metrics.json").read_text(encoding="utf-8")
    )
    embedding = json.loads(
        (RESULTS / "embedding" / "metrics.json").read_text(encoding="utf-8")
    )
    records = load_predictions()
    paths = [
        performance_summary(segmentation, embedding),
        latency_breakdown(segmentation, embedding),
        *confusion_matrix(records),
        top_confusions(records),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
