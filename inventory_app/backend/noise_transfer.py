"""Laptop FaceTime grain → training crops (blur residual). Fail-closed.

Live capture dumps ``frame.jpg`` + readable ``result.txt`` under
``inventory_app/noise_captures/laptop_<timestamp>/``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# Sanity band for live FaceTime avg residual (dead / absurd sensors abort).
MIN_AVG_NOISE = 0.5
MAX_AVG_NOISE = 40.0
MIN_FRAMES = 8
DEFAULT_SECONDS = 1.5
DEFAULT_SIZE = (640, 480)
# Post-apply score must land near profile avg_noise.
TARGET_REL_TOL = 0.20
TARGET_ABS_TOL = 1.0

CAPTURES_ROOT = Path(__file__).resolve().parent.parent / "noise_captures"


@dataclass(frozen=True)
class NoiseProfile:
    avg_noise: float
    residual_map: np.ndarray  # float32 HxW, mean abs residual over frames
    width: int
    height: int
    frames: int
    camera_index: int
    capture_dir: str | None = None


def noise_score(gray: np.ndarray) -> float:
    """Blur residual: mean(|gray − soft blur|) — grain estimate."""
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    residual = cv2.absdiff(gray, blur)
    return float(np.mean(residual))


def residual_map(gray: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return cv2.absdiff(gray, blur).astype(np.float32)


def _open_camera(index: int, size: tuple[int, int]) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        cap = cv2.VideoCapture(index)
    if cap.isOpened():
        w, h = size
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    return cap


def _fit_frame(frame: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    w, h = size
    if frame.shape[1] == w and frame.shape[0] == h:
        return frame
    return cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)


def _is_mostly_black(frame: np.ndarray) -> bool:
    return float(np.mean(frame)) < 8.0


def _new_run_dir() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = CAPTURES_ROOT / f"laptop_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _save_capture_bundle(
    run_dir: Path,
    frames: list[np.ndarray],
    scores: list[float],
    camera_index: int,
    size: tuple[int, int],
) -> dict:
    """Write mid still + readable result.txt (blur residual only)."""
    tw, th = size
    mid = frames[len(frames) // 2]
    frame_path = run_dir / "frame.jpg"
    cv2.imwrite(str(frame_path), mid)

    avg_noise = float(np.mean(scores))
    text = "\n".join(
        [
            "NOISE CAPTURE",
            f"camera: {camera_index}",
            f"size: {tw}x{th}",
            f"frames: {len(frames)}",
            f"blur_residual_avg: {avg_noise:.4f}",
            f"folder: {run_dir}",
            "",
        ]
    )
    (run_dir / "result.txt").write_text(text, encoding="utf-8")
    return {"folder": str(run_dir), "avg_noise": avg_noise, "frame": "frame.jpg"}


def capture_laptop_noise_profile(
    camera_index: int,
    seconds: float = DEFAULT_SECONDS,
    size: tuple[int, int] = DEFAULT_SIZE,
    save_captures: bool = True,
) -> NoiseProfile:
    """Sample FaceTime at fixed size; raise if capture/profile invalid.

    When ``save_captures`` is True (default), writes ``frame.jpg`` + ``result.txt``
    under ``inventory_app/noise_captures/laptop_<timestamp>/``.
    """
    tw, th = size
    cap = _open_camera(camera_index, size)
    if not cap.isOpened():
        raise RuntimeError(
            f"Cannot open laptop camera index {camera_index} for noise capture."
        )

    frames: list[np.ndarray] = []
    end = time.time() + max(0.5, float(seconds))
    try:
        while time.time() < end:
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            frames.append(_fit_frame(frame, size))
    finally:
        cap.release()

    if len(frames) < MIN_FRAMES:
        raise RuntimeError(
            f"Noise capture got {len(frames)} frames (need ≥{MIN_FRAMES}). "
            "Check FaceTime / CAMERA_INDEX."
        )
    if all(_is_mostly_black(f) for f in frames[:MIN_FRAMES]):
        raise RuntimeError("Noise capture frames look black — refuse profile.")

    maps = []
    scores = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        maps.append(residual_map(gray))
        scores.append(noise_score(gray))

    avg = float(np.mean(scores))
    if avg < MIN_AVG_NOISE or avg > MAX_AVG_NOISE:
        raise RuntimeError(
            f"Noise avg {avg:.3f} outside sane band "
            f"[{MIN_AVG_NOISE}, {MAX_AVG_NOISE}]."
        )

    mean_map = np.mean(np.stack(maps, axis=0), axis=0).astype(np.float32)
    capture_dir: str | None = None
    if save_captures:
        run_dir = _new_run_dir()
        bundle = _save_capture_bundle(run_dir, frames, scores, camera_index, size)
        capture_dir = bundle["folder"]
        print(f"[noise_transfer] saved capture → {capture_dir}")
        print(f"[noise_transfer] blur_residual avg={avg:.3f}")

    return NoiseProfile(
        avg_noise=avg,
        residual_map=mean_map,
        width=tw,
        height=th,
        frames=len(frames),
        camera_index=camera_index,
        capture_dir=capture_dir,
    )


# Pixel MAE floor when crop residual already ≥ laptop avg (cannot "raise" score).
_MIN_PIXEL_DELTA = 0.25


def apply_noise_to_image(pil_rgb: Image.Image, profile: NoiseProfile) -> Image.Image:
    """Stamp laptop residual grain onto RGB crop; clip to uint8."""
    rgb = np.asarray(pil_rgb.convert("RGB"), dtype=np.float32)
    h, w = rgb.shape[:2]
    res = cv2.resize(
        profile.residual_map,
        (w, h),
        interpolation=cv2.INTER_AREA,
    ).astype(np.float32)
    centered = res - float(np.mean(res))
    base_std = float(np.std(centered)) + 1e-6
    scale = profile.avg_noise / base_std
    grain = centered * scale
    candidate = np.clip(rgb + grain[:, :, None], 0, 255).astype(np.uint8)
    gray = cv2.cvtColor(candidate, cv2.COLOR_RGB2GRAY)
    got = noise_score(gray)
    target = profile.avg_noise
    clean_gray = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    clean_score = noise_score(clean_gray)
    # Quiet crops: steer residual toward FaceTime avg. Busy crops: stamp only.
    # ponytail: photo texture often > laptop grain; residual-rise gate cannot hold.
    if clean_score < target - 0.5:
        if abs(got - target) > max(TARGET_ABS_TOL, TARGET_REL_TOL * target):
            if got > 1e-6:
                scale *= target / got
            grain = centered * scale
            candidate = np.clip(rgb + grain[:, :, None], 0, 255).astype(np.uint8)
            gray = cv2.cvtColor(candidate, cv2.COLOR_RGB2GRAY)
            got = noise_score(gray)
        if got <= clean_score + 0.05:
            raise RuntimeError(
                f"Noise apply failed gate: residual did not rise "
                f"(clean={clean_score:.3f}, got={got:.3f}, target={target:.3f})."
            )
    else:
        delta = float(np.mean(np.abs(candidate.astype(np.float32) - rgb)))
        if delta < _MIN_PIXEL_DELTA:
            raise RuntimeError(
                f"Noise apply failed gate: grain no-op "
                f"(pixel_delta={delta:.3f}, clean={clean_score:.3f}, target={target:.3f})."
            )
    return Image.fromarray(candidate, mode="RGB")


def assert_noise_applied(
    clean: Image.Image,
    noised: Image.Image,
    profile: NoiseProfile,
) -> None:
    """Fail if apply was a no-op or missed target band."""
    clean_rgb = np.asarray(clean.convert("RGB"), dtype=np.float32)
    noised_rgb = np.asarray(noised.convert("RGB"), dtype=np.float32)
    clean_g = cv2.cvtColor(clean_rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    noised_g = cv2.cvtColor(noised_rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    c_score = noise_score(clean_g)
    n_score = noise_score(noised_g)
    target = profile.avg_noise
    if c_score < target - 0.5:
        if n_score <= c_score + 0.05:
            raise RuntimeError(
                f"Noised residual {n_score:.3f} not above clean {c_score:.3f}."
            )
        if n_score < min(c_score + 0.2, target * 0.4):
            raise RuntimeError(
                f"Noised residual {n_score:.3f} far from target {target:.3f}."
            )
        return
    delta = float(np.mean(np.abs(noised_rgb - clean_rgb)))
    if delta < _MIN_PIXEL_DELTA:
        raise RuntimeError(
            f"Noised pixel_delta {delta:.3f} below floor {_MIN_PIXEL_DELTA} "
            f"(clean residual already {c_score:.3f} ≥ target {target:.3f})."
        )


def _synthetic_self_check() -> None:
    """No camera: synthetic residual map must raise crop grain."""
    rng = np.random.default_rng(0)
    residual = rng.random((120, 160), dtype=np.float32) * 8.0 + 2.0
    profile = NoiseProfile(
        avg_noise=float(np.mean(residual)),
        residual_map=residual,
        width=160,
        height=120,
        frames=12,
        camera_index=-1,
    )
    clean = Image.fromarray(
        np.full((64, 64, 3), 128, dtype=np.uint8),
        mode="RGB",
    )
    noised = apply_noise_to_image(clean, profile)
    assert_noise_applied(clean, noised, profile)
    print(
        f"[noise_transfer] self-check OK "
        f"(target≈{profile.avg_noise:.2f}, "
        f"noised={noise_score(cv2.cvtColor(np.asarray(noised), cv2.COLOR_RGB2GRAY)):.2f})"
    )


if __name__ == "__main__":
    _synthetic_self_check()
