from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Sequence

from .coco_export import export_voc_subset_to_coco, source_class_names
from .foda import find_voc_annotations, parse_voc_annotation, sha256_file


@dataclass(frozen=True)
class TrainingLayoutResult:
    output_root: Path
    manifest_path: Path
    manifest: dict


def _stable_lines_sha256(values: Sequence[str]) -> str:
    payload = "".join(f"{value}\n" for value in values).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _annotation_index(root: Path) -> dict[str, Path]:
    paths = find_voc_annotations(root)
    index = {path.stem: path for path in paths}
    if len(index) != len(paths):
        raise ValueError("duplicate Pascal VOC annotation stems found")
    return index


def _resolve_image(root: Path, annotation_path: Path, filename: str) -> Path:
    if Path(filename).name != filename:
        raise ValueError(f"annotation filename must be a basename: {filename}")

    voc_root = annotation_path.parent.parent
    direct = voc_root / "JPEGImages" / filename
    if direct.is_file():
        return direct

    candidates = sorted(root.rglob(filename))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise FileNotFoundError(f"source image not found for annotation {annotation_path}: {filename}")
    raise ValueError(f"ambiguous source image filename {filename}: {candidates[:5]}")


def _place_file(source: Path, destination: Path, mode: str) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)

    if mode not in {"auto", "hardlink", "copy"}:
        raise ValueError("mode must be one of: auto, hardlink, copy")

    if mode in {"auto", "hardlink"}:
        try:
            os.link(source, destination)
            return "hardlink"
        except OSError:
            if mode == "hardlink":
                raise

    shutil.copy2(source, destination)
    return "copy"


def _materialize_split(
    root: Path,
    annotation_index: dict[str, Path],
    coco_payload: dict,
    destination: Path,
    *,
    mode: str,
) -> dict[str, int]:
    names: set[str] = set()
    counts = {"hardlink": 0, "copy": 0}

    for image in coco_payload["images"]:
        filename = str(image["file_name"])
        source_id = str(image["aeroguard_source_id"])
        if filename in names:
            raise ValueError(f"duplicate image filename inside split: {filename}")
        names.add(filename)

        xml_path = annotation_index[source_id]
        annotation = parse_voc_annotation(xml_path)
        if annotation.filename != filename:
            raise ValueError(
                f"annotation filename changed during export for {source_id}: "
                f"{annotation.filename!r} != {filename!r}"
            )
        source = _resolve_image(root, xml_path, filename)
        used_mode = _place_file(source, destination / filename, mode)
        counts[used_mode] += 1

    return counts


def materialize_yolox_coco_layout(
    dataset_root: str | Path,
    train_ids: Sequence[str],
    val_ids: Sequence[str],
    output_root: str | Path,
    *,
    mode: str = "auto",
) -> TrainingLayoutResult:
    """Build a deterministic YOLOX-compatible COCO directory from frozen FOD-A IDs.

    The output layout is ``annotations/instances_{train,val}2017.json`` plus
    ``train2017/`` and ``val2017/`` image directories. The source test split is never
    accepted here; callers must pass only the derived development train/validation IDs.
    """
    root = Path(dataset_root)
    output = Path(output_root)
    train = tuple(sorted(train_ids))
    val = tuple(sorted(val_ids))

    if not train or not val:
        raise ValueError("train_ids and val_ids must both be non-empty")
    if len(train) != len(set(train)) or len(val) != len(set(val)):
        raise ValueError("train_ids/val_ids must not contain duplicates")
    overlap = sorted(set(train) & set(val))
    if overlap:
        raise ValueError(f"train/validation overlap detected: {overlap[:10]}")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output_root is not empty: {output}")

    classes = source_class_names(root)
    train_export = export_voc_subset_to_coco(root, train, class_names=classes, verify_images=True)
    val_export = export_voc_subset_to_coco(root, val, class_names=classes, verify_images=True)

    annotations_dir = output / "annotations"
    train_dir = output / "train2017"
    val_dir = output / "val2017"
    annotations_dir.mkdir(parents=True, exist_ok=True)
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    train_json = annotations_dir / "instances_train2017.json"
    val_json = annotations_dir / "instances_val2017.json"
    classes_path = output / "classes.txt"
    train_json.write_text(json.dumps(train_export.payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    val_json.write_text(json.dumps(val_export.payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    classes_path.write_text("".join(f"{name}\n" for name in classes), encoding="utf-8")

    index = _annotation_index(root)
    train_materialization = _materialize_split(root, index, train_export.payload, train_dir, mode=mode)
    val_materialization = _materialize_split(root, index, val_export.payload, val_dir, mode=mode)

    manifest = {
        "schema": "aeroguard.foda.yolox_coco_layout.v1",
        "source_format": "FOD-A v2.1 Pascal VOC 300x300",
        "policy": "development train/validation only; source test split remains held out",
        "class_count": len(classes),
        "classes_sha256": sha256_file(classes_path),
        "train": {
            "image_count": len(train_export.payload["images"]),
            "annotation_count": len(train_export.payload["annotations"]),
            "ids_sha256": _stable_lines_sha256(train),
            "annotation_json_sha256": sha256_file(train_json),
            "materialization": train_materialization,
        },
        "val": {
            "image_count": len(val_export.payload["images"]),
            "annotation_count": len(val_export.payload["annotations"]),
            "ids_sha256": _stable_lines_sha256(val),
            "annotation_json_sha256": sha256_file(val_json),
            "materialization": val_materialization,
        },
    }
    manifest_path = output / "aeroguard_training_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return TrainingLayoutResult(output_root=output, manifest_path=manifest_path, manifest=manifest)
