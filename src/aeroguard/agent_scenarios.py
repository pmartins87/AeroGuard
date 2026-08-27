from __future__ import annotations

from dataclasses import dataclass

from .agent import run_agent
from .types import Candidate


@dataclass(frozen=True)
class AgentScenario:
    name: str
    candidate: Candidate
    expected_decision: str
    fail_tools: frozenset[str] = frozenset()


def _candidate(*, contrast: float, area: int, persistence: int, frame: int = 10) -> Candidate:
    return Candidate(frame, 20, 30, 12, 10, area, contrast, persistence)


AGENT_SCENARIOS: tuple[AgentScenario, ...] = (
    AgentScenario("tiny_low_contrast", _candidate(contrast=5, area=20, persistence=1), "close"),
    AgentScenario("large_but_low_contrast", _candidate(contrast=8, area=100, persistence=2), "close"),
    AgentScenario("high_contrast_tiny", _candidate(contrast=70, area=8, persistence=1), "close"),
    AgentScenario("medium_single_frame", _candidate(contrast=35, area=80, persistence=1), "reinspect"),
    AgentScenario("medium_two_frames", _candidate(contrast=40, area=80, persistence=2), "reinspect"),
    AgentScenario("persistent_but_weak", _candidate(contrast=18, area=80, persistence=4), "reinspect"),
    AgentScenario("strong_persistent_three", _candidate(contrast=50, area=100, persistence=3), "human_review"),
    AgentScenario("strong_persistent_six", _candidate(contrast=75, area=120, persistence=6), "human_review"),
    AgentScenario(
        "inspect_frame_failure",
        _candidate(contrast=60, area=100, persistence=4),
        "reinspect",
        frozenset({"inspect_frame"}),
    ),
    AgentScenario(
        "inspect_crop_failure",
        _candidate(contrast=60, area=100, persistence=4),
        "reinspect",
        frozenset({"inspect_crop"}),
    ),
    AgentScenario(
        "compare_baseline_failure",
        _candidate(contrast=60, area=100, persistence=4),
        "reinspect",
        frozenset({"compare_baseline"}),
    ),
    AgentScenario(
        "verify_track_failure",
        _candidate(contrast=60, area=100, persistence=4),
        "reinspect",
        frozenset({"verify_track"}),
    ),
    AgentScenario(
        "human_review_dispatch_failure",
        _candidate(contrast=60, area=100, persistence=4),
        "reinspect",
        frozenset({"request_human_review"}),
    ),
    AgentScenario(
        "temporal_window_failure",
        _candidate(contrast=40, area=80, persistence=2),
        "reinspect",
        frozenset({"inspect_temporal_window"}),
    ),
)


def evaluate_agent_scenarios() -> dict:
    rows: list[dict] = []
    passed = 0
    for scenario in AGENT_SCENARIOS:
        trace = run_agent(scenario.candidate, fail_tools=scenario.fail_tools)
        ok = trace.decision == scenario.expected_decision
        passed += int(ok)
        rows.append(
            {
                "name": scenario.name,
                "expected_decision": scenario.expected_decision,
                "actual_decision": trace.decision,
                "pass": ok,
                "fail_tools": sorted(scenario.fail_tools),
                "tool_sequence": [step.tool for step in trace.steps],
                "trace": trace.to_dict(),
            }
        )

    total = len(rows)
    return {
        "schema": "aeroguard.agent_scenarios.v1",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "task_success_rate": passed / total if total else 0.0,
        "scenarios": rows,
    }
