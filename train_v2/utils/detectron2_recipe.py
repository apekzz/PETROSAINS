"""Detectron2 helpers that mirror the YOLO v2 recipe in train_rtdetr_l_v2.ipynb.

Architecture must change (Mask R-CNN R50-FPN). Data, epochs, batch, imgsz,
0.5 BCE + 0.5 Dice, cls=0.4, cosine LR, mosaic p=0.4 / close_mosaic=10,
and flip / small rotate-translate-scale stay aligned with the YOLO notebook.
"""

from __future__ import annotations

import copy
import logging
import random
import time
from multiprocessing import Value
from pathlib import Path

import cv2
import numpy as np
import torch

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import DatasetCatalog, MetadataCatalog, build_detection_train_loader
from detectron2.data import detection_utils as utils
from detectron2.data import transforms as T
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import DefaultTrainer
from detectron2.engine import defaults as d2_defaults
from detectron2.engine.hooks import BestCheckpointer, HookBase, PeriodicCheckpointer
from detectron2.engine.train_loop import AMPTrainer
from detectron2.evaluation import COCOEvaluator
from detectron2.modeling.roi_heads import mask_head as mask_head_mod
from detectron2.structures import BoxMode
from detectron2.utils.events import CommonMetricPrinter, EventStorage, JSONWriter, get_event_storage

# Same recipe numbers as train_rtdetr_l_v2.ipynb
EPOCHS = 200
BATCH = 4
IMGSZ = 640
CLS_GAIN = 0.4
MOSAIC_P = 0.4
CLOSE_MOSAIC = 10
PATIENCE = 20
FLIP_P = 0.5
DEGREES = 8.0
TRANSLATE = 0.05
SCALE = 0.10
HSV_H = 0.015
HSV_S = 0.50
HSV_V = 0.40

RECIPE = {
    "epochs": EPOCHS,
    "batch": BATCH,
    "imgsz": IMGSZ,
    "cls": CLS_GAIN,
    "mosaic": MOSAIC_P,
    "close_mosaic": CLOSE_MOSAIC,
    "cos_lr": True,
    "patience": PATIENCE,
    "mask_loss": "0.5 BCE + 0.5 Dice",
    "fliplr": FLIP_P,
    "flipud": 0.0,
    "degrees": DEGREES,
    "translate": TRANSLATE,
    "scale": SCALE,
    "hsv_h": HSV_H,
    "hsv_s": HSV_S,
    "hsv_v": HSV_V,
    "mixup": 0.0,
    "copy_paste": 0.0,
    "perspective": 0.0,
    "shear": 0.0,
}


def register_splits(dataset_dir: Path) -> dict[str, str]:
    dataset_dir = Path(dataset_dir)
    names = {}
    for split in ("train", "val", "test"):
        name = f"petrosains_object_{split}"
        json_file = dataset_dir / "coco" / f"{split}.json"
        image_root = dataset_dir / "images" / split
        if name in DatasetCatalog.list():
            DatasetCatalog.remove(name)
            MetadataCatalog.remove(name)
        register_coco_instances(name, {}, str(json_file), str(image_root))
        MetadataCatalog.get(name).thing_classes = ["object"]
        names[split] = name
    return names


