"""Extract image embeddings for similarity search (OpenCLIP or YOLO)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "yolo11n-seg.pt"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / DEFAULT_MODEL
YOLO11N_SEG_URLS = (
    "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n-seg.pt",
    "https://github.com/ultralytics/assets/releases/latest/download/yolo11n-seg.pt",
)


def _find_weights(model_path: str | Path) -> Path | None:
    requested = Path(model_path)
    candidates = [
        requested,
        Path.cwd() / requested.name,
        PROJECT_ROOT / requested.name,
        PROJECT_ROOT / "models" / requested.name,
        PROJECT_ROOT / "inventory_app" / "models" / requested.name,
        PROJECT_ROOT / "aiic_model_handoff" / requested.name,
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _download_yolo11n_seg(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    from ultralytics.utils.downloads import safe_download

    errors: list[str] = []
    for url in YOLO11N_SEG_URLS:
        try:
            safe_download(url=url, file=str(dest), min_bytes=1e5)
            if dest.exists() and dest.stat().st_size > 1e5:
                return dest
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise FileNotFoundError(
        "Could not download yolo11n-seg.pt. " + " | ".join(errors)
    )


CLIP_ARCH = "ViT-B-32"
CLIP_PRETRAINED = "laion2b_s34b_b79k"
CLIP_DIM = 512


@dataclass
class ClipEmbedder:
    """Loaded OpenCLIP image encoder. Keep this object and reuse it."""

    model: Any
    preprocess: Any
    device: str
    arch: str = CLIP_ARCH
    pretrained: str = CLIP_PRETRAINED


def load_clip_model(
    arch: str = CLIP_ARCH,
    pretrained: str = CLIP_PRETRAINED,
) -> ClipEmbedder:
    """Load OpenCLIP ViT-B-32 (LAION-2B). Downloads weights on first run."""
    import open_clip
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading OpenCLIP {arch} ({pretrained}) on {device} ...")
    model, _, preprocess = open_clip.create_model_and_transforms(
        arch,
        pretrained=pretrained,
    )
    model = model.to(device).eval()
    return ClipEmbedder(
        model=model,
        preprocess=preprocess,
        device=device,
        arch=arch,
        pretrained=pretrained,
    )


def _to_pil(source: str | Path | Image.Image | np.ndarray) -> Image.Image:
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(path)
        return Image.open(path).convert("RGB")
    if isinstance(source, Image.Image):
        return source.convert("RGB")
    arr = np.ascontiguousarray(source)
    if arr.ndim == 2:
        return Image.fromarray(arr).convert("RGB")
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr).convert("RGB")


def get_clip_embedding(
    clipper: ClipEmbedder,
    source: str | Path | Image.Image | np.ndarray,
) -> np.ndarray:
    """Return a unit-normalized OpenCLIP image embedding (512-d for ViT-B-32)."""
    import torch

    image = clipper.preprocess(_to_pil(source)).unsqueeze(0).to(clipper.device)
    with torch.no_grad():
        vec = clipper.model.encode_image(image)
        vec = vec / vec.norm(dim=-1, keepdim=True)
    return vec.squeeze(0).float().cpu().numpy().astype(np.float32)


def get_image_embedding(
    model,
    source: str | Path | Image.Image | np.ndarray,
    *,
    imgsz: int = 640,
) -> np.ndarray:
    """Embed with OpenCLIP if ``model`` is a ClipEmbedder, otherwise YOLO."""
    if isinstance(model, ClipEmbedder):
        return get_clip_embedding(model, source)
    return get_yolo_embedding(model, source, imgsz=imgsz)


def load_yolo_model(model_path: str | Path | None = None):
    """Load the original YOLO11 nano segmentation model, downloading it if needed."""
    from ultralytics import YOLO

    requested = DEFAULT_MODEL if model_path is None else str(model_path)
    weights = _find_weights(requested)
    if weights is None:
        if Path(requested).name == DEFAULT_MODEL:
            print(f"Downloading {DEFAULT_MODEL} to {DEFAULT_MODEL_PATH} ...")
            weights = _download_yolo11n_seg(DEFAULT_MODEL_PATH)
        elif Path(requested).exists():
            weights = Path(requested)
        else:
            return YOLO(requested)

    print(f"Loading YOLO: {weights}")
    return YOLO(str(weights))


def get_yolo_embedding(
    model,
    source: str | Path | Image.Image | np.ndarray,
    *,
    imgsz: int = 640,
) -> np.ndarray:
    """Return a 1D YOLO embedding from a path, PIL image, or numpy array."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(path)
        embed_source = str(path)
    elif isinstance(source, Image.Image):
        embed_source = np.ascontiguousarray(source.convert("RGB"))
    else:
        embed_source = np.ascontiguousarray(source)

    if hasattr(model, "embed"):
        vectors = model.embed(source=embed_source, imgsz=imgsz, verbose=False)
    else:
        vectors = model.predict(source=embed_source, embed=[-2], imgsz=imgsz, verbose=False)

    vec = vectors[0]
    if hasattr(vec, "detach"):
        arr = vec.detach().float().cpu().numpy()
    else:
        arr = np.asarray(vec)
    return np.ravel(arr).astype(np.float32)


