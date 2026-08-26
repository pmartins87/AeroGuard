# AeroGuard Vision

Prize-focused entry for the **OpenCV AI Competition 2026, powered by AWS**.

## Mission

Build a judge-ready, reproducible **agentic visual safety-inspection system** that uses **OpenCV 5** for substantive video/image analysis, runs a meaningful workload on **AWS**, and is deliberately engineered to compete for:

- Overall 1st place — **$5,000**
- Best Use of COOL — **$1,000**
- Agentic Vision — **$1,000**

Maximum prize target for one entry: **$7,000** (overall award + both special awards, subject to official rules).

## Working concept

**AeroGuard Vision** analyzes airfield/runway inspection video for safety hazards such as foreign-object debris, wildlife/vehicle intrusion, abnormal scene changes, and surface anomalies. Visual evidence drives a multi-step perception–decision–action loop: uncertain detections trigger targeted re-analysis, temporal verification, or a request for human confirmation before escalation.

The system is a **decision-support and inspection prototype**, not an operational air-traffic-control or autonomous safety system.

## Why this concept is competition-shaped

- **Technical execution:** OpenCV 5 is central to stabilization, ROI geometry, temporal analysis, change detection, tracking, quality checks, overlays, and evaluation.
- **Innovation:** visual evidence changes the next tool call/action rather than producing a one-shot label.
- **Impact:** safety inspection is concrete, measurable, and easy for judges to understand.
- **UX:** evidence-first dashboard with annotated frames, event timeline, confidence, verification state, and human approval.
- **AWS/reproducibility:** pinned environment, repeatable deployment, CloudWatch-style observability, benchmark scripts, and documented failure cases.
- **COOL:** core OpenCV workload benchmarked on AWS Graviton against a vanilla OpenCV 5 baseline.
- **Agentic Vision:** agent must use OpenCV results to choose a later analysis/action; human-in-the-loop for escalation.

## Initial architecture

1. Video/image input (recorded demo first; live stream optional).
2. OpenCV 5 perception pipeline.
3. Hazard candidates + evidence bundle.
4. Agent/orchestrator selects the next action:
   - accept as low-risk,
   - inspect temporal neighborhood,
   - crop/reprocess at higher detail,
   - invoke a second verification tool,
   - compare with baseline/history,
   - request human approval,
   - escalate a verified event.
5. Web dashboard shows detections, traces, actions, latency, and failure handling.
6. AWS deployment with a Graviton/COOL benchmark path.

## Competition dates

- Build phase: **2026-08-26 through 2026-10-26**
- Final deadline: **2026-10-26 23:59 Pacific Time**
- Judging: **2026-10-27 through 2026-11-09**
- Winners scheduled: **2026-11-10**

Always re-check the official Devpost page before irreversible submission decisions.

## Repository governance

This repository is the **source of truth** for research, decisions, code, experiments, benchmarks, AWS deployment, submission material, and progress.

Read in this order when resuming work:

1. `STATUS.md`
2. `ROADMAP.md`
3. `HANDOFF.md`
4. `docs/COMPETITION.md`
5. `docs/STRATEGY.md`

## Official links

- Competition: https://opencv26.devpost.com/
- Rules: https://opencv26.devpost.com/rules
- OpenCV: https://opencv.org/
- COOL: https://opencv.org/COOL
- AWS Marketplace COOL (Graviton4): https://aws.amazon.com/marketplace/pp/prodview-fdvbfiewzuehs
