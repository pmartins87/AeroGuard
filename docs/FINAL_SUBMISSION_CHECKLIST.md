# Final Submission Checklist — OpenCV AI Competition 2026

Source: Devpost finalization screen captured on 2026-08-26. Treat this file as the submission gate. Do not click **Submit project** until every required item below is either complete or deliberately satisfied by an allowed alternative.

## Devpost state

- Project: **AeroGuard Vision**
- Current Devpost completion: **2/5 steps done**
- Project Overview: complete
- Project Details: saved, but remains incomplete because the required final demo video is intentionally pending
- Additional Info: partially filled, but remains incomplete because the required final submission file is intentionally pending
- Final Submit: **DO NOT SUBMIT YET**

## Final Submission Package

- [ ] Technical report covering:
  - problem and users
  - architecture
  - OpenCV 5 implementation
  - AWS deployment
  - evaluation
  - limitations
  - responsible-use considerations
- [x] Judge-accessible code repository: `https://github.com/pmartins87/AeroGuard`
- [x] Pinned Python/OpenCV dependencies exist in `pyproject.toml`
- [x] Local build/test instructions drafted for Devpost
- [ ] AWS deployment instructions frozen and tested from a clean environment
- [ ] Architecture diagram showing OpenCV 5 + AWS + COOL/agent components
- [ ] Working web endpoint **or** arranged live screen-share demonstration
- [ ] Public/unlisted judge-accessible demo video, maximum 5 minutes, showing:
  - team/creator
  - application working
  - architecture
  - principal results
- [ ] Evaluation evidence including failure cases and limitations

## Best Use of COOL Award evidence

- [ ] Exact COOL version recorded
- [ ] Exact AWS instance/deployment configuration recorded
- [ ] Reproducible evaluation method frozen
- [ ] Frozen benchmark inputs and hashes recorded
- [ ] Vanilla OpenCV 5 baseline recorded
- [ ] COOL benchmark results recorded
- [ ] Evidence that COOL executes the claimed core AeroGuard workload
- [ ] Latency/throughput and relevant utilization/cost comparison summarized for judges

## Agentic Vision Award evidence

- [ ] Agent workflow diagram showing perception -> decision/orchestration -> action
- [ ] Trace/demo proving OpenCV 5 output changes a later decision, tool call, or action
- [ ] Agent task-success evaluation
- [ ] Failure-handling evaluation
- [ ] Observability/tracing evidence
- [ ] Human-control behavior demonstrated and documented

## Competitive evidence gates before submission

- [ ] FOD-A official train/validation split frozen
- [ ] First credible real-data detector baseline complete
- [ ] Precision/recall/F1 and bounding-box metrics complete
- [ ] Small-object performance slice complete
- [ ] False-alert reduction from agent verification measured
- [ ] Deterministic negative/transient/weak-evidence/tool-failure scenarios complete
- [ ] Final dashboard/judge-facing UI complete enough for the video/demo
- [ ] Final README and Devpost story updated with measured results only
- [ ] Media gallery contains judge-useful evidence, not filler screenshots
- [ ] Technical report PDF visually reviewed and uploaded
- [ ] Final video visually reviewed and linked
- [ ] Repository URL, testing instructions, special-award selectors, and endpoint/demo details rechecked
- [ ] Official Rules and Devpost Terms reviewed immediately before final submission

## Submission decision rule

Do not submit merely to make Devpost show 5/5. Submission occurs only when the package is judge-ready and the claims in Devpost, report, repository, benchmarks, screenshots, and video agree with one another.

Because Devpost states that the project may still be edited until the deadline after submission, an early administrative submission is technically possible, but the project strategy is to keep the draft state until the final evidence package is materially complete unless a competition-specific reason makes early submission advantageous.
