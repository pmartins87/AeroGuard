from pathlib import Path

import pytest

from aeroguard.datasets.split import hash_ids, labels_by_image, make_class_aware_dev_split


VOC_TEMPLATE = """<annotation>
  <filename>{filename}</filename>
  <size><width>300</width><height>300</height><depth>3</depth></size>
  {objects}
</annotation>
"""
OBJ_TEMPLATE = """<object>
  <name>{name}</name>
  <bndbox><xmin>1</xmin><ymin>2</ymin><xmax>11</xmax><ymax>12</ymax></bndbox>
</object>"""


def _write(path: Path, image_id: str, labels: list[str]) -> None:
    objects = "\n".join(OBJ_TEMPLATE.format(name=label) for label in labels)
    path.write_text(VOC_TEMPLATE.format(filename=f"{image_id}.jpg", objects=objects), encoding="utf-8")


def test_class_aware_split_is_deterministic_and_disjoint():
    labels = {
        "a": frozenset({"common"}),
        "b": frozenset({"common"}),
        "c": frozenset({"common", "rare"}),
        "d": frozenset({"common", "rare"}),
        "e": frozenset({"common"}),
        "f": frozenset({"singleton"}),
        "g": frozenset({"common"}),
        "h": frozenset({"common"}),
        "i": frozenset({"common"}),
        "j": frozenset({"common"}),
    }
    one = make_class_aware_dev_split(labels, val_fraction=0.2, seed=7)
    two = make_class_aware_dev_split(labels, val_fraction=0.2, seed=7)

    assert one == two
    assert len(one.val_ids) == 2
    assert set(one.train_ids).isdisjoint(one.val_ids)
    assert set(one.train_ids) | set(one.val_ids) == set(labels)
    assert "f" in one.train_ids  # singleton label is not intentionally consumed by validation
    assert any("rare" in labels[image_id] for image_id in one.val_ids)


def test_split_hash_changes_with_membership():
    assert hash_ids(("a", "b")) == hash_ids(("a", "b"))
    assert hash_ids(("a", "b")) != hash_ids(("a", "c"))


def test_labels_by_image_reads_requested_source_ids(tmp_path: Path):
    annotations = tmp_path / "VOC2007" / "Annotations"
    annotations.mkdir(parents=True)
    _write(annotations / "a.xml", "a", ["Bolt", "Nut"])
    _write(annotations / "b.xml", "b", ["Bolt"])

    result = labels_by_image(tmp_path, ("b", "a"))
    assert result == {"b": frozenset({"Bolt"}), "a": frozenset({"Bolt", "Nut"})}


def test_labels_by_image_fails_on_missing_annotation(tmp_path: Path):
    annotations = tmp_path / "VOC2007" / "Annotations"
    annotations.mkdir(parents=True)
    _write(annotations / "a.xml", "a", ["Bolt"])

    with pytest.raises(ValueError, match="missing annotations"):
        labels_by_image(tmp_path, ("a", "missing"))


def test_bad_val_fraction_rejected():
    labels = {"a": frozenset({"x"}), "b": frozenset({"x"})}
    with pytest.raises(ValueError, match="val_fraction"):
        make_class_aware_dev_split(labels, val_fraction=1.0)
