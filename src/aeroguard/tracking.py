from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable


BBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class TrackDetection:
    """One detector observation in xyxy image coordinates."""

    frame_index: int
    label: str
    bbox: BBox
    score: float = 1.0

    def validate(self) -> None:
        x1, y1, x2, y2 = self.bbox
        if self.frame_index < 0:
            raise ValueError("frame_index must be non-negative")
        if not self.label:
            raise ValueError("label must not be empty")
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"invalid bbox: {self.bbox}")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be in [0, 1]")


@dataclass(frozen=True)
class TrackState:
    track_id: int
    label: str
    bbox: BBox
    first_frame: int
    last_frame: int
    hits: int
    missed_frames: int
    last_score: float

    @property
    def age_frames(self) -> int:
        return self.last_frame - self.first_frame + 1


@dataclass(frozen=True)
class TrackedDetection:
    detection: TrackDetection
    track_id: int
    hits: int
    age_frames: int
    confirmed: bool
    match_iou: float | None


def bbox_iou(a: BBox, b: BBox) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0.0 else 0.0


class TemporalTracker:
    """Small deterministic tracker for FOD verification.

    Matching is class-aware and greedy by descending IoU with deterministic tie
    breaks. The tracker deliberately avoids a learned motion model: its role is to
    provide auditable multi-frame persistence evidence around detector outputs.
    """

    def __init__(
        self,
        *,
        min_iou: float = 0.20,
        min_hits: int = 3,
        max_missed_frames: int = 1,
    ) -> None:
        if not 0.0 <= min_iou <= 1.0:
            raise ValueError("min_iou must be in [0, 1]")
        if min_hits <= 0:
            raise ValueError("min_hits must be positive")
        if max_missed_frames < 0:
            raise ValueError("max_missed_frames must be non-negative")
        self.min_iou = min_iou
        self.min_hits = min_hits
        self.max_missed_frames = max_missed_frames
        self._tracks: dict[int, TrackState] = {}
        self._next_track_id = 1
        self._last_frame_index: int | None = None

    @property
    def active_tracks(self) -> tuple[TrackState, ...]:
        return tuple(self._tracks[key] for key in sorted(self._tracks))

    def reset(self) -> None:
        self._tracks.clear()
        self._last_frame_index = None

    def update(
        self,
        frame_index: int,
        detections: Iterable[TrackDetection],
    ) -> tuple[TrackedDetection, ...]:
        if frame_index < 0:
            raise ValueError("frame_index must be non-negative")
        if self._last_frame_index is not None and frame_index <= self._last_frame_index:
            raise ValueError("frame_index must increase strictly")

        observations = list(detections)
        for detection in observations:
            detection.validate()
            if detection.frame_index != frame_index:
                raise ValueError("all detection frame_index values must equal update frame_index")

        frame_gap = 1 if self._last_frame_index is None else frame_index - self._last_frame_index
        prior_tracks = dict(self._tracks)

        candidate_pairs: list[tuple[float, int, int]] = []
        for track_id, track in prior_tracks.items():
            for det_index, detection in enumerate(observations):
                if detection.label != track.label:
                    continue
                overlap = bbox_iou(track.bbox, detection.bbox)
                if overlap >= self.min_iou:
                    candidate_pairs.append((-overlap, track_id, det_index))
        candidate_pairs.sort()

        matched_tracks: set[int] = set()
        matched_detections: set[int] = set()
        matches: dict[int, tuple[int, float]] = {}
        for neg_iou, track_id, det_index in candidate_pairs:
            if track_id in matched_tracks or det_index in matched_detections:
                continue
            matched_tracks.add(track_id)
            matched_detections.add(det_index)
            matches[det_index] = (track_id, -neg_iou)

        updated: dict[int, TrackState] = {}
        output: list[TrackedDetection] = []

        for det_index, detection in enumerate(observations):
            if det_index in matches:
                track_id, overlap = matches[det_index]
                old = prior_tracks[track_id]
                state = TrackState(
                    track_id=track_id,
                    label=old.label,
                    bbox=detection.bbox,
                    first_frame=old.first_frame,
                    last_frame=frame_index,
                    hits=old.hits + 1,
                    missed_frames=0,
                    last_score=detection.score,
                )
                updated[track_id] = state
                output.append(
                    TrackedDetection(
                        detection=detection,
                        track_id=track_id,
                        hits=state.hits,
                        age_frames=state.age_frames,
                        confirmed=state.hits >= self.min_hits,
                        match_iou=overlap,
                    )
                )
            else:
                track_id = self._next_track_id
                self._next_track_id += 1
                state = TrackState(
                    track_id=track_id,
                    label=detection.label,
                    bbox=detection.bbox,
                    first_frame=frame_index,
                    last_frame=frame_index,
                    hits=1,
                    missed_frames=0,
                    last_score=detection.score,
                )
                updated[track_id] = state
                output.append(
                    TrackedDetection(
                        detection=detection,
                        track_id=track_id,
                        hits=1,
                        age_frames=1,
                        confirmed=self.min_hits <= 1,
                        match_iou=None,
                    )
                )

        for track_id, old in prior_tracks.items():
            if track_id in matched_tracks:
                continue
            missed = old.missed_frames + frame_gap
            if missed <= self.max_missed_frames:
                updated[track_id] = replace(old, missed_frames=missed)

        self._tracks = updated
        self._last_frame_index = frame_index
        output.sort(key=lambda item: (item.detection.label, item.track_id, item.detection.bbox))
        return tuple(output)
