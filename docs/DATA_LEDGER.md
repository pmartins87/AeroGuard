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
- Verified downloaded archive size: **432,133,110 bytes**
- Verified archive SHA-256: **`408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`**
- Provenance workflow run: **GitHub Actions `foda-probe` run 32994883456**
- Verified annotation XML files: **18,742**
- Verified images represented by non-empty annotations: **18,742**
- Verified annotated objects: **31,493**
- Verified source labels: **31**
- Verified image dimensions: **300x300**
- Status: **ARCHIVE PROVENANCE VERIFIED; SOURCE SPLIT DISCOVERY STILL OPEN**

### Verified class histogram

| Source label | Objects |
|---|---:|
| Bolt_Washer | 1,516 |
| ClampPart | 534 |
| FuelCap | 250 |
| MetalPart | 901 |
| Nail | 1,354 |
| Nut | 866 |
| PaintChip | 900 |
| Pen | 1,040 |
| PlasticPart | 632 |
| Screw | 1,549 |
| SodaCan | 1,677 |
| Washer | 1,367 |
| Wire | 796 |
| Wood | 838 |
| Wrench | 1,776 |
| aircraft_part | 1,228 |
| bearing | 1,290 |
| bit | 1,444 |
| bolt | 1,084 |
| bottlecap | 1,159 |
| candywrapper | 31 |
| cement | 311 |
| hose | 1,152 |
| metal_sheet | 314 |
| nut | 3,812 |
| paper | 681 |
| plastic | 256 |
| rock | 89 |
| soda_can | 1,507 |
| tape | 467 |
| wood | 512 |

### Object-size profile

Object bounding-box area in the 300x300 source images:

- minimum: ~13.74 px^2
- p10: ~131.12 px^2
- p25: ~401.42 px^2
- median: ~1,151.90 px^2
- p75: ~2,996.45 px^2
- p90: ~6,217.20 px^2
- p95: ~9,523.16 px^2
- maximum: ~61,075.34 px^2
- area < 1,024 px^2: **14,621 / 31,493 = ~46.43%**
- area < 256 px^2: **5,727 / 31,493 = ~18.19%**
- area < 64 px^2: **1,190 / 31,493 = ~3.78%**

Competition implication: small-object performance is a first-class evaluation slice. Nearly half of annotated FOD instances occupy less than 1,024 px^2.

### Source quirks discovered during acquisition

1. FOD-A v2.1 Pascal VOC contains **fractional bounding-box coordinates** after resizing. AeroGuard preserves these coordinates as floats instead of silently truncating them.
2. The source taxonomy contains labels that may be semantic/case variants, including `Nut`/`nut`, `Wood`/`wood`, and `SodaCan`/`soda_can`. Raw provenance preserves the original labels. Any canonical mapping used by a detector must be explicit, versioned, and evaluated against the raw taxonomy.
3. The upstream documentation says the Pascal VOC package contains train/validation splits, but the first exact-name probe did not find `train.txt`/`val.txt`. Split filenames/structure must be discovered and frozen before any learned benchmark is reported.

### Planned use

- primary training/validation/evaluation source for the FOD detector;
- small-object and class-frequency robustness slices;
- agent verification scenarios using detector outputs;
- no dataset archive is committed to this repository.

### Acquisition and inspection implementation

- automation: `.github/workflows/foda-probe.yml`
- local/archive inspector: `scripts/foda_inspect.py`
- parser/summary code: `src/aeroguard/datasets/foda.py`
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
- preserve source-provided train/validation/test splits when available;
- never tune thresholds on the final held-out test set;
- record preprocessing and class remapping;
- report results separately by source when mixing datasets;
- keep synthetic fixtures separate from real-data performance metrics.
