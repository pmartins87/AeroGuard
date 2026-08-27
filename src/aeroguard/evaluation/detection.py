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


@dataclass(frozen=True)
class DetectionMatch:
    truth_index: int
    prediction_index: int
    iou: float


@dataclass(frozen=True)
class DetectionMatchResult:
    matches: tuple[DetectionMatch, ...]
    false_positive_prediction_indices: tuple[int, ...]
    false_negative_truth_indices: tuple[int, ...]

    @property
    def matched_truth_indices(self) -> frozenset[int]:
        return frozenset(match.truth_index for match in self.matches)

    @property
    def matched_prediction_indices(self) -> frozenset[int]:
        return frozenset(match.prediction_index for match in self.matches)


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


def greedy_match_boxes(
    ground_truth: Iterable[Box],
    predictions: Iterable[Box],
    *,
    iou_threshold: float = 0.5,
    score_threshold: float = 0.0,
) -> DetectionMatchResult:
    """Return deterministic class-aware one-to-one matches at one operating point.

    Prediction indices and truth indices refer to the original iterable order after it
    is materialized as a list. Predictions below ``score_threshold`` are ignored rather
    than counted as false positives. This helper is the single matching implementation
    used by both aggregate metrics and failure/slice analysis.
    """
    if not (0.0 < iou_threshold <= 1.0):
        raise ValueError("iou_threshold must be in (0, 1]")
    if not (0.0 <= score_threshold <= 1.0):
        raise ValueError("score_threshold must be in [0, 1]")

    truth = list(ground_truth)
    prediction_list = list(predictions)
    ranked = [
        (index, prediction)
        for index, prediction in enumerate(prediction_list)
        if prediction.score >= score_threshold
    ]
    ranked.sort(
        key=lambda item: (
            -item[1].score,
            item[1].image_id,
            item[1].label,
            item[1].xmin,
            item[1].ymin,
            item[0],
        )
    )

    matched_truth: set[int] = set()
    matches: list[DetectionMatch] = []
    false_positive_indices: list[int] = []

    for prediction_index, pred in ranked:
        best_index: int | None = None
        best_iou = -1.0
        for truth_index, gt in enumerate(truth):
            if truth_index in matched_truth:
                continue
            if pred.image_id != gt.image_id or pred.label != gt.label:
                continue
            iou = intersection_over_union(pred, gt)
            if iou >= iou_threshold and iou > best_iou:
                best_iou = iou
                best_index = truth_index

        if best_index is None:
            false_positive_indices.append(prediction_index)
        else:
            matched_truth.add(best_index)
            matches.append(
                DetectionMatch(
                    truth_index=best_index,
                    prediction_index=prediction_index,
                    iou=best_iou,
                )
            )

    false_negative_indices = tuple(
        index for index in range(len(truth)) if index not in matched_truth
    )
    return DetectionMatchResult(
        matches=tuple(matches),
        false_positive_prediction_indices=tuple(false_positive_indices),
        false_negative_truth_indices=false_negative_indices,
    )


def evaluate_boxes(
    ground_truth: Iterable[Box],
    predictions: Iterable[Box],
    *,
    iou_threshold: float = 0.5,
    score_threshold: float = 0.0,
) -> DetectionMetrics:
    """Class-aware precision/recall/F1 at a frozen IoU/score operating point.

    mAP/AP curves are reported separately; this function deliberately measures one
    interpretable operating point used by AeroGuard's verification pipeline and
    failure-case reports.
    """
    truth = list(ground_truth)
    prediction_list = list(predictions)
    result = greedy_match_boxes(
        truth,
        prediction_list,
        iou_threshold=iou_threshold,
        score_threshold=score_threshold,
    )

    tp = len(result.matches)
    fp = len(result.false_positive_prediction_indices)
    fn = len(result.false_negative_truth_indices)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    return DetectionMetrics(tp=tp, fp=fp, fn=fn, precision=precision, recall=recall, f1=f1)
