# Dataset and Media Provenance Ledger

Rule: no external image/video/model asset enters a competition benchmark or public demo until its source, rights, intended use, and local checksum are recorded here.

## D1 - FOD-A (primary dataset)

- Name: Foreign Object Debris in Airports (FOD-A)
- Source repository: https://github.com/FOD-UNOmaha/FOD-data
- Paper: https://arxiv.org/abs/2110.03072
- Repository description: dataset of FOD designed for computer-vision applications
- Repository license: **MIT**, copyright (c) 2020 FOD-UNOmaha
- Official source version: **2.1**
- Frozen format: **Pascal VOC, 300x300**
- Official Google Drive file ID: `1RdErcq8PGRXZUOGauaACkQG44T-QyZ4x`
- Source-reported archive size: 412 MB
- Verified downloaded archive size: **431,758,527 bytes**
- Verified archive SHA-256: **`408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`**
- Retained provenance artifacts: GitHub Actions `foda-probe` runs **32994883456** and **32995768875**
- Verified annotation XML files: **33,793**
- Verified images represented by non-empty annotations: **33,793**
- Verified annotated objects: **34,472**
- Verified source labels: **31**
- Verified image dimensions: **300x300**
- Physical source split files discovered: **`trainval.txt` + `test.txt`**
- Status: **ARCHIVE/CORPUS PROVENANCE VERIFIED; SPLIT MEMBERSHIP AUDIT RE-RUNNING WITH HASH/COVERAGE CHECKS**
- Correction audit: `docs/FODA_AUDIT_20260826.md`

### Verified class histogram

| Source label | Objects |
|---|---:|
| AdjustableClamp | 544 |
| AdjustableWrench | 472 |
| Battery | 1,059 |
| Bolt | 3,300 |
| BoltNutSet | 514 |
| BoltWasher | 1,017 |
| ClampPart | 917 |
| Cutter | 1,352 |
| FuelCap | 548 |
| Hammer | 760 |
| Hose | 294 |
| Label | 1,310 |
| LuggagePart | 738 |
| LuggageTag | 1,686 |
| MetalPart | 970 |
| MetalSheet | 394 |
| Nail | 1,193 |
| Nut | 1,303 |
| PaintChip | 968 |
| Pen | 483 |
| PlasticPart | 2,008 |
| Pliers | 2,884 |
| Rock | 662 |
| Screw | 157 |
| Screwdriver | 811 |
| SodaCan | 950 |
| Tape | 127 |
| Washer | 2,139 |
| Wire | 2,138 |
| Wood | 206 |
| Wrench | 2,568 |

### Object-size profile

Object bounding-box area in the 300x300 source images, recomputed from the retained manifest:

- minimum: ~21.41 px²
- p10: ~217.73 px²
- p25: ~842.08 px²
- median: ~3,250.88 px²
- p75: ~9,261.23 px²
- p90: ~19,337.69 px²
- p95: ~27,386.08 px²
- maximum: ~77,785.68 px²
- area < 1,024 px²: **9,852 / 34,472 = ~28.58%**
- area < 256 px²: **3,718 / 34,472 = ~10.79%**
- area < 64 px²: **776 / 34,472 = ~2.25%**

Competition implication: small-object performance remains a dedicated evaluation slice, but the corrected verified proportion under 1,024 px² is 28.58%.

### Source facts and quirks discovered during acquisition

1. FOD-A v2.1 Pascal VOC contains **fractional bounding-box coordinates** after resizing. AeroGuard preserves these coordinates as floats instead of silently truncating them.
2. The frozen archive exposes **31 clean source labels** listed above. Raw source names are preserved exactly; any future class grouping must be explicit, versioned, and benchmarked against the raw taxonomy.
3. The upstream README says a train/validation split is supplied, while the physical VOC package contains `VOC2007/ImageSets/Main/trainval.txt` and `test.txt`. AeroGuard preserves the physical source split files and keeps `test.txt` held out until the membership audit is frozen.
4. A prior intermediate ledger contained inconsistent provisional corpus counts and taxonomy. Those values are superseded by the retained artifact audit in `docs/FODA_AUDIT_20260826.md`.

### Planned benchmark split discipline

Preferred policy once the source split audit passes:

- keep source `test.txt` untouched as the final held-out evaluation set;
- derive a deterministic train/validation partition **only inside source `trainval.txt`** for model selection and threshold calibration;
- record the derived partition seed/algorithm and hashes;
- never tune on source `test.txt`;
- report final results on source `test.txt` and development results separately.

### Planned use

- primary training/validation/evaluation source for the FOD detector;
- small-object and class-frequency robustness slices;
- agent verification scenarios using detector outputs;
- no dataset archive is committed to this repository.

### Acquisition and inspection implementation

- automation: `.github/workflows/foda-probe.yml`
- local/archive inspector: `scripts/foda_inspect.py`
- parser/summary/split-audit code: `src/aeroguard/datasets/foda.py`
- detection metric primitives: `src/aeroguard/evaluation/detection.py`

### Rights note

The repository carries an MIT license and links the dataset archive from its README. Preserve the MIT notice and paper citation. If the downloaded archive contains narrower or additional terms, those terms take precedence and must be recorded before redistribution or public packaging.

## D2 - FOD-RUNWAY (optional external stress test)

- Source: https://universe.roboflow.com/necamettin-kk/fod-runway
- License shown by source: CC BY 4.0
- Planned use: optional secondary stress test only, to reduce dependence on one source/domain
- Status: **CANDIDATE**
- Required: record dataset version, class mapping, attribution text, download date, and checksum before use

## D3 - AeroGuard deterministic synthetic fixture

- Generator: `src/aeroguard/fixture.py`
- Seed: `20260826`
- Content: synthetic runway-like background and one persistent dark rectangular FOD surrogate
- Rights: project-generated
- Planned use: CI, smoke tests, deterministic agent traces, failure/recovery tests
- Status: **ACTIVE**
- Limitation: synthetic fixture is not evidence of real-world perception quality and must never be presented as such

## Context-only sources

### FAA FOD program
- Source: https://www.faa.gov/airports/airport_safety/fod
- Use: problem framing, terminology, safety context
- Training use: none

## Prohibited/unapproved by default

- Random YouTube/social-media airport footage
- Images discovered by search engines without explicit usage rights
- Dataset mirrors whose license differs from or obscures the original source
- Private airport/security footage
- Any data containing people or sensitive operational information unless a documented lawful/public use case is established

## Split discipline

For every learned detector benchmark:
- preserve source-provided train/validation/test semantics when available;
- never tune thresholds on the final held-out test set;
- record preprocessing and class remapping;
- report results separately by source when mixing datasets;
- keep synthetic fixtures separate from real-data performance metrics.
