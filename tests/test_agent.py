from aeroguard.agent import run_agent
from aeroguard.types import Candidate


def c(*, contrast: float, area: int, persistence: int) -> Candidate:
    return Candidate(10, 10, 10, 10, 10, area, contrast, persistence)


def test_low_evidence_closes():
    trace = run_agent(c(contrast=5, area=20, persistence=1))
    assert trace.decision == "close"
    assert [s.tool for s in trace.steps] == ["inspect_crop"]


def test_medium_evidence_reinspects():
    trace = run_agent(c(contrast=40, area=80, persistence=2))
    assert trace.decision == "reinspect"
    assert trace.steps[-1].tool == "inspect_temporal_window"


def test_persistent_strong_evidence_requests_human():
    trace = run_agent(c(contrast=50, area=100, persistence=4))
    assert trace.decision == "human_review"
    assert trace.steps[-1].tool == "request_human_review"
