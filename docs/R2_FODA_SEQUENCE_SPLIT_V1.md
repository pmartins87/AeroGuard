# R2 FOD-A leakage-aware sequence split v1

Status: **FROZEN FOR FIRST LEARNED BASELINE**

Date: 2026-08-27
Canonical build run: **GitHub Actions `33041421174` — PASS**
Artifact: `foda-sequence-split` (artifact id `9634020305`)
Artifact digest: `sha256:1b68920514d283079a471296fd75fa89494f593d1fdc15b232ff059586ef44a9`

## Decision

The malformed FOD-A mirror `trainval.txt` / `test.txt` lists are not used for AeroGuard's primary competition evaluation. The first learned baseline uses a deterministic **group-disjoint sequence-aware split** derived from the complete 33,793-image v2.1 corpus.

This split is designed for honest model evaluation on video-derived data. It favors temporal separation and reproducibility over artificially convenient class coverage.

## Why a replacement split was necessary

The structurally equivalent public mirror's source lists contain duplicate IDs, four cross-split IDs, and leave 70 annotated images uncovered. Separately, FOD-A was generated from video frames at 15 fps, so ordinary random frame splitting risks placing near-adjacent temporal evidence on both sides of the evaluation boundary.

See `docs/R2_FODA_SPLIT_AUDIT.md` for the complete source-split defect record.

## Grouping policy

Images are assigned to atomic sequence groups before any train/validation/test allocation. A new group begins when any of these conditions occurs in the categorization CSV row order:

- numeric image ID is not consecutive;
- weather category changes;
- light category changes;
- annotation label signature changes;
- an extreme visual discontinuity occurs between otherwise metadata-contiguous frames.

Visual discontinuity metric:

`mean(abs(gray48(frame_t) - gray48(frame_t+1))) / 255`

Frozen threshold: **0.10**.

The sequence probe run `33041114427` measured 33,671 metadata-contiguous transitions:

- median: `0.00785165`;
- 95th percentile: `0.03456308`;
- 99th percentile: `0.04964512`;
- 99.9th percentile: `0.07807046`;
- maximum: `0.16325742`;
- only **7 / 33,671** transitions were >= 0.10.

Thus 0.10 is intentionally conservative: it introduces a visual boundary only for an extreme tail event rather than fragmenting normal video motion.

Seven extreme visual boundaries were added. Together with metadata boundaries, the final split contains **129 atomic groups**.

## Assignment policy

Atomic groups are assigned as whole units. No group may cross partitions.

Target image proportions:

- train: 70%;
- validation: 15%;
- test: 15%.

Deterministic seed: **20260826**.

The optimizer balances total image volume, class coverage, and weather/light coverage while enforcing these safety rules:

1. every declared class must appear in training;
2. a class represented by only one atomic sequence group is forced to training;
3. when a class has at least three groups, independent validation and test coverage are strongly preferred;
4. when a class has two groups, training + independent test coverage is strongly preferred;
5. final test is reserved for final model/threshold evaluation and not used for hyperparameter selection.

Implementation: `src/aeroguard/datasets/group_split.py` and `scripts/foda_make_sequence_split.py`.

## Frozen partition sizes

| Partition | Groups | Images | Objects | Small objects <1,024 px² | Image fraction |
|---|---:|---:|---:|---:|---:|
| train | 81 | 23,502 | 24,181 | 6,818 | 69.55% |
| validation | 23 | 5,092 | 5,092 | 1,420 | 15.07% |
| test | 25 | 5,199 | 5,199 | 1,614 | 15.38% |
| **total** | **129** | **33,793** | **34,472** | **9,852** | **100%** |

Coverage gates:

- annotation IDs: **33,793**;
- covered exactly once: **33,793**;
- train/validation image overlap: **0**;
- train/test image overlap: **0**;
- validation/test image overlap: **0**;
- group overlap across partitions: **0 by construction**;
- all 31 labels represented in train: **PASS**.

