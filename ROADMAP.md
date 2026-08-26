# ROADMAP — OpenCV AI Competition 2026

Goal: maximize probability of an **Overall Award** while remaining fully eligible and competitive for **Best Use of COOL** and **Agentic Vision**.

Final deadline: **2026-10-26 23:59 PT**.

## R0 — Competition intelligence and scope freeze | Aug 26–28

Exit gate:
- [ ] Devpost project profile completed.
- [ ] AWS Compute Grant proposal submitted if form is open.
- [ ] Working concept stress-tested against all six overall judging criteria.
- [ ] Both special-award eligibility requirements mapped to concrete evidence.
- [ ] MVP hazard taxonomy frozen.
- [ ] Dataset/license plan documented.
- [ ] Architecture v1 diagram specified.

## R1 — Reproducible OpenCV 5 baseline | Aug 29–Sep 5

Build the smallest end-to-end pipeline that judges could run.

Deliverables:
- [ ] Python environment with pinned dependencies.
- [ ] OpenCV 5 version check in CI.
- [ ] Deterministic sample video fixtures.
- [ ] Frame ingest, stabilization/registration, ROIs, temporal comparison, candidate extraction, overlays.
- [ ] Baseline detector/tracker interface.
- [ ] CLI producing machine-readable event JSON and annotated output video.
- [ ] Unit/integration tests.

Exit gate: one command turns a known video into reproducible detections + evidence.

## R2 — Perception quality and hazard verification | Sep 6–12

Deliverables:
- [ ] Hazard classes and annotation schema.
- [ ] Primary detection path.
- [ ] Temporal verification and multi-frame tracking.
- [ ] Scene-quality checks (blur, darkness, occlusion/compression where feasible).
- [ ] Confidence calibration/threshold policy.
- [ ] Baseline metrics and failure-case set.

Exit gate: measurable perception baseline with documented limitations.

## R3 — Agentic Vision loop | Sep 13–19

The agent must do more than explain a result. OpenCV output must change a later decision/tool call/action.

Tool set target:
- [ ] `inspect_frame`
- [ ] `inspect_crop`
- [ ] `inspect_temporal_window`
- [ ] `compare_baseline`
- [ ] `verify_track`
- [ ] `request_human_review`
- [ ] `close_or_escalate_event`

Evidence:
- [ ] Trace schema records perception -> decision -> action.
- [ ] Uncertain cases trigger targeted re-analysis.
- [ ] Human approval protects consequential escalation.
- [ ] Timeouts/tool failures have fallback behavior.

Exit gate: at least 10 deterministic scenarios demonstrate correct multi-step behavior.

## R4 — AWS deployment + COOL path | Sep 20–27

Deliverables:
- [ ] Meaningful component deployed on AWS.
- [ ] Graviton ARM path documented.
- [ ] COOL environment/version captured.
- [ ] Benchmark harness compares COOL against vanilla OpenCV 5.
- [ ] Same inputs, comparable hardware/configuration, repeated runs.
- [ ] Latency, throughput, utilization and estimated cost reported.
- [ ] Evidence that COOL executes the claimed core workload.
- [ ] Observability/logging enabled.

Exit gate: reproducible AWS run plus honest, statistically defensible COOL comparison.

## R5 — Evaluation campaign | Sep 28–Oct 5

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

## R6 — Judge-facing product and UX | Oct 6–12

Deliverables:
- [ ] Web dashboard.
- [ ] Annotated evidence viewer.
- [ ] Agent trace/timeline.
- [ ] Clear human approve/reject interaction.
- [ ] Demo mode that cannot depend on fragile external inputs.
- [ ] Architecture diagram v2.

Exit gate: a judge can understand the value and see the core loop in under 60 seconds.

## R7 — Submission package | Oct 13–20

Deliverables required by competition:
- [ ] Technical report.
- [ ] Judge-accessible repository/archive.
- [ ] Pinned dependencies.
- [ ] Build/deploy/test instructions.
- [ ] Architecture diagram.
- [ ] Working web endpoint or arranged live demo.
- [ ] <=5 minute public/unlisted demo video.
- [ ] Evaluation evidence including failures/limitations.
- [ ] Responsible-use section.

Exit gate: complete submission rehearsed from a clean machine/account path.

## R8 — Adversarial review and final freeze | Oct 21–24

- [ ] Re-score project against the official 100-point rubric as a skeptical judge.
- [ ] Remove unsupported marketing claims.
- [ ] Reproduce top benchmark numbers.
- [ ] Test broken-network/demo fallback.
- [ ] Verify all links and judge permissions.
- [ ] Confirm special-award opt-ins and evidence.

Exit gate: zero known submission blockers.

## R9 — Submit with buffer | Oct 25

Target internal submission deadline: **at least 24 hours before official cutoff**.

- [ ] Final Devpost submission.
- [ ] Verify rendered page/video/repo links.
- [ ] Archive submission snapshot and hashes in repo.

## R10 — Emergency buffer | Oct 26

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
