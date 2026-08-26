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
- [x] AWS Compute Grant proposal rewritten as V3 for judge readability.
- [x] Upload-ready AWS Compute Grant V3 PDF generated and visually verified.
- [x] **AWS Compute Grant V3 submitted successfully on 2026-08-26; Jotform confirmation received.**
- [x] Grant submission record frozen in `docs/AWS_GRANT_SUBMISSION.md`.
- [x] Reproducible Python package scaffold created with `opencv-python-headless==5.0.0.93`.
- [x] Deterministic synthetic video fixture generator implemented.
- [x] First OpenCV baseline implemented: reference -> absdiff -> blur -> threshold -> morphology -> connected components -> persistence.
- [x] First bounded multi-step agent trace implemented: crop evidence -> track verification -> re-inspect or human review.
- [x] CLI emits machine-readable event JSON, annotated video, and event-level evidence crops.
- [x] GitHub Actions CI verifies OpenCV 5, tests, and deterministic demo.
- [x] FOD-A acquisition target frozen to official v2.1 Pascal VOC (300x300, source-reported 412 MB, supplied train/validation split).
- [x] FOD-A VOC parser, strict bounding-box validator, dataset summarizer, split checker, SHA-256 helper, and inspection CLI added.
- [x] Automated `foda-probe` GitHub Actions workflow added to download the official archive, hash it, inspect it, and retain only provenance artifacts.

### ACTIVE

- [ ] Complete Devpost draft project profile.
- [ ] Complete automated FOD-A v2.1 provenance probe and record archive SHA-256 + real annotation statistics.
- [ ] Establish the first real-data FOD detection baseline.
- [ ] Expand deterministic scenario suite beyond the single positive fixture.
- [ ] Reconfirm CI after the new dataset utilities/tests settle.

### BLOCKERS

None currently. AWS grant decision is external and does not block local/GitHub development.

## Immediate next actions

1. User-facing Devpost task:
   - Project name: `AeroGuard Vision`
   - Elevator pitch: `An agentic OpenCV 5 system that inspects airfield video, re-checks uncertain hazards, and escalates verified risks through a human-in-the-loop AWS workflow.`
   - Continue through the remaining Devpost draft screens; the AWS grant application is already complete.
2. Finish FOD-A provenance probe and freeze archive/input manifest.
3. Build a real-data detector/evaluator around the source-provided split.
4. Report first perception metrics, including small-object slices.
5. Add false-alarm, transient-object, weak-evidence, and tool-failure agent scenarios.
6. Keep the classical OpenCV path as a reproducible fallback and application-relevant COOL workload while learned perception is added.

## Verified baseline evidence

- Local compatibility test (OpenCV 4.13 environment): prior 5/5 baseline tests PASS; deterministic demo writes JSON trace, annotated video, and evidence crops.
- GitHub Actions competition environment: OpenCV 5.0.0.93 gate PASS; baseline tests PASS; demo smoke test PASS.
- Prior clean CI reference: `https://github.com/pmartins87/OpenCV/actions/runs/32980264697`
- New FOD-A utilities add additional tests; CI revalidation is active after test-vector correction.

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
