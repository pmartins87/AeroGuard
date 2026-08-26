import numpy as np

from aeroguard.vision import build_reference, detect_candidates


def test_detects_inserted_dark_object():
    clean = np.full((120, 160, 3), 120, dtype=np.uint8)
    reference = build_reference([clean.copy() for _ in range(5)])
    frame = clean.copy()
    frame[60:72, 90:108] = 20
    candidates = detect_candidates(frame, reference, 10, threshold=20, min_area=10)
    assert candidates
    best = max(candidates, key=lambda x: x.area)
    assert best.x <= 90 <= best.x + best.w
    assert best.y <= 60 <= best.y + best.h
