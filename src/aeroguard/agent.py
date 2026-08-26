from __future__ import annotations

from .types import AgentStep, Candidate, EventTrace


def inspect_crop(candidate: Candidate) -> dict:
    score = min(1.0, (candidate.contrast / 80.0) * min(1.0, candidate.area / 80.0))
    return {
        "contrast": round(candidate.contrast, 3),
        "area": candidate.area,
        "crop_score": round(score, 4),
    }


def verify_track(candidate: Candidate) -> dict:
    return {
        "persistence_frames": candidate.persistence,
        "persistent": candidate.persistence >= 3,
    }


def run_agent(candidate: Candidate) -> EventTrace:
    """Bounded perception-decision-action loop for the first baseline.

    Later tool calls depend on earlier visual evidence. The controller is
    deliberately deterministic so task success is measurable before R3 adds
    a model-backed orchestrator.
    """
    steps: list[AgentStep] = []

    crop = inspect_crop(candidate)
    steps.append(
        AgentStep(
            step=1,
            tool="inspect_crop",
            reason="quantify local evidence before escalation",
            result=crop,
        )
    )

    if crop["crop_score"] < 0.12:
        return EventTrace(candidate=candidate, decision="close", steps=tuple(steps))

    track = verify_track(candidate)
    steps.append(
        AgentStep(
            step=2,
            tool="verify_track",
            reason="visual evidence is material enough to test temporal persistence",
            result=track,
        )
    )

    if track["persistent"] and crop["crop_score"] >= 0.25:
        steps.append(
            AgentStep(
                step=3,
                tool="request_human_review",
                reason="persistent visual anomaly exceeds conservative review threshold",
                result={"requested": True},
            )
        )
        decision = "human_review"
    else:
        steps.append(
            AgentStep(
                step=3,
                tool="inspect_temporal_window",
                reason="candidate is plausible but insufficiently persistent for escalation",
                result={"requested": True},
            )
        )
        decision = "reinspect"

    return EventTrace(candidate=candidate, decision=decision, steps=tuple(steps))
