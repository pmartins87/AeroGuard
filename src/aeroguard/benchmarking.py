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


def timing_summary(values_ms: list[float]) -> dict[str, float | int]:
    if not values_ms:
        raise ValueError("at least one timing sample is required")
    values = np.asarray(values_ms, dtype=np.float64)
    return {
        "count": int(values.size),
        "min_ms": float(np.min(values)),
        "mean_ms": float(np.mean(values)),
        "p50_ms": float(np.quantile(values, 0.50)),
        "p95_ms": float(np.quantile(values, 0.95)),
        "max_ms": float(np.max(values)),
        "stdev_ms": float(statistics.pstdev(values_ms)),
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