def apply_bce_dice_mask_loss() -> None:
    """Replace Detectron2 mask BCE with 0.5 BCE + 0.5 Dice (same hybrid as YOLO v2)."""
    if getattr(mask_head_mod, "_original_mask_rcnn_loss", None) is None:
        mask_head_mod._original_mask_rcnn_loss = mask_head_mod.mask_rcnn_loss

    def mask_rcnn_bce_dice_loss(pred_mask_logits, instances, vis_period: int = 0):
        loss_bce = mask_head_mod._original_mask_rcnn_loss(
            pred_mask_logits, instances, vis_period
        )
        cls_agnostic_mask = pred_mask_logits.size(1) == 1
        mask_side_len = pred_mask_logits.size(2)
        gt_masks = []
        gt_classes = []
        for inst in instances:
            if len(inst) == 0:
                continue
            gt_masks.append(
                inst.gt_masks.crop_and_resize(inst.proposal_boxes.tensor, mask_side_len).to(
                    device=pred_mask_logits.device
                )
            )
            if not cls_agnostic_mask:
                gt_classes.append(inst.gt_classes.to(dtype=torch.int64))
        if not gt_masks:
            return loss_bce

        from detectron2.layers import cat

        gt = cat(gt_masks, dim=0).to(dtype=torch.float32)
        if cls_agnostic_mask:
            pred = pred_mask_logits[:, 0]
        else:
            indices = torch.arange(pred_mask_logits.size(0), device=pred_mask_logits.device)
            pred = pred_mask_logits[indices, cat(gt_classes, dim=0)]
        pred_prob = pred.float().sigmoid()
        inter = (pred_prob * gt).sum(dim=(1, 2))
        den = pred_prob.sum(dim=(1, 2)) + gt.sum(dim=(1, 2))
        dice = (1.0 - (2.0 * inter + 1e-7) / (den + 1e-7)).mean()
        return 0.5 * loss_bce + 0.5 * dice

    mask_head_mod.mask_rcnn_loss = mask_rcnn_bce_dice_loss
    print("Detectron2 mask loss: 0.5 BCE + 0.5 Dice")


def build_cfg(output_dir: Path, train_name: str, val_name: str, n_train: int):
    iters_per_epoch = max(1, n_train // BATCH)
    max_iter = iters_per_epoch * EPOCHS
    cfg = get_cfg()
    cfg.merge_from_file(
        model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
    )
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
        "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
    )
    cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.DATASETS.TRAIN = (train_name,)
    cfg.DATASETS.TEST = (val_name,)
    # Prefetch on CPU. MosaicProb uses a shared Value so close_mosaic still works.
    cfg.DATALOADER.NUM_WORKERS = 4
    cfg.SOLVER.IMS_PER_BATCH = BATCH
    # Detectron2 Mask R-CNN default is SGD. 0.02 @ batch 16 → 0.005 @ batch 4.
    cfg.SOLVER.BASE_LR = 0.005
    cfg.SOLVER.BASE_LR_END = 0.005 * 0.01
    cfg.SOLVER.MAX_ITER = max_iter
    cfg.SOLVER.STEPS = []
    cfg.SOLVER.WARMUP_ITERS = iters_per_epoch * 3
    cfg.SOLVER.WARMUP_FACTOR = 0.001
    cfg.SOLVER.LR_SCHEDULER_NAME = "WarmupCosineLR"
    cfg.SOLVER.CHECKPOINT_PERIOD = iters_per_epoch * 20
    cfg.SOLVER.AMP.ENABLED = torch.cuda.is_available()
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.25
    cfg.INPUT.MIN_SIZE_TRAIN = (IMGSZ,)
    cfg.INPUT.MAX_SIZE_TRAIN = IMGSZ
    cfg.INPUT.MIN_SIZE_TEST = IMGSZ
    cfg.INPUT.MAX_SIZE_TEST = IMGSZ
    cfg.INPUT.MIN_SIZE_TRAIN_SAMPLING = "choice"
    cfg.TEST.EVAL_PERIOD = iters_per_epoch
    cfg.OUTPUT_DIR = str(output_dir)
    return cfg, iters_per_epoch, max_iter


class MosaicProb:
    """Process-shared mosaic probability so close_mosaic works with DataLoader workers."""

    def __init__(self, value: float = MOSAIC_P):
        self._shared = Value("d", float(value))

    @property
    def value(self) -> float:
        return float(self._shared.value)

    @value.setter
    def value(self, v: float) -> None:
        self._shared.value = float(v)


