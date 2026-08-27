from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class SceneQualityMetrics:
    """Deterministic image-quality measurements used as safety guardrail evidence.

    These are measurements, not semantic FOD confidence. Thresholds are calibrated
    separately from real-data profiles so the safety policy is evidence based.
    """

    mean_luma: float
    p05_luma: float
    p95_luma: float
    dynamic_range: float
    laplacian_variance: float
    dark_fraction: float
    clipped_high_fraction: float
    entropy_bits: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def _gray(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        gray = frame
    elif frame.ndim == 3 and frame.shape[2] in {3, 4}:
        code = cv2.COLOR_BGRA2GRAY if frame.shape[2] == 4 else cv2.COLOR_BGR2GRAY
        gray = cv2.cvtColor(frame, code)
    else:
        raise ValueError(f"unsupported frame shape: {frame.shape}")
    if gray.dtype != np.uint8:
        gray = np.clip(gray, 0, 255).astype(np.uint8)
    return gray


def measure_scene_quality(frame: np.ndarray) -> SceneQualityMetrics:
    """Measure brightness, usable tonal range, sharpness and information content."""
    if frame.size == 0:
        raise ValueError("frame must not be empty")
    gray = _gray(frame)
    pixels = gray.reshape(-1)

    p05, p95 = np.percentile(pixels, [5, 95])
    lap = cv2.Laplacian(gray, cv2.CV_64F)

    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).reshape(-1)
    probs = hist / max(float(hist.sum()), 1.0)
    probs = probs[probs > 0]
    entropy = float(-np.sum(probs * np.log2(probs)))

    return SceneQualityMetrics(
        mean_luma=float(np.mean(pixels)),
        p05_luma=float(p05),
        p95_luma=float(p95),
        dynamic_range=float(p95 - p05),
        laplacian_variance=float(np.var(lap)),
        dark_fraction=float(np.mean(pixels <= 31)),
        clipped_high_fraction=float(np.mean(pixels >= 250)),
        entropy_bits=entropy,
    )
