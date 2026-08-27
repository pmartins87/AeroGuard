import pytest

from aeroguard.tracking import TrackDetection, TemporalTracker, bbox_iou


def det(frame: int, x: float, label: str = "Bolt") -> TrackDetection:
    return TrackDetection(
        frame_index=frame,
        label=label,
        bbox=(x, 10.0, x + 20.0, 30.0),
        score=0.8,
    )


def test_bbox_iou():
    assert bbox_iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert bbox_iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    assert 0.0 < bbox_iou((0, 0, 10, 10), (5, 0, 15, 10)) < 1.0


def test_track_becomes_confirmed_after_three_consistent_observations():
    tracker = TemporalTracker(min_iou=0.2, min_hits=3, max_missed_frames=1)
    a = tracker.update(1, [det(1, 10.0)])[0]
    b = tracker.update(2, [det(2, 12.0)])[0]
    c = tracker.update(3, [det(3, 14.0)])[0]

    assert a.track_id == b.track_id == c.track_id
    assert not a.confirmed
    assert not b.confirmed
    assert c.confirmed
    assert c.hits == 3
    assert c.age_frames == 3
    assert c.match_iou is not None


def test_class_mismatch_never_reuses_track():
    tracker = TemporalTracker(min_hits=2)
    bolt = tracker.update(1, [det(1, 10.0, "Bolt")])[0]
    rock = tracker.update(2, [det(2, 10.0, "Rock")])[0]
    assert bolt.track_id != rock.track_id


def test_one_missing_frame_can_be_bridged_when_configured():
    tracker = TemporalTracker(min_iou=0.2, min_hits=2, max_missed_frames=1)
    first = tracker.update(1, [det(1, 10.0)])[0]
    assert tracker.update(2, []) == ()
    third = tracker.update(3, [det(3, 11.0)])[0]
    assert third.track_id == first.track_id
    assert third.confirmed


def test_track_expires_after_too_many_missing_frames():
    tracker = TemporalTracker(min_hits=2, max_missed_frames=1)
    first = tracker.update(1, [det(1, 10.0)])[0]
    tracker.update(2, [])
    tracker.update(3, [])
    later = tracker.update(4, [det(4, 10.0)])[0]
    assert later.track_id != first.track_id
    assert not later.confirmed


def test_update_requires_strictly_increasing_frame_index():
    tracker = TemporalTracker()
    tracker.update(5, [det(5, 10.0)])
    with pytest.raises(ValueError):
        tracker.update(5, [])


def test_scene_failure_can_reset_temporal_evidence():
    tracker = TemporalTracker(min_hits=2)
    first = tracker.update(1, [det(1, 10.0)])[0]
    tracker.reset()
    after_reset = tracker.update(2, [det(2, 10.0)])[0]
    assert after_reset.track_id != first.track_id
    assert not after_reset.confirmed
