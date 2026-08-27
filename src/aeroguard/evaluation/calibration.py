from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .detection import Box, DetectionMetrics, evaluate_boxes


@dataclass(frozen=True)
class OperatingPoint:
    score_threshold: float
    metrics: DetectionMetrics
    f_beta: float

    def as_dict(self) -> dict:
        return {
            "score_threshold": self.score_threshold,
            **self.metrics.as_dict(),
            "f_beta": self.f_beta,
        }


def f_beta_score(precision: float, recall: float, *, beta: float = 2.0) -> float:
    if beta <= 0.0:
        raise ValueError("beta must be positive")
    if precision < 0.0 or recall < 0.0:
        raise ValueError("precision and recall must be non-negative")
    beta2 = beta * beta
    denominator = beta2 * precision + recall
    return (1.0 + beta2) * precision * recall / denominator if denominator else 0.0


def threshold_sweep(
    ground_truth: Iterable[Box],
    predictions: Iterable[Box],
    thresholds: Sequence[float],
    *,
    iou_threshold: float = 0.5,
    beta: float = 2.0,
) -> tuple[OperatingPoint, ...]:
    """Evaluate frozen score thresholds without touching the held-out test set."""
    truth = list(ground_truth)
    preds = list(predictions)
    clean_thresholds = sorted({float(value) for value in thresholds})
    if not clean_thresholds:
        raise ValueError("at least one score threshold is required")
    if any(value < 0.0 or value > 1.0 for value in clean_thresholds):
        raise ValueError("score thresholds must be in [0, 1]")

    points: list[OperatingPoint] = []
    for score_threshold in clean_thresholds:
        metrics = evaluate_boxes(
            truth,
            preds,
            iou_threshold=iou_threshold,
            score_threshold=score_threshold,
        )
        points.append(
            OperatingPoint(
                score_threshold=score_threshold,
                metrics=metrics,
                f_beta=f_beta_score(metrics.precision, metrics.recall, beta=beta),
            )
        )
    return tuple(points)


def select_recall_weighted_operating_point(
    points: Iterable[OperatingPoint],
) -> OperatingPoint:
    """Select max-F2 style point with deterministic, review-burden-aware ties.

    The caller decides beta during the sweep. Primary ordering is f_beta, then
    recall, precision, and finally the higher threshold to reduce alert burden
    when all measured quality terms are equal.
    """
    values = list(points)
    if not values:
        raise ValueError("at least one operating point is required")
    return max(
        values,
        key=lambda point: (
            point.f_beta,
            point.metrics.recall,
            point.metrics.precision,
            point.score_threshold,
        ),
    )
