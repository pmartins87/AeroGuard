#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aeroguard.datasets.foda import discover_source_splits, load_split_members, sha256_file
from aeroguard.datasets.split import labels_by_image, make_class_aware_dev_split


def _find_unique(root: Path, relative_suffix: str) -> Path:
    matches = sorted(path for path in root.rglob(Path(relative_suffix).name) if str(path).endswith(relative_suffix))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {relative_suffix}, found {len(matches)}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Derive a deterministic class-aware train/validation split inside FOD-A source trainval.txt."
    )
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--val-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/foda_dev_split"))
    args = parser.parse_args()

    source = discover_source_splits(args.dataset_root)
    coverage = source.get("coverage")
    if not coverage:
        raise RuntimeError("source trainval/test split audit is incomplete")
    if any(
        coverage[key] != 0
        for key in ("trainval_test_overlap", "missing_annotation_ids", "extra_split_ids")
    ):
        raise RuntimeError(f"source split coverage gate failed: {coverage}")

    trainval_path = _find_unique(args.dataset_root, "ImageSets/Main/trainval.txt")
    source_ids = load_split_members(trainval_path)
    image_labels = labels_by_image(args.dataset_root, source_ids)
    derived = make_class_aware_dev_split(
        image_labels,
        val_fraction=args.val_fraction,
        seed=args.seed,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.output_dir / "train.txt"
    val_path = args.output_dir / "val.txt"
    train_path.write_text("".join(f"{image_id}\n" for image_id in derived.train_ids), encoding="utf-8")
    val_path.write_text("".join(f"{image_id}\n" for image_id in derived.val_ids), encoding="utf-8")

    manifest = {
        "schema": "aeroguard.foda.dev_split.v1",
        "policy": "class-aware deterministic partition derived only inside source trainval.txt; source test.txt remains held out",
        "source_trainval": {
            "relative_path": str(trainval_path.relative_to(args.dataset_root)),
            "count": len(source_ids),
            "sha256": sha256_file(trainval_path),
        },
        "derived": derived.as_dict(),
        "files": {
            "train": {"path": str(train_path), "sha256": sha256_file(train_path)},
            "val": {"path": str(val_path), "sha256": sha256_file(val_path)},
        },
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
