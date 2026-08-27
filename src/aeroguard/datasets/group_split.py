from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import random
from typing import Iterable, Mapping

SPLITS = ("train", "val", "test")
DEFAULT_TARGET = {"train": 0.70, "val": 0.15, "test": 0.15}


@dataclass(frozen=True)
class GroupSummary:
    """Atomic leakage group used by the deterministic split optimizer."""

    key: str
    size: int
    label_counts: Mapping[str, int]
    environment_counts: Mapping[str, int]


def _group_presence(groups: Iterable[GroupSummary]) -> Counter[str]:
    result: Counter[str] = Counter()
    for group in groups:
        for label, count in group.label_counts.items():
            if count > 0:
                result[label] += 1
    return result


def _summarize_assignment(
    groups: list[GroupSummary], assignment: list[str]
) -> tuple[Counter[str], dict[str, Counter[str]], dict[str, Counter[str]]]:
    sizes: Counter[str] = Counter()
    labels = {split: Counter() for split in SPLITS}
    envs = {split: Counter() for split in SPLITS}
    for group, split in zip(groups, assignment):
        sizes[split] += group.size
        labels[split].update(group.label_counts)
        envs[split].update(group.environment_counts)
    return sizes, labels, envs


def _objective(
    groups: list[GroupSummary],
    assignment: list[str],
    target: Mapping[str, float],
    group_presence: Mapping[str, int],
) -> float:
    sizes, labels, envs = _summarize_assignment(groups, assignment)
    total_images = sum(group.size for group in groups)
    if total_images <= 0:
        return math.inf

    score = 0.0
    # Image-count balance is important, but class/group integrity is more important.
    for split in SPLITS:
        frac = sizes[split] / total_images
        denom = max(float(target[split]), 1e-9)
        score += 25.0 * ((frac - target[split]) / denom) ** 2

    total_label_counts: Counter[str] = Counter()
    total_env_counts: Counter[str] = Counter()
    for group in groups:
        total_label_counts.update(group.label_counts)
        total_env_counts.update(group.environment_counts)

    for label, total in total_label_counts.items():
        if total <= 0:
            continue
        for split in SPLITS:
            frac = labels[split][label] / total
            score += 1.5 * (frac - target[split]) ** 2

        # Every trained class must be represented in train.
        if labels["train"][label] <= 0:
            score += 1_000_000.0

        # When group structure makes independent validation/test coverage feasible,
        # heavily prefer it. For two-group classes, prioritize independent test.
        n_groups = int(group_presence[label])
        if n_groups >= 3:
            if labels["val"][label] <= 0:
                score += 25_000.0
            if labels["test"][label] <= 0:
                score += 25_000.0
        elif n_groups == 2:
            if labels["test"][label] <= 0:
                score += 10_000.0

    for env, total in total_env_counts.items():
        if total <= 0:
            continue
        for split in SPLITS:
            frac = envs[split][env] / total
            score += 0.5 * (frac - target[split]) ** 2

    return score


def assign_groups(
    groups: Iterable[GroupSummary],
    *,
    seed: int = 20260826,
    target: Mapping[str, float] = DEFAULT_TARGET,
    iterations: int = 50_000,
) -> dict[str, str]:
    """Assign atomic groups to train/val/test deterministically.

    The optimizer never splits a group. Groups that are the sole source of a
    class are forced into train so the detector can learn every declared class.
    A seeded local search then balances image volume, class coverage, and
    environment coverage while strongly preferring independent val/test class
    coverage whenever the number of groups makes that possible.
    """

    group_list = sorted(list(groups), key=lambda g: g.key)
    if not group_list:
        raise ValueError("at least one group is required")
    if any(group.size <= 0 for group in group_list):
        raise ValueError("group sizes must be positive")
    if set(target) != set(SPLITS):
        raise ValueError(f"target keys must be {SPLITS}")
    if abs(sum(float(target[s]) for s in SPLITS) - 1.0) > 1e-9:
        raise ValueError("target fractions must sum to 1")

    presence = _group_presence(group_list)
    forced_train: set[int] = set()
    singleton_labels = {label for label, n in presence.items() if n == 1}
    for idx, group in enumerate(group_list):
        if singleton_labels.intersection(group.label_counts):
            forced_train.add(idx)

    rng = random.Random(seed)
    assignment = ["train" if i in forced_train else "train" for i in range(len(group_list))]

    # Give each class a train anchor. Prefer smaller groups to leave large groups
    # available for balancing and independent evaluation.
    labels = sorted(presence, key=lambda label: (presence[label], label))
    for label in labels:
        candidates = [
            i
            for i, group in enumerate(group_list)
            if group.label_counts.get(label, 0) > 0
        ]
        if not candidates:
            continue
        if not any(assignment[i] == "train" and i in forced_train for i in candidates):
            chosen = min(candidates, key=lambda i: (group_list[i].size, group_list[i].key))
            forced_train.add(chosen)
            assignment[chosen] = "train"

    # Seed non-forced groups according to target volume with a class-aware bias.
    mutable = [i for i in range(len(group_list)) if i not in forced_train]
    rng.shuffle(mutable)
    for idx in mutable:
        best_split = None
        best_score = math.inf
        for split in SPLITS:
            assignment[idx] = split
            value = _objective(group_list, assignment, target, presence)
            if value < best_score - 1e-12 or (
                abs(value - best_score) <= 1e-12 and (best_split is None or split < best_split)
            ):
                best_score = value
                best_split = split
        assignment[idx] = best_split or "train"

    best = list(assignment)
    best_score = _objective(group_list, best, target, presence)

    # Deterministic seeded hill-climb over moves and occasional pair swaps.
    for step in range(max(0, iterations)):
        trial = list(best)
        if len(mutable) >= 2 and step % 5 == 0:
            a, b = rng.sample(mutable, 2)
            if trial[a] == trial[b]:
                continue
            trial[a], trial[b] = trial[b], trial[a]
        elif mutable:
            idx = rng.choice(mutable)
            alternatives = [s for s in SPLITS if s != trial[idx]]
            trial[idx] = rng.choice(alternatives)
        else:
            break

        value = _objective(group_list, trial, target, presence)
        if value < best_score - 1e-12:
            best = trial
            best_score = value

    return {group.key: split for group, split in zip(group_list, best)}


def assignment_summary(
    groups: Iterable[GroupSummary], assignment_by_key: Mapping[str, str]
) -> dict:
    group_list = sorted(list(groups), key=lambda g: g.key)
    assignment = [assignment_by_key[group.key] for group in group_list]
    sizes, labels, envs = _summarize_assignment(group_list, assignment)
    presence = _group_presence(group_list)
    return {
        "images": {split: sizes[split] for split in SPLITS},
        "groups": {
            split: sum(1 for value in assignment if value == split) for split in SPLITS
        },
        "label_counts": {split: dict(sorted(labels[split].items())) for split in SPLITS},
        "environment_counts": {split: dict(sorted(envs[split].items())) for split in SPLITS},
        "label_group_presence": dict(sorted(presence.items())),
        "labels_missing_from_train": sorted(
            label for label in presence if labels["train"][label] <= 0
        ),
        "labels_missing_from_val": sorted(
            label for label in presence if labels["val"][label] <= 0
        ),
        "labels_missing_from_test": sorted(
            label for label in presence if labels["test"][label] <= 0
        ),
    }
