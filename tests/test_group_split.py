from aeroguard.datasets.group_split import GroupSummary, assign_groups, assignment_summary


def g(key, size, labels, env="dry|bright"):
    return GroupSummary(
        key=key,
        size=size,
        label_counts={label: size for label in labels},
        environment_counts={env: size},
    )


def test_assignment_is_deterministic_and_atomic():
    groups = [
        g("g0", 100, ["a"]),
        g("g1", 90, ["a"]),
        g("g2", 80, ["a"]),
        g("g3", 100, ["b"]),
        g("g4", 90, ["b"]),
        g("g5", 80, ["b"]),
        g("g6", 50, ["a", "b"]),
    ]
    first = assign_groups(groups, seed=7, iterations=2000)
    second = assign_groups(groups, seed=7, iterations=2000)
    assert first == second
    assert set(first) == {group.key for group in groups}
    assert set(first.values()) <= {"train", "val", "test"}


def test_single_group_class_is_forced_to_train():
    groups = [
        g("only_rare", 20, ["rare"]),
        g("c0", 100, ["common"]),
        g("c1", 100, ["common"]),
        g("c2", 100, ["common"]),
        g("c3", 100, ["common"]),
    ]
    assignment = assign_groups(groups, seed=1, iterations=3000)
    assert assignment["only_rare"] == "train"
    summary = assignment_summary(groups, assignment)
    assert summary["labels_missing_from_train"] == []


def test_three_group_class_prefers_independent_val_and_test_coverage():
    groups = [
        g("a0", 100, ["a"]),
        g("a1", 100, ["a"]),
        g("a2", 100, ["a"]),
        g("a3", 100, ["a"]),
        g("b0", 100, ["b"]),
        g("b1", 100, ["b"]),
        g("b2", 100, ["b"]),
        g("b3", 100, ["b"]),
    ]
    assignment = assign_groups(groups, seed=9, iterations=8000)
    summary = assignment_summary(groups, assignment)
    assert summary["labels_missing_from_train"] == []
    assert summary["labels_missing_from_val"] == []
    assert summary["labels_missing_from_test"] == []
