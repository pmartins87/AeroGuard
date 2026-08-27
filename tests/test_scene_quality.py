import numpy as np

from aeroguard.scene_quality import measure_scene_quality


def test_flat_dark_frame_has_zero_dynamic_range_and_entropy():
    frame = np.zeros((64, 64, 3), dtype=np.uint8)
    metrics = measure_scene_quality(frame)
    assert metrics.mean_luma == 0.0
    assert metrics.dynamic_range == 0.0
    assert metrics.laplacian_variance == 0.0
    assert metrics.dark_fraction == 1.0
    assert metrics.clipped_high_fraction == 0.0
    assert metrics.entropy_bits == 0.0


def test_checkerboard_is_sharp_and_high_information():
    base = (np.indices((64, 64)).sum(axis=0) % 2 * 255).astype(np.uint8)
    frame = np.dstack([base, base, base])
    metrics = measure_scene_quality(frame)
    assert 120.0 < metrics.mean_luma < 135.0
    assert metrics.dynamic_range == 255.0
    assert metrics.laplacian_variance > 1000.0
    assert metrics.entropy_bits == 1.0


def test_float_input_is_clipped_deterministically():
    frame = np.array([[-10.0, 10.0], [260.0, 120.0]], dtype=np.float32)
    metrics = measure_scene_quality(frame)
    assert 0.0 <= metrics.mean_luma <= 255.0
    assert 0.0 <= metrics.dark_fraction <= 1.0
    assert 0.0 <= metrics.clipped_high_fraction <= 1.0
