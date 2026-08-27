# AeroGuard Vision — Devpost Draft

Status: working draft for the OpenCV AI Competition 2026 submission. Update claims as benchmarks become available; do not publish unverified performance claims.

## About the project

# AeroGuard Vision

## Inspiration

Foreign Object Debris (FOD) on runways and taxiways can be small, visually ambiguous, and easy to miss, yet even a minor object can become a meaningful aviation-safety hazard. Many computer-vision systems stop after producing a detection. AeroGuard Vision explores a different question: **when visual evidence is uncertain, what should the system inspect next before asking a human to act?**

That question shaped the project into an agentic visual-inspection system rather than a one-shot detector.

## What it does

AeroGuard Vision analyzes airfield imagery and recorded inspection video for possible FOD hazards. OpenCV 5 produces visual evidence and candidate events. A bounded agent then uses that evidence to choose the next inspection action, such as:

- crop and re-process the suspicious region at higher detail;
- inspect nearby frames;
- verify persistence or motion over time;
- compare the candidate with scene history or a reference;
- close weak evidence;
- request human review for a verified risk.

The goal is to reduce unnecessary alerts while making every escalation explainable through visible evidence and a traceable sequence of actions.

AeroGuard Vision is a **decision-support and inspection prototype**, not an autonomous air-traffic-control or operational airport-safety system. Consequential escalation remains human-controlled.

## How we built it

The project is being built as a reproducible Python package around **OpenCV 5**. The first deterministic perception baseline follows a classical vision path:

`reference -> absdiff -> blur -> threshold -> morphology -> connected components -> temporal persistence`

The pipeline emits machine-readable event JSON, annotated video, and event-level evidence crops. A bounded multi-step agent consumes those outputs and can request additional visual analysis before deciding whether an event should be closed, re-inspected, or sent to human review.

To keep development testable from the beginning, we created deterministic synthetic video fixtures and GitHub Actions CI that verify the pinned OpenCV 5 environment, unit tests, and a repeatable end-to-end demo.

For real-data evaluation, we froze the official **FOD-A v2.1 Pascal VOC 300x300** dataset as the primary corpus and recorded its provenance and checksum. Our automated inspection verified **18,742 annotated images, 31,493 annotated objects, and 31 source labels**. The data also revealed a central technical challenge: **46.43% of annotated objects occupy less than 1,024 px²**, making small-object performance a first-class evaluation slice.

The dataset pipeline preserves source quirks instead of silently hiding them. For example, FOD-A contains fractional bounding-box coordinates after resizing and source-label variants such as case or naming differences. AeroGuard preserves the raw annotations and requires explicit, versioned transformations before benchmarking.

We also implemented deterministic class-aware IoU, precision, recall, and F1 evaluation primitives so model changes can be measured against frozen operating points rather than judged only by visual examples.

On AWS, the target architecture is designed around a reproducible OpenCV-heavy workload on **Graviton4**, with an application-relevant comparison between vanilla OpenCV 5 and **COOL**. The benchmark plan measures latency, throughput, CPU behavior where practical, and effective processing cost. CloudWatch-style observability and explicit failure traces are part of the deployment plan.

## The agentic loop

The core idea is that the agent must change what the vision system does next. A representative trace is:

`candidate -> inspect temporal window -> crop/reprocess -> verify persistence/motion -> human review or close event`

This makes the agent measurable. We can test whether it selected the correct next action, whether verification reduced false escalation, how it behaved when tools failed, and whether consequential decisions remained under human control.

## Challenges we faced

### Small FOD objects

Nearly half of the annotated FOD-A objects fall below our 1,024 px² small-object threshold. That makes resolution, preprocessing, detector choice, and evaluation by object size especially important.

### Dataset provenance and annotation quirks

Before training anything, we built acquisition, checksum, validation, and inspection tools. This exposed fractional boxes, taxonomy variants, and source-split details that need to be frozen before credible benchmark claims are possible.

### Making "agentic" behavior real

It would be easy to add an agent that only explains a detector result. We deliberately avoided that design. The agent must select a later visual action, receive new OpenCV evidence, and allow that evidence to change the event state.

### Safety and human control

Aviation is a high-consequence domain. The project therefore focuses on inspection support, evidence, uncertainty, and escalation discipline rather than autonomous operational decisions.

## What we learned

The most important lesson so far is that reliable visual AI starts before model training. Provenance, deterministic fixtures, dataset validation, explicit metrics, failure cases, and reproducible environments make later performance claims much more trustworthy.

We also learned that agentic vision is most useful when it can be evaluated as a task: **did the system gather the right additional evidence, and did that evidence improve the final action?** That framing is guiding both the architecture and the benchmark suite.

## What's next

The next milestones are:

1. freeze the exact FOD-A source train/validation split;
2. establish the first real-data detector baseline;
3. report precision, recall, F1, and dedicated small-object results;
4. feed real detector outputs into the agent verification loop and quantify false-alert reduction;
5. expand deterministic scenarios to include transient objects, weak evidence, false alarms, and tool failures;
6. run the Graviton4 + COOL application benchmark on AWS;
7. finish the evidence-first dashboard and final judge demo.

The final objective is simple to state and hard to fake: **AeroGuard Vision sees a possible airfield hazard, decides what visual evidence it still needs, re-checks the scene with OpenCV 5, and only escalates verified risk through a human-controlled AWS workflow.**

## Built with — suggested tags

- OpenCV 5
- Python
- AWS
- AWS Graviton4
- COOL
- Amazon EC2
- Amazon CloudWatch
- GitHub Actions
- NumPy
- pytest
- Pascal VOC

## Try it out

- Source code and reproducibility materials: https://github.com/pmartins87/OpenCV

## Media plan

Do not use filler screenshots. Add final media after the real detector/dashboard is available:

1. hero image: annotated runway/FOD event + AeroGuard branding;
2. agent trace: candidate -> re-inspect -> verified/human review;
3. dashboard screenshot;
4. real-data benchmark plot including the small-object slice;
5. COOL vs vanilla OpenCV 5 benchmark plot on Graviton4;
6. architecture diagram.

## Video plan

The final video should be recorded after the first real-data and AWS/COOL benchmarks are frozen. It should show the problem, one complete agentic trace, measurable evaluation, failure handling/human control, AWS deployment, and the COOL comparison. Avoid a temporary public demo video that could weaken the final project presentation.
