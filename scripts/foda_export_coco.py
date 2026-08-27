#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aeroguard.datasets.coco_export import export_voc_subset_to_coco, source_class_names
from aeroguard.datasets.foda import load_split_members, sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a frozen FOD-A VOC ID subset to deterministic COCO JSON.")
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("ids_file", type=Path, help="newline-delimited source image IDs")
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--classes-output", type=Path, default=None)
    parser.add_argument("--skip-image-check", action="store_true")
    args = parser.parse_args()

    ids = load_split_members(args.ids_file)
    classes = source_class_names(args.dataset_root)
    result = export_voc_subset_to_coco(
        args.dataset_root,
        ids,
        class_names=classes,
        verify_images=not args.skip_image_check,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result.payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    classes_output = args.classes_output or args.output_json.with_suffix(".classes.txt")
    classes_output.write_text("".join(f"{name}\n" for name in result.class_names), encoding="utf-8")

    summary = {
        "ids_file": str(args.ids_file),
        "ids_file_sha256": sha256_file(args.ids_file),
        "image_count": len(result.payload["images"]),
        "annotation_count": len(result.payload["annotations"]),
        "class_count": len(result.class_names),
        "output_json": str(args.output_json),
        "output_json_sha256": sha256_file(args.output_json),
        "classes_output": str(classes_output),
        "classes_sha256": sha256_file(classes_output),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
