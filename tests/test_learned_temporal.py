import numpy as np

from aeroguard.evaluation.detection import Box
from aeroguard.learned_temporal import LearnedTemporalVerifier, boxes_to_track_detections
from aeroguard.tracking import TemporalTracker


class FakeDetector:
    def __init__(self, predictions_by_id: dict[str, list[Box]]) -> None:
        self.predictions_by_id = predictions_by_id
        self.calls: list[str] = []

    def predict(self, image: np.ndarray, *, image_id: str) -> list[Box]:
        self.calls.append(image_id)
        return list(self.predictions_by_id.get(image_id, []))


def textured_frame(seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    gray = rng.normal(128, 30, size=(96, 96)).clip(0, 255).astype(np.uint8)
    return np.dstack([gray, gray, gray])


def box(image_id: str, x: float) -> Box:
    return Box(
        image_id=image_id,
        label="Bolt",
        xmin=x,
        ymin=10.0,
        xmax=x + 20.0,
        ymax=30.0,
        score=0.8,
    )


def test_box_adapter_preserves_detector_geometry_and_score():
    source = box("f1", 12.0)
    converted = boxes_to_track_detections([source], frame_index=7)[0]
    assert converted.frame_index == 7
    assert converted.label == "Bolt"
    assert converted.bbox == (12.0, 10.0, 32.0, 30.0)
    assert converted.score == 0.8


def test_three_consistent_learned_predictions_become_confirmed():
    detector = FakeDetector({
        "f1": [box("f1", 10.0)],
        "f2": [box("f2", 11.0)],
        "f3": [box("f3", 12.0)],
    })
    verifier = LearnedTemporalVerifier(
        detector,
        tracker=TemporalTracker(min_iou=0.2, min_hits=3, max_missed_frames=1),
    )

    a = verifier.process(textured_frame(1), frame_index=1, image_id="f1")
    b = verifier.process(textured_frame(2), frame_index=2, image_id="f2")
    c = verifier.process(textured_frame(3), frame_index=3, image_id="f3")

    assert a.action == "observe"
    assert b.action == "observe"
    assert c.action == "verify_confirmed"
    assert c.confirmed[0].hits == 3
    assert detector.calls == ["f1", "f2", "f3"]


def test_scene_failure_blocks_detector_and_resets_track_continuity():
    detector = FakeDetector({
        "f1": [box("f1", 10.0)],
        "f3": [box("f3", 10.0)],
    })
    verifier = LearnedTemporalVerifier(
        detector,
        tracker=TemporalTracker(min_iou=0.2, min_hits=2, max_missed_frames=1),
    )

    first = verifier.process(textured_frame(1), frame_index=1, image_id="f1")
    bad = verifier.process(np.zeros((96, 96, 3), dtype=np.uint8), frame_index=2, image_id="bad")
    third = verifier.process(textured_frame(3), frame_index=3, image_id="f3")

    assert first.tracked[0].hits == 1
    assert bad.action == "reacquire"
    assert bad.predictions == ()
    assert third.tracked[0].hits == 1
    assert not third.confirmed
    assert detector.calls == ["f1", "f3"]


def test_no_predictions_remains_observe_not_alert():
    detector = FakeDetector({})
    verifier = LearnedTemporalVerifier(detector)
    result = verifier.process(textured_frame(8), frame_index=8, image_id="empty")
    assert result.action == "observe"
    assert result.tracked == ()
    assert result.confirmed == ()
