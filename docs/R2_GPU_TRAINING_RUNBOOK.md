# R2 GPU Training Runbook — FOD-A YOLOX-tiny

Status: frozen first learned-detector execution path.

## Purpose

This stage produces the first trainable FOD detector whose judge-facing inference path is OpenCV 5 DNN. Training uses the official YOLOX implementation at commit `6ddff4824372906469a7fae2dc3206c7aa4bbaee`; deployment/evaluation uses the exported decoded ONNX model through `OpenCVYOLOXDetector`.

The source FOD-A `test.txt` split remains held out during model selection. The training script accepts only the derived development `train` and `val` ID files.

## GPU requirement

The official YOLOX trainer is CUDA-oriented. GitHub-hosted Ubuntu runners are used for tests, provenance, export/inference contract checks, and reproducibility gates; the actual training stage must run on a CUDA GPU environment such as an approved cloud/GPU notebook or a future AWS GPU instance.

## One-command execution

From a Linux GPU environment with Python, Git, curl, and a CUDA-enabled PyTorch installation:

```bash
BATCH_SIZE=16 bash scripts/run_foda_yolox_gpu.sh \
  /path/to/foda/extracted \
  /path/to/dev_train.txt \
  /path/to/dev_val.txt \
  artifacts/foda_yolox_training
```

If the GPU cannot fit batch 16, lower `BATCH_SIZE`; record the final value in the produced environment evidence.

## Frozen baseline

- architecture: YOLOX-tiny;
- raw source classes: 31;
- input/test resolution: 640 x 640;
- development split only for model selection;
- initialization: official YOLOX-tiny pretrained checkpoint;
- 100 epochs, 5 warmup epochs, 10 no-augmentation epochs;
- mixup disabled;
- seed: `20260826`;
- ONNX export: decoded inference output;
- operating point: score 0.25, NMS 0.45, IoU 0.50;
- small-object slice: GT area < 1,024 px².

## Evidence emitted

The run records:

- AeroGuard commit and exact YOLOX commit;
- package/GPU environment and batch size;
- hashes of pretrained checkpoint, trained checkpoint, and ONNX model;
- deterministic prepared-data manifest and annotation hashes;
- OpenCV 5 DNN validation precision/recall/F1 at the frozen operating point;
- small-object recall;
- per-class recall;
- mean/p50/p95 OpenCV DNN CPU latency and derived throughput;
- high-score false positives and smallest false negatives for failure analysis;
- complete validation predictions JSON.

## Promotion gate

Do not promote YOLOX-s merely because it is larger. First inspect the tiny baseline for overall recall/precision, small-object recall, failure modes, and runtime. Escalate model size only when the evidence shows a meaningful quality gap worth the added latency/cost.

Do not evaluate the source `test.txt` repeatedly. It is reserved for the final frozen model-selection decision and final evidence package.
