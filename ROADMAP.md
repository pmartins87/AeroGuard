# ROADMAP - OpenCV AI Competition 2026

Goal: maximize probability of an **Overall Award** while remaining fully eligible and competitive for **Best Use of COOL** and **Agentic Vision**.

Final deadline: **2026-10-26 23:59 PT**.
Internal target: **submit on 2026-10-25 with at least 24 hours of buffer**.

Current position (2026-08-27): **R0 closed; R1/R2 active; the deterministic R3 Agentic Vision exit gate has already been met in parallel.**

## R0 - Competition intelligence and scope freeze | Aug 26-28

Exit gate:
- [~] Devpost project overview saved; final Project Details/Additional Info intentionally remain open until final media/report artifacts exist.
- [x] AWS Compute Grant proposal submitted on 2026-08-26.
- [x] Working concept stress-tested against all six overall judging criteria.
- [x] Both special-award eligibility requirements mapped to concrete evidence.
- [x] MVP hazard taxonomy frozen around FOD inspection.
- [x] Dataset/license plan documented in `docs/DATA_LEDGER.md`.
- [x] Architecture v1 documented in `docs/ARCHITECTURE.md`.
- [x] FOD-A v2.1 archive provenance frozen and corrected corpus audit recorded.

Status: **complete for build purposes.** Final Devpost fields are a submission-package task, not an R0 blocker.

## R1 - Reproducible OpenCV 5 baseline | Aug 29-Sep 5

Build the smallest end-to-end pipeline that judges could run.

Deliverables:
- [x] Python environment with pinned `opencv-python-headless==5.0.0.93`.
- [x] OpenCV 5 version check in CI.
- [x] Deterministic sample video fixture generator.
- [~] Frame ingest, reference comparison, candidate extraction and temporal persistence implemented; stabilization/ROI policy still pending.
- [~] Connected-components baseline + persistence exists; learned detector OpenCV DNN interface and GPU train/eval path are implemented, while first trained FOD weights remain pending.
- [x] CLI produces machine-readable event JSON, annotated output video, and event-level evidence crops.
- [x] Unit/integration tests, including artifact generation.
- [x] GitHub Actions OpenCV 5 smoke test. Current full CI reference `33033468004`: PASS.

Exit gate: one command turns a known video into reproducible detections + evidence.

Synthetic/deterministic exit gate is met. R1 remains open until the first real-data FOD detector is integrated and the reference/ROI assumptions are documented against real data.

## R2 - Perception quality and hazard verification | Sep 6-12

Deliverables:
- [x] High-level FOD hazard/event taxonomy and evaluation schema frozen.
- [~] Primary real-data detection path engineered: deterministic FOD-A preparation, YOLOX-tiny training runbook, ONNX export, OpenCV 5 DNN inference, metric/failure-analysis evaluator. First trained checkpoint/metrics pending.
- [ ] Temporal verification and multi-frame tracking beyond simple persistence on real detector outputs.
- [ ] Scene-quality checks (blur, darkness, occlusion/compression where feasible).
- [ ] Confidence calibration/threshold policy from real validation data.
- [ ] Baseline precision/recall/F1/AP and failure-case set.
- [ ] Dedicated small-object performance slice on the audited FOD-A corpus.

Current external/mechanical issues:
- The official FOD-A Google Drive download is temporarily rate-limited in CI. Earlier verified provenance artifacts remain valid, but exact source split counts/hashes still need a successful fresh archive pass.
- The first YOLOX/OpenCV contract workflow exposed a build-isolation issue; the workflow has been corrected to make the already-installed frozen CPU Torch visible to YOLOX setup and is being revalidated.

Exit gate: measurable real-data perception baseline with documented limitations.

## R3 - Agentic Vision loop | Sep 13-19

The agent must do more than explain a result. OpenCV output must change a later decision/tool call/action.

Tool set:
- [x] `inspect_frame`
- [x] `inspect_crop`
- [x] `inspect_temporal_window`
- [x] `compare_baseline`
- [x] `verify_track`
- [x] `request_human_review`
- [x] `close_or_escalate_event`

Evidence:
- [x] Trace schema records perception -> decision -> action.
- [x] Uncertain cases trigger targeted re-analysis actions.
- [x] Human-review action protects consequential escalation.
- [x] Judge-visible evidence crops and annotated video are generated for the deterministic trace.
- [x] Deterministic tool-failure fallback implemented; failures never upgrade risk.
- [x] Frozen deterministic scenario suite contains 14 cases and requires 100% expected-decision success.
- [ ] Feed real learned-detector outputs into this controller and measure false-alert reduction.
- [ ] Model-backed orchestrator experiment (e.g. Bedrock) only if it improves measured task success.

Exit gate: at least 10 deterministic scenarios demonstrate correct multi-step behavior.

Status: **deterministic exit gate met ahead of schedule.** Real-data integration remains part of R2/R5 evidence.

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
- [ ] Precision/recall/AP or equivalent perception metrics.
- [ ] Agent task-success rate on integrated scenarios.
- [ ] False-alarm reduction after verification.
- [ ] End-to-end latency.
- [ ] Failure categories and stress tests.
- [ ] Small-object and adverse-condition slices where supported by data.

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
- [~] Devpost working copy exists; final fields/media intentionally pending.

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
