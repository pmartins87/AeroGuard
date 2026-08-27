import pytest

from aeroguard.evaluation.calibration import (
    f_beta_score,
    select_recall_weighted_operating_point,
    threshold_sweep,
)
from aeroguard.evaluation.detection import Box


def box(image: str, score: float = 1.0, *, offset: float = 0.0) -> Box:
    return Box(
        image_id=image,
        label="Bolt",
        xmin=offset,
        ymin=0.0,
        xmax=offset + 10.0,
        ymax=10.0,
        score=score,
    )


def test_f2_values_recall_more_than_precision():
    high_recall = f_beta_score(0.5, 1.0, beta=2.0)
    high_precision = f_beta_score(1.0, 0.5, beta=2.0)
    assert high_recall > high_precision


def test_threshold_sweep_and_selection_are_deterministic():
    truth = [box("a"), box("b")]
    predictions = [
        box("a", 0.90),
        box("b", 0.40),
        box("noise", 0.45),
    ]
    points = threshold_sweep(truth, predictions, [0.3, 0.5, 0.8], beta=2.0)
    assert [point.score_threshold for point in points] == [0.3, 0.5, 0.8]
    assert points[0].metrics.recall == 1.0
    assert points[1].metrics.recall == 0.5

    selected = select_recall_weighted_operating_point(points)
    assert selected.score_threshold == 0.3
    assert selected.metrics.tp == 2
    assert selected.metrics.fp == 1
    assert selected.metrics.fn == 0


def test_selection_prefers_higher_threshold_when_quality_is_identical():
    truth = [box("a")]
    predictions = [box("a", 0.9)]
    points = threshold_sweep(truth, predictions, [0.1, 0.5, 0.8])
    selected = select_recall_weighted_operating_point(points)
    assert selected.score_threshold == 0.8


def test_invalid_threshold_sweep_fails_closed():
    with pytest.raises(ValueError):
        threshold_sweep([], [], [])
    with pytest.raises(ValueError):
        threshold_sweep([], [], [-0.1])
