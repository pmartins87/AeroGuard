# ROADMAP - OpenCV AI Competition 2026

Goal: maximize probability of an **Overall Award** while remaining fully eligible and competitive for **Best Use of COOL** and **Agentic Vision**.

Final deadline: **2026-10-26 23:59 PT**.

## R0 - Competition intelligence and scope freeze | Aug 26-28

Exit gate:
- [ ] Devpost project profile completed.
- [ ] AWS Compute Grant proposal submitted if form is open. Proposal content and PDF are ready.
- [x] Working concept stress-tested against all six overall judging criteria.
- [x] Both special-award eligibility requirements mapped to concrete evidence.
- [x] MVP hazard taxonomy frozen around FOD inspection.
- [x] Dataset/license plan documented in `docs/DATA_LEDGER.md`.
- [x] Architecture v1 documented in `docs/ARCHITECTURE.md`.

Status: **substantively complete; only user-facing Devpost/grant submission and dataset archive verification remain.**

## R1 - Reproducible OpenCV 5 baseline | Aug 29-Sep 5

Build the smallest end-to-end pipeline that judges could run.

Deliverables:
- [x] Python environment with pinned `opencv-python-headless==5.0.0.93`.
- [x] OpenCV 5 version check in CI.
- [x] Deterministic sample video fixture generator.
- [~] Frame ingest, reference comparison, candidate extraction and temporal persistence implemented; stabilization/ROI policy still pending.
- [~] Baseline detector/tracker behavior exists via connected components + persistence; learned detector interface still pending.
- [x] CLI produces machine-readable event JSON, annotated output video, and event-level evidence crops.
- [x] Unit/integration tests, including artifact generation.
- [x] GitHub Actions OpenCV 5 smoke test. Latest verified run `32980264697`: PASS.

Exit gate: one command turns a known video into reproducible detections + evidence.

The synthetic/deterministic portion of this exit gate is already met. R1 remains open until the first real-data FOD baseline is integrated and the reference/ROI assumptions are documented against that data.

## R2 - Perception quality and hazard verification | Sep 6-12

Deliverables:
- [x] High-level FOD hazard/event taxonomy and evaluation schema frozen.
- [ ] Primary real-data detection path.
- [ ] Temporal verification and multi-frame tracking beyond simple persistence.
- [ ] Scene-quality checks (blur, darkness, occlusion/compression where feasible).
- [ ] Confidence calibration/threshold policy.
- [ ] Baseline metrics and failure-case set.

Exit gate: measurable perception baseline with documented limitations.

## R3 - Agentic Vision loop | Sep 13-19

The agent must do more than explain a result. OpenCV output must change a later decision/tool call/action.

Tool set target:
- [ ] `inspect_frame`
- [x] `inspect_crop` (first deterministic baseline semantics)
- [~] `inspect_temporal_window` (action emitted; richer implementation pending)
- [ ] `compare_baseline` as explicit tool
- [x] `verify_track` (persistence baseline)
- [x] `request_human_review` (trace action)
- [~] `close_or_escalate_event` (decision state exists; explicit tool/API pending)

Evidence:
- [x] Trace schema records perception -> decision -> action.
- [x] Uncertain baseline cases trigger targeted re-analysis actions.
- [x] Human-review action protects consequential escalation in the baseline controller.
- [x] Judge-visible evidence crops and annotated video are generated for the deterministic trace.
- [ ] Timeouts/tool failures and deterministic fallback behavior.
- [ ] Model-backed orchestrator experiment (e.g. Bedrock) only if it improves measured task success.

Exit gate: at least 10 deterministic scenarios demonstrate correct multi-step behavior.

## R4 - AWS deployment + COOL path | Sep 20-27

Deliverables:
- [ ] Meaningful component deployed on AWS.
- [x] Graviton4 + COOL target architecture documented.
- [ ] COOL environment/version captured from a real run.
- [ ] Benchmark harness compares COOL against vanilla OpenCV 5.
- [ ] Same inputs, comparable hardware/configuration, repeated runs.
- [ ] Latency, throughput, utilization and estimated cost reported.
- [ ] Evidence that COOL executes the claimed core workload.
- [ ] Observability/logging enabled.

Exit gate: reproducible AWS run plus honest, statistically defensible COOL comparison.

## R5 - Evaluation campaign | Sep 28-Oct 5

Overall evaluation:
- [ ] Precision/recall or equivalent perception metrics.
- [ ] Agent task-success rate.
- [ ] False-alarm reduction after verification.
- [ ] End-to-end latency.
- [ ] Failure categories and stress tests.

Special-award evaluation:
- [ ] COOL performance/value table.
- [ ] Agentic decision-quality table.
- [ ] Failure handling, observability, security, human-control evidence.

Exit gate: every important claim in the final submission has a reproducible artifact behind it.

## R6 - Judge-facing product and UX | Oct 6-12

Deliverables:
- [ ] Web dashboard.
- [ ] Annotated evidence viewer.
- [ ] Agent trace/timeline.
- [ ] Clear human approve/reject interaction.
- [ ] Demo mode that cannot depend on fragile external inputs.
- [ ] Architecture diagram v2.

Exit gate: a judge can understand the value and see the core loop in under 60 seconds.

## R7 - Submission package | Oct 13-20

Deliverables required by competition:
- [ ] Technical report.
- [ ] Judge-accessible repository/archive.
- [x] Dependency pinning started; final lock/reproducibility verification pending.
- [ ] Build/deploy/test instructions.
- [x] Architecture v1 available; final diagram pending.
- [ ] Working web endpoint or arranged live demo.
- [ ] <=5 minute public/unlisted demo video.
- [ ] Evaluation evidence including failures/limitations.
- [x] Responsible-use posture established; final section pending.

Exit gate: complete submission rehearsed from a clean machine/account path.

## R8 - Adversarial review and final freeze | Oct 21-24

- [ ] Re-score project against the official 100-point rubric as a skeptical judge.
- [ ] Remove unsupported marketing claims.
- [ ] Reproduce top benchmark numbers.
- [ ] Test broken-network/demo fallback.
- [ ] Verify all links and judge permissions.
- [ ] Confirm special-award opt-ins and evidence.

Exit gate: zero known submission blockers.

## R9 - Submit with buffer | Oct 25

Target internal submission deadline: **at least 24 hours before official cutoff**.

- [ ] Final Devpost submission.
- [ ] Verify rendered page/video/repo links.
- [ ] Archive submission snapshot and hashes in repo.

## R10 - Emergency buffer | Oct 26

Reserved only for Devpost/AWS/link failures or a critical correctness issue. No feature work unless required to restore a broken submission.

---

## Scope discipline

Features are accepted only if they improve at least one judging criterion or special-award rubric **and** do not materially threaten reproducibility/demo reliability.

Priority order:

1. Correct, measurable OpenCV 5 execution.
2. Convincing real-world problem and judge-visible value.
3. Agentic behavior that materially changes actions.
4. Reproducible AWS + COOL evidence.
5. Reliability and failure handling.
6. UX/presentation polish.
7. Extra features.