class ModernAMPTrainer(AMPTrainer):
    """Detectron2 0.6 still calls torch.cuda.amp, which PyTorch 2.4+ warns on every step."""

    def __init__(self, *args, **kwargs):
        if kwargs.get("grad_scaler") is None:
            kwargs = dict(kwargs)
            kwargs["grad_scaler"] = torch.amp.GradScaler("cuda")
        super().__init__(*args, **kwargs)

    def run_step(self):
        assert self.model.training, "[AMPTrainer] model was changed to eval mode!"
        assert torch.cuda.is_available(), "[AMPTrainer] CUDA is required for AMP training!"

        start = time.perf_counter()
        data = next(self._data_loader_iter)
        data_time = time.perf_counter() - start

        if self.zero_grad_before_forward:
            self.optimizer.zero_grad()
        with torch.amp.autocast("cuda", dtype=self.precision):
            loss_dict = self.model(data)
            if isinstance(loss_dict, torch.Tensor):
                losses = loss_dict
                loss_dict = {"total_loss": loss_dict}
            else:
                losses = sum(loss_dict.values())

        if not self.zero_grad_before_forward:
            self.optimizer.zero_grad()

        self.grad_scaler.scale(losses).backward()

        if self.log_grad_scaler:
            storage = get_event_storage()
            storage.put_scalar("[metric]grad_scaler", self.grad_scaler.get_scale())

        self.after_backward()

        if self.async_write_metrics:
            self.concurrent_executor.submit(
                self._write_metrics, loss_dict, data_time, iter=self.iter
            )
        else:
            self._write_metrics(loss_dict, data_time)

        self.grad_scaler.step(self.optimizer)
        self.grad_scaler.update()


# DefaultTrainer constructs AMPTrainer from this module-level name.
d2_defaults.AMPTrainer = ModernAMPTrainer


def _hsv_jitter(image: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 0] = (hsv[:, :, 0] + (random.random() * 2 - 1) * HSV_H * 180) % 180
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + (random.random() * 2 - 1) * HSV_S), 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + (random.random() * 2 - 1) * HSV_V), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def _ensure_bbox_mode(anno: dict) -> dict:
    if "bbox_mode" not in anno:
        anno["bbox_mode"] = BoxMode.XYWH_ABS
    return anno


