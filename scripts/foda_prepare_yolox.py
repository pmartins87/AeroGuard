#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aeroguard.datasets.foda import load_split_members, sha256_file
from aeroguard.datasets.training_layout import materialize_yolox_coco_layout


def _limited(ids: tuple[str, ...], limit: int | None) -> tuple[str, ...]:
    ordered = tuple(sorted(ids))
    if limit is None:
        return ordered
    if limit <= 0:
        raise ValueError("limits must be positive")
    return ordered[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize frozen FOD-A development IDs as a YOLOX-compatible COCO directory."
    )
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("train_ids", type=Path)
    parser.add_argument("val_ids", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--limit-train", type=int, default=None)
    parser.add_argument("--limit-val", type=int, default=None)
    parser.add_argument("--mode", choices=("auto", "hardlink", "copy"), default="auto")
    args = parser.parse_args()

    source_train = load_split_members(args.train_ids)
    source_val = load_split_members(args.val_ids)
    train = _limited(source_train, args.limit_train)
    val = _limited(source_val, args.limit_val)

    result = materialize_yolox_coco_layout(
        args.dataset_root,
        train,
        val,
        args.output_root,
        mode=args.mode,
    )
    manifest = dict(result.manifest)
    manifest["source_id_files"] = {
        "train": {
            "path": str(args.train_ids),
            "full_count": len(source_train),
            "effective_count": len(train),
            "sha256": sha256_file(args.train_ids),
        },
        "val": {
            "path": str(args.val_ids),
            "full_count": len(source_val),
            "effective_count": len(val),
            "sha256": sha256_file(args.val_ids),
        },
    }
    result.manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
