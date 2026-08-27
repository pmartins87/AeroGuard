#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aeroguard.datasets.foda import discover_source_splits, sha256_file, summarize_voc_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect an extracted FOD-A Pascal VOC dataset.")
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--archive", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("artifacts/foda_manifest.json"))
    args = parser.parse_args()

    summary = summarize_voc_dataset(args.dataset_root)
    payload = {
        "dataset": "FOD-A",
        "source_version": "2.1 Pascal VOC",
        "dataset_root": str(args.dataset_root.resolve()),
        "summary": summary.as_dict(),
        "source_splits": discover_source_splits(args.dataset_root),
    }
    if args.archive is not None:
        payload["archive"] = {
            "path": str(args.archive.resolve()),
            "bytes": args.archive.stat().st_size,
            "sha256": sha256_file(args.archive),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
