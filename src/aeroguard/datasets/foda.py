from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


FODA_REPOSITORY = "https://github.com/FOD-UNOmaha/FOD-data"
FODA_VERSION = "2.1"
FODA_FORMAT = "Pascal VOC"
FODA_IMAGE_SIZE = (300, 300)
FODA_DRIVE_FILE_ID = "1RdErcq8PGRXZUOGauaACkQG44T-QyZ4x"
FODA_SPLIT_CANDIDATES = ("trainval.txt", "test.txt", "train.txt", "val.txt")


@dataclass(frozen=True)
class VOCObject:
    name: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def width(self) -> float:
        return max(0.0, self.xmax - self.xmin)

    @property
    def height(self) -> float:
        return max(0.0, self.ymax - self.ymin)

    @property
    def area(self) -> float:
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
    object_areas: tuple[float, ...]

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
    """Parse one Pascal VOC XML file with strict bounding-box validation.

    FOD-A v2.1 contains fractional box coordinates after its 400->300 resize.
    They are preserved as floats rather than silently truncated.
    """
    root = ET.parse(Path(path)).getroot()
    filename = _required_text(root, "filename")
    width = int(float(_required_text(root, "size/width")))
    height = int(float(_required_text(root, "size/height")))
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid image dimensions in {path}: {width}x{height}")

    objects: list[VOCObject] = []
    for node in root.findall("object"):
        name = _required_text(node, "name")
        xmin = float(_required_text(node, "bndbox/xmin"))
        ymin = float(_required_text(node, "bndbox/ymin"))
        xmax = float(_required_text(node, "bndbox/xmax"))
        ymax = float(_required_text(node, "bndbox/ymax"))

        if not (0.0 <= xmin < xmax <= width and 0.0 <= ymin < ymax <= height):
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
    object_areas: list[float] = []
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


def _split_file_matches(root: Path, split_name: str) -> list[Path]:
    matches = [path for path in root.rglob(split_name) if "ImageSets" in path.parts]
    return sorted(matches)


def load_split_members(path: str | Path) -> tuple[str, ...]:
    """Load one VOC split file and reject duplicate IDs."""
    split_path = Path(path)
    values = tuple(
        line.strip().split()[0]
        for line in split_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate IDs in split file: {split_path}")
    return values


def discover_source_splits(
    root: str | Path,
    split_files: Iterable[str] = FODA_SPLIT_CANDIDATES,
) -> dict[str, dict]:
    """Describe source-provided VOC split files with hashes and membership checks.

    FOD-A v2.1 uses ``trainval.txt`` and ``test.txt`` inside ``ImageSets/Main``.
    We still probe conventional ``train.txt``/``val.txt`` names so the inspector is
    robust to future source revisions. Ambiguous duplicate split filenames fail
    closed rather than silently selecting one.
    """
    base = Path(root)
    annotations = find_voc_annotations(base)
    annotation_ids = {path.stem for path in annotations}
    result: dict[str, dict] = {}
    member_sets: dict[str, set[str]] = {}

    for split_name in split_files:
        matches = _split_file_matches(base, split_name)
        if not matches:
            continue
        if len(matches) > 1:
            raise ValueError(
                f"ambiguous source split {split_name}: "
                + ", ".join(str(path) for path in matches)
            )
        path = matches[0]
        members = load_split_members(path)
        member_set = set(members)
        key = split_name.removesuffix(".txt")
        member_sets[key] = member_set
        unknown = sorted(member_set - annotation_ids)
        result[key] = {
            "count": len(members),
            "relative_path": str(path.relative_to(base)),
            "sha256": sha256_file(path),
            "unknown_annotation_ids": len(unknown),
            "unknown_annotation_id_examples": unknown[:10],
        }

    if "trainval" in member_sets and "test" in member_sets:
        overlap = member_sets["trainval"] & member_sets["test"]
        covered = member_sets["trainval"] | member_sets["test"]
        missing = sorted(annotation_ids - covered)
        extra = sorted(covered - annotation_ids)
        result["coverage"] = {
            "annotation_ids": len(annotation_ids),
            "trainval_test_overlap": len(overlap),
            "covered_annotation_ids": len(covered & annotation_ids),
            "missing_annotation_ids": len(missing),
            "extra_split_ids": len(extra),
            "overlap_examples": sorted(overlap)[:10],
            "missing_examples": missing[:10],
            "extra_examples": extra[:10],
        }

    return result


def verify_split_members(
    root: str | Path,
    split_files: Iterable[str] = FODA_SPLIT_CANDIDATES,
) -> dict[str, int]:
    """Return counts for source-provided split files when available.

    Kept as a compact compatibility helper; use :func:`discover_source_splits`
    when hashes and coverage evidence are required.
    """
    details = discover_source_splits(root, split_files)
    return {
        name: int(info["count"])
        for name, info in details.items()
        if name != "coverage" and isinstance(info, dict) and "count" in info
    }
