from pathlib import Path

import cv2
import numpy as np

from aeroguard.cli import analyze_video


def _write_flat_video(path: Path, *, value: int, frames: int = 30) -> None:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        20.0,
        (96, 64),
    )
    assert writer.isOpened()
    frame = np.full((64, 96, 3), value, dtype=np.uint8)
    for _ in range(frames):
        writer.write(frame)
    writer.release()


def test_unusable_frames_are_reacquired_and_do_not_create_events(tmp_path):
    video = tmp_path / "dark.mp4"
    output = tmp_path / "events.json"
    _write_flat_video(video, value=0)

    payload = analyze_video(video, output, output_video=None, evidence_dir=None)

    assert payload["events"] == []
    assert len(payload["scene_quality_failures"]) == 10
    assert all(item["action"] == "reacquire" for item in payload["scene_quality_failures"])
    assert all(not item["usable"] for item in payload["scene_quality_failures"])
    assert all("extreme_darkness" in item["reasons"] for item in payload["scene_quality_failures"])
