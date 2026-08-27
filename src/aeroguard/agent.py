from __future__ import annotations

from collections.abc import AbstractSet

from .types import AgentStep, Candidate, EventTrace


def inspect_frame(candidate: Candidate) -> dict:
    return {
        "frame_index": candidate.frame_index,
        "bbox": list(candidate.bbox),
        "visual_material": candidate.contrast >= 8.0 and candidate.area >= 16,
    }


def inspect_crop(candidate: Candidate) -> dict:
    score = min(1.0, (candidate.contrast / 80.0) * min(1.0, candidate.area / 80.0))
    return {
        "contrast": round(candidate.contrast, 3),
        "area": candidate.area,
        "crop_score": round(score, 4),
    }


def compare_baseline(candidate: Candidate, crop: dict) -> dict:
    novelty = min(1.0, float(crop["crop_score"]) * (1.0 + min(candidate.persistence, 3) * 0.05))
    return {
        "novelty_score": round(novelty, 4),
        "above_background": novelty >= 0.15,
    }


def verify_track(candidate: Candidate) -> dict:
    return {
        "persistence_frames": candidate.persistence,
        "persistent": candidate.persistence >= 3,
    }


def inspect_temporal_window(candidate: Candidate) -> dict:
    return {
        "requested": True,
        "center_frame": candidate.frame_index,
        "observed_persistence_frames": candidate.persistence,
        "needs_more_evidence": candidate.persistence < 3,
    }


def request_human_review(candidate: Candidate) -> dict:
    return {
        "requested": True,
        "frame_index": candidate.frame_index,
        "bbox": list(candidate.bbox),
        "requires_human_action": True,
    }


def close_or_escalate_event(decision: str) -> dict:
    if decision not in {"close", "reinspect", "human_review"}:
        raise ValueError(f"unsupported event decision: {decision}")
    return {"final_state": decision}


def _step(
    steps: list[AgentStep],
    *,
    tool: str,
    reason: str,
    result: dict,
) -> None:
    steps.append(AgentStep(step=len(steps) + 1, tool=tool, reason=reason, result=result))


def _tool_result(tool: str, result: dict, fail_tools: AbstractSet[str]) -> dict:
    if tool in fail_tools:
        return {"ok": False, "error": "deterministic_tool_failure"}
    return {"ok": True, **result}


def _finalize(
    candidate: Candidate,
    steps: list[AgentStep],
    decision: str,
    reason: str,
    fail_tools: AbstractSet[str],
) -> EventTrace:
    result = _tool_result(
        "close_or_escalate_event",
        close_or_escalate_event(decision),
        fail_tools,
    )
    _step(steps, tool="close_or_escalate_event", reason=reason, result=result)
    # A finalizer failure never upgrades risk. Re-inspection is the deterministic safe fallback.
    if not result["ok"] and decision != "close":
        decision = "reinspect"
    return EventTrace(candidate=candidate, decision=decision, steps=tuple(steps))


def run_agent(candidate: Candidate, *, fail_tools: AbstractSet[str] = frozenset()) -> EventTrace:
    """Bounded deterministic perception-decision-action loop.

    Each later action depends on earlier visual evidence. ``fail_tools`` exists to
    exercise deterministic failure handling without adding network or model
    nondeterminism to the qualification suite. Tool failures never cause an
    autonomous consequential escalation.
    """
    steps: list[AgentStep] = []

    frame = _tool_result("inspect_frame", inspect_frame(candidate), fail_tools)
    _step(
        steps,
        tool="inspect_frame",
        reason="establish candidate geometry and minimum usable visual evidence",
        result=frame,
    )
    if not frame["ok"]:
        return _finalize(
            candidate,
            steps,
            "reinspect",
            "frame inspection failed; request another bounded visual pass",
            fail_tools,
        )

    crop = _tool_result("inspect_crop", inspect_crop(candidate), fail_tools)
    _step(
        steps,
        tool="inspect_crop",
        reason="quantify local evidence before persistence or escalation checks",
        result=crop,
    )
    if not crop["ok"]:
        return _finalize(
            candidate,
            steps,
            "reinspect",
            "crop inspection failed; do not escalate without visual evidence",
            fail_tools,
        )

    if crop["crop_score"] < 0.12:
        return _finalize(
            candidate,
            steps,
            "close",
            "local evidence is below the conservative candidate threshold",
            fail_tools,
        )

    baseline = _tool_result("compare_baseline", compare_baseline(candidate, crop), fail_tools)
    _step(
        steps,
        tool="compare_baseline",
        reason="check that the anomaly remains distinct from expected background variation",
        result=baseline,
    )
    if not baseline["ok"]:
        return _finalize(
            candidate,
            steps,
            "reinspect",
            "baseline comparison failed; defer escalation and reacquire evidence",
            fail_tools,
        )
    if not baseline["above_background"]:
        return _finalize(
            candidate,
            steps,
            "close",
            "candidate is not sufficiently distinct from the reference background",
            fail_tools,
        )

    track = _tool_result("verify_track", verify_track(candidate), fail_tools)
    _step(
        steps,
        tool="verify_track",
        reason="material visual evidence now warrants a temporal persistence check",
        result=track,
    )
    if not track["ok"]:
        return _finalize(
            candidate,
            steps,
            "reinspect",
            "track verification failed; consequential escalation remains blocked",
            fail_tools,
        )

    if track["persistent"] and crop["crop_score"] >= 0.25:
        review = _tool_result("request_human_review", request_human_review(candidate), fail_tools)
        _step(
            steps,
            tool="request_human_review",
            reason="persistent strong anomaly requires a human-controlled safety decision",
            result=review,
        )
        if not review["ok"]:
            return _finalize(
                candidate,
                steps,
                "reinspect",
                "human-review dispatch failed; keep the event open without autonomous escalation",
                fail_tools,
            )
        return _finalize(
            candidate,
            steps,
            "human_review",
            "verified evidence is routed to a human rather than an autonomous operational action",
            fail_tools,
        )

    temporal = _tool_result("inspect_temporal_window", inspect_temporal_window(candidate), fail_tools)
    _step(
        steps,
        tool="inspect_temporal_window",
        reason="candidate is plausible but needs additional temporal evidence",
        result=temporal,
    )
    return _finalize(
        candidate,
        steps,
        "reinspect",
        "collect another bounded visual window before any escalation",
        fail_tools,
    )
