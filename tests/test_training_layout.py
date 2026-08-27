from __future__ import annotations

import json
from pathlib import Path

import pytest

from aeroguard.datasets.training_layout import materialize_yolox_coco_layout


def _write_sample(root: Path, image_id: str, filename: str, label: str, *, xmin: float = 1.5) -> None:
    annotations = root / "VOC" / "Annotations"
    images = root / "VOC" / "JPEGImages"
    annotations.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)
    (images / filename).write_bytes(b"synthetic-image-bytes")
    (annotations / f"{image_id}.xml").write_text(
        f"""<annotation>
  <filename>{filename}</filename>
  <size><width>300</width><height>300</height><depth>3</depth></size>
  <object>
    <name>{label}</name>
    <bndbox><xmin>{xmin}</xmin><ymin>2.25</ymin><xmax>20.5</xmax><ymax>25.75</ymax></bndbox>
  </object>
</annotation>
""",
        encoding="utf-8",
    )


def test_materialize_yolox_coco_layout(tmp_path: Path) -> None:
    source = tmp_path / "source"
    _write_sample(source, "a", "a.jpg", "metal")
    _write_sample(source, "b", "b.jpg", "plastic")
    _write_sample(source, "c", "c.jpg", "metal", xmin=3.75)
    _write_sample(source, "d", "d.jpg", "plastic")

    output = tmp_path / "prepared"
    result = materialize_yolox_coco_layout(
        source,
        train_ids=("b", "a"),
        val_ids=("d", "c"),
        output_root=output,
        mode="copy",
    )

    assert (output / "train2017" / "a.jpg").is_file()
    assert (output / "train2017" / "b.jpg").is_file()
    assert (output / "val2017" / "c.jpg").is_file()
    assert (output / "val2017" / "d.jpg").is_file()

    train = json.loads((output / "annotations" / "instances_train2017.json").read_text(encoding="utf-8"))
    val = json.loads((output / "annotations" / "instances_val2017.json").read_text(encoding="utf-8"))
    assert [category["name"] for category in train["categories"]] == ["metal", "plastic"]
    assert train["images"][0]["aeroguard_source_id"] == "a"
    assert val["annotations"][0]["bbox"][0] == pytest.approx(3.75)

    manifest = result.manifest
    assert manifest["class_count"] == 2
    assert manifest["train"]["image_count"] == 2
    assert manifest["val"]["image_count"] == 2
    assert manifest["train"]["materialization"] == {"hardlink": 0, "copy": 2}
    assert result.manifest_path.is_file()


def test_materialize_rejects_train_val_overlap(tmp_path: Path) -> None:
    source = tmp_path / "source"
    _write_sample(source, "a", "a.jpg", "metal")
    _write_sample(source, "b", "b.jpg", "plastic")

    with pytest.raises(ValueError, match="overlap"):
        materialize_yolox_coco_layout(
            source,
            train_ids=("a",),
            val_ids=("a", "b"),
            output_root=tmp_path / "prepared",
            mode="copy",
        )
