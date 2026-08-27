import pytest

from aeroguard.benchmarking import numeric_summary, timing_summary


def test_timing_summary_is_deterministic():
    result = timing_summary([1.0, 2.0, 3.0, 4.0])
    assert result["count"] == 4
    assert result["min_ms"] == 1.0
    assert result["mean_ms"] == 2.5
    assert result["p50_ms"] == 2.5
    assert result["max_ms"] == 4.0
    assert result["stdev_ms"] > 0.0


def test_numeric_summary_does_not_mislabel_units():
    result = numeric_summary([100.0, 200.0, 300.0])
    assert result["count"] == 3
    assert result["mean"] == 200.0
    assert result["p50"] == 200.0
    assert result["max"] == 300.0
    assert "mean_ms" not in result


def test_summaries_reject_empty_input():
    with pytest.raises(ValueError):
        timing_summary([])
    with pytest.raises(ValueError):
        numeric_summary([])
