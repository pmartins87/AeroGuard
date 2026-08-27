from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Mapping, Sequence

from .foda import find_voc_annotations, parse_voc_annotation


@dataclass(frozen=True)
class DevSplit:
    train_ids: tuple[str, ...]
    val_ids: tuple[str, ...]
    seed: int
    val_fraction: float

    def as_dict(self) -> dict:
        return {
            "seed": self.seed,
            "val_fraction": self.val_fraction,
            "train_count": len(self.train_ids),
            "val_count": len(self.val_ids),
            "train_ids_sha256": hash_ids(self.train_ids),
            "val_ids_sha256": hash_ids(self.val_ids),
        }


def hash_ids(ids: Sequence[str]) -> str:
    """Hash an ordered ID list using a canonical newline-delimited encoding."""
    payload = "".join(f"{image_id}\n" for image_id in ids).encode("utf-8")
    return sha256(payload).hexdigest()


def _stable_rank(seed: int, image_id: str) -> str:
    return sha256(f"{seed}:{image_id}".encode("utf-8")).hexdigest()


def labels_by_image(root: str | Path, member_ids: Sequence[str]) -> dict[str, frozenset[str]]:
    """Return raw VOC label sets for the requested annotation IDs.

    Missing source IDs fail closed because silently dropping them would alter the
    benchmark population.
    """
    wanted = set(member_ids)
    annotation_paths = {path.stem: path for path in find_voc_annotations(root) if path.stem in wanted}
    missing = sorted(wanted - annotation_paths.keys())
    if missing:
        raise ValueError(f"missing annotations for {len(missing)} split IDs; examples: {missing[:10]}")

    result: dict[str, frozenset[str]] = {}
    for image_id in member_ids:
        annotation = parse_voc_annotation(annotation_paths[image_id])
        result[image_id] = frozenset(obj.name for obj in annotation.objects)
    return result


def _validation_targets(
    image_labels: Mapping[str, frozenset[str]],
    val_fraction: float,
) -> dict[str, int]:
    label_image_counts: Counter[str] = Counter()
    for labels in image_labels.values():
        label_image_counts.update(labels)

    targets: dict[str, int] = {}
    for label, count in label_image_counts.items():
        # Singletons stay in development-train. For labels seen in >=2 images,
        # allocate at least one validation example when validation is non-empty,
        # but never consume every image of a label.
        if count < 2:
            targets[label] = 0
            continue
        raw = int(round(count * val_fraction))
        targets[label] = min(count - 1, max(1, raw))
    return targets


def make_class_aware_dev_split(
    image_labels: Mapping[str, frozenset[str]],
    *,
    val_fraction: float = 0.2,
    seed: int = 20260826,
) -> DevSplit:
    """Create a deterministic validation slice from a source trainval population.

    The algorithm prioritizes underrepresented labels in validation while keeping
    singleton labels in train. It is intentionally dependency-free and records a
    seed plus hashes so a later benchmark can prove the exact partition.
    """
    if not 0.0 < val_fraction < 1.0:
        raise ValueError("val_fraction must be between 0 and 1")
    if not image_labels:
        raise ValueError("image_labels cannot be empty")

    ids = tuple(sorted(image_labels))
    target_val_size = max(1, min(len(ids) - 1, int(round(len(ids) * val_fraction))))
    targets = _validation_targets(image_labels, val_fraction)
    selected: set[str] = set()
    selected_counts: Counter[str] = Counter()

    label_frequency = Counter()
    for labels in image_labels.values():
        label_frequency.update(labels)

    # Rare labels are serviced first. Within a label, prefer images that satisfy
    # the largest number of still-unmet label targets, then use a stable hash.
    for label in sorted(targets, key=lambda x: (label_frequency[x], x)):
        while selected_counts[label] < targets[label] and len(selected) < target_val_size:
            candidates = [
                image_id
                for image_id, labels in image_labels.items()
                if image_id not in selected and label in labels
            ]
            if not candidates:
                break

            def candidate_key(image_id: str) -> tuple[float, str]:
                benefit = 0.0
                for image_label in image_labels[image_id]:
                    deficit = targets.get(image_label, 0) - selected_counts[image_label]
                    if deficit > 0:
                        benefit += deficit / max(1, label_frequency[image_label])
                return (-benefit, _stable_rank(seed, image_id))

            choice = min(candidates, key=candidate_key)
            selected.add(choice)
            selected_counts.update(image_labels[choice])

    # Fill any remaining validation capacity deterministically. Prefer images
    # whose labels are still below target, then stable hash order.
    if len(selected) < target_val_size:
        remaining = [image_id for image_id in ids if image_id not in selected]

        def fill_key(image_id: str) -> tuple[float, str]:
            unmet = sum(
                max(0, targets.get(label, 0) - selected_counts[label])
                / max(1, label_frequency[label])
                for label in image_labels[image_id]
            )
            return (-unmet, _stable_rank(seed, image_id))

        for image_id in sorted(remaining, key=fill_key)[: target_val_size - len(selected)]:
            selected.add(image_id)
            selected_counts.update(image_labels[image_id])

    val_ids = tuple(sorted(selected))
    train_ids = tuple(image_id for image_id in ids if image_id not in selected)

    if set(train_ids) & set(val_ids):
        raise AssertionError("derived train/val overlap")
    if len(train_ids) + len(val_ids) != len(ids):
        raise AssertionError("derived split does not cover source population")

    return DevSplit(train_ids, val_ids, seed, val_fraction)
