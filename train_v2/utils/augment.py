"""Label-aware Ultralytics train() kwargs.

Aggressive geometry (mosaic, mixup, copy-paste, perspective, large
translate / scale / shear) can slide polygons off the frame or crop the
ROI in half. These settings keep photometric augs and only small
in-frame geometry so the object of interest stays visible.
"""

from __future__ import annotations

# Passed straight into YOLO.train() / RTDETR.train().
LABEL_AWARE_AUG: dict[str, float | int] = {
    "mosaic": 0.0,
    "mixup": 0.0,
    "copy_paste": 0.0,
    "cutmix": 0.0,
    "perspective": 0.0,
    "shear": 0.0,
    "translate": 0.05,
    "scale": 0.10,
    "degrees": 8.0,
    "fliplr": 0.5,
    "flipud": 0.0,
    "hsv_h": 0.015,
    "hsv_s": 0.50,
    "hsv_v": 0.40,
    "erasing": 0.0,
    "multi_scale": 0.0,
    "close_mosaic": 0,
}
