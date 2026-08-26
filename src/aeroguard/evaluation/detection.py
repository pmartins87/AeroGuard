from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Box:
    image_id: str
    label: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    score: float = 1.0

    @property
    def area(self) -> float:
        return max(0.0, self.xmax - self.xmin) * max(0.0, self.ymax - self.ymin)


@dataclass(frozen=True)
class DetectionMetrics:
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


def intersection_over_union(a: Box, b: Box) -> float:
    ix1 = max(a.xmin, b.xmin)
    iy1 = max(a.ymin, b.ymin)
    ix2 = min(a.xmax, b.xmax)
    iy2 = min(a.ymax, b.ymax)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    intersection = iw * ih
    union = a.area + b.area - intersection
    return intersection / union if union > 0.0 else 0.0


def evaluate_boxes(
    ground_truth: Iterable[Box],
    predictions: Iterable[Box],
    *,
    iou_threshold: float = 0.5,
    score_threshold: float = 0.0,
) -> DetectionMetrics:
    """Greedy class-aware one-to-one matching for a frozen IoU/score operating point.

    This is intentionally simple and deterministic. mAP/AP curves can be layered on later,
    while this function provides the operating-point precision/recall/F1 used by the
    AeroGuard verification pipeline and failure-case reports.
    """
    if not (0.0 < iou_threshold <= 1.0):
        raise ValueError("iou_threshold must be in (0, 1]")

    truth = list(ground_truth)
    preds = [p for p in predictions if p.score >= score_threshold]
    preds.sort(key=lambda p: (-p.score, p.image_id, p.label, p.xmin, p.ymin))

    matched_truth: set[int] = set()
    tp = 0
    fp = 0

    for pred in preds:
        best_index: int | None = None
        best_iou = -1.0
        for index, gt in enumerate(truth):
            if index in matched_truth:
                continue
            if pred.image_id != gt.image_id or pred.label != gt.label:
                continue
            iou = intersection_over_union(pred, gt)
            if iou >= iou_threshold and iou > best_iou:
                best_iou = iou
                best_index = index

        if best_index is None:
            fp += 1
        else:
            matched_truth.add(best_index)
            tp += 1

    fn = len(truth) - len(matched_truth)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    return DetectionMetrics(tp=tp, fp=fp, fn=fn, precision=precision, recall=recall, f1=f1)
