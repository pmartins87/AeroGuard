#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import cv2
import numpy as np

from aeroguard.datasets.group_split import GroupSummary, assign_groups, assignment_summary


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_unique(root: Path, pattern: str, *, directory: bool = False) -> Path:
    matches = [p for p in root.rglob(pattern) if p.is_dir() == directory]
    if len(matches) != 1:
        raise ValueError(f"expected one {pattern!r} below {root}, found {len(matches)}")
    return matches[0]


def load_annotation_metadata(ann_dir: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in sorted(ann_dir.glob("*.xml")):
        tree = ET.parse(path)
        labels: list[str] = []
        areas: list[float] = []
        for obj in tree.findall("object"):
            label = obj.findtext("name", "").strip()
            if label:
                labels.append(label)
            bb = obj.find("bndbox")
            if bb is not None:
                xmin = float(bb.findtext("xmin", "0"))
                ymin = float(bb.findtext("ymin", "0"))
                xmax = float(bb.findtext("xmax", "0"))
                ymax = float(bb.findtext("ymax", "0"))
                areas.append(max(0.0, xmax - xmin) * max(0.0, ymax - ymin))
        result[path.stem] = {
            "labels": tuple(sorted(labels)),
            "unique_labels": tuple(sorted(set(labels))),
            "areas": tuple(areas),
        }
    return result


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("categorization CSV is empty")
    if not {"File", "Weather", "Light"}.issubset(rows[0]):
        raise ValueError("categorization CSV must contain File, Weather, Light")
    ids = [Path(row["File"]).stem for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("categorization CSV contains duplicate image IDs")
    return rows


def read_gray48(image_dir: Path, sid: str) -> np.ndarray:
    candidates = [image_dir / f"{sid}.jpg", image_dir / f"{sid}.JPG", image_dir / f"{sid}.png", image_dir / f"{sid}.PNG"]
    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        matches = list(image_dir.glob(f"{sid}.*"))
        if len(matches) != 1:
            raise FileNotFoundError(f"cannot resolve image for ID {sid}")
        path = matches[0]
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"OpenCV could not read {path}")
    return cv2.resize(img, (48, 48), interpolation=cv2.INTER_AREA).astype(np.float32)


def make_groups(
    rows: list[dict[str, str]],
    metadata: dict[str, dict],
    image_dir: Path,
    *,
    visual_threshold: float,
) -> tuple[list[dict], Counter[str], list[dict]]:
    groups: list[list[dict[str, str]]] = []
    current: list[dict[str, str]] = []
    reasons: Counter[str] = Counter()
    visual_boundaries: list[dict] = []
    previous_small: np.ndarray | None = None

    for row in rows:
        sid = Path(row["File"]).stem
        if sid not in metadata:
            raise ValueError(f"CSV ID {sid} has no annotation")
        if not current:
            current = [row]
            previous_small = None
            continue

        prev = current[-1]
        pid = Path(prev["File"]).stem
        boundary: list[str] = []
        if int(sid) != int(pid) + 1:
            boundary.append("nonconsecutive_id")
        if row["Weather"] != prev["Weather"]:
            boundary.append("weather_change")
        if row["Light"] != prev["Light"]:
            boundary.append("light_change")
        if metadata[sid]["labels"] != metadata[pid]["labels"]:
            boundary.append("label_signature_change")

        if not boundary:
            if previous_small is None:
                previous_small = read_gray48(image_dir, pid)
            current_small = read_gray48(image_dir, sid)
            mad48 = float(np.mean(np.abs(previous_small - current_small)) / 255.0)
            if mad48 >= visual_threshold:
                boundary.append("extreme_visual_discontinuity")
                visual_boundaries.append({
                    "left": pid,
                    "right": sid,
                    "mad48": mad48,
                    "labels": list(metadata[sid]["unique_labels"]),
                    "weather": row["Weather"],
                    "light": row["Light"],
                })
            previous_small = current_small
        else:
            previous_small = None

        if boundary:
            groups.append(current)
            reasons.update(boundary)
            current = [row]
            previous_small = None
        else:
            current.append(row)

    if current:
        groups.append(current)

    result: list[dict] = []
    seen: set[str] = set()
    for index, rows_in_group in enumerate(groups):
        ids = [Path(row["File"]).stem for row in rows_in_group]
        overlap = seen.intersection(ids)
        if overlap:
            raise ValueError(f"IDs appear in multiple groups: {sorted(overlap)[:5]}")
        seen.update(ids)
        label_counts: Counter[str] = Counter()
        environment_counts: Counter[str] = Counter()
        object_count = 0
        small_count = 0
        for row, sid in zip(rows_in_group, ids):
            for label in metadata[sid]["unique_labels"]:
                label_counts[label] += 1
            environment_counts[f"{row['Weather']}|{row['Light']}"] += 1
            areas = metadata[sid]["areas"]
            object_count += len(areas)
            small_count += sum(area < 1024.0 for area in areas)
        result.append({
            "key": f"g{index:03d}",
            "ids": ids,
            "size": len(ids),
            "first_id": ids[0],
            "last_id": ids[-1],
            "label_counts": dict(sorted(label_counts.items())),
            "environment_counts": dict(sorted(environment_counts.items())),
            "object_count": object_count,
            "small_object_count": small_count,
        })
    return result, reasons, visual_boundaries


def write_ids(path: Path, ids: list[str]) -> None:
    path.write_text("".join(f"{sid}\n" for sid in sorted(ids, key=int)), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic leakage-aware FOD-A split.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument("--visual-threshold", type=float, default=0.10)
    parser.add_argument("--iterations", type=int, default=50_000)
    args = parser.parse_args()

    root = args.root
    ann_dir = find_unique(root, "Annotations", directory=True)
    image_dir = find_unique(root, "JPEGImages", directory=True)
    csv_path = find_unique(root, "FOD_categorization_annotations.csv")
    metadata = load_annotation_metadata(ann_dir)
    rows = load_rows(csv_path)
    csv_ids = {Path(row["File"]).stem for row in rows}
    annotation_ids = set(metadata)
    if csv_ids != annotation_ids:
        raise ValueError(
            f"CSV/annotation ID mismatch: missing={len(annotation_ids-csv_ids)} extra={len(csv_ids-annotation_ids)}"
        )

    groups, boundary_reasons, visual_boundaries = make_groups(
        rows,
        metadata,
        image_dir,
        visual_threshold=args.visual_threshold,
    )
    summaries = [
        GroupSummary(
            key=group["key"],
            size=group["size"],
            label_counts=group["label_counts"],
            environment_counts=group["environment_counts"],
        )
        for group in groups
    ]
    assignment = assign_groups(summaries, seed=args.seed, iterations=args.iterations)
    summary = assignment_summary(summaries, assignment)

    split_ids = {split: [] for split in ("train", "val", "test")}
    split_objects = Counter()
    split_small = Counter()
    group_records = []
    for group in groups:
        split = assignment[group["key"]]
        split_ids[split].extend(group["ids"])
        split_objects[split] += group["object_count"]
        split_small[split] += group["small_object_count"]
        group_records.append({
            **{k: v for k, v in group.items() if k != "ids"},
            "split": split,
            "member_ids_sha256": hashlib.sha256(
                "".join(f"{sid}\n" for sid in group["ids"]).encode("utf-8")
            ).hexdigest(),
        })

    sets = {split: set(values) for split, values in split_ids.items()}
    if sets["train"] & sets["val"] or sets["train"] & sets["test"] or sets["val"] & sets["test"]:
        raise AssertionError("image overlap between output splits")
    union = sets["train"] | sets["val"] | sets["test"]
    if union != annotation_ids:
        raise AssertionError(
            f"split union mismatch: covered={len(union)} annotations={len(annotation_ids)}"
        )

    outdir = args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)
    files = {}
    for split in ("train", "val", "test"):
        path = outdir / f"{split}.txt"
        write_ids(path, split_ids[split])
        files[split] = {
            "path": path.name,
            "count": len(split_ids[split]),
            "sha256": sha256_file(path),
            "objects": split_objects[split],
            "small_objects_lt_1024": split_small[split],
        }

    groups_path = outdir / "groups.json"
    groups_path.write_text(json.dumps(group_records, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {
        "schema": "aeroguard.foda.sequence_split.v1",
        "seed": args.seed,
        "target_fraction": {"train": 0.70, "val": 0.15, "test": 0.15},
        "group_policy": {
            "categorization_csv_row_order": True,
            "break_on_nonconsecutive_numeric_id": True,
            "break_on_weather_change": True,
            "break_on_light_change": True,
            "break_on_label_signature_change": True,
            "break_on_extreme_visual_discontinuity": True,
            "visual_metric": "mean absolute difference on 48x48 grayscale / 255",
            "visual_threshold": args.visual_threshold,
            "rationale": "0.10 was above the measured 99.9th percentile (0.0781) and selected only 7/33,671 metadata-contiguous transitions in probe run 33041114427.",
        },
        "group_count": len(groups),
        "boundary_reasons": dict(sorted(boundary_reasons.items())),
        "extreme_visual_boundaries": visual_boundaries,
        "files": files,
        "assignment_summary": summary,
        "group_manifest": {
            "path": groups_path.name,
            "sha256": sha256_file(groups_path),
        },
        "coverage": {
            "annotation_ids": len(annotation_ids),
            "covered_once": len(union),
            "train_val_overlap": len(sets["train"] & sets["val"]),
            "train_test_overlap": len(sets["train"] & sets["test"]),
            "val_test_overlap": len(sets["val"] & sets["test"]),
        },
        "evaluation_policy": {
            "primary": "group-disjoint sequence-aware split",
            "single_group_classes": "forced to train and explicitly absent from independent held-out evaluation when atomic sequence grouping makes coverage impossible",
            "test_usage": "final model/threshold evaluation only; no hyperparameter selection",
            "source_split": "preserved for provenance only; rejected provisionally due duplicates, overlap and uncovered IDs",
        },
    }
    manifest_path = outdir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
