from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .foda import find_voc_annotations, parse_voc_annotation


@dataclass(frozen=True)
class COCOExport:
    payload: dict
    class_names: tuple[str, ...]


def source_class_names(root: str | Path) -> tuple[str, ...]:
    """Return the globally frozen raw FOD-A class list in deterministic order."""
    labels: set[str] = set()
    for xml_path in find_voc_annotations(root):
        annotation = parse_voc_annotation(xml_path)
        labels.update(obj.name for obj in annotation.objects)
    if not labels:
        raise ValueError("no source classes found")
    return tuple(sorted(labels))


def _annotation_index(root: Path) -> dict[str, Path]:
    paths = find_voc_annotations(root)
    index = {path.stem: path for path in paths}
    if len(index) != len(paths):
        raise ValueError("duplicate Pascal VOC annotation stems found")
    return index


def _resolve_image(root: Path, annotation_path: Path, filename: str) -> Path:
    """Resolve the source image without silently accepting a missing/mismatched file."""
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


def export_voc_subset_to_coco(
    root: str | Path,
    member_ids: Sequence[str],
    *,
    class_names: Sequence[str] | None = None,
    verify_images: bool = True,
) -> COCOExport:
    """Convert a frozen Pascal VOC ID subset to deterministic COCO JSON data.

    Source IDs are sorted before numeric COCO IDs are assigned. Bounding boxes stay
    floating-point so the FOD-A resize coordinates are not truncated.
    """
    base = Path(root)
    ids = tuple(sorted(member_ids))
    if not ids:
        raise ValueError("member_ids cannot be empty")
    if len(ids) != len(set(ids)):
        raise ValueError("member_ids contain duplicates")

    classes = tuple(class_names) if class_names is not None else source_class_names(base)
    if not classes or len(classes) != len(set(classes)):
        raise ValueError("class_names must be non-empty and unique")
    category_id = {name: index + 1 for index, name in enumerate(classes)}

    annotation_paths = _annotation_index(base)
    missing = sorted(set(ids) - annotation_paths.keys())
    if missing:
        raise ValueError(f"missing annotations for {len(missing)} member IDs; examples: {missing[:10]}")

    images: list[dict] = []
    annotations: list[dict] = []
    annotation_id = 1

    for image_numeric_id, source_id in enumerate(ids, start=1):
        xml_path = annotation_paths[source_id]
        annotation = parse_voc_annotation(xml_path)
        if verify_images:
            _resolve_image(base, xml_path, annotation.filename)

        images.append(
            {
                "id": image_numeric_id,
                "file_name": annotation.filename,
                "width": annotation.width,
                "height": annotation.height,
                "aeroguard_source_id": source_id,
            }
        )

        for obj in annotation.objects:
            if obj.name not in category_id:
                raise ValueError(f"source label absent from class_names: {obj.name}")
            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_numeric_id,
                    "category_id": category_id[obj.name],
                    "bbox": [obj.xmin, obj.ymin, obj.width, obj.height],
                    "area": obj.area,
                    "iscrowd": 0,
                    "aeroguard_source_label": obj.name,
                }
            )
            annotation_id += 1

    payload = {
        "info": {
            "description": "AeroGuard deterministic FOD-A Pascal VOC subset conversion",
            "source_format": "FOD-A v2.1 Pascal VOC 300x300",
        },
        "licenses": [],
        "images": images,
        "annotations": annotations,
        "categories": [
            {"id": category_id[name], "name": name, "supercategory": "FOD"}
            for name in classes
        ],
    }
    return COCOExport(payload=payload, class_names=classes)
