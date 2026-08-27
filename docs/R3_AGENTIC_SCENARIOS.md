# R3 Agentic Vision deterministic scenario gate

Status: baseline gate implemented on 2026-08-27.

## Purpose

The Agentic Vision award requires visual output to materially change a later plan, tool call, action, or human-approval request. AeroGuard therefore uses a bounded deterministic controller before any optional model-backed orchestrator is considered.

The current causal chain is:

`inspect_frame -> inspect_crop -> compare_baseline -> verify_track -> inspect_temporal_window OR request_human_review -> close_or_escalate_event`

Low-evidence candidates can close earlier, but still pass through the explicit final event-state tool. Persistent strong visual evidence is routed to human review. Tool failures never autonomously upgrade an event.

## Frozen deterministic suite

`src/aeroguard/agent_scenarios.py` defines 14 scenarios covering:

- low-evidence closure from different area/contrast combinations;
- plausible single-frame and two-frame candidates that require re-inspection;
- persistent-but-weak evidence;
- persistent strong evidence that requests human review;
- deterministic failures of frame inspection, crop inspection, baseline comparison, track verification, temporal-window inspection, and human-review dispatch.

Run:

```bash
python scripts/agent_scenario_suite.py --output artifacts/agent_scenarios.json
```

The command exits non-zero if any expected action changes. The CI test gate also requires at least 10 scenarios and 100% expected-decision success for this frozen deterministic suite.

## Safety property

A perception/tool failure does not create an operational escalation. The safe fallback is bounded re-inspection, and consequential decisions remain human controlled.

## What this proves and what it does not

This gate proves deterministic orchestration semantics, causal tool sequencing, failure fallback, and human-control behavior. It does not yet prove real-data perception quality or false-alert reduction. Those claims remain blocked until the learned FOD detector is trained/evaluated and its real outputs are fed into this loop.
