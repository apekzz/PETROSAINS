"""Pure Dice instance-mask loss for Ultralytics YOLO-seg.

Patches ``v8SegmentationLoss.single_mask_loss`` the same way as the
existing ``training_dice.ipynb`` experiment: box / cls / DFL stay default,
only the mask term becomes Dice. The crop is applied through a ones-mask
so autograd is not broken by in-place ``crop_mask``.
"""

from __future__ import annotations

import torch

import torch.nn.functional as F

from ultralytics.utils.loss import v8SegmentationLoss
from ultralytics.utils.ops import crop_mask


def dice_single_mask_loss(
    gt_mask: torch.Tensor,
    pred: torch.Tensor,
    proto: torch.Tensor,
    xyxy: torch.Tensor,
    area: torch.Tensor,
) -> torch.Tensor:
    """Dice loss for one image's assigned instances. ``area`` is unused."""
    pred_mask = torch.einsum("in,nhw->ihw", pred, proto)
    pred_prob = pred_mask.float().sigmoid()
    gt_mask = gt_mask.float()

    crop_region = crop_mask(torch.ones_like(pred_prob), xyxy)
    pred_crop = pred_prob * crop_region
    gt_crop = gt_mask * crop_region

    intersection = (pred_crop * gt_crop).sum(dim=(1, 2))
    pred_sum = pred_crop.sum(dim=(1, 2))
    gt_sum = gt_crop.sum(dim=(1, 2))
    eps = 1e-7
    dice_score = (2.0 * intersection + eps) / (pred_sum + gt_sum + eps)
    return (1.0 - dice_score).sum()


def apply_dice_mask_loss() -> None:
    """Replace Ultralytics BCE mask loss with pure Dice for this process."""
    if not hasattr(v8SegmentationLoss, "_original_single_mask_loss"):
        v8SegmentationLoss._original_single_mask_loss = v8SegmentationLoss.single_mask_loss
    v8SegmentationLoss.single_mask_loss = staticmethod(dice_single_mask_loss)
    print("Mask loss: pure Dice (box / cls / DFL unchanged)")


def bce_dice_single_mask_loss(
    gt_mask: torch.Tensor,
    pred: torch.Tensor,
    proto: torch.Tensor,
    xyxy: torch.Tensor,
    area: torch.Tensor,
) -> torch.Tensor:
    """0.5 BCE + 0.5 Dice. BCE is cropped in-place on a fresh tensor; Dice uses a ones-mask crop."""
    pred_mask = torch.einsum("in,nhw->ihw", pred, proto)
    gt_mask = gt_mask.float()

    bce = F.binary_cross_entropy_with_logits(pred_mask, gt_mask, reduction="none")
    bce_loss = (crop_mask(bce, xyxy).mean(dim=(1, 2)) / area).sum()

    pred_prob = pred_mask.float().sigmoid()
    crop_region = crop_mask(torch.ones_like(pred_prob), xyxy)
    pred_crop = pred_prob * crop_region
    gt_crop = gt_mask * crop_region
    intersection = (pred_crop * gt_crop).sum(dim=(1, 2))
    pred_sum = pred_crop.sum(dim=(1, 2))
    gt_sum = gt_crop.sum(dim=(1, 2))
    eps = 1e-7
    dice_loss = (1.0 - (2.0 * intersection + eps) / (pred_sum + gt_sum + eps)).sum()
    return 0.5 * bce_loss + 0.5 * dice_loss


def apply_bce_dice_mask_loss() -> None:
    """Replace Ultralytics BCE mask loss with 0.5 BCE + 0.5 Dice."""
    if not hasattr(v8SegmentationLoss, "_original_single_mask_loss"):
        v8SegmentationLoss._original_single_mask_loss = v8SegmentationLoss.single_mask_loss
    v8SegmentationLoss.single_mask_loss = staticmethod(bce_dice_single_mask_loss)
    print("Mask loss: 0.5 BCE + 0.5 Dice (box / cls / DFL unchanged)")
