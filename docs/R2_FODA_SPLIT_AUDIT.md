# R2 FOD-A split audit and leakage policy

Status: **source-provided split rejected provisionally; replacement leakage-aware split in design.**

Date: 2026-08-27

## Why this audit exists

FOD-A is video-derived data. The dataset tooling produces frames at 15 fps, which means neighboring images can be strongly correlated. A random frame-level split can therefore put near-duplicate temporal evidence in training and evaluation and produce optimistic metrics.

AeroGuard requires a split that is both internally consistent and defensible against temporal leakage before the first serious learned-detector training run is accepted.

## Canonical data provenance

Canonical source: `FOD-UNOmaha/FOD-data` / FOD-A v2.1 Pascal VOC.

Previously frozen official-archive SHA-256:

`408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`

The official Google Drive file is temporarily quota-limited. A public Kaggle mirror is being used only as an acquisition fallback. Its extracted corpus reproduced the previously frozen official-corpus audit exactly:

- 33,793 annotation/image IDs;
- 34,472 annotated objects;
- 31 labels with exact frozen per-class counts;
- all images 300x300;
- 9,852 objects below 1,024 px².

Mirror verification run: `33040936854` — PASS.

This structural match is strong evidence that the mirror contains the same v2.1 corpus, but it is not a byte-for-byte proof of the original archive container. Official source/archive provenance remains canonical.

## Provided split audit

The mirror contains `VOC2007/ImageSets/Main/trainval.txt` and `test.txt`. Their raw contents fail the clean-holdout gate.

### trainval.txt

- raw entries: **25,345**;
- unique IDs: **25,298**;
- duplicate occurrences beyond first occurrence: **47**;
- raw SHA-256: `d2ff26ab657dad9ca523ff8f52030cda8fc20509c9a8c5fd0d62ef7d99980dc0`;
- unique-only normalized SHA-256: `c2192d87524db539b815df3c289126bd9e6996417db11a95888417f498884f6a`.

### test.txt

- raw entries: **8,448**;
- unique IDs: **8,429**;
- duplicate occurrences beyond first occurrence: **19**;
- raw SHA-256: `f5a24f43df692b07985200d8c8f3937057f9bb6c2c0bfc70a5e9b675d8e0ef1f`;
- unique-only normalized SHA-256: `7272daaa19620187df968a75b707bc134739671967a86e6902483fd2bde8e3f8`.

### Cross-split defects

Four IDs occur in both lists:

- `014567` — 31 trainval entries and 9 test entries;
- `015731` — 4 trainval and 2 test entries;
- `016653` — 6 trainval and 5 test entries;
- `016763` — 10 trainval and 7 test entries.

The unique trainval/test union contains **33,723** IDs, while the corpus has **33,793** annotation IDs. Exactly **70** annotated images are uncovered. The missing IDs are the contiguous tail `033723` through `033792`. There are no split IDs without annotations.

The raw list lengths sum to 33,793, but repeated/cross-listed IDs consume the slots that otherwise would have represented the 70 uncovered images. This is a strong indication of malformed split lists in the mirror rather than a parser/counting artifact.

## Gate decision

`source_split_usable_as_clean_holdout = false`

AeroGuard will **not** use the mirror's raw `trainval.txt` and `test.txt` as the competition evaluation split.

The defect result remains marked **provisional** until the split files can be compared against a fresh extraction of the official byte-source archive after the Google Drive quota clears. If the official archive contains different clean split files, those official files supersede the mirror split. If it contains the same defect, this audit becomes final source-split evidence.

## Temporal leakage evidence

The categorization metadata contains 33,793 rows and unique flattened filenames. Weather/light coverage is:

- weather 0 / light 0: 16,942 images;
- weather 0 / light 1: 5,248;
- weather 0 / light 2: 4,387;
- weather 1 / light 1: 7,216.

The annotation IDs form only 55 long contiguous same-label runs, with median length 522 frames and maximum 1,958. The categorization CSV row order also contains long sequences of numerically consecutive frame IDs. Together with the 15 fps dataset-generation process, this makes ordinary random frame splitting inappropriate for judge-facing accuracy claims.

## Replacement-split requirements

The replacement split must:

1. assign inferred temporal/recording groups atomically to one partition;
2. have zero group overlap across train, validation, and final test;
3. keep all 33,793 unique annotation IDs accounted for exactly once unless an explicit embargo set is used and hashed;
4. preserve useful class and weather/light coverage as far as the group structure permits;
5. use a deterministic seed and emit exact file hashes;
6. report group counts, image counts, class distributions, environment distributions, and small-object distributions per partition;
7. keep final test untouched during model/hyperparameter selection;
8. preserve the malformed source split separately for provenance and paper-comparability analysis;
9. document any unavoidable class-coverage limitation caused by sequence grouping;
10. be reproducible from dataset metadata/images by one command.

## Active experiment

Workflow `foda-sequence-probe` run `33041114427` is measuring candidate temporal groups and adjacent-frame visual transitions. The split policy will be frozen only after this probe establishes defensible sequence-boundary evidence.

No first-prize-quality detector training should be promoted before this gate closes.
