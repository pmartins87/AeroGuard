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
- [x] AWS Compute Grant proposal rewritten as V3 for judge readability: introduction first, plain-language problem, four-step product flow, execution proof, then AWS/technical detail.
- [x] Upload-ready AWS Compute Grant V3 PDF generated and visually verified as a clean two-page document.
- [x] Reproducible Python package scaffold created with `opencv-python-headless==5.0.0.93`.
- [x] Deterministic synthetic video fixture generator implemented.
- [x] First OpenCV baseline implemented: reference -> absdiff -> blur -> threshold -> morphology -> connected components -> persistence.
- [x] First bounded multi-step agent trace implemented: crop evidence -> track verification -> re-inspect or human review.
- [x] CLI now emits machine-readable event JSON, annotated video, and event-level evidence crops.
- [x] Unit/integration tests created and locally validated (5/5 PASS in compatibility environment).
- [x] GitHub Actions CI verifies OpenCV 5, tests, and deterministic demo.
- [x] Latest CI run `32980264697` completed **SUCCESS** on 2026-08-26.

### ACTIVE

- [ ] Complete Devpost draft project profile.
- [ ] Submit AWS Compute Grant V3 PDF while the proposal form remains open.
- [ ] Acquire FOD-A and record exact archive provenance/checksum/license applicability.
- [ ] Establish the first real-data FOD detection baseline.
- [ ] Expand deterministic scenario suite beyond the single positive fixture.

### BLOCKERS

None currently.

## Immediate next actions

1. User-facing registration tasks:
   - Devpost project name: `AeroGuard Vision`
   - Elevator pitch: `An agentic OpenCV 5 system that inspects airfield video, re-checks uncertain hazards, and escalates verified risks through a human-in-the-loop AWS workflow.`
   - Upload the verified V3 AWS Compute Grant PDF to the official proposal form.
2. Acquire FOD-A primary dataset and freeze a reproducible manifest.
3. Establish the first real-data detector baseline and size-conditioned metrics.
4. Add scenario fixtures for false alarms, transient objects, weak evidence, and failure recovery.
5. Keep the classical OpenCV path as a reproducible fallback and application-relevant COOL workload while learned perception is added.

## Verified baseline evidence

- Local compatibility test (OpenCV 4.13 environment): 5/5 tests PASS; deterministic demo writes JSON trace, annotated video, and evidence crops.
- GitHub Actions competition environment: OpenCV 5.0.0.93 gate PASS; tests PASS; demo smoke test PASS.
- Latest CI run: `https://github.com/pmartins87/OpenCV/actions/runs/32980264697`

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
