#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "Usage: $0 DATASET_ROOT TRAIN_IDS VAL_IDS [OUTPUT_ROOT]" >&2
  exit 2
fi

DATASET_ROOT="$(cd "$1" && pwd)"
TRAIN_IDS="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
VAL_IDS="$(cd "$(dirname "$3")" && pwd)/$(basename "$3")"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_ROOT="${4:-$ROOT/artifacts/foda_yolox_training}"
YOLOX_DIR="$OUTPUT_ROOT/YOLOX"
PREPARED_DIR="$OUTPUT_ROOT/data"
WEIGHTS_DIR="$OUTPUT_ROOT/weights"
RESULTS_DIR="$OUTPUT_ROOT/results"
YOLOX_COMMIT="6ddff4824372906469a7fae2dc3206c7aa4bbaee"
BATCH_SIZE="${BATCH_SIZE:-16}"

mkdir -p "$OUTPUT_ROOT" "$WEIGHTS_DIR" "$RESULTS_DIR"

python - <<'PY'
import torch
if not torch.cuda.is_available():
    raise SystemExit("CUDA GPU is required for the frozen YOLOX training stage")
print("CUDA device:", torch.cuda.get_device_name(0))
print("torch:", torch.__version__)
PY

python -m pip install -e "$ROOT"
python -m pip install loguru tqdm thop ninja tabulate psutil tensorboard pycocotools onnx

if [[ ! -d "$YOLOX_DIR/.git" ]]; then
  git clone https://github.com/Megvii-BaseDetection/YOLOX.git "$YOLOX_DIR"
fi
git -C "$YOLOX_DIR" fetch --all --tags
if [[ -n "$(git -C "$YOLOX_DIR" status --porcelain)" ]]; then
  echo "Refusing to overwrite a modified YOLOX checkout: $YOLOX_DIR" >&2
  exit 3
fi
git -C "$YOLOX_DIR" checkout --detach "$YOLOX_COMMIT"
python -m pip install -e "$YOLOX_DIR" --no-deps

rm -rf "$PREPARED_DIR"
python "$ROOT/scripts/foda_prepare_yolox.py" \
  "$DATASET_ROOT" "$TRAIN_IDS" "$VAL_IDS" "$PREPARED_DIR" --mode auto \
  | tee "$RESULTS_DIR/data_manifest_stdout.json"

PRETRAINED="$WEIGHTS_DIR/yolox_tiny_pretrained.pth"
if [[ ! -f "$PRETRAINED" ]]; then
  curl -L --fail --retry 3 \
    https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_tiny.pth \
    -o "$PRETRAINED"
fi
sha256sum "$PRETRAINED" | tee "$RESULTS_DIR/pretrained.sha256"

{
  echo "aeroguard_commit=$(git -C "$ROOT" rev-parse HEAD)"
  echo "yolox_commit=$(git -C "$YOLOX_DIR" rev-parse HEAD)"
  echo "batch_size=$BATCH_SIZE"
  python - <<'PY'
import cv2, numpy, torch
print("opencv=" + cv2.__version__)
print("numpy=" + numpy.__version__)
print("torch=" + torch.__version__)
print("cuda=" + str(torch.version.cuda))
print("gpu=" + torch.cuda.get_device_name(0))
PY
  nvidia-smi || true
} | tee "$RESULTS_DIR/environment.txt"

export AEROGUARD_COCO_DIR="$PREPARED_DIR"
cd "$ROOT"
python "$YOLOX_DIR/tools/train.py" \
  -f "$ROOT/training/yolox/foda_tiny.py" \
  -d 1 \
  -b "$BATCH_SIZE" \
  -c "$PRETRAINED"

BEST_CKPT="$ROOT/YOLOX_outputs/foda_tiny/best_ckpt.pth"
if [[ ! -f "$BEST_CKPT" ]]; then
  echo "Expected best checkpoint was not produced: $BEST_CKPT" >&2
  exit 4
fi
cp "$BEST_CKPT" "$WEIGHTS_DIR/foda_tiny_best.pth"
sha256sum "$WEIGHTS_DIR/foda_tiny_best.pth" | tee "$RESULTS_DIR/trained_checkpoint.sha256"

ONNX="$WEIGHTS_DIR/foda_tiny_decoded.onnx"
python "$YOLOX_DIR/tools/export_onnx.py" \
  -f "$ROOT/training/yolox/foda_tiny.py" \
  -c "$WEIGHTS_DIR/foda_tiny_best.pth" \
  --output-name "$ONNX" \
  --decode_in_inference \
  --no-onnxsim
sha256sum "$ONNX" | tee "$RESULTS_DIR/onnx.sha256"

python "$ROOT/scripts/foda_eval_yolox_opencv.py" \
  "$DATASET_ROOT" "$VAL_IDS" "$ONNX" "$RESULTS_DIR/validation_opencv.json" \
  --predictions-output "$RESULTS_DIR/validation_predictions.json" \
  --input-size 640 \
  --score-threshold 0.25 \
  --nms-threshold 0.45 \
  --iou-threshold 0.5

echo "Training/evaluation artifacts: $OUTPUT_ROOT"
