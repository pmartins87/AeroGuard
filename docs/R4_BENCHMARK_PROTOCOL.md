# R4 benchmark protocol - vanilla OpenCV 5 vs COOL

Status: harness v1 implemented before AWS/COOL access. No competition speedup claim is made from the development runner.

## Purpose

The Best Use of COOL submission must show value on an AeroGuard workload, not only an isolated primitive. `scripts/benchmark_opencv_core.py` therefore records an application-level OpenCV workload with a frozen input hash, warmup policy, repeated runs and machine/build fingerprints.

Current v1 workload:

`video decode -> background reference -> scene-quality metrics -> OpenCV candidate extraction -> temporal persistence -> bounded agent`

This is valid reproducibility infrastructure now and an application-relevant classical path/fallback. Once the trained FOD YOLOX ONNX artifact exists, the harness will gain a learned-detector mode so the final COOL comparison includes the production OpenCV DNN path as well.

## Evidence contract

Every benchmark JSON records:

- schema and workload name;
- input SHA-256;
- reference-frame count;
- warmup count and measured repeat count;
- Python/OpenCV/platform/machine fingerprint;
- SHA-256 of `cv2.getBuildInformation()`;
- processed frame count;
- candidate and agent-event counts per repeat;
- mean/p50/p95/min/max/stdev milliseconds per frame;
- derived frames per second;
- per-run evidence.

## Final Graviton4/COOL comparison gate

A performance claim is eligible only when both sides use:

1. the same frozen AeroGuard commit;
2. the same frozen input manifest/video hashes;
3. the same model artifact and thresholds when learned mode is enabled;
4. comparable AWS Graviton4 instance class/configuration;
5. the same warmup and repeat policy;
6. an explicitly captured vanilla OpenCV 5 build and COOL build/version;
7. medians/distributions rather than a selected best run;
8. CPU utilization and estimated cost per processed video minute when practical.

Cloud variance must be acknowledged. If observed differences are small relative to run-to-run dispersion, the submission will report that instead of claiming a speedup.

## Current development use

The deterministic fixture can be used as a CI smoke benchmark. Its numbers prove that the harness is executable and stable; they are **not** evidence for the COOL award because GitHub-hosted x86 hardware is neither Graviton4 nor COOL.

Example:

```bash
python -m aeroguard.cli generate-fixture --output artifacts/fixture.mp4
python scripts/benchmark_opencv_core.py \
  --video artifacts/fixture.mp4 \
  --output artifacts/benchmark.json \
  --warmup-runs 1 \
  --repeats 5
```
