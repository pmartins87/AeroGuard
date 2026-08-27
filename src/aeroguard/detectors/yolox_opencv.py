from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

from aeroguard.evaluation.detection import Box


@dataclass(frozen=True)
class LetterboxMeta:
    original_width: int
    original_height: int
    input_width: int
    input_height: int
    resized_width: int
    resized_height: int
    scale: float


@dataclass(frozen=True)
class YOLOXConfig:
    input_width: int = 640
    input_height: int = 640
    confidence_threshold: float = 0.25
    nms_threshold: float = 0.45
    pad_value: int = 114

    def validate(self) -> None:
        if self.input_width <= 0 or self.input_height <= 0:
            raise ValueError("input dimensions must be positive")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be in [0, 1]")
        if not 0.0 <= self.nms_threshold <= 1.0:
            raise ValueError("nms_threshold must be in [0, 1]")
        if not 0 <= self.pad_value <= 255:
            raise ValueError("pad_value must be in [0, 255]")


def letterbox_top_left(
    image: np.ndarray,
    *,
    input_width: int,
    input_height: int,
    pad_value: int = 114,
) -> tuple[np.ndarray, LetterboxMeta]:
    """Apply the top-left YOLOX letterbox used by the official preprocessing path.

    The source image keeps aspect ratio, is placed at the top-left of a constant
    canvas, and is padded only on the right/bottom. This behavior must match the
    training/export preprocessing contract used for the ONNX model.
    """
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must be an HxWx3 array")
    if input_width <= 0 or input_height <= 0:
        raise ValueError("input dimensions must be positive")

    original_height, original_width = image.shape[:2]
    if original_width <= 0 or original_height <= 0:
        raise ValueError("image dimensions must be positive")

    scale = min(input_width / original_width, input_height / original_height)
    resized_width = max(1, min(input_width, int(original_width * scale)))
    resized_height = max(1, min(input_height, int(original_height * scale)))

    resized = cv2.resize(image, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((input_height, input_width, 3), pad_value, dtype=np.uint8)
    canvas[:resized_height, :resized_width] = resized
    meta = LetterboxMeta(
        original_width=original_width,
        original_height=original_height,
        input_width=input_width,
        input_height=input_height,
        resized_width=resized_width,
        resized_height=resized_height,
        scale=scale,
    )
    return canvas, meta


def make_yolox_blob(image: np.ndarray, config: YOLOXConfig) -> tuple[np.ndarray, LetterboxMeta]:
    """Return an OpenCV DNN blob matching the standard YOLOX BGR/no-scale input contract."""
    config.validate()
    padded, meta = letterbox_top_left(
        image,
        input_width=config.input_width,
        input_height=config.input_height,
        pad_value=config.pad_value,
    )
    blob = cv2.dnn.blobFromImage(
        padded,
        scalefactor=1.0,
        size=(config.input_width, config.input_height),
        mean=(0.0, 0.0, 0.0),
        swapRB=False,
        crop=False,
        ddepth=cv2.CV_32F,
    )
    return blob, meta


def _rows_from_output(output: np.ndarray, class_count: int) -> np.ndarray:
    values = np.asarray(output, dtype=np.float32)
    values = np.squeeze(values)
    expected_columns = 5 + class_count

    if values.ndim == 1:
        values = values.reshape(1, -1)
    if values.ndim != 2:
        raise ValueError(f"unexpected YOLOX output shape after squeeze: {values.shape}")

    if values.shape[1] == expected_columns:
        return values
    if values.shape[0] == expected_columns:
        return values.T
    raise ValueError(
        f"YOLOX output does not match {class_count} classes: "
        f"shape={values.shape}, expected one dimension={expected_columns}"
    )


def _class_aware_nms(
    boxes_xywh: Sequence[list[float]],
    scores: Sequence[float],
    class_ids: Sequence[int],
    *,
    score_threshold: float,
    nms_threshold: float,
) -> list[int]:
    kept: list[int] = []
    for class_id in sorted(set(class_ids)):
        members = [index for index, value in enumerate(class_ids) if value == class_id]
        class_boxes = [boxes_xywh[index] for index in members]
        class_scores = [float(scores[index]) for index in members]
        if not class_boxes:
            continue
        indices = cv2.dnn.NMSBoxes(
            class_boxes,
            class_scores,
            score_threshold,
            nms_threshold,
        )
        if len(indices) == 0:
            continue
        for relative_index in np.asarray(indices).reshape(-1).tolist():
            kept.append(members[int(relative_index)])
    return sorted(kept, key=lambda index: (-scores[index], class_ids[index], index))


def decode_yolox_output(
    output: np.ndarray,
    labels: Sequence[str],
    meta: LetterboxMeta,
    *,
    image_id: str,
    confidence_threshold: float = 0.25,
    nms_threshold: float = 0.45,
) -> list[Box]:
    """Decode a YOLOX ONNX output exported with ``--decode_in_inference``.

    Expected rows are ``cx, cy, w, h, objectness, class probabilities...`` in
    letterboxed input coordinates. Final scores use objectness * class score.
    NMS is class-aware and output boxes are mapped back to original-image pixels.
    """
    if not labels:
        raise ValueError("labels cannot be empty")
    if meta.scale <= 0.0:
        raise ValueError("letterbox scale must be positive")
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("confidence_threshold must be in [0, 1]")
    if not 0.0 <= nms_threshold <= 1.0:
        raise ValueError("nms_threshold must be in [0, 1]")

    rows = _rows_from_output(output, len(labels))
    raw_boxes: list[list[float]] = []
    raw_scores: list[float] = []
    raw_classes: list[int] = []

    for row in rows:
        objectness = float(row[4])
        class_scores = row[5:]
        class_id = int(np.argmax(class_scores))
        score = objectness * float(class_scores[class_id])
        if score < confidence_threshold:
            continue

        cx, cy, width, height = (float(value) for value in row[:4])
        if width <= 0.0 or height <= 0.0:
            continue
        xmin = cx - width / 2.0
        ymin = cy - height / 2.0
        raw_boxes.append([xmin, ymin, width, height])
        raw_scores.append(score)
        raw_classes.append(class_id)

    if not raw_boxes:
        return []

    kept = _class_aware_nms(
        raw_boxes,
        raw_scores,
        raw_classes,
        score_threshold=confidence_threshold,
        nms_threshold=nms_threshold,
    )

    detections: list[Box] = []
    for index in kept:
        xmin, ymin, width, height = raw_boxes[index]
        xmax = xmin + width
        ymax = ymin + height

        # Official YOLOX preprocessing is top-left aligned, so no x/y padding
        # offset is subtracted before undoing scale.
        xmin = max(0.0, min(float(meta.original_width), xmin / meta.scale))
        ymin = max(0.0, min(float(meta.original_height), ymin / meta.scale))
        xmax = max(0.0, min(float(meta.original_width), xmax / meta.scale))
        ymax = max(0.0, min(float(meta.original_height), ymax / meta.scale))
        if xmax <= xmin or ymax <= ymin:
            continue

        detections.append(
            Box(
                image_id=image_id,
                label=str(labels[raw_classes[index]]),
                xmin=xmin,
                ymin=ymin,
                xmax=xmax,
                ymax=ymax,
                score=float(raw_scores[index]),
            )
        )
    return detections


class OpenCVYOLOXDetector:
    """ONNX YOLOX detector whose production inference path is OpenCV DNN."""

    def __init__(
        self,
        model_path: str | Path,
        labels: Sequence[str],
        *,
        config: YOLOXConfig | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        if not self.model_path.is_file():
            raise FileNotFoundError(self.model_path)
        self.labels = tuple(labels)
        if not self.labels:
            raise ValueError("labels cannot be empty")
        self.config = config or YOLOXConfig()
        self.config.validate()
        self.net = cv2.dnn.readNetFromONNX(str(self.model_path))
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def predict(self, image: np.ndarray, *, image_id: str) -> list[Box]:
        blob, meta = make_yolox_blob(image, self.config)
        self.net.setInput(blob)
        output = self.net.forward()
        return decode_yolox_output(
            output,
            self.labels,
            meta,
            image_id=image_id,
            confidence_threshold=self.config.confidence_threshold,
            nms_threshold=self.config.nms_threshold,
        )
