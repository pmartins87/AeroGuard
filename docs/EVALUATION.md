# Evaluation Plan

The final submission must support every important claim with a reproducible artifact. Synthetic smoke tests and real-data quality metrics are reported separately.

## 1. Perception

Primary metrics for FOD detection:
- precision;
- recall;
- F1;
- AP/mAP when a learned bounding-box detector is active;
- false positives per image/video minute;
- detection recall by object-size bucket;
- robustness slices by light/weather when supported by dataset labels.

Critical rule: choose thresholds on validation data and freeze them before held-out evaluation.

## 2. Verification value

Compare the single-pass detector against the verification pipeline.

Report:
- false alarms before verification;
- false alarms after verification;
- true detections lost by verification;
- net precision/recall change;
- time added per event.

The agentic story is strongest if verification demonstrably removes false escalations while retaining true hazards.

## 3. Agentic Vision task evaluation

Build a deterministic scenario suite with expected actions.

Scenario dimensions:
- weak transient candidate;
- strong transient candidate;
- persistent strong candidate;
- candidate near ROI boundary;
- blur/low-quality frame;
- missing/corrupt frame;
- visual tool timeout/error;
- conflicting evidence across tools;
- repeated duplicate event;
- human-review required case.

Metrics:
- next-tool selection accuracy;
- final decision accuracy;
- unnecessary human-review rate;
- missed human-review rate;
- successful recovery from tool failures;
- trace completeness/observability.

R3 exit gate: at least 10 deterministic scenarios, then expand toward >=50 scenarios before final submission.

## 4. COOL benchmark

Frozen benchmark manifest must include:
- input hashes;
- OpenCV/COOL versions;
- EC2 instance type and region;
- CPU/vCPU count;
- Python version;
- application commit SHA;
- warmup count;
- measured repetition count.

Report:
- median and p95 frame-processing latency;
- frames/sec or video-minutes processed per wall-clock minute;
- CPU utilization where practical;
- application-level end-to-end runtime;
- estimated cost per processed video minute;
- confidence intervals or run-to-run dispersion.

Never compare different inputs or materially different instance sizes as the headline COOL-vs-vanilla result.

## 5. Reliability

Tests must cover:
- empty/too-short video;
- unsupported/corrupt input;
- dimension mismatch;
- no detected hazard;
- many candidate regions;
- deterministic replay of a fixture;
- failed optional model-backed agent path with deterministic fallback.

## 6. Judge-facing success criteria

A judge should be able to see, within 60 seconds:
1. the suspected object;
2. the initial evidence;
3. the tool/action selected by the agent because of that evidence;
4. the new evidence;
5. the final close/reinspect/human-review decision.

The full video should additionally show the AWS/COOL architecture and one compact result table.
