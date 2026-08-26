# HANDOFF

Use this file to resume the project without relying on chat history.

## Objective

Compete seriously for prize money in the **OpenCV AI Competition 2026, powered by AWS**. The entry should be designed for the Overall Award and both optional $1,000 special awards when feasible.

## Source of truth

Repository: `pmartins87/OpenCV`

Canonical read order:
1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/COMPETITION.md`
4. `docs/STRATEGY.md`
5. code / experiment artifacts referenced by STATUS

When chat statements conflict with committed repository state, verify the repository and update it deliberately.

## Current working concept

**AeroGuard Vision** — agentic visual safety inspection for airfield/runway video.

Core behavior:
- OpenCV 5 produces visual evidence.
- Evidence drives a later decision/action.
- Uncertain hazards cause targeted re-analysis rather than immediate escalation.
- Consequential alerts require appropriate human control.
- AWS hosts a meaningful component.
- COOL is benchmarked on Graviton against vanilla OpenCV 5 with reproducible evidence.

## Current immediate work

1. Finish the Devpost project overview.
2. Prepare/submit the AWS Compute Grant proposal if still available.
3. Research and lock legal/public data sources.
4. Implement R1 reproducible OpenCV 5 baseline.

## Devpost copy currently approved as working text

**Project name**

`AeroGuard Vision`

**Elevator pitch**

`An agentic OpenCV 5 system that inspects airfield video, re-checks uncertain hazards, and escalates verified risks through a human-in-the-loop AWS workflow.`

## Guardrails

- Do not claim operational aviation safety capability.
- Do not use restricted/private operational imagery or data unless explicitly cleared for competition use.
- Do not optimize for a flashy demo at the cost of measurable evaluation.
- Do not add an LLM/agent merely as presentation glue; vision output must materially change later behavior.
- Do not claim COOL performance without same-input, reproducible benchmark evidence.
- Keep costs controlled; expensive AWS resources should have explicit purpose and shutdown instructions.
- Preserve failure cases. Judges explicitly require evaluation evidence including limitations.
