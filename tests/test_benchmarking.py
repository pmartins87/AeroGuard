import pytest

from aeroguard.benchmarking import timing_summary


def test_timing_summary_is_deterministic():
    result = timing_summary([1.0, 2.0, 3.0, 4.0])
    assert result["count"] == 4
    assert result["min_ms"] == 1.0
    assert result["mean_ms"] == 2.5
    assert result["p50_ms"] == 2.5
    assert result["max_ms"] == 4.0
    assert result["stdev_ms"] > 0.0


def test_timing_summary_rejects_empty_input():
    with pytest.raises(ValueError):
        timing_summary([])
