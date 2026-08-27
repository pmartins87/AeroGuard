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
OUTPUT_ROOT="${4:-$ROOT/artifacts/foda_yolox_smoke}"
YOLOX_DIR="$OUTPUT_ROOT/YOLOX"
PREPARED_DIR="$OUTPUT_ROOT/data"
WEIGHTS_DIR="$OUTPUT_ROOT/weights"
RESULTS_DIR="$OUTPUT_ROOT/results"
YOLOX_COMMIT="6ddff4824372906469a7fae2dc3206c7aa4bbaee"
DEVICE_COUNT="${DEVICE_COUNT:-2}"
BATCH_SIZE="${BATCH_SIZE:-32}"
LIMIT_TRAIN="${LIMIT_TRAIN:-512}"
LIMIT_VAL="${LIMIT_VAL:-128}"

mkdir -p "$OUTPUT_ROOT" "$WEIGHTS_DIR" "$RESULTS_DIR"

python - <<PY
import torch
required = int(${DEVICE_COUNT})
assert torch.cuda.is_available(), "CUDA unavailable"
assert torch.cuda.device_count() >= required, (torch.cuda.device_count(), required)
for i in range(required):
    x = torch.randn(512, 512, device=f"cuda:{i}")
    _ = x @ x
    torch.cuda.synchronize(i)
    print(f"GPU {i}: {torch.cuda.get_device_name(i)} COMPUTE PASS")
print("torch", torch.__version__, "cuda", torch.version.cuda)
PY

python -m pip install -q -e "$ROOT"
python -m pip install -q loguru tqdm thop ninja tabulate psutil tensorboard pycocotools onnx

if [[ ! -d "$YOLOX_DIR/.git" ]]; then
  git clone -q https://github.com/Megvii-BaseDetection/YOLOX.git "$YOLOX_DIR"
fi
git -C "$YOLOX_DIR" fetch -q --all --tags
git -C "$YOLOX_DIR" reset --hard -q
git -C "$YOLOX_DIR" clean -fdq
git -C "$YOLOX_DIR" checkout -q --detach "$YOLOX_COMMIT"
python -m pip install -q -e "$YOLOX_DIR" --no-deps --no-build-isolation

rm -rf "$PREPARED_DIR"
python "$ROOT/scripts/foda_prepare_yolox.py" \
  "$DATASET_ROOT" "$TRAIN_IDS" "$VAL_IDS" "$PREPARED_DIR" \
  --limit-train "$LIMIT_TRAIN" --limit-val "$LIMIT_VAL" --mode auto \
  > "$RESULTS_DIR/data_manifest_stdout.json"

PRETRAINED="$WEIGHTS_DIR/yolox_tiny_pretrained.pth"
if [[ ! -f "$PRETRAINED" ]]; then
  curl -L --fail --retry 3 -sS \
    https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_tiny.pth \
    -o "$PRETRAINED"
fi
sha256sum "$PRETRAINED" > "$RESULTS_DIR/pretrained.sha256"

{
  echo "aeroguard_commit=$(git -C "$ROOT" rev-parse HEAD)"
  echo "yolox_commit=$(git -C "$YOLOX_DIR" rev-parse HEAD)"
  echo "device_count=$DEVICE_COUNT"
  echo "batch_size=$BATCH_SIZE"
  echo "limit_train=$LIMIT_TRAIN"
  echo "limit_val=$LIMIT_VAL"
  python - <<'PY'
import cv2, numpy, torch
print("opencv=" + cv2.__version__)
print("numpy=" + numpy.__version__)
print("torch=" + torch.__version__)
print("cuda=" + str(torch.version.cuda))
for i in range(torch.cuda.device_count()):
    print(f"gpu_{i}=" + torch.cuda.get_device_name(i))
PY
} | tee "$RESULTS_DIR/environment.txt"

export AEROGUARD_COCO_DIR="$PREPARED_DIR"
cd "$ROOT"
rm -rf "$ROOT/YOLOX_outputs/foda_tiny_smoke"

python "$YOLOX_DIR/tools/train.py" \
  -f "$ROOT/training/yolox/foda_tiny.py" \
  -expn foda_tiny_smoke \
  -d "$DEVICE_COUNT" \
  -b "$BATCH_SIZE" \
  -c "$PRETRAINED" \
  max_epoch 1 warmup_epochs 0 no_aug_epochs 0 eval_interval 1 print_interval 1

CKPT="$ROOT/YOLOX_outputs/foda_tiny_smoke/latest_ckpt.pth"
if [[ ! -f "$CKPT" ]]; then
  CKPT="$ROOT/YOLOX_outputs/foda_tiny_smoke/best_ckpt.pth"
fi
if [[ ! -f "$CKPT" ]]; then
  echo "Smoke training did not produce a checkpoint" >&2
  exit 4
fi
cp "$CKPT" "$WEIGHTS_DIR/foda_tiny_smoke.pth"
sha256sum "$WEIGHTS_DIR/foda_tiny_smoke.pth" | tee "$RESULTS_DIR/trained_checkpoint.sha256"

sed -i 's/torch\.onnx\._export(/torch.onnx.export(/' "$YOLOX_DIR/tools/export_onnx.py"
ONNX="$WEIGHTS_DIR/foda_tiny_smoke_decoded.onnx"
python "$YOLOX_DIR/tools/export_onnx.py" \
  -f "$ROOT/training/yolox/foda_tiny.py" \
  -c "$WEIGHTS_DIR/foda_tiny_smoke.pth" \
  --output-name "$ONNX" \
  --decode_in_inference \
  --no-onnxsim
sha256sum "$ONNX" | tee "$RESULTS_DIR/onnx.sha256"

echo "AEROGUARD YOLOX TWO-GPU SMOKE: PASS"
echo "checkpoint=$WEIGHTS_DIR/foda_tiny_smoke.pth"
echo "onnx=$ONNX"
