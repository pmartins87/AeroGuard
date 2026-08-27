#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from aeroguard.datasets.coco_export import source_class_names
from aeroguard.datasets.foda import find_voc_annotations, load_split_members, parse_voc_annotation, sha256_file
from aeroguard.detectors.yolox_opencv import OpenCVYOLOXDetector, YOLOXConfig
from aeroguard.evaluation.detection import Box, evaluate_boxes, greedy_match_boxes


def stable_ids_hash(ids: tuple[str, ...]) -> str:
    return hashlib.sha256("".join(f"{x}\n" for x in ids).encode()).hexdigest()


def annotation_index(root: Path) -> dict[str, Path]:
    paths = find_voc_annotations(root)
    result = {p.stem: p for p in paths}
    if len(result) != len(paths):
        raise ValueError("duplicate annotation stems")
    return result


def resolve_image(root: Path, xml_path: Path, filename: str) -> Path:
    direct = xml_path.parent.parent / "JPEGImages" / filename
    if direct.is_file():
        return direct
    matches = sorted(root.rglob(filename))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(filename)
    raise ValueError(f"ambiguous image filename: {filename}")


def box_dict(box: Box) -> dict:
    return {
        "image_id": box.image_id,
        "label": box.label,
        "bbox_xyxy": [box.xmin, box.ymin, box.xmax, box.ymax],
        "area": box.area,
        "score": box.score,
    }


def recall_summary(indices: list[int], matched: frozenset[int]) -> dict:
    total = len(indices)
    hits = sum(i in matched for i in indices)
    return {"matched": hits, "total": total, "recall": hits / total if total else 0.0}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate FOD-A YOLOX ONNX through OpenCV 5 DNN.")
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("member_ids", type=Path)
    parser.add_argument("model", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--predictions-output", type=Path)
    parser.add_argument("--input-size", type=int, default=640)
    parser.add_argument("--score-threshold", type=float, default=0.25)
    parser.add_argument("--nms-threshold", type=float, default=0.45)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--small-area", type=float, default=1024.0)
    parser.add_argument("--warmup-runs", type=int, default=3)
    parser.add_argument("--max-images", type=int)
    parser.add_argument("--failure-limit", type=int, default=50)
    args = parser.parse_args()

    ids = tuple(sorted(load_split_members(args.member_ids)))
    if args.max_images is not None:
        if args.max_images <= 0:
            raise ValueError("max-images must be positive")
        ids = ids[: args.max_images]
    if not ids:
        raise ValueError("evaluation split is empty")

    labels = source_class_names(args.dataset_root)
    detector = OpenCVYOLOXDetector(
        args.model,
        labels,
        config=YOLOXConfig(
            input_width=args.input_size,
            input_height=args.input_size,
            confidence_threshold=args.score_threshold,
            nms_threshold=args.nms_threshold,
        ),
    )
    xml_by_id = annotation_index(args.dataset_root)
    missing = sorted(set(ids) - xml_by_id.keys())
    if missing:
        raise ValueError(f"missing annotations: {missing[:10]}")

    first_ann = parse_voc_annotation(xml_by_id[ids[0]])
    first_image = cv2.imread(str(resolve_image(args.dataset_root, xml_by_id[ids[0]], first_ann.filename)))
    if first_image is None:
        raise ValueError("failed to read warmup image")
    for _ in range(args.warmup_runs):
        detector.predict(first_image, image_id=ids[0])

    truth: list[Box] = []
    predictions: list[Box] = []
    latency_ms: list[float] = []
    for source_id in ids:
        xml_path = xml_by_id[source_id]
        ann = parse_voc_annotation(xml_path)
        image = cv2.imread(str(resolve_image(args.dataset_root, xml_path, ann.filename)))
        if image is None:
            raise ValueError(f"failed to read {ann.filename}")
        truth.extend(
            Box(source_id, obj.name, obj.xmin, obj.ymin, obj.xmax, obj.ymax)
            for obj in ann.objects
        )
        started = perf_counter()
        predictions.extend(detector.predict(image, image_id=source_id))
        latency_ms.append((perf_counter() - started) * 1000.0)

    metrics = evaluate_boxes(
        truth, predictions, iou_threshold=args.iou_threshold, score_threshold=args.score_threshold
    )
    matching = greedy_match_boxes(
        truth, predictions, iou_threshold=args.iou_threshold, score_threshold=args.score_threshold
    )
    matched = matching.matched_truth_indices
    small = [i for i, box in enumerate(truth) if box.area < args.small_area]
    per_class = {
        label: recall_summary([i for i, box in enumerate(truth) if box.label == label], matched)
        for label in labels
    }

    lat = np.asarray(latency_ms, dtype=np.float64)
    mean_ms = float(lat.mean())
    false_negatives = [truth[i] for i in matching.false_negative_truth_indices]
    false_positives = [predictions[i] for i in matching.false_positive_prediction_indices]
    false_negatives.sort(key=lambda b: (b.area, b.image_id, b.label))
    false_positives.sort(key=lambda b: (-b.score, b.image_id, b.label))

    report = {
        "schema": "aeroguard.foda.opencvdnn_eval.v1",
        "operating_point": {
            "score_threshold": args.score_threshold,
            "nms_threshold": args.nms_threshold,
            "iou_threshold": args.iou_threshold,
            "small_area_lt_px2": args.small_area,
        },
        "dataset": {
            "member_ids_sha256": sha256_file(args.member_ids),
            "effective_ids_sha256": stable_ids_hash(ids),
            "images": len(ids),
            "ground_truth_objects": len(truth),
            "small_ground_truth_objects": len(small),
            "classes": len(labels),
        },
        "model": {"sha256": sha256_file(args.model), "path": str(args.model)},
        "metrics": {
            "overall": metrics.as_dict(),
            "small_object_recall": recall_summary(small, matched),
            "per_class_recall": per_class,
        },
        "runtime": {
            "backend": "OpenCV DNN CPU",
            "opencv_version": cv2.__version__,
            "input_size": args.input_size,
            "warmup_runs": args.warmup_runs,
            "mean_latency_ms": mean_ms,
            "p50_latency_ms": float(np.percentile(lat, 50)),
            "p95_latency_ms": float(np.percentile(lat, 95)),
            "throughput_fps": 1000.0 / mean_ms if mean_ms > 0 else 0.0,
        },
        "failure_examples": {
            "false_negative_count": len(false_negatives),
            "false_positive_count": len(false_positives),
            "false_negatives_smallest_first": [box_dict(b) for b in false_negatives[: args.failure_limit]],
            "false_positives_highest_score_first": [box_dict(b) for b in false_positives[: args.failure_limit]],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.predictions_output:
        args.predictions_output.parent.mkdir(parents=True, exist_ok=True)
        payload = {"model_sha256": report["model"]["sha256"], "predictions": [box_dict(b) for b in predictions]}
        args.predictions_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
