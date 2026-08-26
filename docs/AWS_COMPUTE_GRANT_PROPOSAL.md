# AWS Compute Grant Proposal - AeroGuard Vision

**Team name:** AeroGuard Vision  
**Competition:** OpenCV AI Competition 2026, powered by AWS  
**Focus paths:** Best Use of COOL + Agentic Vision

## Problem and intended impact

Foreign Object Debris (FOD) on airport runways and taxiways can damage aircraft and creates a recurring inspection burden. AeroGuard Vision is a computer-vision inspection assistant that detects a possible foreign object, evaluates the quality and persistence of the visual evidence, chooses what visual check to perform next, and routes only verified risk candidates to human review.

The project is intentionally designed as inspection decision support rather than an autonomous airport-control system. The intended beneficiaries are airport safety and maintenance teams who need faster triage, fewer nuisance alerts, and clear visual evidence behind each review request.

## OpenCV 5 image/video analysis

OpenCV 5 is the core perception layer. The initial reproducible pipeline uses video decoding, color conversion, Gaussian filtering, background/reference comparison, absolute difference, thresholding, morphology, connected components, ROI/crop processing, and temporal persistence. The next stage will add a learned FOD detector while keeping OpenCV 5 responsible for preprocessing, geometry, temporal verification, tracking, post-processing, evidence extraction, visualization, and evaluation.

The primary public-data candidate is FOD-A, a dataset created specifically for airport foreign-object-debris computer vision and reported to contain 31 object categories and more than 30,000 annotated instances, including lighting and weather metadata.

## Agentic Vision plan

AeroGuard does not stop after a fixed detection. Visual evidence changes what the system does next.

Example loop:

1. OpenCV identifies a candidate and returns confidence, size, location, image-quality, and temporal metrics.
2. The orchestrator determines whether evidence is weak, uncertain, or strong.
3. It chooses a subsequent visual tool: targeted crop inspection, temporal-window inspection, baseline comparison, or track verification.
4. New OpenCV evidence is returned.
5. The event is closed, re-inspected, or sent to human review.

A deterministic bounded controller is being implemented first so task success can be measured. A model-backed orchestrator using Amazon Bedrock may be added if it improves correct tool selection and final decisions while preserving deterministic safety gates and fallback behavior.

## AWS architecture

The planned AWS path is:

`video/images -> Amazon S3 -> EC2 Graviton4 + COOL/OpenCV 5 -> agent orchestration -> evidence/event API -> judge-facing UI`

Supporting services:
- Amazon CloudWatch for structured logs, performance metrics, failures, and traceability;
- Amazon Bedrock as an optional R3 model-backed orchestration component;
- an official COOL Graviton4 Marketplace AMI for the optimized OpenCV 5 workload.

The application will preserve a local deterministic demo path so judging never depends on a fragile live camera or external model response.

## COOL evaluation

The project is pursuing the Best Use of COOL award with a real application workload rather than a microbenchmark-only claim. We will run the same frozen video/image manifest on comparable AWS Graviton4 configurations using vanilla OpenCV 5 and COOL, with fixed warmup and repeated runs.

Measurements will include application-level latency, throughput, run-to-run dispersion, CPU utilization where practical, and estimated cost per processed video minute. The benchmark record will include instance type, region, OpenCV/COOL version, Python version, application commit SHA, and input hashes.

## Evaluation and judge demonstration

Perception evaluation will report precision, recall, F1/AP where appropriate, false positives, object-size slices, and lighting/weather robustness when supported by the source dataset. Verification will be evaluated by measuring how many false alerts are removed and how many true detections are lost or retained.

Agentic evaluation will use deterministic scenarios with expected next actions and final outcomes. Metrics include correct next-tool selection, final task success, unnecessary human-review rate, missed review rate, failure recovery, and trace completeness.

The judge demonstration will show one complete event in under a minute: suspected object -> initial OpenCV evidence -> agent-selected re-check -> new evidence -> final human-review or close decision. The final demo will also show the AWS/COOL architecture and benchmark results.

## Target users

Primary target users are airport safety, airfield inspection, and maintenance teams. The broader architecture also generalizes to industrial visual inspection workflows where a first detection should be verified before a person is interrupted or an action is recommended.

## Responsible operation

AeroGuard will not claim runway closure authority, aircraft-control capability, or deployment readiness. Consequential decisions remain human-controlled. The system will expose uncertainty, retain visual traces, record failures, and document known limitations and dataset domain shift.

## Team bio

AeroGuard Vision is a solo, engineering-focused project organized around reproducible experimentation, measurable evidence, and disciplined scope control. Development is maintained publicly in `pmartins87/OpenCV`, with status, roadmap, architecture, dataset provenance, tests, and benchmark methodology tracked from the start. The project is being built specifically to turn limited compute resources into a polished, judge-reproducible OpenCV 5 and AWS application.

## Why the AWS Compute Grant matters

The grant will be used directly for the parts of the project that must run on AWS: early Graviton4/COOL validation, application-level benchmark repetitions, logging/observability tests, and the judge-accessible deployment path. Receiving compute early reduces the risk of discovering Arm/COOL integration issues late in the two-month build period and increases the quality of the special-award evidence.
