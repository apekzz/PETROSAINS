#!/usr/bin/env python3
"""Evaluate OpenCLIP nearest-class matching on merged val+test mask crops."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT / "train_v2" / "dataset"
DEFAULT_CATALOG = (
    ROOT / "inventory_app" / "saved_tables" / "inventory_emb.csv"
)
DEFAULT_CHECKPOINT = (
    ROOT / "inventory_app" / "models" / "open_clip_pytorch_model.bin"
)
DEFAULT_OUTPUT = ROOT / "train_v2" / "evaluation" / "results" / "embedding"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def inventory_name_from_filename(path: Path) -> str:
    """Match inventory_app.dataset_importer.inventory_name_from_filename."""
    key = path.stem.split("__", 1)[0]
    raw = key.split("_", 1)[1] if "_" in key else key
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", raw)
    return " ".join(spaced.replace("_", " ").split())


def canonical_name(name: str) -> str:
    return " ".join(str(name or "").replace("_", " ").lower().split())


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


def build_samples(dataset: Path) -> tuple[list[dict], dict]:
    samples = []
    split_counts = {}
    missing_labels = 0
    invalid_polygons = 0
    for split in ("val", "test"):
        image_dir = dataset / "images" / split
        images = sorted(
            path for path in image_dir.rglob("*")
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
    diagnostics = {
        "val_images": split_counts.get("val", 0),
        "test_images": split_counts.get("test", 0),
        "missing_labels": missing_labels,
        "images_without_valid_polygons": invalid_polygons,
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


def rank_like_inventory_app(
    query: np.ndarray,
    catalog_names: list[str],
    catalog_matrix: np.ndarray,
) -> list[tuple[float, str]]:
    """Replicate top-100, >=3-support, mean-score production matching."""
    scores = catalog_matrix @ query
    count = min(100, scores.size)
    if count == scores.size:
        indices = np.argsort(scores)[::-1]
    else:
        candidates = np.argpartition(scores, -count)[-count:]
        indices = candidates[np.argsort(scores[candidates])[::-1]]
    grouped: dict[str, list[float]] = defaultdict(list)
    display_names = {}
    for index in indices:
        name = catalog_names[int(index)]
        key = canonical_name(name)
        grouped[key].append(float(scores[int(index)]))
        display_names.setdefault(key, name)
    supported = [
        (float(np.mean(class_scores)), display_names[key])
        for key, class_scores in grouped.items()
        if len(class_scores) >= 3
    ]
    if not supported and len(indices):
        best = int(indices[0])
        supported = [(float(scores[best]), catalog_names[best])]
    return sorted(supported, reverse=True)


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
    macro_precision = float(np.mean([row["precision"] for row in per_class]))
    macro_recall = float(np.mean([row["recall"] for row in per_class]))
    macro_f1 = float(np.mean([row["f1"] for row in per_class]))
    weighted_f1 = (
        sum(row["f1"] * row["support"] for row in per_class) / total
        if total
        else 0.0
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
            sum(record["top5_correct"] for record in records) / total
            if total
            else 0.0
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


def quality_by_split(records: list[dict]) -> dict:
    """Overall accuracy for validation and test, counted per mask object."""
    grouped = {}
    for split in ("val", "test"):
        subset = [record for record in records if record["split"] == split]
        classes = sorted({record["true_key"] for record in subset})
        quality = classification_metrics(subset, classes)
        quality.pop("per_class")
        quality["images"] = len({record["image"] for record in subset})
        grouped[split] = quality
    return grouped


def load_prediction_records(path: Path) -> list[dict]:
    records = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            accepted = row["accepted"].strip().lower() == "true"
            records.append(
                {
                    "split": row["split"],
                    "image": row["image"],
                    "true_key": canonical_name(row["true_name"]),
                    "pred_key": (
                        canonical_name(row["predicted_name"]) if accepted else ""
                    ),
                    "similarity": float(row["similarity"]),
                    "accepted": accepted,
                    "correct": row["correct"].strip().lower() == "true",
                    "top5_correct": row["top5_correct"].strip().lower() == "true",
                }
            )
    if not records:
        raise RuntimeError(f"No prediction rows found in {path}")
    return records


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def score_lines(report: dict) -> list[str]:
    quality = report["quality"]
    by_split = report.get("by_split", {})
    lines = ["ACCURACY"]
    labels = (("val", "Validation"), ("test", "Test"))
    for split, label in labels:
        split_quality = by_split.get(split)
        if split_quality:
            lines.append(
                f"{label}: {percent(split_quality['top1_accuracy_with_rejections'])}"
            )
    lines.append(f"Overall: {percent(quality['top1_accuracy_with_rejections'])}")
    return lines


def refresh_saved_report(predictions: Path, output: Path) -> None:
    """Add val/test accuracy to an existing run without re-embedding."""
    metrics_path = output / "metrics.json"
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Existing metrics not found: {metrics_path}")
    report = json.loads(metrics_path.read_text(encoding="utf-8"))
    records = load_prediction_records(predictions)
    classes = sorted({record["true_key"] for record in records})
    quality = classification_metrics(records, classes)
    quality.pop("per_class")
    report["quality"] = quality
    report["by_split"] = quality_by_split(records)
    metrics_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_text_report(output / "report.txt", report)
    note = "\n".join(score_lines(report)) + "\n"
    (output / "accuracy.txt").write_text(note, encoding="utf-8")
    print(note, end="")
    print(f"Wrote {output / 'accuracy.txt'}")


def write_records(path: Path, records: list[dict]) -> None:
    columns = [
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
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(
            {column: record[column] for column in columns}
            for record in records
        )


def write_class_metrics(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_text_report(path: Path, report: dict) -> None:
    quality = report["quality"]
    efficiency = report["efficiency"]
    data = report["dataset"]
    similarity = report["similarity"]
    lines = [
        *score_lines(report),
        "",
        "OPENCLIP MASKED-CROP CLASSIFICATION EVALUATION",
        "=" * 48,
        f"Generated: {report['generated_at']}",
        f"Checkpoint: {report['checkpoint']}",
        f"Catalog: {report['catalog']}",
        f"Device: {report['runtime']['device']}",
        "",
        "EVALUATION DATA",
        f"Validation images: {data['val_images']}",
        f"Test images: {data['test_images']}",
        f"Merged mask instances evaluated: {data['evaluated_samples']}",
        f"True classes: {data['true_classes']}",
        f"Catalog embeddings: {data['catalog_embeddings']}",
        f"Catalog classes: {data['catalog_classes']}",
        f"True classes absent from catalog: {data['classes_absent_from_catalog']}",
        f"Skipped invalid crops: {data['skipped_invalid_crops']}",
        "",
        "CLASSIFICATION QUALITY",
        f"Threshold: > {similarity['threshold']:.3f}",
        f"Top-1 accuracy (rejections incorrect): {quality['top1_accuracy_with_rejections']:.6f}",
        f"Top-5 accuracy: {quality['top5_accuracy']:.6f}",
        f"Coverage: {quality['coverage']:.6f}",
        f"Accepted-only accuracy: {quality['accepted_accuracy']:.6f}",
        f"Macro precision: {quality['macro_precision']:.6f}",
        f"Macro recall: {quality['macro_recall']:.6f}",
        f"Macro F1: {quality['macro_f1']:.6f}",
        f"Weighted F1: {quality['weighted_f1']:.6f}",
        f"Micro precision: {quality['micro_precision']:.6f}",
        f"Micro recall: {quality['micro_recall']:.6f}",
        f"Micro F1: {quality['micro_f1']:.6f}",
        f"Accepted: {quality['accepted']} / {quality['samples']}",
        f"Rejected: {quality['rejected']} / {quality['samples']}",
        "",
    ]
    for split, title in (("val", "VALIDATION"), ("test", "TEST")):
        split_quality = report.get("by_split", {}).get(split)
        if not split_quality:
            continue
        lines.extend(
            [
                title,
                f"Images: {split_quality['images']}",
                f"Mask objects: {split_quality['samples']}",
                f"Top-1 accuracy (rejections incorrect): {split_quality['top1_accuracy_with_rejections']:.6f}",
                f"Top-5 accuracy: {split_quality['top5_accuracy']:.6f}",
                f"Coverage: {split_quality['coverage']:.6f}",
                f"Accepted-only accuracy: {split_quality['accepted_accuracy']:.6f}",
                f"Accepted: {split_quality['accepted']} / {split_quality['samples']}",
                f"Rejected: {split_quality['rejected']} / {split_quality['samples']}",
                "",
            ]
        )
    lines.extend(
        [
        "SIMILARITY",
        f"Mean best similarity: {similarity['mean_best']:.6f}",
        f"Mean correct best similarity: {similarity['mean_correct']:.6f}",
        f"Mean incorrect/rejected best similarity: {similarity['mean_incorrect']:.6f}",
        f"Mean top-1/top-2 margin: {similarity['mean_margin']:.6f}",
        "",
        "EFFICIENCY",
        f"Model load time: {efficiency['model_load_seconds']:.3f} s",
        f"Evaluation wall time: {efficiency['wall_seconds']:.3f} s",
        f"End-to-end throughput: {efficiency['samples_per_second']:.3f} crops/s",
        f"Mask crop latency: {efficiency['crop_ms_per_sample']:.3f} ms/crop",
        f"Preprocess latency: {efficiency['preprocess_ms_per_sample']:.3f} ms/crop",
        f"OpenCLIP inference latency: {efficiency['embedding_ms_per_sample']:.3f} ms/crop",
        f"Similarity search latency: {efficiency['matching_ms_per_sample']:.3f} ms/crop",
        f"Measured pipeline latency: {efficiency['pipeline_ms_per_sample']:.3f} ms/crop",
        "",
        "METHODOLOGY",
        "Ground-truth segmentation polygons isolate embedding/classification quality.",
        "Non-object pixels are black and crops are tight, matching catalog creation.",
        "Final ranking replicates inventory_app: top 100 embedding matches, class mean",
        "requires at least 3 supporting embeddings, then threshold rejection.",
        "Catalog embeddings were produced from train split masks; val and test are queries.",
        "One sample is one ground-truth mask object. Top-1 accuracy is correct class",
        "matches divided by all objects. A match below the similarity threshold is rejected",
        "and counted incorrect. Top-5 ignores that threshold.",
    ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate OpenCLIP classification on merged test+val masks."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--threshold", type=float, default=0.60)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument(
        "--from-predictions",
        type=Path,
        default=None,
        help="Rebuild val/test accuracy from predictions.csv without re-embedding.",
    )
    args = parser.parse_args()

    if args.from_predictions is not None:
        refresh_saved_report(
            args.from_predictions.resolve(),
            args.output.resolve(),
        )
        return

    dataset = args.dataset.resolve()
    catalog_path = args.catalog.resolve()
    checkpoint = args.checkpoint.resolve()
    output = args.output.resolve()
    if not catalog_path.is_file():
        raise FileNotFoundError(f"Catalog CSV not found: {catalog_path}")
    if not checkpoint.is_file():
        raise FileNotFoundError(f"OpenCLIP checkpoint not found: {checkpoint}")
    output.mkdir(parents=True, exist_ok=True)

    print("Indexing merged validation and test samples...", flush=True)
    samples, diagnostics = build_samples(dataset)
    if not samples:
        raise RuntimeError("No valid val/test segmentation samples were found.")
    print(f"Indexed {len(samples)} ground-truth mask instances.", flush=True)
    print("Loading inventory embedding catalog...", flush=True)
    catalog_names, catalog_matrix = load_catalog(catalog_path)
    catalog_classes = sorted({canonical_name(name) for name in catalog_names})
    print(
        f"Loaded {len(catalog_names)} embeddings across "
        f"{len(catalog_classes)} classes.",
        flush=True,
    )

    import open_clip

    print(f"Loading OpenCLIP on {args.device}...", flush=True)
    load_started = time.perf_counter()
    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32",
        pretrained=str(checkpoint),
    )
    model = model.to(args.device).eval()
    if args.device.startswith("cuda"):
        torch.cuda.synchronize()
    model_load_seconds = time.perf_counter() - load_started
    print(f"OpenCLIP loaded in {model_load_seconds:.2f}s.", flush=True)

    records = []
    crop_seconds = 0.0
    preprocess_seconds = 0.0
    embedding_seconds = 0.0
    matching_seconds = 0.0
    skipped_invalid_crops = 0

    # Warm up the exact preprocessing and encoder path outside timed inference.
    first = samples[0]
    with Image.open(first["image"]) as source:
        warmup_crop = make_masked_crop(source.convert("RGB"), first["polygon"])
    if warmup_crop is None:
        raise RuntimeError("First evaluation crop is invalid.")
    warmup_tensor = preprocess(warmup_crop).unsqueeze(0).to(args.device)
    with torch.inference_mode():
        warmup_vector = model.encode_image(warmup_tensor)
        warmup_vector = warmup_vector / warmup_vector.norm(dim=-1, keepdim=True)
    if args.device.startswith("cuda"):
        torch.cuda.synchronize()
    del warmup_tensor, warmup_vector, warmup_crop
    print("Warmup complete; starting timed evaluation.", flush=True)

    evaluation_started = time.perf_counter()
    for offset in range(0, len(samples), max(1, args.batch)):
        batch_samples = samples[offset:offset + max(1, args.batch)]
        valid_samples = []
        crops = []
        crop_started = time.perf_counter()
        source_images = {}
        for sample in batch_samples:
            source_image = source_images.get(sample["image"])
            if source_image is None:
                with Image.open(sample["image"]) as source:
                    source_image = source.convert("RGB")
                source_images[sample["image"]] = source_image
            crop = make_masked_crop(source_image, sample["polygon"])
            if crop is None:
                skipped_invalid_crops += 1
                continue
            valid_samples.append(sample)
            crops.append(crop)
        crop_seconds += time.perf_counter() - crop_started
        if not crops:
            continue

        preprocess_started = time.perf_counter()
        tensor = torch.stack([preprocess(crop) for crop in crops]).to(args.device)
        preprocess_seconds += time.perf_counter() - preprocess_started

        if args.device.startswith("cuda"):
            torch.cuda.synchronize()
        embedding_started = time.perf_counter()
        with torch.inference_mode():
            vectors = model.encode_image(tensor)
            vectors = vectors / vectors.norm(dim=-1, keepdim=True).clamp_min(1e-8)
        if args.device.startswith("cuda"):
            torch.cuda.synchronize()
        embedding_seconds += time.perf_counter() - embedding_started
        vectors_np = vectors.detach().float().cpu().numpy().astype(np.float32)

        for sample, vector in zip(valid_samples, vectors_np):
            matching_started = time.perf_counter()
            ranking = rank_like_inventory_app(vector, catalog_names, catalog_matrix)
            matching_seconds += time.perf_counter() - matching_started
            best_score, predicted_name = ranking[0] if ranking else (-1.0, "")
            second_score = ranking[1][0] if len(ranking) > 1 else -1.0
            accepted = bool(ranking and best_score > args.threshold)
            true_key = canonical_name(sample["true_name"])
            pred_key = canonical_name(predicted_name)
            correct = accepted and pred_key == true_key
            top5_correct = true_key in {
                canonical_name(name) for _score, name in ranking[:5]
            }
            records.append(
                {
                    "split": sample["split"],
                    "image": sample["image"].name,
                    "polygon_index": sample["polygon_index"],
                    "true_name": sample["true_name"],
                    "predicted_name": predicted_name if accepted else "UNKNOWN",
                    "true_key": true_key,
                    "pred_key": pred_key,
                    "similarity": best_score,
                    "second_similarity": second_score,
                    "margin": best_score - second_score if second_score >= -0.5 else 0.0,
                    "accepted": accepted,
                    "correct": correct,
                    "top5_correct": top5_correct,
                }
            )
        del tensor, vectors, vectors_np
        completed = min(offset + len(batch_samples), len(samples))
        if completed == len(samples) or completed % (max(1, args.batch) * 10) == 0:
            elapsed = time.perf_counter() - evaluation_started
            print(
                f"Processed {completed}/{len(samples)} mask instances "
                f"({completed / elapsed:.2f} crops/s).",
                flush=True,
            )
    wall_seconds = time.perf_counter() - evaluation_started

    if not records:
        raise RuntimeError("No mask crops could be evaluated.")
    true_classes = sorted({record["true_key"] for record in records})
    quality = classification_metrics(records, true_classes)
    class_rows = quality.pop("per_class")
    best_scores = [record["similarity"] for record in records]
    correct_scores = [record["similarity"] for record in records if record["correct"]]
    incorrect_scores = [
        record["similarity"] for record in records if not record["correct"]
    ]
    margins = [record["margin"] for record in records]
    evaluated = len(records)
    pipeline_seconds = (
        crop_seconds + preprocess_seconds + embedding_seconds + matching_seconds
    )
    absent_classes = sorted(set(true_classes) - set(catalog_classes))

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint": str(checkpoint),
        "catalog": str(catalog_path),
        "dataset": {
            **diagnostics,
            "candidate_mask_instances": len(samples),
            "evaluated_samples": evaluated,
            "skipped_invalid_crops": skipped_invalid_crops,
            "true_classes": len(true_classes),
            "catalog_embeddings": len(catalog_names),
            "catalog_classes": len(catalog_classes),
            "classes_absent_from_catalog": len(absent_classes),
            "absent_class_names": absent_classes,
        },
        "runtime": {
            "device": args.device,
            "torch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "python": platform.python_version(),
            "batch_size": args.batch,
        },
        "quality": quality,
        "by_split": quality_by_split(records),
        "similarity": {
            "threshold": args.threshold,
            "mean_best": float(np.mean(best_scores)),
            "mean_correct": float(np.mean(correct_scores)) if correct_scores else 0.0,
            "mean_incorrect": (
                float(np.mean(incorrect_scores)) if incorrect_scores else 0.0
            ),
            "mean_margin": float(np.mean(margins)),
        },
        "efficiency": {
            "model_load_seconds": model_load_seconds,
            "wall_seconds": wall_seconds,
            "samples_per_second": evaluated / wall_seconds,
            "crop_ms_per_sample": crop_seconds * 1000.0 / evaluated,
            "preprocess_ms_per_sample": preprocess_seconds * 1000.0 / evaluated,
            "embedding_ms_per_sample": embedding_seconds * 1000.0 / evaluated,
            "matching_ms_per_sample": matching_seconds * 1000.0 / evaluated,
            "pipeline_ms_per_sample": pipeline_seconds * 1000.0 / evaluated,
        },
    }

    write_records(output / "predictions.csv", records)
    write_class_metrics(output / "per_class_metrics.csv", class_rows)
    (output / "metrics.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    write_text_report(output / "report.txt", report)
    note = "\n".join(score_lines(report)) + "\n"
    (output / "accuracy.txt").write_text(note, encoding="utf-8")
    print(note, end="")
    print(f"Wrote {output / 'accuracy.txt'}")


if __name__ == "__main__":
    main()
