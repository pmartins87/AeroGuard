# AWS Compute Grant Proposal - AeroGuard Vision

**Team name:** AeroGuard Vision  
**Team member:** Paulo Martins (solo builder)  
**Competition:** OpenCV AI Competition 2026, powered by AWS  
**Focus paths:** Best Use of COOL + Agentic Vision  
**Repository:** `pmartins87/OpenCV`

## One-sentence project

AeroGuard Vision detects a possible runway Foreign Object Debris (FOD) hazard, decides what visual evidence it still needs, re-checks the scene with OpenCV 5, and routes only verified risk to human review.

## Why this team can execute

The project lead is a professional air traffic controller with firsthand operational aviation experience and ongoing software/computer-science work. That creates unusually strong problem/domain fit for an airport-safety computer-vision project: the application is being designed around auditable evidence, uncertainty, human control, and operationally understandable outputs rather than a purely academic detector.

Competition experience includes active participation in 2026 AI/code competitions, including ARC Prize 2026 and Kaggle challenges. Development is tracked in a public GitHub repository with a roadmap, status ledger, architecture, dataset provenance, tests, CI, and evaluation methodology.

### Execution proof already completed

Before requesting AWS compute, the project has already moved beyond the idea stage:

- OpenCV `5.0.0.93` is pinned and verified in GitHub Actions.
- The latest CI run passes the OpenCV 5 version gate, unit/integration tests, and deterministic demo.
- Five automated tests currently pass.
- A deterministic synthetic runway fixture generator is implemented.
- The first OpenCV pipeline runs end to end: reference comparison -> `absdiff` -> blur -> threshold -> morphology -> connected components -> temporal persistence.
- The CLI emits machine-readable event JSON, annotated evidence video, and event-level evidence crops.
- A bounded multi-step agent trace already uses visual evidence to trigger crop inspection, persistence/track verification, and a later `reinspect` or `human_review` action.

The AWS grant therefore funds the remaining AWS-specific execution risk - Graviton4, COOL, repeated application benchmarks, observability, and judge-accessible deployment - rather than basic feasibility discovery.

## Problem and intended real-world impact

Foreign Object Debris on airport runways and taxiways can damage aircraft and creates a recurring inspection burden. AeroGuard Vision is a computer-vision inspection assistant that detects a possible foreign object, evaluates the quality and persistence of the visual evidence, chooses what visual check to perform next, and routes only verified risk candidates to human review.

The intended beneficiaries are airport safety, airfield inspection, and maintenance teams that need faster triage, fewer nuisance alerts, and clear visual evidence behind each review request. The system is inspection decision support, not an autonomous airport-control or runway-closure system.

## OpenCV 5 image/video analysis

OpenCV 5 is the core perception layer. The reproducible baseline already uses video decoding, color conversion, Gaussian filtering, reference/background comparison, absolute difference, thresholding, morphology, connected components, ROI/crop processing, temporal persistence, evidence extraction, and visualization.

The real-data stage will add a learned FOD detector while OpenCV remains responsible for preprocessing, geometry, temporal verification, tracking, post-processing, evidence extraction, visualization, and evaluation. The primary public-data candidate is FOD-A, an airport FOD dataset reported to contain 31 object categories and more than 30,000 annotated instances with lighting and weather metadata. Exact archive provenance, license applicability, and checksums will be frozen before model training/evaluation.

## Agentic Vision workflow

AeroGuard does not stop after a fixed detection. Visual evidence changes what the system does next.

1. OpenCV identifies a candidate and returns location, size, persistence, scene-quality, and evidence metrics.
2. The orchestrator classifies the evidence as weak, uncertain, or strong.
3. It selects a later visual tool: targeted crop inspection, temporal-window inspection, baseline comparison, or track/persistence verification.
4. New OpenCV evidence is produced and recorded in the trace.
5. The event is closed, re-inspected, or routed to human review.

A deterministic bounded controller is implemented first so task success is measurable and reproducible. Amazon Bedrock may be added later as a model-backed orchestrator only if it improves measured tool selection/final decisions while preserving deterministic safety gates and fallback behavior.

## Planned AWS architecture

Primary path:

`video/images -> Amazon S3 -> EC2 Graviton4 + COOL/OpenCV 5 -> bounded agent/orchestrator -> evidence/event output -> human review / judge UI`

Supporting services:

- Amazon CloudWatch for structured logs, performance metrics, failures, and traceability.
- Amazon Bedrock as an optional later orchestration component if it earns its complexity through measured task-success gains.
- The official COOL Graviton4 Marketplace path for the optimized OpenCV 5 workload.

The application preserves a deterministic local demo path so judging never depends on a fragile camera feed or external model response.

## How the $150 grant will be used

The project is aligned with the competition's two-stage grant process.

### First 50% - integration and de-risking

- Bring the existing OpenCV 5 workload onto EC2 Graviton4.
- Validate the official COOL environment and freeze exact versions/configuration.
- Build the vanilla OpenCV 5 vs COOL application benchmark harness.
- Add CloudWatch instrumentation and structured trace logging.
- Run the first real-data FOD baseline on the AWS path.

### Progress check-in milestone

By the required September check-in, the target evidence is:

- core OpenCV 5 workload running reproducibly on Graviton4;
- COOL executing the claimed application workload;
- first paired baseline/COOL measurements;
- real-data perception baseline underway;
- public repo showing active development, tests, and benchmark records.

### Remaining 50% - benchmark campaign and judge path

- Repeat frozen-manifest COOL vs vanilla runs with warmup and multiple repetitions.
- Measure median/p95 latency, throughput, dispersion, utilization where practical, and estimated cost per processed video minute.
- Run reliability/failure tests and verify trace/observability coverage.
- Maintain a small judge-accessible AWS demonstration path and capture final submission evidence.

## Evaluation and judge demonstration

Perception evaluation will report precision, recall, F1/AP where appropriate, false positives, object-size slices, and lighting/weather robustness when supported by the source data. Verification value will be measured by false-alert reduction and retained/missed true detections.

Agentic evaluation will use deterministic scenarios with expected next tools and final outcomes. Metrics include correct next-tool selection, final task success, unnecessary human-review rate, missed-review rate, failure recovery, and trace completeness.

COOL evaluation will use the same frozen input manifest, comparable Graviton4 configurations, fixed warmup, repeated runs, and recorded environment metadata. Every result will capture instance type, region, OpenCV/COOL version, Python version, application commit SHA, and input hashes.

The judge demo will show one complete event in under a minute: suspected object -> initial OpenCV evidence -> agent-selected re-check -> new evidence -> final close/reinspect/human-review decision, followed by the architecture and a compact COOL benchmark result.

## Responsible operation

AeroGuard will not claim runway-closure authority, aircraft-control capability, or deployment readiness. Consequential decisions remain human-controlled. The system will expose uncertainty, retain visual traces, record failures, and document dataset/domain-shift limitations.

## References

- Competition: `https://opencv26.devpost.com/`
- Repository: `https://github.com/pmartins87/OpenCV`
- Primary dataset candidate: `https://github.com/FOD-UNOmaha/FOD-data`
