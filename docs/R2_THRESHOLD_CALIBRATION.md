# R2 detector threshold calibration protocol

Status: calibration code and selection rule implemented; real operating point remains pending the first trained validation predictions.

## Purpose

The initial YOLOX/OpenCV path uses score `0.25` as a reproducible engineering baseline. The final detector threshold must be selected from the frozen **validation** partition rather than tuned against the held-out test set.

## Frozen procedure

1. Export validation predictions once per candidate checkpoint before any held-out test evaluation.
2. Evaluate a predeclared score-threshold grid with class-aware IoU `0.50` matching.
3. Compute precision, recall, F1 and recall-weighted F-beta for every threshold.
4. Use `beta=2` for the primary candidate-generation operating point because missed FOD evidence is more costly at this stage and later temporal/agent verification is explicitly designed to suppress false alerts.
5. Select the maximum F2 point. Ties are resolved in this fixed order: higher recall, higher precision, then higher score threshold to reduce review burden when measured detection quality is otherwise identical.
6. Freeze the selected threshold and prediction/model hashes **before** the primary held-out test evaluation.
7. Report the conventional F1/precision/recall values alongside F2 so the recall preference is transparent rather than hidden inside one metric.

The implementation lives in `src/aeroguard/evaluation/calibration.py` and is covered by deterministic tests.

## Anti-overfitting rule

The strict test partition is not a threshold-selection resource. If the first test evaluation reveals a weakness, any subsequent model change creates a new model version and must return to validation. Repeated test-driven threshold changes are prohibited for the primary competition claim.

## Relationship to agent verification

The detector threshold decides what becomes a **candidate**, not what becomes an operational alert. The agentic layer still requires temporal/visual verification and routes consequential cases to human review. This separation lets the detector remain recall-oriented without pretending every low-threshold candidate is a confirmed hazard.

## Pending evidence

After GPU training becomes available, record:

- model/checkpoint/ONNX hashes;
- exact validation prediction hash;
- threshold grid and all points;
- selected threshold and tie-break evidence;
- small-object and per-class behavior at the selected point;
- alert-candidate volume per image/video minute;
- one frozen primary test evaluation after selection.
