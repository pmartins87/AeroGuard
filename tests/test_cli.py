from pathlib import Path

from aeroguard.cli import analyze_video
from aeroguard.fixture import generate_fixture


def test_demo_writes_trace_video_and_evidence(tmp_path: Path):
    video = generate_fixture(tmp_path / "fixture.mp4")
    payload = analyze_video(
        video,
        tmp_path / "events.json",
        output_video=tmp_path / "annotated.mp4",
        evidence_dir=tmp_path / "evidence",
    )
    assert payload["events"]
    assert (tmp_path / "events.json").exists()
    assert (tmp_path / "annotated.mp4").stat().st_size > 0
    assert any((tmp_path / "evidence").glob("*.jpg"))
    assert any(event.get("evidence_crop") for event in payload["events"])
