from __future__ import annotations

from dataclasses import replace

import cv2
import numpy as np

from .types import Candidate


def build_reference(frames: list[np.ndarray]) -> np.ndarray:
    """Build a deterministic background reference from clean frames."""
    if not frames:
        raise ValueError("at least one reference frame is required")
    stack = np.stack(frames, axis=0)
    return np.median(stack, axis=0).astype(np.uint8)


def _to_gray(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        return frame
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def detect_candidates(
    frame: np.ndarray,
    reference: np.ndarray,
    frame_index: int,
    *,
    threshold: int = 28,
    min_area: int = 18,
    max_area: int = 5000,
) -> list[Candidate]:
    """Detect scene changes using OpenCV primitives.

    R1 baseline: absdiff -> blur -> threshold -> morphology -> connected components.
    """
    if frame.shape != reference.shape:
        raise ValueError("frame and reference must have the same shape")

    gray = _to_gray(frame)
    ref_gray = _to_gray(reference)
    diff = cv2.absdiff(gray, ref_gray)
    diff = cv2.GaussianBlur(diff, (5, 5), 0)
    _, mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    n, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    out: list[Candidate] = []
    for label in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[label])
        if area < min_area or area > max_area:
            continue
        roi = diff[y : y + h, x : x + w]
        contrast = float(np.mean(roi)) if roi.size else 0.0
        out.append(
            Candidate(
                frame_index=frame_index,
                x=x,
                y=y,
                w=w,
                h=h,
                area=area,
                contrast=contrast,
            )
        )
    return sorted(out, key=lambda c: (c.y, c.x, -c.area))


def iou(a: Candidate, b: Candidate) -> float:
    ax1, ay1, aw, ah = a.bbox
    bx1, by1, bw, bh = b.bbox
    ax2, ay2 = ax1 + aw, ay1 + ah
    bx2, by2 = bx1 + bw, by1 + bh
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    union = aw * ah + bw * bh - inter
    return inter / union if union else 0.0


def attach_persistence(
    candidate: Candidate,
    historical: list[list[Candidate]],
    *,
    min_iou: float = 0.25,
) -> Candidate:
    persistence = 1
    for prior_frame in reversed(historical):
        if any(iou(candidate, prior) >= min_iou for prior in prior_frame):
            persistence += 1
        else:
            break
    return replace(candidate, persistence=persistence)


def crop_with_margin(frame: np.ndarray, candidate: Candidate, margin: int = 12) -> np.ndarray:
    h, w = frame.shape[:2]
    x1 = max(0, candidate.x - margin)
    y1 = max(0, candidate.y - margin)
    x2 = min(w, candidate.x + candidate.w + margin)
    y2 = min(h, candidate.y + candidate.h + margin)
    return frame[y1:y2, x1:x2]
