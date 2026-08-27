# STATUS

Last updated: 2026-08-27

## Competition

- Competition: OpenCV AI Competition 2026, powered by AWS
- Final deadline: **2026-10-26 23:59 PT**
- Internal submission target: **2026-10-25**
- Repo: `pmartins87/AeroGuard`
- Project: **AeroGuard Vision**
- Frozen MVP: **agentic runway/taxiway Foreign Object Debris (FOD) inspection**
- Prize strategy: **Overall + Best Use of COOL + Agentic Vision**

## Roadmap position

- **R0:** complete for build purposes. AWS Compute Grant V3 was submitted successfully on 2026-08-26.
- **R1:** active and mostly complete. Deterministic OpenCV 5 end-to-end baseline, evidence artifacts and gross scene-failure handling are reproducible; first real-data learned detector remains pending.
- **R2:** active. FOD-A acquisition/audit, leakage-aware split, scene-quality guardrails, detector training/export, OpenCV DNN inference/evaluation, deterministic temporal-tracking infrastructure and validation-only threshold-calibration code are in place. The first trained FOD checkpoint/metrics are the main remaining gate.
- **R3:** deterministic Agentic Vision exit gate is already met ahead of schedule with explicit perception/action tools, safe failure fallback and 14 frozen scenarios.
- **R4:** architecture and a hardware-neutral application-level benchmark harness are already implemented; actual AWS Graviton4 + COOL execution remains pending access/credits.
- **R5-R10:** planned, with Devpost draft, responsible-use posture and submission checklist already reducing later risk.

## Verified DONE

- [x] Repository is the project source of truth and canonical URL is `https://github.com/pmartins87/AeroGuard`.
- [x] Official rules/rubrics reviewed and MVP narrowed to FOD.
- [x] Architecture v1 and Overall/COOL/Agentic prize strategy documented.
- [x] AWS Compute Grant V3 submitted and submission record frozen.
- [x] OpenCV `5.0.0.93` package pinned; runtime reports OpenCV `5.0.0`.
- [x] Deterministic runway fixture, classic OpenCV baseline, CLI event JSON, annotated video and evidence crops implemented.
- [x] Synthetic fixture improved with stable asphalt-like spatial texture so lossy MP4 compression remains a realistic input to scene-quality checks.
- [x] Latest full core CI reference `33043364964`: **SUCCESS**, including all current tracking/scene-quality/calibration tests and deterministic demo smoke.

### FOD-A provenance and evaluation split

- [x] FOD-A v2.1 official archive SHA-256 previously frozen at `408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`.
- [x] Corrected audited corpus frozen at **33,793 annotated images / 34,472 objects / 31 labels**, all 300x300.
- [x] Dedicated small-object slice: **9,852 objects (28.58%)** below 1,024 px².
- [x] Public Kaggle acquisition fallback structurally reproduces the frozen corpus audit; mirror verification run `33040936854`: **SUCCESS**. Canonical provenance remains the official source/archive.
- [x] Defective mirror `trainval.txt` / `test.txt` rejected for primary evaluation: duplicates, four cross-split IDs and 70 uncovered annotation IDs.
- [x] Video-derived temporal leakage measured; sequence-boundary probe run `33041114427`: **SUCCESS**.
- [x] Deterministic leakage-aware replacement split verified in run `33041421174`: **SUCCESS**.
- [x] Frozen split covers all **33,793** IDs exactly once with zero train/val/test group overlap across **129 atomic groups**.
- [x] Split sizes: train **23,502 images / 24,181 objects / 81 groups**, val **5,092 / 5,092 / 23**, test **5,199 / 5,199 / 25**.
- [x] Small-object counts: train **6,818**, val **1,420**, test **1,614**.
- [x] Split hashes: train `57a42dce2f8336bbf5eac31f3d7243bc6d126e2a4017f3883e52b12cdb37de91`; val `a5f292105159e75f3693181e1b9ca878c535bdba41a0767b2f3786e059371b57`; test `ff86d8f896fb069c1d2c1e58997566c8a9472ec0107a1e4616101a3376f9f193`.
- [x] Six singleton-sequence classes stay in train to avoid leakage; primary strict test therefore covers **25/31 classes**, explicitly documented.

### Learned detector and evaluation contract

- [x] Learned path frozen around YOLOX-tiny training -> decoded ONNX -> **OpenCV 5 DNN production inference**.
- [x] YOLOX -> ONNX -> OpenCV DNN numeric contract passed in run `33037208949`.
- [x] Contract evidence: preprocessing max abs diff **0.0**; decoded output max abs diff **0.0047874451**, mean abs diff **4.45198e-06**, `rtol=atol=0.01`, `allclose=true`.
- [x] GPU runbook/script implements sequence-split preparation -> training -> export -> OpenCV evaluation -> evidence/hashes.
- [x] Evaluator reports TP/FP/FN, precision/recall/F1, small-object recall, per-class recall, latency/throughput and failure examples.
- [x] Validation-only threshold sweep and deterministic selection infrastructure implemented in `src/aeroguard/evaluation/calibration.py`; protocol frozen in `docs/R2_THRESHOLD_CALIBRATION.md`. Primary selection is recall-weighted F2 with fixed tie-breaks, and held-out test is prohibited from threshold tuning.

### Scene quality and failure handling

