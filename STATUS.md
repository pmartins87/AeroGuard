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
- **R1:** active and mostly complete. The deterministic OpenCV 5 end-to-end baseline is reproducible; first real-data learned detector remains pending.
- **R2:** active early. FOD-A preparation, YOLOX-tiny training, ONNX export, OpenCV 5 DNN evaluation and failure-analysis tooling are implemented; first trained checkpoint/metrics remain pending.
- **R3:** deterministic Agentic Vision exit gate has already been implemented ahead of schedule with explicit perception/action tools, safe failure fallback and 14 frozen scenarios.
- **R4-R10:** planned. Architecture, Devpost draft, responsible-use posture and submission checklist already reduce later risk.

## Verified DONE

- [x] Repository is the project source of truth and canonical URL is `https://github.com/pmartins87/AeroGuard`.
- [x] Official rules/rubrics reviewed and MVP narrowed to FOD.
- [x] Architecture v1 and Overall/COOL/Agentic prize strategy documented.
- [x] AWS Compute Grant V3 submitted and submission record frozen.
- [x] OpenCV `5.0.0.93` environment pinned.
- [x] Deterministic synthetic video fixture and classic OpenCV baseline implemented.
- [x] CLI emits event JSON, annotated video and evidence crops.
- [x] Full CI run `33033468004` passed after the GPU training/evaluation execution path was added.
- [x] FOD-A v2.1 archive SHA-256 frozen at `408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`.
- [x] Corrected audited corpus frozen at **33,793 annotated images / 34,472 objects / 31 labels**, all 300x300.
- [x] Dedicated small-object slice established: **28.58%** of objects are below 1,024 px².
- [x] Strict VOC parser, source split auditor, deterministic class-aware development split builder and deterministic COCO exporter implemented.
- [x] Learned-detector path frozen around YOLOX-tiny training -> ONNX -> **OpenCV 5 DNN production inference**.
- [x] GPU runbook/script created for dataset prep -> train -> export -> OpenCV evaluation -> evidence/hashes.
- [x] Evaluator reports TP/FP/FN, precision/recall/F1, small-object recall, per-class recall, latency/throughput and failure examples.
- [x] Agentic tool chain explicitly includes `inspect_frame`, `inspect_crop`, `compare_baseline`, `verify_track`, `inspect_temporal_window`, `request_human_review`, and `close_or_escalate_event`.
- [x] Deterministic tool-failure behavior is fail-safe: failures do not autonomously escalate consequential risk.
- [x] Agentic qualification suite expanded to **14 deterministic scenarios** and CI requires 100% expected-decision success.
- [x] Devpost Overview saved; final Project Details/Additional Info remain intentionally open until final report/video/demo artifacts exist.

## ACTIVE / NEXT

1. Revalidate the corrected YOLOX -> ONNX -> OpenCV 5 contract workflow. Previous run `33033177439` failed mechanically because pip build isolation hid the already-installed Torch dependency; the workflow now uses `--no-build-isolation`. New run `33037034202` is executing.
2. Complete exact `trainval.txt` / `test.txt` counts, hashes, overlap and annotation coverage. Latest FOD-A probe `33033177424` was blocked by the official Google Drive download quota, not by AeroGuard code.
3. Freeze the deterministic development split from source `trainval.txt` while preserving source `test.txt` as held-out.
4. Execute the first GPU YOLOX-tiny training baseline and export it to ONNX.
5. Produce real-data precision/recall/F1/AP plus small-object results and failure cases.
6. Feed learned detector outputs into the agent loop and quantify false-alert reduction.
7. Add scene-quality checks and threshold calibration only where validation evidence shows value.
8. Execute AWS Graviton4 + COOL benchmarking when credits/access are available.
9. Build judge-facing dashboard/demo after perception and agent evidence stabilize.
10. Finalize report/video/Devpost in R7, adversarially review in R8 and submit Oct 25.

## Current risks

There is **no project-design blocker**. Current friction is mechanical/external: temporary FOD-A Google Drive quota, the YOLOX contract revalidation now running after a known build-isolation fix, first real GPU training, and later AWS/COOL access.

## Competition-ready evidence still required

- Real-data perception quality and small-object performance.
- Integrated agent task-success and false-alarm reduction.
- End-to-end latency/throughput.
- COOL vs vanilla OpenCV 5 comparison on comparable Graviton hardware.
- Judge-accessible deployment/demo and reproducible clean-environment path.
- Technical report, <=5-minute demo video, final Devpost fields, failure/limitation evidence and final link/permission audit.

See `ROADMAP.md` for the complete R0-R10 plan and `docs/R3_AGENTIC_SCENARIOS.md` for the deterministic Agentic Vision gate.
