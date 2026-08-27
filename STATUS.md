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
- **R2:** active. FOD-A corpus acquisition/audit, YOLOX-tiny training/export, OpenCV 5 DNN inference and evaluation tooling are implemented. The YOLOX -> ONNX -> OpenCV 5 numeric contract is now verified. A defective source split discovered in the structurally equivalent mirror is being replaced by a leakage-aware evaluation split before training.
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
- [x] Current core CI reference `33040936852`: **SUCCESS**.
- [x] FOD-A v2.1 official archive SHA-256 previously frozen at `408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`.
- [x] Corrected audited corpus frozen at **33,793 annotated images / 34,472 objects / 31 labels**, all 300x300.
- [x] Dedicated small-object slice established: **9,852 objects (28.58%)** below 1,024 px².
- [x] Public Kaggle mirror acquisition path verified to reproduce the frozen corpus audit exactly: same image/annotation count, object count, class counts, dimensions and small-object count. Canonical provenance remains the official source/archive.
- [x] Mirror verification run `33040936854`: **SUCCESS** and evidence artifact retained.
- [x] Strict VOC parser, split-audit tooling, deterministic split utilities and deterministic COCO exporter implemented.
- [x] Learned-detector path frozen around YOLOX-tiny training -> ONNX -> **OpenCV 5 DNN production inference**.
- [x] YOLOX -> decoded ONNX -> OpenCV 5 DNN contract passed in run `33037208949`.
- [x] Contract evidence: preprocessing max abs diff **0.0**; PyTorch/OpenCV decoded output max abs diff **0.0047874451**, mean abs diff **4.45198e-06**, `rtol=atol=0.01`, `allclose=true`.
- [x] GPU runbook/script created for dataset prep -> train -> export -> OpenCV evaluation -> evidence/hashes.
- [x] Evaluator reports TP/FP/FN, precision/recall/F1, small-object recall, per-class recall, latency/throughput and failure examples.
- [x] Agentic tool chain explicitly includes `inspect_frame`, `inspect_crop`, `compare_baseline`, `verify_track`, `inspect_temporal_window`, `request_human_review`, and `close_or_escalate_event`.
- [x] Deterministic tool-failure behavior is fail-safe: failures do not autonomously escalate consequential risk.
- [x] Agentic qualification suite expanded to **14 deterministic scenarios** and CI requires 100% expected-decision success.
- [x] Devpost Overview saved; final Project Details/Additional Info remain intentionally open until final report/video/demo artifacts exist.

## Important R2 finding: source split gate failed

The FOD-A v2.1 tree obtained from the public Kaggle mirror is structurally equivalent to the previously audited official corpus, but its provided Pascal VOC `trainval.txt` / `test.txt` split is **not acceptable as a clean evaluation holdout**:

- `trainval.txt`: 25,345 raw entries, 25,298 unique IDs, 47 duplicate occurrences;
- `test.txt`: 8,448 raw entries, 8,429 unique IDs, 19 duplicate occurrences;
- four IDs occur in both trainval and test: `014567`, `015731`, `016653`, `016763`;
- the union covers 33,723 of 33,793 annotation IDs, leaving 70 images uncovered;
- there are no split IDs without annotations.

This split evidence is currently marked **provisional** because the current official Google Drive quota prevents a fresh byte-source comparison of the split files against the official archive. We will not train/evaluate against the defective mirror split. The official source URL and previously frozen official archive hash remain canonical provenance.

The dataset was generated from video frames (15 fps), so random frame-level splitting would also create a material temporal-leakage risk. The active task is therefore to infer/freeze sequence groups and create a deterministic leakage-aware replacement split. Run `33041114427` is measuring metadata and adjacent-frame visual transitions for that purpose.

## ACTIVE / NEXT

1. Finish the sequence-boundary probe and freeze a deterministic leakage-aware FOD-A train/validation/test policy.
2. Recheck the split files against the official byte-source archive as soon as the Google Drive quota permits; preserve the defect result either way.
3. Generate and hash the replacement split, including class/environment/group-coverage evidence and explicit zero group overlap.
4. Execute the first GPU YOLOX-tiny training baseline and export it to ONNX.
5. Repeat the OpenCV DNN numeric acceptance gate on the trained FOD checkpoint.
6. Produce real-data precision/recall/F1/AP plus small-object results and failure cases.
7. Feed learned-detector outputs into the agent loop and quantify false-alert reduction.
8. Add scene-quality checks and threshold calibration only where validation evidence shows value.
9. Execute AWS Graviton4 + COOL benchmarking when credits/access are available.
10. Build judge-facing dashboard/demo, finalize report/video/Devpost, adversarially review, and submit Oct 25.

## Current risks

There is **no project-design blocker**. Current friction is concentrated in: deriving a leakage-defensible evaluation split from video-derived FOD-A frames, temporary official Google Drive quota, first real GPU training, and later AWS/COOL access. The YOLOX/OpenCV runtime contract is no longer a blocker.

## Competition-ready evidence still required

- Leakage-aware frozen real-data split and source-provenance reconciliation.
- Real-data perception quality and small-object performance.
- Integrated agent task-success and false-alarm reduction.
- End-to-end latency/throughput.
- COOL vs vanilla OpenCV 5 comparison on comparable Graviton hardware.
- Judge-accessible deployment/demo and reproducible clean-environment path.
- Technical report, <=5-minute demo video, final Devpost fields, failure/limitation evidence and final link/permission audit.

See `ROADMAP.md` for the complete R0-R10 plan, `docs/R2_LEARNED_BASELINE.md` for the detector contract, and `docs/R3_AGENTIC_SCENARIOS.md` for the deterministic Agentic Vision gate.
