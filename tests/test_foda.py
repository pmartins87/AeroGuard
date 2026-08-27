from pathlib import Path

import pytest

from aeroguard.datasets.foda import (
    discover_source_splits,
    parse_voc_annotation,
    sha256_file,
    summarize_voc_dataset,
    verify_split_members,
)


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


def _write_annotation(path: Path, filename: str, objects: list[dict]) -> None:
    object_xml = "\n".join(OBJ_TEMPLATE.format(**obj) for obj in objects)
    path.write_text(VOC_TEMPLATE.format(filename=filename, objects=object_xml), encoding="utf-8")


def test_parse_voc_annotation_and_summary(tmp_path: Path):
    annotations = tmp_path / "VOC2007" / "Annotations"
    annotations.mkdir(parents=True)
    _write_annotation(
        annotations / "a.xml",
        "a.jpg",
        [{"name": "bolt", "xmin": 10, "ymin": 20, "xmax": 30, "ymax": 50}],
    )
    _write_annotation(
        annotations / "b.xml",
        "b.jpg",
        [
            {"name": "bolt", "xmin": 1, "ymin": 2, "xmax": 11, "ymax": 12},
            {"name": "stone", "xmin": 100, "ymin": 120, "xmax": 140, "ymax": 160},
        ],
    )

    one = parse_voc_annotation(annotations / "a.xml")
    assert one.filename == "a.jpg"
    assert one.objects[0].area == 600

    summary = summarize_voc_dataset(tmp_path)
    assert summary.annotation_files == 2
    assert summary.total_objects == 3
    assert summary.class_count == 2
    assert summary.class_counts == {"bolt": 2, "stone": 1}
    assert summary.image_widths == (300,)
    assert summary.image_heights == (300,)


def test_fractional_coordinates_are_preserved(tmp_path: Path):
    xml = tmp_path / "fractional.xml"
    _write_annotation(
        xml,
        "fractional.jpg",
        [{"name": "metal", "xmin": 138.2219, "ymin": 10.5, "xmax": 160.75, "ymax": 40.25}],
    )
    annotation = parse_voc_annotation(xml)
    box = annotation.objects[0]
    assert box.xmin == pytest.approx(138.2219)
    assert box.ymax == pytest.approx(40.25)
    assert box.area > 0


def test_invalid_box_is_rejected(tmp_path: Path):
    xml = tmp_path / "bad.xml"
    _write_annotation(
        xml,
        "bad.jpg",
        [{"name": "bad", "xmin": 20, "ymin": 20, "xmax": 10, "ymax": 30}],
    )
    with pytest.raises(ValueError, match="invalid bounding box"):
        parse_voc_annotation(xml)


def test_source_trainval_test_split_discovery_and_coverage(tmp_path: Path):
    annotations = tmp_path / "VOC2007" / "Annotations"
    annotations.mkdir(parents=True)
    for image_id in ("a", "b", "c"):
        _write_annotation(
            annotations / f"{image_id}.xml",
            f"{image_id}.jpg",
            [{"name": "bolt", "xmin": 1, "ymin": 2, "xmax": 11, "ymax": 12}],
        )

    split_dir = tmp_path / "VOC2007" / "ImageSets" / "Main"
    split_dir.mkdir(parents=True)
    (split_dir / "trainval.txt").write_text("a\nb\n", encoding="utf-8")
    (split_dir / "test.txt").write_text("c\n", encoding="utf-8")

    assert verify_split_members(tmp_path) == {"trainval": 2, "test": 1}
    details = discover_source_splits(tmp_path)
    assert details["trainval"]["count"] == 2
    assert details["test"]["count"] == 1
    assert details["coverage"]["annotation_ids"] == 3
    assert details["coverage"]["covered_annotation_ids"] == 3
    assert details["coverage"]["trainval_test_overlap"] == 0
    assert details["coverage"]["missing_annotation_ids"] == 0
    assert details["coverage"]["extra_split_ids"] == 0


def test_split_duplicate_guard(tmp_path: Path):
    split_dir = tmp_path / "VOC2007" / "ImageSets" / "Main"
    split_dir.mkdir(parents=True)
    (split_dir / "trainval.txt").write_text("a\na\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate IDs"):
        verify_split_members(tmp_path)


def test_sha256_file(tmp_path: Path):
    payload = tmp_path / "archive.bin"
    payload.write_bytes(b"aeroguard")
    assert sha256_file(payload) == "6ad1b087cdcc74008f080b2c7cf1168b5c8c63556dd6ce70523f51d88b12a8c1"
