from __future__ import annotations

import hashlib
import platform
import statistics
import sys
from pathlib import Path

import cv2
import numpy as np


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def numeric_summary(values_in: list[float]) -> dict[str, float | int]:
    if not values_in:
        raise ValueError("at least one numeric sample is required")
    values = np.asarray(values_in, dtype=np.float64)
    return {
        "count": int(values.size),
        "min": float(np.min(values)),
        "mean": float(np.mean(values)),
        "p50": float(np.quantile(values, 0.50)),
        "p95": float(np.quantile(values, 0.95)),
        "max": float(np.max(values)),
        "stdev": float(statistics.pstdev(values_in)),
    }


def timing_summary(values_ms: list[float]) -> dict[str, float | int]:
    base = numeric_summary(values_ms)
    return {
        "count": base["count"],
        "min_ms": base["min"],
        "mean_ms": base["mean"],
        "p50_ms": base["p50"],
        "p95_ms": base["p95"],
        "max_ms": base["max"],
        "stdev_ms": base["stdev"],
    }


def runtime_fingerprint() -> dict[str, str]:
    build_info = cv2.getBuildInformation().encode("utf-8")
    return {
        "python": sys.version.split()[0],
        "opencv": cv2.__version__,
        "opencv_build_sha256": hashlib.sha256(build_info).hexdigest(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
