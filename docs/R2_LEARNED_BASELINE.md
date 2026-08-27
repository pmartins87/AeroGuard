# R2 learned-detector baseline — OpenCV DNN + YOLOX

Status: **implementation scaffold active; training waits only for source split audit**.

## Decision

The first learned FOD baseline will use the **YOLOX family**, with final competition inference executed through **OpenCV 5 DNN from an ONNX model**.

Initial experiment order:

1. **YOLOX-tiny** as the fast baseline, using a 640x640 experiment configuration to give the substantial small-object tail more input pixels.
2. **YOLOX-s** if the tiny baseline leaves meaningful accuracy on the table and training cost remains acceptable.
3. Larger architectures are not justified until measured error analysis shows model capacity is the limiting factor.

This is an experiment plan, not a performance claim.

## Why this baseline fits the competition

The official OpenCV 5 YOLO DNN tutorial explicitly uses YOLOX as its worked example and documents exporting a trained YOLOX model to ONNX and running the result through OpenCV DNN. It also stresses that preprocessing values must match training/export exactly.

Official OpenCV reference:
- https://docs.opencv.org/5.0/tutorials/dnn/dnn_yolo/dnn_yolo.html

Official YOLOX repository:
- https://github.com/Megvii-BaseDetection/YOLOX
- repository license: Apache-2.0
- official ONNX exporter: `tools/export_onnx.py`

Competition advantage: the learned detector does not hide OpenCV behind a training framework. The judge-facing runtime path is:

`image/video -> OpenCV preprocessing -> OpenCV DNN ONNX inference -> OpenCV/Numpy post-processing -> evidence -> agent-selected re-check -> decision`

The classical temporal/change-detection path remains a separate OpenCV tool used for verification and agentic re-inspection.

## Export contract

The trained checkpoint must be exported using the official YOLOX ONNX path with decoded inference boxes included (`--decode_in_inference`). The final model artifact must record:

- exact YOLOX source commit/tag;
- exact training configuration;
- checkpoint SHA-256;
- ONNX SHA-256;
- ONNX opset;
- class list/order and hash;
- input dimensions;
- export command;
- OpenCV version used for inference.

Pretrained-weight provenance must be recorded separately from the Apache-2.0 code license before any weights are redistributed in the final submission archive.

## Preprocessing contract

`src/aeroguard/detectors/yolox_opencv.py` implements the standard YOLOX-style preprocessing contract expected by the planned export:

- BGR input from OpenCV;
- preserve aspect ratio;
- top-left aligned resize;
- pad right/bottom with value 114;
- float32 tensor;
- no 1/255 normalization in this path;
- no RGB channel swap.

This contract must be cross-checked numerically against the exact training/export implementation before a model is accepted.

## Output/post-processing contract

For an ONNX graph exported with decoded boxes, AeroGuard expects rows shaped as:

`cx, cy, width, height, objectness, class_probability_0 ... class_probability_N`

Final confidence is:

`objectness * best_class_probability`

AeroGuard then:

1. applies a frozen confidence threshold;
2. performs class-aware NMS;
3. reverses the letterbox scale to source-image coordinates;
4. emits the common `evaluation.Box` representation;
5. evaluates against preserved Pascal VOC annotations.

## Data split gate

No YOLOX training is valid until FOD-A split provenance passes all of these:

- exact source `trainval.txt` count and SHA-256 frozen;
- exact source `test.txt` count and SHA-256 frozen;
- no duplicate IDs;
- no trainval/test overlap;
- union covers all expected annotation IDs;
- no unexplained extra IDs.

After that:

- source `test.txt` remains untouched as final held-out evaluation;
- AeroGuard derives a deterministic class-aware development train/validation partition only inside source `trainval.txt`;
- the derived ID files and hashes are frozen;
- model choice, hyperparameters, confidence threshold, and NMS threshold are selected only on development data.

## First benchmark outputs

The first real-data report must include at minimum:

- precision / recall / F1 at a frozen IoU and score threshold;
- AP/mAP when the evaluation implementation is frozen;
- result on the full held-out source test set;
- dedicated object-size slices, including area <1,024 px²;
- per-class results or at least class-frequency/error analysis;
- latency of OpenCV DNN inference on the development machine;
- examples of false positives and false negatives.

The baseline is useful even if its numbers are weak: the next architecture decision will be driven by measured error modes rather than preference.

## Acceptance gate for OpenCV inference

Before a trained model is called competition-ready:

1. PyTorch/YOLOX and OpenCV DNN run on the same frozen validation images.
2. Pre-NMS decoded outputs are compared within a documented numeric tolerance where practical.
3. Final detections are compared after the same confidence/NMS policy.
4. Any discrepancy is resolved or explicitly documented.
5. The OpenCV DNN path becomes the canonical competition runtime.

## Relation to Agentic Vision

The learned detector is the first perception tool, not the entire product. Detector uncertainty/evidence must feed the bounded agent, which can select later OpenCV tools such as temporal persistence, crop reprocessing, scene/reference comparison, or track verification. The later visual evidence must be able to change the event state before human escalation.
