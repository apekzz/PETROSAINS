#!/usr/bin/env python3
"""Evaluate YOLO11 segmentation on the merged validation and test splits."""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import yaml
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT / "train_v2" / "dataset"
DEFAULT_WEIGHTS = (
    ROOT
    / "train_v2"
    / "runs"
    / "v2"
    / "yolo11l_seg_object_bce_dice"
    / "weights"
    / "best.pt"
)
DEFAULT_OUTPUT = ROOT / "train_v2" / "evaluation" / "results" / "segmentation"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def split_images(dataset: Path, split: str) -> list[Path]:
    folder = dataset / "images" / split
    return sorted(
        path for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def count_instances(dataset: Path, images: list[Path]) -> tuple[int, int]:
    instances = 0
    missing_labels = 0
    for image in images:
        split = image.parent.name
        label = dataset / "labels" / split / f"{image.stem}.txt"
        if not label.is_file():
            missing_labels += 1
            continue
        instances += len({
            line.strip()
            for line in label.read_text(encoding="utf-8").splitlines()
            if line.strip()
        })
    return instances, missing_labels


def metric_value(metric, name: str) -> float:
    value = getattr(metric, name, 0.0)
    return float(value() if callable(value) else value)


def write_text_report(path: Path, report: dict) -> None:
    quality = report["quality"]
    efficiency = report["efficiency"]
    dataset = report["dataset"]
    lines = [
        "YOLO11L SEGMENTATION EVALUATION",
        "=" * 40,
        f"Generated: {report['generated_at']}",
        f"Weights: {report['weights']}",
        f"Device: {report['runtime']['device']}",
        "",
        "EVALUATION DATA",
        f"Validation images: {dataset['val_images']}",
        f"Test images: {dataset['test_images']}",
        f"Merged images: {dataset['merged_images']}",
        f"Ground-truth instances: {dataset['instances']}",
        f"Missing label files: {dataset['missing_labels']}",
        "",
        "BOX METRICS",
        f"Precision: {quality['box_precision']:.6f}",
        f"Recall: {quality['box_recall']:.6f}",
        f"F1: {quality['box_f1']:.6f}",
        f"mAP@0.50: {quality['box_map50']:.6f}",
        f"mAP@0.50:0.95: {quality['box_map50_95']:.6f}",
        "",
        "MASK METRICS",
        f"Precision: {quality['mask_precision']:.6f}",
        f"Recall: {quality['mask_recall']:.6f}",
        f"F1: {quality['mask_f1']:.6f}",
        f"mAP@0.50: {quality['mask_map50']:.6f}",
        f"mAP@0.50:0.95: {quality['mask_map50_95']:.6f}",
        "",
        "EFFICIENCY",
        f"Wall-clock evaluation time: {efficiency['wall_seconds']:.3f} s",
        f"Wall-clock throughput: {efficiency['wall_images_per_second']:.3f} images/s",
        f"Preprocess latency: {efficiency['preprocess_ms_per_image']:.3f} ms/image",
        f"Inference latency: {efficiency['inference_ms_per_image']:.3f} ms/image",
        f"Postprocess latency: {efficiency['postprocess_ms_per_image']:.3f} ms/image",
        f"Model pipeline latency: {efficiency['pipeline_ms_per_image']:.3f} ms/image",
        f"Model pipeline throughput: {efficiency['pipeline_images_per_second']:.3f} images/s",
        "",
        "NOTE",
        "Plain classification accuracy is not defined for object detection/segmentation.",
        "Precision, recall, F1, and mAP are the relevant predictive metrics.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate YOLO11l-seg on merged test+validation images."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--device", default="0" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    dataset = args.dataset.resolve()
    weights = args.weights.resolve()
    output = args.output.resolve()
    if not weights.is_file():
        raise FileNotFoundError(f"Model weights not found: {weights}")
    val_images = split_images(dataset, "val")
    test_images = split_images(dataset, "test")
    merged_images = val_images + test_images
    if not merged_images:
        raise RuntimeError("No validation or test images were found.")
    instances, missing_labels = count_instances(dataset, merged_images)

    output.mkdir(parents=True, exist_ok=True)
    merged_yaml = output / "merged_test_val.yaml"
    merged_yaml.write_text(
        yaml.safe_dump(
            {
                "path": str(dataset),
                "train": "images/train",
                "val": ["images/val", "images/test"],
                "nc": 1,
                "names": {0: "object"},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    model = YOLO(str(weights))
    started = time.perf_counter()
    metrics = model.val(
        data=str(merged_yaml),
        split="val",
        imgsz=args.imgsz,
        batch=args.batch,
        workers=0,
        device=args.device,
        conf=0.001,
        iou=0.7,
        plots=True,
        save_json=False,
        project=str(output),
        name="ultralytics_run",
        exist_ok=True,
        verbose=True,
    )
    wall_seconds = time.perf_counter() - started

    box_p = metric_value(metrics.box, "mp")
    box_r = metric_value(metrics.box, "mr")
    mask_p = metric_value(metrics.seg, "mp")
    mask_r = metric_value(metrics.seg, "mr")
    speed = getattr(metrics, "speed", {}) or {}
    preprocess_ms = float(speed.get("preprocess", 0.0))
    inference_ms = float(speed.get("inference", 0.0))
    postprocess_ms = float(speed.get("postprocess", 0.0))
    pipeline_ms = preprocess_ms + inference_ms + postprocess_ms
    instance_counts = np.asarray(getattr(metrics.box, "nt_per_class", []))
    instances_evaluated = (
        int(instance_counts.sum()) if instance_counts.size else instances
    )

    def f1(precision: float, recall: float) -> float:
        return (
            2.0 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "weights": str(weights),
        "dataset": {
            "path": str(dataset),
            "val_images": len(val_images),
            "test_images": len(test_images),
            "merged_images": len(merged_images),
            "instances": instances_evaluated,
            "missing_labels": missing_labels,
        },
        "runtime": {
            "device": str(args.device),
            "torch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "python": platform.python_version(),
            "image_size": args.imgsz,
            "batch_size": args.batch,
        },
        "quality": {
            "box_precision": box_p,
            "box_recall": box_r,
            "box_f1": f1(box_p, box_r),
            "box_map50": metric_value(metrics.box, "map50"),
            "box_map50_95": metric_value(metrics.box, "map"),
            "mask_precision": mask_p,
            "mask_recall": mask_r,
            "mask_f1": f1(mask_p, mask_r),
            "mask_map50": metric_value(metrics.seg, "map50"),
            "mask_map50_95": metric_value(metrics.seg, "map"),
        },
        "efficiency": {
            "wall_seconds": wall_seconds,
            "wall_images_per_second": len(merged_images) / wall_seconds,
            "preprocess_ms_per_image": preprocess_ms,
            "inference_ms_per_image": inference_ms,
            "postprocess_ms_per_image": postprocess_ms,
            "pipeline_ms_per_image": pipeline_ms,
            "pipeline_images_per_second": 1000.0 / pipeline_ms if pipeline_ms else 0.0,
        },
    }
    (output / "metrics.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    write_text_report(output / "report.txt", report)
    print(json.dumps(report, indent=2))
    print(f"Wrote {output / 'report.txt'}")


if __name__ == "__main__":
    main()
