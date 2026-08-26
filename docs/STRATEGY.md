# Prize strategy

## Primary objective

Optimize for **judge score and award eligibility**, not feature count.

Target prize stack:
- Overall 1st place: $5,000
- Best Use of COOL: $1,000
- Agentic Vision: $1,000

One strong entry can, under the official rules, receive an Overall Award plus one or both Special Awards.

## Working concept decision

### Selected: AeroGuard Vision

Agentic visual inspection of airfield/runway video for safety hazards.

Primary MVP hazard families:
1. Foreign-object / unexpected-object candidate.
2. Wildlife or vehicle intrusion candidate.
3. Persistent abnormal scene change / obstruction.
4. Surface-anomaly candidate only if data quality supports credible evaluation.

The system intentionally avoids claiming fully autonomous operational decisions. Its strongest story is **visual inspection + uncertainty-aware verification + human-controlled escalation**.

## Why this concept wins on fit

### Technical execution — 30%

OpenCV 5 is visible and indispensable rather than a wrapper dependency:
- frame decode / sampling;
- geometric stabilization and registration;
- ROI/perspective geometry;
- temporal differencing / background modeling;
- morphology / contours / connected components;
- optical flow and/or tracking;
- image-quality diagnostics;
- DNN pre/post-processing where useful;
- visual overlays and reproducible evaluation.

### Innovation — 20%

The differentiator is not merely hazard detection. The system uses visual uncertainty to choose the next perception action. Example:

`candidate -> inspect temporal window -> crop/reprocess -> verify persistence/motion -> request human review or close event`

This directly matches the competition's emphasis on active perception and agentic orchestration.

### Real-world impact — 20%

Airfield inspection has an intuitive safety benefit and clear target users. The submission can demonstrate measurable value without claiming deployment readiness.

### User experience — 10%

Judge-facing dashboard should answer immediately:
- What did the system see?
- Why is it suspicious?
- What did the agent do next?
- What evidence changed its decision?
- Is a human action required?

### Documentation/presentation — 10%

The project is designed around traceable evidence, diagrams, deterministic fixtures, and a short visual demo storyline.

### AWS/reproducibility/responsibility — 10%

The deployment and evidence are first-class artifacts, with cost controls, logs, human approval, reproducible benchmarks, and known limitations.

## Special-award strategy

### Agentic Vision

Do not use an LLM as decorative explanation. The agent must have tools and a trace.

Minimum qualifying trace:
1. OpenCV reports a candidate + metrics.
2. Orchestrator reasons over those metrics.
3. It selects a specific next visual tool/action.
4. New OpenCV evidence returns.
5. The new evidence changes status/action.
6. Consequential escalation can require human approval.

Evaluation dimensions:
- correct next-action selection;
- final task success;
- avoided false escalation;
- tool failure recovery;
- human-control behavior.

### COOL

Use a benchmarkable OpenCV-heavy section of the real application, not a synthetic microbenchmark only.

Compare:
- same input corpus;
- vanilla OpenCV 5 baseline;
- COOL on AWS Graviton;
- repeated runs with warmup;
- latency/video throughput;
- CPU utilization if practical;
- effective cost per processed minute or equivalent.

A small microbenchmark suite can supplement the end-to-end workload, but final claims should center on application-relevant operations.

## Architecture principle

Keep the MVP narrow enough to finish and deep enough to score.

Suggested logical components:

- `ingest`: local file / S3 object first.
- `vision`: OpenCV 5 perception and evidence extraction.
- `detectors`: pluggable learned/classical detectors.
- `agent`: bounded tool-using orchestrator.
- `events`: typed event/evidence model.
- `ui`: evidence-first judge dashboard.
- `benchmarks`: perception, agent, COOL, latency.
- `deploy`: AWS infrastructure/config scripts.

## Data strategy

Data must be legally usable and demonstrable.

Preferred order:
1. public datasets with explicit license;
2. public-domain or permissively licensed video;
3. deterministic synthetic/composited test fixtures with full provenance;
4. user-generated safe demo footage if useful.

Never build the submission around data that cannot be redistributed to judges or whose rights are ambiguous.

Maintain a ledger with source URL, license, permitted use, split, preprocessing, and checksum.

## Evaluation before model sophistication

A simpler system with clean evidence can beat a larger model stack with vague claims.

Every experiment should answer one of these:
- Does perception improve?
- Does agent verification reduce false alarms or improve task success?
- Does COOL provide measurable value?
- Does AWS deployment remain reliable/reproducible?
- Does the judge demo become easier to understand?

## Scope kill rules

Cut a feature when:
- no dataset permits credible evaluation;
- it does not affect a rubric item;
- it makes the demo fragile;
- it consumes AWS cost without judge-visible value;
- it cannot be explained in the 5-minute video;
- it introduces high-stakes autonomy without adequate human control.

## Submission narrative

The final story should fit in one sentence:

> AeroGuard Vision sees a possible airfield hazard, decides what visual evidence it still needs, re-checks the scene with OpenCV 5, and only escalates verified risk through a human-controlled AWS workflow.

That sentence should remain true in the live demo, trace logs, benchmark results, report, and video.
