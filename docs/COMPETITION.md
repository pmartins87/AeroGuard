# Competition facts — OpenCV AI Competition 2026

Verified against the official Devpost competition page/rules on 2026-08-26.

## Core requirement

Every final entry must:

- use **OpenCV 5** for substantive image/video analysis; and
- run a **meaningful component on AWS**.

## Schedule

- Build phase: 2026-08-26 to 2026-10-26
- Final deadline: 2026-10-26 23:59 Pacific Time
- Judging: 2026-10-27 to 2026-11-09
- Winner announcement scheduled: 2026-11-10

## Prize structure

Overall:
- 1st: $5,000
- 2nd: $3,000
- 3rd: $2,000

Special:
- Best Use of COOL: $1,000
- Agentic Vision: $1,000

Per the rules, an entry may win no more than one Overall Award and may also receive one or both Special Awards.

## Overall judging rubric — 100 points

- Technical execution — 30%
- Innovation — 20%
- Real-world impact — 20%
- User experience — 10%
- Documentation and presentation — 10%
- Cloud delivery, reproducibility, and responsible operation — 10%

## Best Use of COOL rubric

- Verified COOL integration on AWS Graviton / documented Arm hybrid path — 30%
- Architecture and technical quality — 25%
- Measured performance, cost, reliability, or developer-productivity value — 20%
- Innovation — 15%
- Reproducibility and demonstration — 10%

Required evidence includes:
- COOL version;
- AWS instance/deployment configuration;
- reproducible inputs/baseline/method/results;
- evidence that COOL executes the claimed core workload.

## Agentic Vision rubric

- Substantive OpenCV 5 + agent integration — 30%
- Orchestration and appropriate autonomy — 25%
- Task effectiveness and evaluation — 20%
- Failure handling, observability, security, human control — 15%
- UX, documentation, demonstration — 10%

Eligibility principle: image/video results must influence a subsequent plan, tool call, action, or human-approval request. A chatbot that only explains a fixed vision result is insufficient.

Required evidence includes:
- agent workflow diagram;
- trace showing OpenCV output changes a later decision/tool call/action;
- task-success evaluation;
- failure handling, observability, and appropriate human control.

## Final submission package

- Technical report covering problem, users, architecture, OpenCV 5, AWS, evaluation, limitations, responsible use.
- Public or private judge-accessible code repository/archive.
- Pinned dependencies and clear build/deployment/test instructions.
- Architecture diagram.
- Working web endpoint or arranged live screen-share demo.
- Public/unlisted judge-accessible video, maximum 5 minutes.
- Evaluation evidence including failure cases/limitations.

## AWS Compute Grant

The official competition page advertises up to 50 AWS compute grants valued at $150. The proposal form requests a PDF and asks for:

- team name;
- problem and intended impact;
- planned OpenCV 5 analysis;
- planned AWS architecture/services;
- high-level architecture description/diagram;
- target users;
- evaluation method and judge demo;
- intent to pursue COOL, Agentic Vision, both, or neither;
- team bio/competition experience.

Proposal form observed active on 2026-08-26:
https://www.jotform.com/form/262145877145059

## Official sources

- https://opencv26.devpost.com/
- https://opencv26.devpost.com/rules
- https://opencv.org/opencv-ai-competition-2026
- https://opencv.org/COOL

## Freshness rule

The Devpost rules/page are authoritative for current prize amounts and judging requirements. Older announcement posts may contain superseded figures; re-check before submission.
