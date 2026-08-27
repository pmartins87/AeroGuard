#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

# Running `python scripts/<name>.py` places scripts/ rather than the repository
# root on sys.path. Add the root explicitly so we can reuse the already-frozen
# sequence grouping implementation without duplicating it.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aeroguard.tracking import TrackDetection, TemporalTracker
from scripts.foda_make_sequence_split import (
    find_unique,
    load_annotation_metadata,
    load_rows,
    make_groups,
)


def load_boxes(ann_dir: Path, sid: str, frame_index: int) -> list[TrackDetection]:
    path = ann_dir / f"{sid}.xml"
    tree = ET.parse(path)
    result: list[TrackDetection] = []
    for obj in tree.findall("object"):
        label = obj.findtext("name", "").strip()
        bb = obj.find("bndbox")
        if not label or bb is None:
            continue
        xmin = float(bb.findtext("xmin", "0"))
        ymin = float(bb.findtext("ymin", "0"))
        xmax = float(bb.findtext("xmax", "0"))
        ymax = float(bb.findtext("ymax", "0"))
        result.append(
            TrackDetection(
                frame_index=frame_index,
                label=label,
                bbox=(xmin, ymin, xmax, ymax),
                score=1.0,
            )
        )
    return result


def audit_threshold(
    groups: list[dict],
    ann_dir: Path,
    *,
    min_iou: float,
    min_hits: int,
    max_missed_frames: int,
) -> dict:
    observations = 0
    matched_observations = 0
    confirmed_observations = 0
    matched_ious: list[float] = []
    fragmentation_excess = 0
    group_label_tracks: dict[tuple[str, str], set[int]] = defaultdict(set)
    group_label_max_simultaneous: dict[tuple[str, str], int] = defaultdict(int)
    confirmable_groups = 0
    groups_with_confirmed = 0

    for group in groups:
        tracker = TemporalTracker(
            min_iou=min_iou,
            min_hits=min_hits,
            max_missed_frames=max_missed_frames,
        )
        group_confirmed = False
        for local_index, sid in enumerate(group["ids"]):
            detections = load_boxes(ann_dir, sid, local_index)
            counts = Counter(d.label for d in detections)
            for label, count in counts.items():
                group_label_max_simultaneous[(group["key"], label)] = max(
                    group_label_max_simultaneous[(group["key"], label)], count
                )
            tracked = tracker.update(local_index, detections)
            observations += len(tracked)
            for item in tracked:
                group_label_tracks[(group["key"], item.detection.label)].add(item.track_id)
                if item.match_iou is not None:
                    matched_observations += 1
                    matched_ious.append(float(item.match_iou))
                if item.confirmed:
                    confirmed_observations += 1
                    group_confirmed = True
        if group["size"] >= min_hits:
            confirmable_groups += 1
            if group_confirmed:
                groups_with_confirmed += 1

    for key, track_ids in group_label_tracks.items():
        expected = max(1, group_label_max_simultaneous[key])
        fragmentation_excess += max(0, len(track_ids) - expected)

    matched_ious_sorted = sorted(matched_ious)
    return {
        "min_iou": min_iou,
        "min_hits": min_hits,
        "max_missed_frames": max_missed_frames,
        "observations": observations,
        "matched_observations": matched_observations,
        "matched_observation_fraction": matched_observations / observations if observations else 0.0,
        "confirmed_observations": confirmed_observations,
        "confirmed_observation_fraction": confirmed_observations / observations if observations else 0.0,
        "confirmable_groups": confirmable_groups,
        "groups_with_confirmed_track": groups_with_confirmed,
        "confirmable_group_success_fraction": groups_with_confirmed / confirmable_groups if confirmable_groups else 0.0,
        "fragmentation_excess_tracks": fragmentation_excess,
        "matched_iou_min": min(matched_ious_sorted) if matched_ious_sorted else None,
        "matched_iou_median": statistics.median(matched_ious_sorted) if matched_ious_sorted else None,
        "matched_iou_p05": matched_ious_sorted[max(0, int(0.05 * (len(matched_ious_sorted) - 1)))] if matched_ious_sorted else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit deterministic tracker continuity on FOD-A GT sequences.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--visual-threshold", type=float, default=0.10)
    parser.add_argument("--min-hits", type=int, default=3)
    parser.add_argument("--max-missed-frames", type=int, default=1)
    parser.add_argument("--iou-grid", default="0.05,0.10,0.20,0.30,0.40,0.50")
    args = parser.parse_args()

    ann_dir = find_unique(args.root, "Annotations", directory=True)
    image_dir = find_unique(args.root, "JPEGImages", directory=True)
    csv_path = find_unique(args.root, "FOD_categorization_annotations.csv")
    metadata = load_annotation_metadata(ann_dir)
    rows = load_rows(csv_path)
    groups, reasons, visual_boundaries = make_groups(
        rows,
        metadata,
        image_dir,
        visual_threshold=args.visual_threshold,
    )

    thresholds = sorted({float(value.strip()) for value in args.iou_grid.split(",") if value.strip()})
    if not thresholds or any(value < 0.0 or value > 1.0 for value in thresholds):
        raise ValueError("IoU grid must contain values in [0,1]")

    audits = [
        audit_threshold(
            groups,
            ann_dir,
            min_iou=value,
            min_hits=args.min_hits,
            max_missed_frames=args.max_missed_frames,
        )
        for value in thresholds
    ]

    # Selection prioritizes continuity, then lower fragmentation, then the higher
    # threshold when evidence quality is tied. This is a GT-geometry diagnostic;
    # final learned-detector tracking parameters still require validation outputs.
    selected = max(
        audits,
        key=lambda item: (
            item["matched_observation_fraction"],
            -item["fragmentation_excess_tracks"],
            item["confirmable_group_success_fraction"],
            item["min_iou"],
        ),
    )

    payload = {
        "schema": "aeroguard.foda.gt_tracking_audit.v1",
        "dataset_images": len(metadata),
        "sequence_groups": len(groups),
        "group_boundary_reasons": dict(sorted(reasons.items())),
        "extreme_visual_boundary_count": len(visual_boundaries),
        "policy": {
            "visual_group_threshold": args.visual_threshold,
            "min_hits": args.min_hits,
            "max_missed_frames": args.max_missed_frames,
            "iou_grid": thresholds,
            "selection_note": "GT geometry diagnostic only; learned-detector validation can revise the runtime IoU threshold before test freeze.",
        },
        "audits": audits,
        "gt_geometry_selected": selected,
        "limitations": [
            "FOD-A annotations do not expose persistent object identity, so continuity is inferred within leakage groups and class labels.",
            "Multiple same-class objects can make fragmentation accounting approximate.",
            "Perfect GT boxes are easier to associate than learned detector boxes; this audit does not replace validation on detector outputs.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
