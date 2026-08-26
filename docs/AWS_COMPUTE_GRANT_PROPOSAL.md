# AWS Compute Grant Proposal - AeroGuard Vision

**Team name:** AeroGuard Vision  
**Team member:** Paulo Martins (solo builder)  
**Competition:** OpenCV AI Competition 2026, powered by AWS  
**Focus paths:** Best Use of COOL + Agentic Vision  
**Repository:** `pmartins87/OpenCV`

## What this proposal is about

AeroGuard Vision is a computer-vision assistant for airport runway inspection. It looks for Foreign Object Debris (FOD) - objects that should not be on a runway or taxiway - and uses additional visual checks before asking a person to intervene.

We are requesting the AWS Compute Grant to move our already-working OpenCV 5 prototype to AWS Graviton4, validate COOL, and produce reproducible performance evidence for the final competition submission.

## The problem

Small pieces of debris, tools, stones, metal, plastic, or other unexpected objects can create real risk on airport movement areas. Visual inspection is therefore important, but automated systems can create too many false alarms if every weak detection is treated as an emergency.

AeroGuard Vision is designed around a simple principle:

**detect first -> verify intelligently -> involve a human when the visual evidence justifies it**

The intended users are airport safety, airfield inspection, and maintenance teams. The project is inspection decision support, not an autonomous runway-control or runway-closure system.

## How AeroGuard Vision works

1. **Detect:** OpenCV sees a possible object on the runway or taxiway.
2. **Question:** the system checks whether the evidence is strong enough to trust.
3. **Re-check:** if the result is uncertain, the agent requests the most useful next visual inspection - for example a tighter crop, temporal window, baseline comparison, or persistence/track verification.
4. **Decide:** the new evidence can close the event, trigger another inspection, or request human review.

This is the Agentic Vision part of the project. The system does more than label an image: an OpenCV result changes which visual tool is called next, and the next result can change the final action.

## What already exists today

The project is beyond the idea stage before requesting AWS compute:

- OpenCV `5.0.0.93` is pinned and verified in GitHub Actions.
- Five automated tests currently pass.
- A deterministic synthetic runway/video fixture generator exists.
- The first perception pipeline runs end to end: reference comparison -> `absdiff` -> blur -> threshold -> morphology -> connected components -> temporal persistence.
- A bounded multi-step agent trace uses visual evidence to trigger crop inspection and persistence/track verification before choosing `reinspect` or `human_review`.
- The CLI produces machine-readable event JSON, an annotated output video, and event-level evidence crops.
- GitHub Actions verifies the OpenCV 5 environment and runs the deterministic demo successfully.
- Latest passing CI run recorded by the project: `32980264697`.

The main technical unknown is therefore AWS-specific rather than basic feasibility.

## Why AWS compute is the next step

The next question is whether the real OpenCV workload runs cleanly on AWS Graviton4 with COOL, and what measurable performance or cost benefit COOL provides compared with a vanilla OpenCV 5 baseline.

The grant directly funds that validation:

- Graviton4 + COOL integration;
- paired vanilla OpenCV 5 vs COOL application benchmarks;
- CloudWatch observability and structured logs;
- repeated benchmark runs;
- the first real-data FOD baseline on the AWS path;
- a small judge-accessible deployment/demo path.

## Why this team

The project lead is a professional air traffic controller with operational aviation experience and ongoing computer-science/software work. That gives the project direct domain context for airport operations while keeping the engineering focus on auditable evidence, uncertainty, human control, and reproducibility.

Competition experience includes active participation in 2026 AI/code competitions including ARC Prize 2026 and Kaggle challenges. Development is tracked publicly with roadmap, status, architecture, dataset provenance, tests, CI, and evaluation methodology.

## Technical plan on AWS

Primary path:

`video/images -> Amazon S3 -> EC2 Graviton4 + COOL/OpenCV 5 -> bounded agent/orchestrator -> evidence/event output -> human review / judge UI`

Supporting services:

- **Amazon CloudWatch:** structured logs, failures, traces, and performance measurements.
- **Amazon Bedrock:** optional later orchestration component; it stays only if measured agent task success improves without weakening deterministic safety gates.
- **COOL on Graviton4:** the optimized OpenCV 5 path used for the competition benchmark.

A deterministic local demo remains available so judging does not depend on a fragile live feed or external model response.

## What the $150 grant will produce

### 1. Integration

Move the existing OpenCV 5 workload to Graviton4, validate COOL, and freeze exact versions and configuration.

### 2. Paired benchmark

Run the same frozen inputs on vanilla OpenCV 5 and COOL using the same Graviton4 setup, fixed warmup, and repeated measurements.

### 3. Real-data baseline

Acquire and validate FOD-A provenance/license, then establish a first real FOD detection baseline and failure-case set.

### 4. Final evidence

Produce reproducible measurements for latency, throughput, dispersion, utilization where practical, estimated cost per processed video minute, agent task success, false-alert reduction, and trace completeness.

## How we will judge whether it works

### Perception quality

Precision, recall, F1/AP where appropriate, false positives, and performance by object size and scene conditions when the data supports those slices.

### Value of re-checking

How many false alerts are removed after verification, while tracking whether true detections are retained or missed.

### Agentic behavior

Correct next-tool selection, final task success, unnecessary or missed human-review requests, failure recovery, and trace completeness.

### COOL value

Median and p95 latency, throughput, run-to-run dispersion, CPU utilization where practical, and estimated cost per processed video minute.

### Reproducibility

Instance type, region, OpenCV/COOL versions, Python version, application commit SHA, frozen input hashes, and structured logs.

## What a judge will see

A suspected object appears -> OpenCV creates the first evidence -> the agent chooses a targeted visual re-check -> new evidence arrives -> the event is closed, re-inspected, or sent to human review.

The demo then shows the AWS/COOL benchmark that measures the same real application workload.

## Responsible scope

AeroGuard Vision is an inspection decision-support prototype. It does not claim authority to close a runway, control aircraft, or replace certified airport procedures. Consequential decisions remain human-controlled. The final submission will expose uncertainty, visual evidence, failures, dataset provenance, and known domain-shift limitations.

## References

- Competition: `https://opencv26.devpost.com/`
- Repository: `https://github.com/pmartins87/OpenCV`
- Primary data candidate: `https://github.com/FOD-UNOmaha/FOD-data`
