# STATUS

Last updated: 2026-08-26

## Competition

- Competition: OpenCV AI Competition 2026, powered by AWS
- Phase: build phase opened
- Final deadline: 2026-10-26 23:59 PT
- Repo: `pmartins87/AeroGuard`
- Project name: **AeroGuard Vision**
- Frozen MVP: **agentic runway/taxiway Foreign Object Debris (FOD) inspection**
- Prize strategy: pursue **Overall + COOL + Agentic Vision**

## Current state

### DONE

- [x] Repository designated as project source of truth.
- [x] Repository renamed from `pmartins87/OpenCV` to **`pmartins87/AeroGuard`**; new canonical URL is `https://github.com/pmartins87/AeroGuard`.
- [x] Official competition requirements and judging rubric reviewed.
- [x] Prize stack identified: $5k / $3k / $2k overall + $1k COOL + $1k Agentic Vision.
- [x] Broad concept stress-tested and narrowed to a measurable FOD MVP.
- [x] MVP taxonomy frozen: candidate -> verified persistent candidate -> human-review event.
- [x] Agentic and COOL special-award evidence mapped to concrete evaluation artifacts.
- [x] Architecture v1 documented, including Graviton4 + COOL + CloudWatch and optional Bedrock path.
- [x] AWS Compute Grant proposal rewritten as V3 for judge readability.
- [x] **AWS Compute Grant V3 submitted successfully on 2026-08-26; Jotform confirmation received.**
- [x] Grant submission record frozen in `docs/AWS_GRANT_SUBMISSION.md`.
- [x] Reproducible Python package scaffold created with `opencv-python-headless==5.0.0.93`.
- [x] Deterministic synthetic video fixture generator implemented.
- [x] First OpenCV baseline implemented: reference -> absdiff -> blur -> threshold -> morphology -> connected components -> persistence.
- [x] First bounded multi-step agent trace implemented: crop evidence -> track verification -> re-inspect or human review.
- [x] CLI emits machine-readable event JSON, annotated video, and event-level evidence crops.
- [x] GitHub Actions CI verifies OpenCV 5, tests, and deterministic demo.
- [x] FOD-A acquisition target frozen to official v2.1 Pascal VOC, 300x300.
- [x] FOD-A VOC parser, fractional-box support, strict validation, dataset summarizer, SHA-256 helper, and inspection CLI added.
- [x] FOD-A archive SHA-256 frozen at **`408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`**.
- [x] Retained provenance artifact audited; earlier provisional corpus counts were found inconsistent and explicitly superseded in `docs/FODA_AUDIT_20260826.md`.
- [x] Corrected verified corpus: **33,793 annotated images, 34,472 objects, 31 source labels, 300x300 images**.
- [x] Corrected small-object slice: **28.58%** of objects have bounding-box area below 1,024 px².
- [x] Physical source split filenames discovered: `VOC2007/ImageSets/Main/trainval.txt` and `test.txt`.
- [x] Split inspector upgraded to record SHA-256, duplicate IDs, overlap, missing IDs, extra IDs, and full annotation coverage.
- [x] Deterministic class-aware development split builder implemented; it derives validation only inside source `trainval.txt` and leaves source `test.txt` untouched.
- [x] Deterministic class-aware IoU / precision / recall / F1 evaluation primitives implemented with tests.
- [x] Devpost Project Overview saved.
- [x] Devpost Project Details story and technology/link plan drafted and preserved in `docs/DEVPOST_DRAFT.md`.
- [x] Devpost working copy corrected to the audited FOD-A corpus facts before final submission.
- [x] Devpost finalization requirements captured into `docs/FINAL_SUBMISSION_CHECKLIST.md`.

### ACTIVE

- [ ] Complete Devpost draft project profile only when final video/report artifacts exist.
- [ ] Project Details remains intentionally incomplete until the required final demo video is available.
- [ ] Additional Info remains intentionally incomplete until the final technical report and final endpoint/live-demo choice are available.
- [ ] Final Submit page reached; **do not submit yet**. Terms acceptance and final submission remain pending until the evidence package is judge-ready.
- [ ] Complete the automated hash/coverage audit of source `trainval.txt` and `test.txt`; current `foda-probe` jobs are queued after rapid repository updates.
- [ ] Generate and freeze the deterministic development train/validation manifest from source `trainval.txt` once the source split gate passes.
- [ ] Establish the first real-data FOD detection baseline.
- [ ] Report first real-data precision/recall/F1/AP as appropriate plus a dedicated small-object slice.
- [ ] Expand deterministic agent scenarios beyond the single positive fixture.

### BLOCKERS

No project-design blocker. GitHub Actions currently has a queue of CI/provenance jobs created by the rapid sequence of audit commits; development can continue while they execute. AWS grant decision is external and non-blocking.

## Immediate next actions

1. Leave Devpost in draft state; use `docs/FINAL_SUBMISSION_CHECKLIST.md` as the final gate.
2. Wait for the newest FOD-A provenance workflow to complete, then freeze exact `trainval.txt` / `test.txt` counts, hashes, zero-overlap, and full annotation coverage.
3. Run `scripts/foda_make_dev_split.py` only after that gate passes; freeze the derived train/validation IDs and hashes while preserving source `test.txt` as final held-out data.
4. Add a model-agnostic real-data detector training/evaluation scaffold and establish the first measured baseline.
5. Measure precision/recall/F1/AP at frozen operating points, with separate small-object results.
6. Feed real detector outputs into the bounded agent verification loop and quantify false-alert reduction.
7. Expand agent scenarios and generate the workflow/evidence artifacts required for the Agentic Vision award.
8. When AWS grant/credits arrive, execute the Graviton4 + COOL benchmark plan; no development waits on that decision.
9. Only after measured evidence exists, finalize the technical report, <=5-minute demo video, architecture diagrams, judge-accessible endpoint/live-demo path, and Devpost media.

## Verified evidence

- Prior clean OpenCV 5 CI reference: `https://github.com/pmartins87/AeroGuard/actions/runs/32980264697`
- Retained FOD-A provenance workflows: `32994883456` and `32995768875`
- FOD-A verified archive SHA-256: `408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`
- FOD-A corrected verified corpus: **33,793 annotated images / 34,472 objects / 31 labels**.
- Audit/correction record: `docs/FODA_AUDIT_20260826.md`.
- Upstream FOD-A README confirms v2.1 Pascal VOC at 300x300 and the supplied split package.

## Key success metrics

The project is not considered competition-ready until it has measured evidence for all of the following:

- Perception quality: precision/recall and bounding-box metrics on real FOD data.
- Small-object performance as a dedicated slice.
- Agent task success: percentage of scenarios where visual evidence leads to the correct next action.
- False-alarm reduction from verification/re-checking.
- End-to-end latency and throughput.
- COOL vs vanilla OpenCV 5 performance on comparable AWS Graviton hardware.
- Reproducible deploy/test path from a clean environment.
- Explicit failure cases and safe human-control behavior.

## Decision log pointer

Major scope decisions belong in `docs/STRATEGY.md` / `docs/R0_SCOPE_FREEZE.md` and must be reflected here when they change execution status.
