import pytest

from aeroguard.evaluation.detection import Box, evaluate_boxes, intersection_over_union


def test_iou_identity_and_disjoint():
    a = Box("img", "fod", 0, 0, 10, 10)
    b = Box("img", "fod", 0, 0, 10, 10)
    c = Box("img", "fod", 20, 20, 30, 30)
    assert intersection_over_union(a, b) == 1.0
    assert intersection_over_union(a, c) == 0.0


def test_class_aware_one_to_one_matching():
    truth = [
        Box("a", "bolt", 0, 0, 10, 10),
        Box("a", "stone", 20, 20, 40, 40),
    ]
    predictions = [
        Box("a", "bolt", 0, 0, 10, 10, 0.9),
        Box("a", "bolt", 0, 0, 10, 10, 0.8),
        Box("a", "stone", 20, 20, 40, 40, 0.7),
    ]
    metrics = evaluate_boxes(truth, predictions)
    assert (metrics.tp, metrics.fp, metrics.fn) == (2, 1, 0)
    assert metrics.precision == pytest.approx(2 / 3)
    assert metrics.recall == 1.0
    assert metrics.f1 == pytest.approx(0.8)


def test_score_threshold_changes_operating_point():
    truth = [Box("a", "fod", 0, 0, 10, 10)]
    predictions = [
        Box("a", "fod", 0, 0, 10, 10, 0.4),
        Box("a", "fod", 50, 50, 60, 60, 0.2),
    ]
    low = evaluate_boxes(truth, predictions, score_threshold=0.0)
    high = evaluate_boxes(truth, predictions, score_threshold=0.5)
    assert (low.tp, low.fp, low.fn) == (1, 1, 0)
    assert (high.tp, high.fp, high.fn) == (0, 0, 1)


def test_invalid_iou_threshold_rejected():
    with pytest.raises(ValueError):
        evaluate_boxes([], [], iou_threshold=0.0)