def _resize_record(image, annos, out_w, out_h):
    h, w = image.shape[:2]
    image = cv2.resize(image, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
    sx, sy = out_w / w, out_h / h
    new_annos = []
    for anno in annos:
        anno = _ensure_bbox_mode(copy.deepcopy(anno))
        bbox = anno["bbox"]
        anno["bbox"] = [bbox[0] * sx, bbox[1] * sy, bbox[2] * sx, bbox[3] * sy]
        segs = []
        for poly in anno.get("segmentation", []):
            pts = np.asarray(poly, dtype=np.float32).reshape(-1, 2)
            pts[:, 0] *= sx
            pts[:, 1] *= sy
            segs.append(pts.reshape(-1).tolist())
        anno["segmentation"] = segs
        new_annos.append(anno)
    return image, new_annos


def _shift_annos(annos, dx, dy, canvas_w=IMGSZ, canvas_h=IMGSZ):
    shifted = []
    for anno in annos:
        anno = _ensure_bbox_mode(copy.deepcopy(anno))
        bbox = list(anno["bbox"])
        x1, y1, bw, bh = bbox[0] + dx, bbox[1] + dy, bbox[2], bbox[3]
        x1 = float(np.clip(x1, 0, canvas_w))
        y1 = float(np.clip(y1, 0, canvas_h))
        bw = float(min(bw, canvas_w - x1))
        bh = float(min(bh, canvas_h - y1))
        if bw < 1 or bh < 1:
            continue
        anno["bbox"] = [x1, y1, bw, bh]
        segs = []
        for poly in anno.get("segmentation", []):
            pts = np.asarray(poly, dtype=np.float32).reshape(-1, 2)
            pts[:, 0] = np.clip(pts[:, 0] + dx, 0, canvas_w)
            pts[:, 1] = np.clip(pts[:, 1] + dy, 0, canvas_h)
            if pts.shape[0] < 3:
                continue
            segs.append(pts.reshape(-1).tolist())
        if not segs:
            continue
        anno["segmentation"] = segs
        shifted.append(anno)
    return shifted


class V2DatasetMapper:
    """YOLO-v2-like augs: HSV, flip, small rotate/translate/scale, mosaic p=0.4."""

    def __init__(self, cfg, dataset_dicts, mosaic_prob: MosaicProb, is_train: bool = True):
        self.is_train = is_train
        self.dataset_dicts = dataset_dicts
        self.mosaic_prob = mosaic_prob
        self.img_format = cfg.INPUT.FORMAT
        self.tfm = [
            T.RandomFlip(prob=FLIP_P, horizontal=True, vertical=False),
            T.RandomRotation(angle=[-DEGREES, DEGREES], sample_style="range", expand=False),
            T.RandomExtent(
                scale_range=(1.0 - SCALE, 1.0 + SCALE),
                shift_range=(TRANSLATE, TRANSLATE),
            ),
            T.ResizeShortestEdge(
                short_edge_length=cfg.INPUT.MIN_SIZE_TRAIN,
                max_size=cfg.INPUT.MAX_SIZE_TRAIN,
                sample_style="choice",
            ),
        ]
        self.test_tfm = [
            T.ResizeShortestEdge(cfg.INPUT.MIN_SIZE_TEST, cfg.INPUT.MAX_SIZE_TEST, "choice")
        ]

    def _load(self, dataset_dict):
        dataset_dict = copy.deepcopy(dataset_dict)
        image = utils.read_image(dataset_dict["file_name"], format=self.img_format)
        return dataset_dict, image

    def _mosaic(self, dataset_dict):
        others = random.sample(self.dataset_dicts, k=min(3, len(self.dataset_dicts)))
        tiles = [dataset_dict] + others
        half = IMGSZ // 2
        canvas = np.zeros((IMGSZ, IMGSZ, 3), dtype=np.uint8)
        merged = []
        offsets = [(0, 0), (half, 0), (0, half), (half, half)]
        for rec, (dx, dy) in zip(tiles, offsets):
            rec, image = self._load(rec)
            image, annos = _resize_record(image, rec.get("annotations", []), half, half)
            canvas[dy : dy + half, dx : dx + half] = image
            merged.extend(_shift_annos(annos, dx, dy))
        out = copy.deepcopy(dataset_dict)
        out["width"] = IMGSZ
        out["height"] = IMGSZ
        out["annotations"] = merged
        return out, canvas

    def __call__(self, dataset_dict):
        if (
            self.is_train
            and random.random() < self.mosaic_prob.value
            and len(self.dataset_dicts) >= 4
        ):
            dataset_dict, image = self._mosaic(dataset_dict)
        else:
            dataset_dict, image = self._load(dataset_dict)
        if self.is_train:
            image = _hsv_jitter(image)
            tfms = self.tfm
        else:
            tfms = self.test_tfm
        aug_input = T.AugInput(image)
        transforms = T.AugmentationList(tfms)(aug_input)
        image = aug_input.image
        image_shape = image.shape[:2]
        dataset_dict["image"] = torch.as_tensor(np.ascontiguousarray(image.transpose(2, 0, 1)))
        if not self.is_train:
            dataset_dict.pop("annotations", None)
            return dataset_dict
        annos = [
            utils.transform_instance_annotations(obj, transforms, image_shape)
            for obj in dataset_dict.pop("annotations", [])
            if obj.get("iscrowd", 0) == 0
        ]
        instances = utils.annotations_to_instances(annos, image_shape, mask_format="polygon")
        dataset_dict["instances"] = utils.filter_empty_instances(instances)
        return dataset_dict


class ClsGainWrapper(torch.nn.Module):
    """Scale Detectron2 loss_cls to match YOLO cls=0.4 without breaking AMP/checkpointer."""

    def __init__(self, model, gain: float = CLS_GAIN):
        super().__init__()
        self.model = model
        self.gain = gain

    def forward(self, batched_inputs):
        out = self.model(batched_inputs)
        if self.training and isinstance(out, dict) and "loss_cls" in out:
            out = dict(out)
            out["loss_cls"] = out["loss_cls"] * self.gain
        return out


class CloseMosaicHook(HookBase):
    def __init__(self, close_after_iter: int, mosaic_prob: MosaicProb):
        self.close_after_iter = close_after_iter
        self.mosaic_prob = mosaic_prob

    def after_step(self):
        if self.trainer.iter + 1 >= self.close_after_iter and self.mosaic_prob.value != 0.0:
            self.mosaic_prob.value = 0.0
            print(f"close_mosaic: mosaic off at iter {self.trainer.iter + 1}")


class EarlyStopHook(HookBase):
    """YOLO-style patience on val mask AP50 (one eval = one epoch)."""

    def __init__(self, patience: int = PATIENCE, metric: str = "segm/AP50"):
        self.patience = patience
        self.metric = metric
        self.best = None
        self.bad = 0

    def after_step(self):
        period = self.trainer.cfg.TEST.EVAL_PERIOD
        next_iter = self.trainer.iter + 1
        if period <= 0 or next_iter % period != 0:
            return
        metric_tuple = self.trainer.storage.latest().get(self.metric)
        if metric_tuple is None:
            return
        val = float(metric_tuple[0])
        if self.best is None or val > self.best:
            self.best = val
            self.bad = 0
        else:
            self.bad += 1
            print(
                f"patience: {self.bad}/{self.patience} without {self.metric} improve "
                f"(best={self.best:.3f}, now={val:.3f})"
            )
            if self.bad >= self.patience:
                print(f"Early stop at iter {next_iter} (patience={self.patience})")
                self.trainer._should_stop = True


class EpochMetricPrinter(CommonMetricPrinter):
    """Detectron2 is iter-based; print the matching YOLO-style epoch next to iter."""

    def __init__(self, max_iter, iters_per_epoch: int, epochs: int = EPOCHS):
        super().__init__(max_iter)
        self._ipe = max(int(iters_per_epoch), 1)
        self._epochs = epochs

    def write(self):
        storage = get_event_storage()
        epoch = min(self._epochs, storage.iter // self._ipe + 1)
        orig = self.logger.info

        def info(msg, *args, **kwargs):
            if isinstance(msg, str) and "iter:" in msg:
                msg = f" epoch: {epoch}/{self._epochs} " + msg
            orig(msg, *args, **kwargs)

        self.logger.info = info
        try:
            super().write()
        finally:
            self.logger.info = orig


class MLflowHook(HookBase):
    def __init__(self, period: int = 20):
        self.period = period
        try:
            import mlflow

            self.mlflow = mlflow
        except ImportError:
            self.mlflow = None

    def after_step(self):
        if self.mlflow is None or self.mlflow.active_run() is None:
            return
        if (self.trainer.iter + 1) % self.period != 0:
            return
        storage = get_event_storage()
        metrics = {}
        for k, v in storage.latest_with_smoothing_hint(self.period).items():
            if isinstance(v, tuple):
                v = v[0]
            try:
                metrics[k.replace("/", "_")] = float(v)
            except (TypeError, ValueError):
                continue
        ipe = getattr(self.trainer, "_iters_per_epoch", None)
        if ipe:
            metrics["epoch"] = float((self.trainer.iter // ipe) + 1)
        if metrics:
            self.mlflow.log_metrics(metrics, step=self.trainer.iter)


class ObjectTrainer(DefaultTrainer):
    def __init__(self, cfg, dataset_dicts, iters_per_epoch: int):
        self._dataset_dicts = dataset_dicts
        self._iters_per_epoch = iters_per_epoch
        self._mosaic_prob = MosaicProb(MOSAIC_P)
        self._should_stop = False
        super().__init__(cfg)
        # Wrap after DefaultTrainer binds the checkpointer to the raw model.
        self._trainer.model = ClsGainWrapper(self._trainer.model, CLS_GAIN)

    @classmethod
    def build_evaluator(cls, cfg, dataset_name, output_folder=None):
        if output_folder is None:
            output_folder = Path(cfg.OUTPUT_DIR) / "eval"
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        return COCOEvaluator(dataset_name, output_dir=str(output_folder))

    def build_hooks(self):
        hooks = super().build_hooks()
        close_at = self._iters_per_epoch * (EPOCHS - CLOSE_MOSAIC)
        hooks.insert(0, CloseMosaicHook(close_at, self._mosaic_prob))
        rewritten = []
        for hook in hooks:
            if isinstance(hook, PeriodicCheckpointer):
                rewritten.append(
                    PeriodicCheckpointer(
                        self.checkpointer,
                        self.cfg.SOLVER.CHECKPOINT_PERIOD,
                        max_iter=self.cfg.SOLVER.MAX_ITER,
                        max_to_keep=3,
                    )
                )
            else:
                rewritten.append(hook)
        rewritten.append(
            BestCheckpointer(
                self.cfg.TEST.EVAL_PERIOD,
                self.checkpointer,
                val_metric="segm/AP50",
                mode="max",
                file_prefix="model_best",
            )
        )
        rewritten.append(EarlyStopHook(PATIENCE, "segm/AP50"))
        rewritten.append(MLflowHook(period=20))
        return rewritten

    def build_writers(self):
        # Same as YOLO v2 SETTINGS["tensorboard"] = False: NumPy 2 + this
        # TensorBoard/TF stack crashes on import (_ARRAY_API / notf).
        Path(self.cfg.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        return [
            EpochMetricPrinter(self.max_iter, self._iters_per_epoch, EPOCHS),
            JSONWriter(str(Path(self.cfg.OUTPUT_DIR) / "metrics.json")),
        ]

    def build_train_loader(self, cfg):
        mapper = V2DatasetMapper(cfg, self._dataset_dicts, self._mosaic_prob, is_train=True)
        return build_detection_train_loader(cfg, mapper=mapper)

    def train(self):
        """Same Detectron2 loop, plus YOLO-style patience."""
        start_iter = self.start_iter
        max_iter = self.max_iter
        logger = logging.getLogger("detectron2")
        logger.info("Starting training from iteration {}".format(start_iter))
        self.iter = self.start_iter = start_iter
        self.max_iter = max_iter
        self._should_stop = False
        with EventStorage(start_iter) as self.storage:
            try:
                self.before_train()
                for self.iter in range(start_iter, max_iter):
                    self.before_step()
                    self.run_step()
                    self.after_step()
                    if self._should_stop:
                        logger.info("Stopped early (patience=%s)", PATIENCE)
                        break
                self.iter += 1
            except Exception:
                logger.exception("Exception during training:")
                raise
            finally:
                self.after_train()
        return getattr(self, "_last_eval_results", None)


def print_recipe(cfg, iters_per_epoch: int, max_iter: int) -> None:
    print("v2 recipe (kept) vs Detectron2 mapping:")
    for key, value in RECIPE.items():
        print(f"  {key:14s} {value}")
    print()
    print(f"  iters/epoch   {iters_per_epoch}")
    print(f"  max_iter      {max_iter}  (= {iters_per_epoch} x {EPOCHS})")
    print(f"  close_mosaic  last {CLOSE_MOSAIC} epochs → iter {iters_per_epoch * (EPOCHS - CLOSE_MOSAIC)}")
    print(f"  optimizer     SGD  lr={cfg.SOLVER.BASE_LR}  cosine→{cfg.SOLVER.BASE_LR_END}")
    print(f"  AMP           {cfg.SOLVER.AMP.ENABLED}  (torch.amp.autocast('cuda'))")
    print(f"  workers       {cfg.DATALOADER.NUM_WORKERS}")
    print(f"  output        {cfg.OUTPUT_DIR}")
