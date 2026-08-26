# STATUS

Last updated: 2026-08-26

## Competition

- Competition: OpenCV AI Competition 2026, powered by AWS
- Phase: build phase opened
- Final deadline: 2026-10-26 23:59 PT
- Repo: `pmartins87/OpenCV`
- Working project name: **AeroGuard Vision**
- Prize strategy: pursue **Overall + COOL + Agentic Vision**

## Current state

### DONE

- [x] Repository designated as project source of truth.
- [x] Official competition requirements and judging rubric reviewed.
- [x] Prize stack identified: $5k / $3k / $2k overall + $1k COOL + $1k Agentic Vision.
- [x] Competition-shaped concept selected provisionally: agentic airfield visual safety inspection.
- [x] Initial architecture and evaluation philosophy defined.
- [x] Repository governance initialized.

### ACTIVE

- [ ] Complete Devpost draft project profile.
- [ ] Submit AWS Compute Grant proposal while the form remains open.
- [ ] Validate public/synthetic data sources for a credible demo and benchmark.
- [ ] Freeze MVP hazard taxonomy and evaluation protocol.

### BLOCKERS

None currently.

## Immediate next actions

1. Fill Devpost Project Overview:
   - Project name: `AeroGuard Vision`
   - Elevator pitch: `An agentic OpenCV 5 system that inspects airfield video, re-checks uncertain hazards, and escalates verified risks through a human-in-the-loop AWS workflow.`
2. Prepare the AWS Compute Grant proposal PDF.
3. Create baseline OpenCV 5 pipeline and deterministic test fixtures.
4. Establish dataset/license ledger before model or demo development.
5. Build the first end-to-end trace: frame -> perception -> agent decision -> second tool call -> human-visible result.

## Key success metrics

The project is not considered competition-ready until it has measured evidence for all of the following:

- Perception quality: precision/recall and/or task-appropriate detection metrics.
- Agent task success: percentage of scenarios where visual evidence leads to the correct next action.
- False-alarm reduction from verification/re-checking.
- End-to-end latency and throughput.
- COOL vs vanilla OpenCV 5 performance on comparable AWS Graviton hardware.
- Reproducible deploy/test path from a clean environment.
- Explicit failure cases and safe human-control behavior.

## Decision log pointer

Major scope decisions belong in `docs/STRATEGY.md` and must be reflected here when they change execution status.
