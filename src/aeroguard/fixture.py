from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def generate_fixture(path: str | Path, *, width: int = 640, height: int = 360, fps: int = 20) -> Path:
    """Generate a deterministic runway-like clip with one persistent FOD object."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"failed to open video writer for {path}")

    rng = np.random.default_rng(20260826)
    for i in range(90):
        frame = np.full((height, width, 3), 104, dtype=np.uint8)
        noise = rng.normal(0, 2.0, size=(height, width, 1)).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        cv2.line(frame, (width // 2, 0), (width // 2, height), (210, 210, 210), 5)
        cv2.line(frame, (width // 2 - 90, 0), (width // 2 - 90, height), (130, 130, 130), 2)
        cv2.line(frame, (width // 2 + 90, 0), (width // 2 + 90, height), (130, 130, 130), 2)
        if 35 <= i <= 70:
            cv2.rectangle(frame, (408, 238), (429, 252), (25, 25, 25), -1)
        writer.write(frame)
    writer.release()
    return path
