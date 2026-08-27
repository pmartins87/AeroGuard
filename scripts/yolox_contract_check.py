#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import torch

from aeroguard.detectors.yolox_opencv import YOLOXConfig, make_yolox_blob


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _as_array(value) -> np.ndarray:
    if isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError(f"expected a single output tensor, got {len(value)}")
        value = value[0]
    if isinstance(value, torch.Tensor):
        value = value.detach().cpu().numpy()
    return np.asarray(value, dtype=np.float32)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare official YOLOX preprocessing/PyTorch output with AeroGuard OpenCV 5 DNN."
    )
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--onnx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--input-size", type=int, default=416)
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument("--rtol", type=float, default=1e-2)
    parser.add_argument("--atol", type=float, default=1e-2)
    parser.add_argument(
        "--yolox-commit",
        default="6ddff4824372906469a7fae2dc3206c7aa4bbaee",
    )
    args = parser.parse_args()

    from yolox.data.data_augment import preproc
    from yolox.exp import get_exp

    rng = np.random.default_rng(args.seed)
    image = rng.integers(0, 256, size=(300, 500, 3), dtype=np.uint8)

    config = YOLOXConfig(input_width=args.input_size, input_height=args.input_size)
    aeroguard_blob, _ = make_yolox_blob(image, config)
    official_chw, official_scale = preproc(image, (args.input_size, args.input_size))
    official_blob = official_chw[np.newaxis, ...]

    preprocess_diff = np.abs(aeroguard_blob - official_blob)
    preprocess_max_abs = float(preprocess_diff.max(initial=0.0))
    preprocess_mean_abs = float(preprocess_diff.mean())
    if aeroguard_blob.shape != official_blob.shape or preprocess_max_abs > 1e-6:
        raise AssertionError(
            f"YOLOX preprocessing mismatch: ours={aeroguard_blob.shape}, "
            f"official={official_blob.shape}, max_abs={preprocess_max_abs}"
        )

    exp = get_exp(None, "yolox-tiny")
    if tuple(exp.test_size) != (args.input_size, args.input_size):
        raise AssertionError(f"unexpected YOLOX tiny test_size: {exp.test_size}")
    model = exp.get_model()
    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    state_dict = checkpoint["model"] if isinstance(checkpoint, dict) and "model" in checkpoint else checkpoint
    model.load_state_dict(state_dict)
    model.eval()
    model.head.decode_in_inference = True

    with torch.no_grad():
        torch_output = _as_array(model(torch.from_numpy(aeroguard_blob)))

    net = cv2.dnn.readNetFromONNX(str(args.onnx))
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    net.setInput(aeroguard_blob)
    opencv_output = _as_array(net.forward())

    if torch_output.shape != opencv_output.shape:
        raise AssertionError(
            f"PyTorch/OpenCV output shape mismatch: {torch_output.shape} != {opencv_output.shape}"
        )

    output_diff = np.abs(torch_output - opencv_output)
    max_abs = float(output_diff.max(initial=0.0))
    mean_abs = float(output_diff.mean())
    allclose = bool(np.allclose(torch_output, opencv_output, rtol=args.rtol, atol=args.atol))

    manifest = {
        "schema": "aeroguard.yolox_opencv_contract.v1",
        "yolox_commit": args.yolox_commit,
        "seed": args.seed,
        "input_size": args.input_size,
        "official_preproc_scale": float(official_scale),
        "preprocessing": {
            "shape": list(aeroguard_blob.shape),
            "max_abs_diff": preprocess_max_abs,
            "mean_abs_diff": preprocess_mean_abs,
            "exact_within_1e-6": preprocess_max_abs <= 1e-6,
        },
        "inference": {
            "output_shape": list(torch_output.shape),
            "max_abs_diff": max_abs,
            "mean_abs_diff": mean_abs,
            "rtol": args.rtol,
            "atol": args.atol,
            "allclose": allclose,
        },
        "versions": {
            "opencv": cv2.__version__,
            "torch": torch.__version__,
            "numpy": np.__version__,
        },
        "artifacts": {
            "checkpoint": {"path": str(args.checkpoint), "sha256": _sha256(args.checkpoint)},
            "onnx": {"path": str(args.onnx), "sha256": _sha256(args.onnx)},
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))

    if not allclose:
        raise AssertionError(
            f"OpenCV DNN output diverged from PyTorch: max_abs={max_abs}, mean_abs={mean_abs}, "
            f"rtol={args.rtol}, atol={args.atol}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
