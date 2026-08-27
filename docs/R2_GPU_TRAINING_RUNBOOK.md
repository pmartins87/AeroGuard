# R2 GPU Training Runbook — FOD-A YOLOX-tiny

Status: frozen first learned-detector execution path.

## Purpose

This stage produces the first trainable FOD detector whose judge-facing inference path is OpenCV 5 DNN. Training uses the official YOLOX implementation at commit `6ddff4824372906469a7fae2dc3206c7aa4bbaee`; deployment/evaluation uses the exported decoded ONNX model through `OpenCVYOLOXDetector`.

The malformed mirror source `trainval.txt` / `test.txt` lists are **not** used for primary model selection or evaluation. The accepted data contract is the frozen **FOD-A sequence split v1** documented in `docs/R2_FODA_SEQUENCE_SPLIT_V1.md` and reproduced by `scripts/foda_make_sequence_split.py`.

Frozen partition hashes:

- train: `57a42dce2f8336bbf5eac31f3d7243bc6d126e2a4017f3883e52b12cdb37de91` — 23,502 IDs;
- validation: `a5f292105159e75f3693181e1b9ca878c535bdba41a0767b2f3786e059371b57` — 5,092 IDs;
- test: `ff86d8f896fb069c1d2c1e58997566c8a9472ec0107a1e4616101a3376f9f193` — 5,199 IDs.

Training and hyperparameter selection may use only train + validation. The group-disjoint test remains untouched until the checkpoint/threshold policy is frozen.

## GPU requirement

The official YOLOX trainer is CUDA-oriented. GitHub-hosted Ubuntu runners are used for tests, provenance, split generation, export/inference contract checks, and reproducibility gates; the actual training stage must run on a CUDA GPU environment such as an approved cloud/GPU notebook or a future AWS GPU instance.

## Reproduce the split before training

From the extracted FOD-A v2.1 corpus:

```bash
python scripts/foda_make_sequence_split.py /path/to/foda/extracted \
  --output-dir artifacts/foda_sequence_split \
  --seed 20260826 \
  --visual-threshold 0.10 \
  --iterations 50000
```

Verify that the emitted hashes match the frozen values above. If they do not, stop before training and investigate the dataset/acquisition environment.

## One-command training execution

From a Linux GPU environment with Python, Git, curl, and a CUDA-enabled PyTorch installation:

```bash
BATCH_SIZE=16 bash scripts/run_foda_yolox_gpu.sh \
  /path/to/foda/extracted \
  artifacts/foda_sequence_split/train.txt \
  artifacts/foda_sequence_split/val.txt \
  artifacts/foda_yolox_training
```

If the GPU cannot fit batch 16, lower `BATCH_SIZE`; record the final value in the produced environment evidence.

## Frozen baseline

- architecture: YOLOX-tiny;
- raw source classes: 31;
- input/test resolution: 640 x 640;
- sequence-group-disjoint train/validation split for model selection;
- initialization: official YOLOX-tiny pretrained checkpoint;
- 100 epochs, 5 warmup epochs, 10 no-augmentation epochs;
- mixup disabled;
- seed: `20260826`;
- ONNX export: decoded inference output;
- initial operating point: score 0.25, NMS 0.45, IoU 0.50;
- small-object slice: GT area < 1,024 px².

The initial score/NMS operating point is a baseline. Any calibration change must be selected on validation only and frozen before the first primary test evaluation.

## Evidence emitted

The run records:

- AeroGuard commit and exact YOLOX commit;
- package/GPU environment and batch size;
- hashes of pretrained checkpoint, trained checkpoint, and ONNX model;
- deterministic prepared-data manifest and annotation hashes;
- frozen sequence-split hashes;
- OpenCV 5 DNN validation precision/recall/F1 at the selected operating point;
- small-object recall;
- per-class recall;
- mean/p50/p95 OpenCV DNN CPU latency and derived throughput;
- high-score false positives and smallest false negatives for failure analysis;
- complete validation predictions JSON.

After checkpoint and thresholds are frozen, run the same evaluator exactly once on `artifacts/foda_sequence_split/test.txt` for the primary held-out report.

## Test-coverage limitation

The strict sequence-held-out test independently covers 25/31 classes. Six singleton-sequence classes are forced to training because placing their only sequence in test would make them unlearnable. This limitation must remain explicit in every primary result table.

Any optional all-class diagnostic that reuses frames from one of those singleton recordings must be labeled **secondary / within-sequence** and must never be mixed with the primary group-disjoint metric.

## Promotion gate

Do not promote YOLOX-s merely because it is larger. First inspect the tiny baseline for overall recall/precision, small-object recall, failure modes, and runtime. Escalate model size only when the evidence shows a meaningful quality gap worth the added latency/cost.

Do not repeatedly evaluate the frozen sequence test. It is reserved for the final tiny-baseline checkpoint/threshold decision and the competition evidence package.
