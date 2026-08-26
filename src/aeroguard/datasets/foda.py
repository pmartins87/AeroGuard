from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


@dataclass(frozen=True)
class VOCObject:
    name: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int

    @property
    def width(self) -> int:
        return max(0, self.xmax - self.xmin)

    @property
    def height(self) -> int:
        return max(0, self.ymax - self.ymin)

    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass(frozen=True)
class VOCAnnotation:
    filename: str
    width: int
    height: int
    objects: tuple[VOCObject, ...]


@dataclass(frozen=True)
class FODASummary:
    annotation_files: int
    images_with_objects: int
    total_objects: int
    class_counts: dict[str, int]
    image_widths: tuple[int, ...]
    image_heights: tuple[int, ...]
    object_areas: tuple[int, ...]

    @property
    def classes(self) -> tuple[str, ...]:
        return tuple(sorted(self.class_counts))

    @property
    def class_count(self) -> int:
        return len(self.class_counts)

    def as_dict(self) -> dict:
        return {
            "annotation_files": self.annotation_files,
            "images_with_objects": self.images_with_objects,
            "total_objects": self.total_objects,
            "class_count": self.class_count,
            "class_counts": dict(sorted(self.class_counts.items())),
            "image_widths": list(self.image_widths),
            "image_heights": list(self.image_heights),
            "object_areas": list(self.object_areas),
        }


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 digest of a local dataset archive or manifest."""
    digest = sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _required_text(root: ET.Element, path: str) -> str:
    value = root.findtext(path)
    if value is None or not value.strip():
        raise ValueError(f"missing required VOC field: {path}")
    return value.strip()


def parse_voc_annotation(path: str | Path) -> VOCAnnotation:
    """Parse one Pascal VOC XML file with strict bounding-box validation."""
    root = ET.parse(Path(path)).getroot()
    filename = _required_text(root, "filename")
    width = int(_required_text(root, "size/width"))
    height = int(_required_text(root, "size/height"))
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid image dimensions in {path}: {width}x{height}")

    objects: list[VOCObject] = []
    for node in root.findall("object"):
        name = _required_text(node, "name")
        xmin = int(_required_text(node, "bndbox/xmin"))
        ymin = int(_required_text(node, "bndbox/ymin"))
        xmax = int(_required_text(node, "bndbox/xmax"))
        ymax = int(_required_text(node, "bndbox/ymax"))

        if not (0 <= xmin < xmax <= width and 0 <= ymin < ymax <= height):
            raise ValueError(
                f"invalid bounding box in {path}: "
                f"{name} ({xmin}, {ymin}, {xmax}, {ymax}) for {width}x{height}"
            )
        objects.append(VOCObject(name, xmin, ymin, xmax, ymax))

    return VOCAnnotation(filename, width, height, tuple(objects))


def find_voc_annotations(root: str | Path) -> list[Path]:
    """Locate annotation XMLs in a VOC tree without assuming one archive wrapper name."""
    base = Path(root)
    preferred = sorted(base.rglob("Annotations/*.xml"))
    if preferred:
        return preferred
    return sorted(base.rglob("*.xml"))


def summarize_voc_dataset(root: str | Path) -> FODASummary:
    """Build a deterministic summary used to freeze FOD-A provenance and sanity-check extraction."""
    xml_paths = find_voc_annotations(root)
    if not xml_paths:
        raise FileNotFoundError(f"no Pascal VOC XML annotations found under {root}")

    class_counts: Counter[str] = Counter()
    widths: set[int] = set()
    heights: set[int] = set()
    object_areas: list[int] = []
    images_with_objects = 0

    for xml_path in xml_paths:
        annotation = parse_voc_annotation(xml_path)
        widths.add(annotation.width)
        heights.add(annotation.height)
        if annotation.objects:
            images_with_objects += 1
        for obj in annotation.objects:
            class_counts[obj.name] += 1
            object_areas.append(obj.area)

    return FODASummary(
        annotation_files=len(xml_paths),
        images_with_objects=images_with_objects,
        total_objects=sum(class_counts.values()),
        class_counts=dict(class_counts),
        image_widths=tuple(sorted(widths)),
        image_heights=tuple(sorted(heights)),
        object_areas=tuple(sorted(object_areas)),
    )


def verify_split_members(root: str | Path, split_files: Iterable[str] = ("train.txt", "val.txt")) -> dict[str, int]:
    """Count IDs in source-provided split files when available.

    This deliberately does not invent a split when the source archive already provides one.
    """
    base = Path(root)
    result: dict[str, int] = {}
    for split_name in split_files:
        matches = sorted(base.rglob(split_name))
        if not matches:
            continue
        values = [line.strip() for line in matches[0].read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(values) != len(set(values)):
            raise ValueError(f"duplicate IDs in split file: {matches[0]}")
        result[split_name.removesuffix(".txt")] = len(values)
    return result