def embed_from_dataframe(
    model,
    df: pd.DataFrame,
    index: int,
    *,
    dataset_dir: Path | None = None,
    imgsz: int = 640,
    pad: int = 8,
) -> dict:
    """Load image + labels, crop each bbox, and embed crops one by one.

    Returns a dictionary with image metadata and one entry per cropped object.
    """
    from .dataset import crop_labeled_objects, load_image_and_label

    path = df.at[index, "path"]
    image, labels = load_image_and_label(image_path=path, dataset_dir=dataset_dir)
    crops = crop_labeled_objects(image, labels, pad=pad)

    objects: list[dict] = []
    for item in crops:
        embedding = get_image_embedding(model, item["crop"], imgsz=imgsz)
        objects.append(
            {
                "instance_id": item["instance_id"],
                "class_id": item["class_id"],
                "class_name": item["class_name"],
                "kind": item["kind"],
                "bbox_xyxy": item["bbox_xyxy"],
                "crop_width": item["crop_width"],
                "crop_height": item["crop_height"],
                "embedding": embedding,
                "embedding_dim": int(embedding.size),
            }
        )

    result = {
        "index": int(index),
        "image_name": Path(path).name,
        "path": str(path),
        "image_width": image.size[0],
        "image_height": image.size[1],
        "n_objects": len(objects),
        "objects": objects,
    }

    if "embedding" in df.columns:
        df["embedding"] = df["embedding"].astype(object)
        df.at[index, "embedding"] = [obj["embedding"] for obj in objects]
    return result


def build_embedding_df(
    model,
    catalog: pd.DataFrame,
    *,
    dataset_dir: Path | None = None,
    imgsz: int = 640,
    pad: int = 8,
    fail_log_path: str | Path | None = None,
) -> pd.DataFrame:
    """Embed every labeled crop in ``catalog`` and return one row per object.

    Columns: image_name, class_name, bbox_xyxy, embedding.
    Failed files are appended to ``fail_log_path`` (default: embed_failures.txt).
    """
    from tqdm import tqdm

    log_path = Path(fail_log_path) if fail_log_path is not None else PROJECT_ROOT / "embed_failures.txt"
    log_path.write_text("image_name\tpath\terror\n", encoding="utf-8")

    def log_failure(image_name: str, path: str, error: object) -> None:
        line = f"{image_name}\t{path}\t{error}\n"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(line)

    rows: list[dict] = []
    n_failed = 0
    for index in tqdm(
        range(len(catalog)),
        desc="Embedding object crops",
        unit="img",
        dynamic_ncols=True,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
    ):
        image_name = str(catalog.at[index, "image_name"]) if "image_name" in catalog.columns else str(index)
        path = str(catalog.at[index, "path"]) if "path" in catalog.columns else ""
        try:
            result = embed_from_dataframe(
                model,
                catalog,
                index,
                dataset_dir=dataset_dir,
                imgsz=imgsz,
                pad=pad,
            )
        except Exception as exc:
            n_failed += 1
            log_failure(image_name, path, exc)
            tqdm.write(f"Skip {image_name}: {exc}")
            continue

        for obj in result["objects"]:
            rows.append(
                {
                    "image_name": result["image_name"],
                    "class_name": obj["class_name"],
                    "bbox_xyxy": list(obj["bbox_xyxy"]),
                    "embedding": obj["embedding"],
                }
            )

    embedding_df = pd.DataFrame(
        rows,
        columns=["image_name", "class_name", "bbox_xyxy", "embedding"],
    )
    if len(embedding_df):
        embedding_df["embedding"] = embedding_df["embedding"].astype(object)
        embedding_df["bbox_xyxy"] = embedding_df["bbox_xyxy"].astype(object)

    print(f"Embedded {len(embedding_df)} crops from {len(catalog) - n_failed}/{len(catalog)} images.")
    print(f"Failed files logged to {log_path} ({n_failed})")
    return embedding_df