## Frozen split hashes

- `train.txt`: **23,502 IDs** — SHA-256 `57a42dce2f8336bbf5eac31f3d7243bc6d126e2a4017f3883e52b12cdb37de91`
- `val.txt`: **5,092 IDs** — SHA-256 `a5f292105159e75f3693181e1b9ca878c535bdba41a0767b2f3786e059371b57`
- `test.txt`: **5,199 IDs** — SHA-256 `ff86d8f896fb069c1d2c1e58997566c8a9472ec0107a1e4616101a3376f9f193`
- `groups.json`: SHA-256 recorded in the split manifest produced by run `33041421174`.

## Environment coverage

Weather/light codes are preserved in all three partitions:

| Weather\|Light | Train | Validation | Test |
|---|---:|---:|---:|
| `0|0` | 12,820 | 1,560 | 2,562 |
| `0|1` | 2,945 | 1,388 | 915 |
| `0|2` | 2,626 | 1,031 | 730 |
| `1|1` | 5,111 | 1,113 | 992 |

## Independent class coverage and dataset limitation

Strict sequence grouping exposes a real limitation of FOD-A: several classes are represented by only one inferred sequence group. Those classes cannot simultaneously appear in training and an independent sequence-held-out test without violating the no-group-leakage policy.

Classes absent from the strict **test** because only one independent atomic group is available and therefore must remain in train:

- `AdjustableClamp`;
- `AdjustableWrench`;
- `BoltNutSet`;
- `Screw`;
- `Tape`;
- `Wood`.

The strict test therefore independently covers **25 of 31 classes**.

Validation lacks the same six singleton-group classes plus `Hose`, `MetalSheet`, and `Nail`, which have only two atomic groups and are reserved for train + independent test. Validation independently covers **22 of 31 classes**.

This limitation must be stated in final evaluation rather than hidden. Primary judge-facing claims will use the group-disjoint test. Any additional all-class diagnostic that reuses a recording must be explicitly labeled as a secondary within-sequence diagnostic and must never be mixed with the primary leakage-aware score.

## Extreme visual boundaries selected by threshold 0.10

The seven additional boundaries occur at:

- Bolt `012168 -> 012169`, MAD48 `0.12820`;
- Bolt `012685 -> 012686`, `0.11513`;
- Nut `012808 -> 012809`, `0.10641`;
- MetalSheet `013964 -> 013965`, `0.16326`;
- Hose `014248 -> 014249`, `0.11243`;
- PaintChip `024068 -> 024069`, `0.12666`;
- PlasticPart `026548 -> 026549`, `0.10972`.

## Reproducibility

Canonical command:

```bash
python scripts/foda_make_sequence_split.py /path/to/FOD-A-v2.1-extracted \
  --output-dir artifacts/foda_sequence_split \
  --seed 20260826 \
  --visual-threshold 0.10 \
  --iterations 50000
```

The CI gate verifies:

- exact corpus image count;
- all IDs covered exactly once;
- zero partition overlap;
- total object count 34,472;
- all labels present in train;
- deterministic optimizer tests;
- frozen per-file hashes emitted in `manifest.json`.

## Provenance caveat

This split was generated from the Kaggle acquisition fallback whose extracted corpus matches the previously audited official v2.1 corpus exactly on counts, dimensions, class distribution, and small-object statistics. The current official Google Drive quota still prevents fresh byte-source reconciliation of its split files.

The official repository/archive remains canonical provenance. Once the quota clears, AeroGuard will repeat the source split audit. The replacement sequence split is based on the complete corpus rather than the malformed source lists, so its evaluation logic does not depend on those lists.

## R2 gate consequence

The data/evaluation-split blocker is closed for the **first learned baseline**. The next critical gate is now:

**train YOLOX-tiny on `train.txt` -> select threshold/checkpoint on `val.txt` -> export ONNX -> verify OpenCV 5 DNN contract -> evaluate exactly once on `test.txt`.**
