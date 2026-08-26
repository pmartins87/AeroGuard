# STATUS

Last updated: 2026-08-26

## Competition

- Competition: OpenCV AI Competition 2026, powered by AWS
- Phase: build phase opened
- Final deadline: 2026-10-26 23:59 PT
- Repo: `pmartins87/OpenCV`
- Project name: **AeroGuard Vision**
- Frozen MVP: **agentic runway/taxiway Foreign Object Debris (FOD) inspection**
- Prize strategy: pursue **Overall + COOL + Agentic Vision**

## Current state

### DONE

- [x] Repository designated as project source of truth.
- [x] Official competition requirements and judging rubric reviewed.
- [x] Prize stack identified: $5k / $3k / $2k overall + $1k COOL + $1k Agentic Vision.
- [x] Broad concept stress-tested and narrowed to a measurable FOD MVP.
- [x] MVP taxonomy frozen: candidate -> verified persistent candidate -> human-review event.
- [x] Agentic and COOL special-award evidence mapped to concrete evaluation artifacts.
- [x] Dataset/provenance ledger created; FOD-A selected as primary acquisition candidate.
- [x] Architecture v1 documented, including Graviton4 + COOL + CloudWatch and optional Bedrock path.
- [x] AWS Compute Grant proposal source completed and upload-ready PDF generated.
- [x] Reproducible Python package scaffold created with `opencv-python-headless==5.0.0.93`.
- [x] Deterministic synthetic video fixture generator implemented.
- [x] First OpenCV baseline implemented: reference -> absdiff -> blur -> threshold -> morphology -> connected components -> persistence.
- [x] First bounded multi-step agent trace implemented: crop evidence -> track verification -> re-inspect or human review.
- [x] Unit tests created and locally validated.
- [x] GitHub Actions CI verifies OpenCV 5, tests, and deterministic demo.
- [x] CI run `32979620618` completed **SUCCESS** on 2026-08-26.

### ACTIVE

- [ ] Complete Devpost draft project profile.
- [ ] Submit AWS Compute Grant PDF while the proposal form remains open.
- [ ] Acquire FOD-A and record exact archive provenance/checksum/license applicability.
- [ ] Add annotated output video and evidence overlays to the CLI.
- [ ] Establish the first real-data detection baseline.

### BLOCKERS

None currently.

## Immediate next actions

1. User-facing registration tasks:
   - Devpost project name: `AeroGuard Vision`
   - Elevator pitch: `An agentic OpenCV 5 system that inspects airfield video, re-checks uncertain hazards, and escalates verified risks through a human-in-the-loop AWS workflow.`
   - Upload `AeroGuard_Vision_AWS_Compute_Grant_Proposal.pdf` to the official AWS Compute Grant proposal form.
2. Acquire FOD-A primary dataset and freeze a reproducible manifest.
3. Extend R1 CLI to produce annotated evidence video and event-level crops.
4. Add scenario fixtures for false alarms/transient objects and validate agent decisions quantitatively.
5. Begin real-data detector baseline while preserving the classical OpenCV pipeline as a reproducible fallback and COOL workload.

## Verified baseline evidence

- Local compatibility test (OpenCV 4.13 environment): 4/4 tests PASS; deterministic demo emits trace events.
- GitHub Actions competition environment: OpenCV 5.0.0.93 gate PASS; tests PASS; demo smoke test PASS.
- CI run: `https://github.com/pmartins87/OpenCV/actions/runs/32979620618`

## Key success metrics

The project is not considered competition-ready until it has measured evidence for all of the following:

- Perception quality: precision/recall and bounding-box metrics on real FOD data.
- Agent task success: percentage of scenarios where visual evidence leads to the correct next action.
- False-alarm reduction from verification/re-checking.
- End-to-end latency and throughput.
- COOL vs vanilla OpenCV 5 performance on comparable AWS Graviton hardware.
- Reproducible deploy/test path from a clean environment.
- Explicit failure cases and safe human-control behavior.

## Decision log pointer

Major scope decisions belong in `docs/STRATEGY.md` / `docs/R0_SCOPE_FREEZE.md` and must be reflected here when they change execution status.