- [x] Full 33,793-image FOD-A scene-quality profile completed with OpenCV 5 in run `33042687798`.
- [x] Final conservative policy gate revalidated against the full corpus in run `33043345704`: **SUCCESS**.
- [x] Frozen gross-failure thresholds: mean luma >=60, dynamic range >=8, Laplacian variance >=9, entropy >=3.5 bits, dark fraction <=0.18, highlight-clipped fraction <=0.07.
- [x] Runtime behavior is fail-safe: an unusable frame records `reacquire`, produces no FOD escalation and breaks temporal continuity.
- [x] Integration test proves an all-black post-reference sequence yields reacquisition events and zero FOD events.
- [x] Evidence and limitations documented in `docs/R2_SCENE_QUALITY.md`.

### Temporal and Agentic Vision infrastructure

- [x] Deterministic class-aware `TemporalTracker` implemented with IoU association, confirmation after configurable hits, missed-frame expiry and explicit reset for broken evidence continuity.
- [x] Tracker tests cover persistent motion, label isolation, one-frame gap recovery, expiration and scene-failure reset. Integration with the learned detector awaits its trained ONNX output.
- [x] Agentic tool chain includes `inspect_frame`, `inspect_crop`, `compare_baseline`, `verify_track`, `inspect_temporal_window`, `request_human_review`, and `close_or_escalate_event`.
- [x] Deterministic tool failures never autonomously upgrade risk.
- [x] Agentic qualification suite has **14 deterministic scenarios** and requires 100% expected-decision success.

### R4 / COOL preparation with current resources

- [x] Hardware-neutral application-level OpenCV benchmark harness implemented and documented in `docs/R4_BENCHMARK_PROTOCOL.md`.
- [x] Harness records input SHA, runtime/OpenCV build fingerprint, warmup/repeats, p50/p95 latency, throughput and deterministic candidate/event counts.
- [x] Corrected statistic schema keeps milliseconds and frames/second units distinct.
- [x] Latest benchmark smoke run `33043345709`: **SUCCESS** on x86_64 OpenCV 5, with deterministic **36 candidate / 35 agent-event** counts in each repeat.
- [x] Current smoke fixture SHA-256: `068ade86c3aea768c247da6a094c4c38e266a5188fdce4c835d65279ae2b6f61`.
- [x] Smoke-only runtime on that GitHub runner: p50 **5.3537 ms/frame**, p95 **5.4433 ms/frame**, p50 **186.79 fps**. These are reproducibility diagnostics only and are **not** COOL performance claims.

## Important R2 finding: source split gate failed

The structurally equivalent public mirror contains a malformed Pascal VOC split:

- `trainval.txt`: 25,345 raw entries, 25,298 unique IDs, 47 duplicate occurrences;
- `test.txt`: 8,448 raw entries, 8,429 unique IDs, 19 duplicate occurrences;
- four IDs occur in both trainval and test: `014567`, `015731`, `016653`, `016763`;
- the union covers 33,723 of 33,793 annotation IDs, leaving 70 images uncovered;
- there are no split IDs without annotations.

This split evidence remains **provisional** until the split files can be rechecked against the official byte-source archive after Google Drive quota clears. We will not train/evaluate against the defective mirror split. The official source URL and previously frozen archive hash remain canonical provenance.

## ACTIVE / NEXT

1. Execute the first serious YOLOX-tiny training baseline when a CUDA GPU becomes available, using the frozen group-disjoint train/val files.
2. Repeat the OpenCV DNN numeric acceptance gate on the trained FOD checkpoint.
3. Run the frozen validation threshold sweep, select/freeze the operating point, then perform one primary strict-test evaluation.
4. Produce real-data precision/recall/F1/AP, small-object/per-class results and failure cases.
5. Feed learned OpenCV detector outputs through the new temporal tracker and Agentic Vision controller; quantify candidate suppression / false-alert reduction.
6. Recheck defective source split files against the official byte-source archive when Google Drive quota permits.
7. Extend the benchmark harness with learned OpenCV DNN mode as soon as the trained ONNX artifact exists.
8. Execute AWS Graviton4 vanilla OpenCV 5 vs COOL benchmark when credits/access are available.
9. Use remaining CPU-only development time for judge-facing evidence/UX skeleton and additional deterministic failure/stress scenarios without inventing real-data claims.
10. Finalize report/video/Devpost in R7, adversarially review in R8 and submit Oct 25.

## Current risks

There is **no project-design blocker**. Current external-resource gates are first real GPU training, temporary official Google Drive quota, and later AWS/COOL access. Dataset integrity, leakage-aware evaluation design, OpenCV/YOLOX runtime contract, gross scene-failure handling, temporal-tracking code and benchmark reproducibility infrastructure are no longer design blockers.

## Competition-ready evidence still required

- First trained real-data FOD model and validation-selected operating point.
- Primary strict-test perception quality, small-object/per-class performance and failure analysis.
- Integrated learned-detector + tracker + agent task-success / false-alert reduction.
- End-to-end latency/throughput with learned OpenCV DNN path.
- COOL vs vanilla OpenCV 5 comparison on comparable Graviton hardware.
- Judge-accessible deployment/demo and reproducible clean-environment path.
- Technical report, <=5-minute demo video, final Devpost fields, failure/limitation evidence and final link/permission audit.

See `ROADMAP.md`, `docs/R2_FODA_SEQUENCE_SPLIT_V1.md`, `docs/R2_SCENE_QUALITY.md`, `docs/R2_THRESHOLD_CALIBRATION.md`, `docs/R2_LEARNED_BASELINE.md`, `docs/R3_AGENTIC_SCENARIOS.md`, and `docs/R4_BENCHMARK_PROTOCOL.md`.
