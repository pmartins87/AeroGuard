# R0 Scope Freeze - AeroGuard Vision

Date: 2026-08-26

## Decision

Freeze the MVP around **agentic foreign-object-debris (FOD) inspection of runway/taxiway imagery and video**.

The earlier broad concept included wildlife, vehicle intrusion, abnormal scene changes, and surface anomalies. Those remain future extensions, but the competition MVP will optimize for depth, measurable evidence, and a reliable judge demo.

## Why the scope is now narrower

A strong public FOD dataset exists, the safety problem is easy to understand, OpenCV 5 can remain visibly central to the processing pipeline, and the agent can perform useful multi-step verification instead of merely describing detections.

Primary public data candidate:
- FOD-A official repository: https://github.com/FOD-UNOmaha/FOD-data
- Dataset paper: https://arxiv.org/abs/2110.03072

The FOD-A project reports 31 object categories and more than 30,000 annotated instances, including light-level and weather labels. This gives us a credible path for both detection evaluation and robustness slices.

## Frozen MVP hazard taxonomy

### P0 - Foreign object candidate
An unexpected localized object or visual anomaly on a runway/taxiway surface that may warrant inspection.

### P1 - Verified persistent FOD candidate
A P0 candidate that survives temporal or alternate-processing verification.

### P2 - Human-review event
A verified candidate whose visual evidence crosses a conservative review threshold. The system does not claim authority to close a runway or issue an operational instruction.

Deferred until after the P0-P2 path is quantitatively strong:
- wildlife classification;
- vehicle/person intrusion;
- pavement defect classification;
- autonomous operational actions.

## Required agentic loop

The minimum competition trace is:

1. `inspect_frame` or baseline comparison produces a candidate and visual metrics.
2. The orchestrator evaluates uncertainty/severity.
3. It chooses a later visual action such as crop inspection, temporal verification, alternative preprocessing, or track verification.
4. New OpenCV evidence is returned.
5. The new evidence changes the next decision.
6. Consequential escalation routes to human review.

The deterministic R1 controller is only the measurable baseline. R3 may introduce an AWS Bedrock-backed orchestrator if it improves task success without making the demo fragile.

## AWS + COOL path

Target execution path:
- input/demo assets in S3;
- competition service on EC2 Graviton4 using the official COOL OpenCV 5 AMI;
- CloudWatch for logs/metrics;
- optional Bedrock component for the model-backed agent;
- judge-facing web UI/API in the simplest reliable form.

COOL must execute application-relevant OpenCV operations, not only isolated synthetic microbenchmarks.

## Rubric stress test

This is a target potential score, not a current score.

| Criterion | Weight | Prize-focused execution target |
|---|---:|---|
| Technical execution | 30 | OpenCV 5 is core; deterministic tests; detection metrics; failure cases; reproducible trace |
| Innovation | 20 | Active visual verification: evidence selects the next perception tool/action |
| Real-world impact | 20 | Aviation FOD is an established safety/inspection problem; avoid deployment-readiness overclaim |
| UX | 10 | Evidence-first dashboard that shows candidate, re-check, changed confidence, and human review |
| Documentation/presentation | 10 | Clean repo, architecture, one-command demo, <=5-minute story |
| Cloud/reproducibility/responsibility | 10 | AWS/COOL evidence, observability, security basics, human control, cost discipline |

Internal target: **>=85/100 in skeptical pre-submission scoring**, with no single category depending on an unsupported claim.

## Main risks and mitigations

1. **Tiny-object difficulty / domain shift**
   - Use FOD-A as the primary benchmark, preserve realistic resolution, report size-conditioned metrics, and build synthetic deterministic fixtures only as supplementary tests.

2. **Agentic behavior feels decorative**
   - Measure correct next-tool selection and final event decision on deterministic scenarios; show traces where later visual evidence changes the outcome.

3. **COOL path becomes a late deployment problem**
   - Introduce benchmarkable OpenCV operations from R1 and validate the official Graviton4 AMI path early in R4.

4. **Safety overclaim**
   - Frame AeroGuard as decision support/inspection assistance with human review, not autonomous airport control.

5. **Demo fragility**
   - Keep a fully deterministic local/video demo path that does not depend on live camera feeds or an external model response.

## R0 exit criteria remaining

- Complete the Devpost project draft.
- Submit the AWS Compute Grant PDF while the proposal form remains open.
- Confirm primary dataset download and exact license/provenance of the archive used.
- Finalize architecture diagram artwork for the proposal/submission.

Everything else needed to start R1 is now sufficiently frozen.
