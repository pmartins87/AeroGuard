#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from aeroguard.scene_quality import measure_scene_quality


METRICS = (
    "mean_luma",
    "p05_luma",
    "p95_luma",
    "dynamic_range",
    "laplacian_variance",
    "dark_fraction",
    "clipped_high_fraction",
    "entropy_bits",
)
QUANTILES = (0.001, 0.005, 0.01, 0.05, 0.50, 0.95, 0.99, 0.995, 0.999)


def find_unique(root: Path, pattern: str, *, directory: bool = False) -> Path:
    matches = [p for p in root.rglob(pattern) if p.is_dir() == directory]
    if len(matches) != 1:
        raise ValueError(f"expected one {pattern!r} below {root}, found {len(matches)}")
    return matches[0]


def load_environment(csv_path: Path) -> dict[str, tuple[str, str]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    result: dict[str, tuple[str, str]] = {}
    for row in rows:
        sid = Path(row["File"]).stem
        result[sid] = (row["Weather"], row["Light"])
    if len(result) != len(rows):
        raise ValueError("categorization CSV contains duplicate image IDs")
    return result


def resolve_image(image_dir: Path, sid: str) -> Path:
    for suffix in (".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"):
        path = image_dir / f"{sid}{suffix}"
        if path.exists():
            return path
    matches = list(image_dir.glob(f"{sid}.*"))
    if len(matches) != 1:
        raise FileNotFoundError(f"cannot resolve image for ID {sid}")
    return matches[0]


def summarize(records: list[dict[str, float]]) -> dict:
    if not records:
        return {"count": 0, "metrics": {}}
    result = {"count": len(records), "metrics": {}}
    for metric in METRICS:
        values = np.asarray([float(record[metric]) for record in records], dtype=np.float64)
        result["metrics"][metric] = {
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "mean": float(np.mean(values)),
            "quantiles": {
                f"q{q:g}": float(np.quantile(values, q, method="linear"))
                for q in QUANTILES
            },
        }
    return result


def extremes(records: list[dict], metric: str, *, n: int = 20, reverse: bool = False) -> list[dict]:
    ordered = sorted(records, key=lambda r: (float(r[metric]), r["id"]), reverse=reverse)
    return [
        {
            "id": r["id"],
            "weather": r["weather"],
            "light": r["light"],
            metric: r[metric],
        }
        for r in ordered[:n]
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile FOD-A image quality with OpenCV.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--records-output", type=Path)
    args = parser.parse_args()

    image_dir = find_unique(args.root, "JPEGImages", directory=True)
    csv_path = find_unique(args.root, "FOD_categorization_annotations.csv")
    environment = load_environment(csv_path)

    records: list[dict] = []
    by_light: dict[str, list[dict]] = defaultdict(list)
    by_weather: dict[str, list[dict]] = defaultdict(list)
    by_environment: dict[str, list[dict]] = defaultdict(list)

    for index, sid in enumerate(sorted(environment, key=int), start=1):
        path = resolve_image(image_dir, sid)
        frame = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError(f"OpenCV could not read {path}")
        quality = measure_scene_quality(frame).as_dict()
        weather, light = environment[sid]
        record = {"id": sid, "weather": weather, "light": light, **quality}
        records.append(record)
        by_light[light].append(record)
        by_weather[weather].append(record)
        by_environment[f"{weather}|{light}"].append(record)
        if index % 5000 == 0:
            print(f"profiled {index}/{len(environment)} images", flush=True)

    if len(records) != len(environment):
        raise AssertionError("profile record count mismatch")

    payload = {
        "schema": "aeroguard.foda.scene_quality_profile.v1",
        "opencv_version": cv2.__version__,
        "image_count": len(records),
        "metric_definitions": {
            "mean_luma": "mean grayscale intensity in [0,255]",
            "p05_luma": "5th percentile grayscale intensity",
            "p95_luma": "95th percentile grayscale intensity",
            "dynamic_range": "p95_luma - p05_luma",
            "laplacian_variance": "variance of CV_64F Laplacian; lower implies less high-frequency detail",
            "dark_fraction": "fraction of pixels <=31",
            "clipped_high_fraction": "fraction of pixels >=250",
            "entropy_bits": "Shannon entropy of the 256-bin grayscale histogram",
        },
        "overall": summarize(records),
        "by_light": {key: summarize(value) for key, value in sorted(by_light.items())},
        "by_weather": {key: summarize(value) for key, value in sorted(by_weather.items())},
        "by_environment": {key: summarize(value) for key, value in sorted(by_environment.items())},
        "extremes": {
            "lowest_mean_luma": extremes(records, "mean_luma"),
            "highest_dark_fraction": extremes(records, "dark_fraction", reverse=True),
            "lowest_dynamic_range": extremes(records, "dynamic_range"),
            "lowest_laplacian_variance": extremes(records, "laplacian_variance"),
            "lowest_entropy_bits": extremes(records, "entropy_bits"),
            "highest_clipped_high_fraction": extremes(records, "clipped_high_fraction", reverse=True),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "opencv_version": payload["opencv_version"],
        "image_count": payload["image_count"],
        "output": str(args.output),
    }, sort_keys=True))

    if args.records_output is not None:
        args.records_output.parent.mkdir(parents=True, exist_ok=True)
        args.records_output.write_text(json.dumps(records, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
