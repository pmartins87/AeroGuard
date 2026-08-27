from pathlib import Path

import pytest

from aeroguard.datasets.coco_export import export_voc_subset_to_coco, source_class_names


VOC_TEMPLATE = """<annotation>
  <filename>{filename}</filename>
  <size><width>300</width><height>300</height><depth>3</depth></size>
  {objects}
</annotation>
"""
OBJ_TEMPLATE = """<object>
  <name>{name}</name>
  <bndbox><xmin>{xmin}</xmin><ymin>{ymin}</ymin><xmax>{xmax}</xmax><ymax>{ymax}</ymax></bndbox>
</object>"""


def _write_sample(root: Path, image_id: str, objects: list[dict]) -> None:
    annotations = root / "VOC2007" / "Annotations"
    images = root / "VOC2007" / "JPEGImages"
    annotations.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)
    object_xml = "\n".join(OBJ_TEMPLATE.format(**obj) for obj in objects)
    (annotations / f"{image_id}.xml").write_text(
        VOC_TEMPLATE.format(filename=f"{image_id}.jpg", objects=object_xml),
        encoding="utf-8",
    )
    (images / f"{image_id}.jpg").write_bytes(b"fixture")


def test_source_classes_and_coco_export_are_deterministic(tmp_path: Path):
    _write_sample(
        tmp_path,
        "b",
        [{"name": "Rock", "xmin": 1.5, "ymin": 2.5, "xmax": 11.5, "ymax": 12.5}],
    )
    _write_sample(
        tmp_path,
        "a",
        [
            {"name": "Bolt", "xmin": 10, "ymin": 20, "xmax": 30, "ymax": 50},
            {"name": "Rock", "xmin": 100, "ymin": 120, "xmax": 140, "ymax": 160},
        ],
    )

    classes = source_class_names(tmp_path)
    assert classes == ("Bolt", "Rock")

    result = export_voc_subset_to_coco(tmp_path, ("b", "a"), class_names=classes)
    payload = result.payload
    assert [image["aeroguard_source_id"] for image in payload["images"]] == ["a", "b"]
    assert [category["name"] for category in payload["categories"]] == ["Bolt", "Rock"]
    assert len(payload["annotations"]) == 3

    # Fractional source geometry remains fractional in COCO bbox format.
    rock_b = next(
        item
        for item in payload["annotations"]
        if item["image_id"] == 2 and item["aeroguard_source_label"] == "Rock"
    )
    assert rock_b["bbox"] == pytest.approx([1.5, 2.5, 10.0, 10.0])


def test_missing_member_annotation_fails_closed(tmp_path: Path):
    _write_sample(
        tmp_path,
        "a",
        [{"name": "Bolt", "xmin": 1, "ymin": 2, "xmax": 11, "ymax": 12}],
    )
    with pytest.raises(ValueError, match="missing annotations"):
        export_voc_subset_to_coco(tmp_path, ("a", "missing"), class_names=("Bolt",))


def test_missing_source_image_fails_closed(tmp_path: Path):
    _write_sample(
        tmp_path,
        "a",
        [{"name": "Bolt", "xmin": 1, "ymin": 2, "xmax": 11, "ymax": 12}],
    )
    (tmp_path / "VOC2007" / "JPEGImages" / "a.jpg").unlink()
    with pytest.raises(FileNotFoundError, match="source image not found"):
        export_voc_subset_to_coco(tmp_path, ("a",), class_names=("Bolt",))


def test_unknown_source_label_in_frozen_classes_is_rejected(tmp_path: Path):
    _write_sample(
        tmp_path,
        "a",
        [{"name": "Rock", "xmin": 1, "ymin": 2, "xmax": 11, "ymax": 12}],
    )
    with pytest.raises(ValueError, match="source label absent"):
        export_voc_subset_to_coco(tmp_path, ("a",), class_names=("Bolt",))
