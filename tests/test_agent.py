from aeroguard.agent import run_agent
from aeroguard.agent_scenarios import AGENT_SCENARIOS, evaluate_agent_scenarios
from aeroguard.types import Candidate


def c(*, contrast: float, area: int, persistence: int) -> Candidate:
    return Candidate(10, 10, 10, 10, 10, area, contrast, persistence)


def test_low_evidence_closes_through_explicit_finalizer():
    trace = run_agent(c(contrast=5, area=20, persistence=1))
    assert trace.decision == "close"
    assert [s.tool for s in trace.steps] == ["inspect_frame", "inspect_crop", "close_or_escalate_event"]


def test_medium_evidence_reinspects_temporal_window():
    trace = run_agent(c(contrast=40, area=80, persistence=2))
    assert trace.decision == "reinspect"
    tools = [s.tool for s in trace.steps]
    assert "compare_baseline" in tools
    assert "verify_track" in tools
    assert "inspect_temporal_window" in tools
    assert tools[-1] == "close_or_escalate_event"


def test_persistent_strong_evidence_requests_human():
    trace = run_agent(c(contrast=50, area=100, persistence=4))
    assert trace.decision == "human_review"
    tools = [s.tool for s in trace.steps]
    assert "request_human_review" in tools
    assert tools[-1] == "close_or_escalate_event"


def test_tool_failure_never_upgrades_to_human_review():
    trace = run_agent(
        c(contrast=60, area=100, persistence=4),
        fail_tools=frozenset({"verify_track"}),
    )
    assert trace.decision == "reinspect"
    assert trace.steps[-2].tool == "verify_track"
    assert trace.steps[-2].result["ok"] is False


def test_deterministic_scenario_suite_meets_r3_exit_gate():
    result = evaluate_agent_scenarios()
    assert len(AGENT_SCENARIOS) >= 10
    assert result["failed"] == 0
    assert result["task_success_rate"] == 1.0
