from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class SceneQualityMetrics:
    """Deterministic image-quality measurements used as safety guardrail evidence."""

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


@dataclass(frozen=True)
class SceneQualityPolicy:
    """Conservative reacquisition thresholds frozen from the FOD-A profile.

    The defaults sit just outside the observed FOD-A support rather than using
    ordinary dark/dim imagery as failure examples. They are safety guardrails,
    not detector-confidence thresholds.
    """

    min_mean_luma: float = 60.0
    min_dynamic_range: float = 8.0
    min_laplacian_variance: float = 9.0
    min_entropy_bits: float = 3.5
    max_dark_fraction: float = 0.18
    max_clipped_high_fraction: float = 0.07


@dataclass(frozen=True)
class SceneQualityAssessment:
    usable: bool
    reasons: tuple[str, ...]
    metrics: SceneQualityMetrics

    def as_dict(self) -> dict:
        return {
            "usable": self.usable,
            "reasons": list(self.reasons),
            "metrics": self.metrics.as_dict(),
        }


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


def assess_scene_quality(
    frame: np.ndarray,
    policy: SceneQualityPolicy | None = None,
) -> SceneQualityAssessment:
    """Return fail-safe reacquisition reasons for frames outside supported quality."""
    policy = policy or SceneQualityPolicy()
    metrics = measure_scene_quality(frame)
    reasons: list[str] = []

    if metrics.mean_luma < policy.min_mean_luma:
        reasons.append("extreme_darkness")
    if metrics.dynamic_range < policy.min_dynamic_range:
        reasons.append("collapsed_dynamic_range")
    if metrics.laplacian_variance < policy.min_laplacian_variance:
        reasons.append("extreme_blur")
    if metrics.entropy_bits < policy.min_entropy_bits:
        reasons.append("low_information")
    if metrics.dark_fraction > policy.max_dark_fraction:
        reasons.append("excessive_dark_pixels")
    if metrics.clipped_high_fraction > policy.max_clipped_high_fraction:
        reasons.append("highlight_clipping")

    return SceneQualityAssessment(
        usable=not reasons,
        reasons=tuple(reasons),
        metrics=metrics,
    )
