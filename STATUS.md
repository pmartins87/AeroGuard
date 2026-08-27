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
- [x] FOD-A provenance probe completed successfully in run **32994883456**.
- [x] Official FOD-A archive frozen at **432,133,110 bytes**, SHA-256 **`408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`**.
- [x] Real corpus verified: **18,742 annotated images, 31,493 objects, 31 source labels, 300x300 images**.
- [x] Small-object risk quantified: **46.43%** of objects have bounding-box area below 1,024 px^2.
- [x] Source taxonomy quirks identified and raw labels preserved pending an explicit canonicalization decision.
- [x] Deterministic class-aware IoU / precision / recall / F1 evaluation primitives implemented with tests.
- [x] Devpost Project Overview saved.
- [x] Devpost Project Details story and technology/link plan drafted and preserved in `docs/DEVPOST_DRAFT.md`.

### ACTIVE

- [ ] Complete Devpost draft project profile.
- [ ] Project Details remains intentionally incomplete until the required final demo video is available.
- [ ] Additional Info can be partially filled now; final technical-report upload and final endpoint/live-demo details remain intentionally pending.
- [ ] Discover and freeze the exact source train/validation split filenames and counts inside FOD-A v2.1.
- [ ] Establish the first real-data FOD detection baseline.
- [ ] Report first real-data precision/recall/F1 plus a dedicated small-object slice.
- [ ] Expand deterministic agent scenarios beyond the single positive fixture.

### BLOCKERS

None currently. AWS grant decision is external and does not block local/GitHub development.

## Immediate next actions

1. Devpost Additional Info:
   - opt into **Best Use of COOL Award** and **Agentic Vision Award** in both applicable selectors;
   - repository URL: `https://github.com/pmartins87/AeroGuard`;
   - add reproducible local testing instructions;
   - leave the required final report upload pending until the technical report contains measured results;
   - leave Working web endpoint blank until a real judge-accessible endpoint exists (or use the permitted live screen-share path later).
2. Finish FOD-A source split discovery; the workflow records candidate train/validation/test/ImageSets files as provenance artifacts.
3. Freeze any source-label canonicalization policy without altering raw provenance.
4. Build the first learned or otherwise credible real-data detector baseline on the source split.
5. Measure precision/recall/F1 at frozen operating points, with separate small-object results.
6. Feed real detector outputs into the bounded agent verification loop and quantify false-alert reduction.
7. When AWS grant/credits arrive, execute the Graviton4 + COOL benchmark plan; no development waits on that decision.

## Verified evidence

- Prior clean OpenCV 5 CI reference: `https://github.com/pmartins87/AeroGuard/actions/runs/32980264697`
- Successful FOD-A provenance run: `https://github.com/pmartins87/AeroGuard/actions/runs/32994883456`
- FOD-A verified archive SHA-256: `408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`
- FOD-A verified corpus: 18,742 annotated images / 31,493 objects / 31 labels.

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
