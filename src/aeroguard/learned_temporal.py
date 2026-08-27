from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from aeroguard.evaluation.detection import Box
from aeroguard.scene_quality import SceneQualityAssessment, SceneQualityPolicy, assess_scene_quality
from aeroguard.tracking import TrackDetection, TemporalTracker, TrackedDetection


class DetectorProtocol(Protocol):
    def predict(self, image: np.ndarray, *, image_id: str) -> list[Box]: ...


@dataclass(frozen=True)
class LearnedFrameVerification:
    """One learned-detector frame plus its temporal verification state."""

    frame_index: int
    image_id: str
    action: str
    scene_quality: SceneQualityAssessment
    predictions: tuple[Box, ...]
    tracked: tuple[TrackedDetection, ...]

    @property
    def confirmed(self) -> tuple[TrackedDetection, ...]:
        return tuple(item for item in self.tracked if item.confirmed)

    def as_dict(self) -> dict:
        return {
            "frame_index": self.frame_index,
            "image_id": self.image_id,
            "action": self.action,
            "scene_quality": self.scene_quality.as_dict(),
            "prediction_count": len(self.predictions),
            "tracked_count": len(self.tracked),
            "confirmed_count": len(self.confirmed),
            "tracks": [
                {
                    "track_id": item.track_id,
                    "label": item.detection.label,
                    "bbox": list(item.detection.bbox),
                    "score": item.detection.score,
                    "hits": item.hits,
                    "age_frames": item.age_frames,
                    "confirmed": item.confirmed,
                    "match_iou": item.match_iou,
                }
                for item in self.tracked
            ],
        }


def boxes_to_track_detections(
    boxes: list[Box] | tuple[Box, ...],
    *,
    frame_index: int,
) -> tuple[TrackDetection, ...]:
    """Convert OpenCV detector Box outputs into tracker observations losslessly."""
    result: list[TrackDetection] = []
    for box in boxes:
        result.append(
            TrackDetection(
                frame_index=frame_index,
                label=box.label,
                bbox=(box.xmin, box.ymin, box.xmax, box.ymax),
                score=box.score,
            )
        )
    return tuple(result)


class LearnedTemporalVerifier:
    """Production glue from OpenCV DNN predictions to temporal evidence.

    Gross scene-quality failure resets track continuity and blocks detector use for
    the affected frame. Usable frames are passed to the detector, then through the
    deterministic class-aware tracker. A confirmed track is only evidence for the
    next agent step; it is not an autonomous operational alert.
    """

    def __init__(
        self,
        detector: DetectorProtocol,
        *,
        tracker: TemporalTracker | None = None,
        scene_policy: SceneQualityPolicy | None = None,
    ) -> None:
        self.detector = detector
        self.tracker = tracker or TemporalTracker()
        self.scene_policy = scene_policy or SceneQualityPolicy()

    def reset(self) -> None:
        self.tracker.reset()

    def process(
        self,
        frame: np.ndarray,
        *,
        frame_index: int,
        image_id: str,
    ) -> LearnedFrameVerification:
        quality = assess_scene_quality(frame, self.scene_policy)
        if not quality.usable:
            self.tracker.reset()
            return LearnedFrameVerification(
                frame_index=frame_index,
                image_id=image_id,
                action="reacquire",
                scene_quality=quality,
                predictions=(),
                tracked=(),
            )

        predictions = tuple(self.detector.predict(frame, image_id=image_id))
        observations = boxes_to_track_detections(predictions, frame_index=frame_index)
        tracked = self.tracker.update(frame_index, observations)
        action = "verify_confirmed" if any(item.confirmed for item in tracked) else "observe"
        return LearnedFrameVerification(
            frame_index=frame_index,
            image_id=image_id,
            action=action,
            scene_quality=quality,
            predictions=predictions,
            tracked=tracked,
        )
