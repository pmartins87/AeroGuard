# Dataset and Media Provenance Ledger

Rule: no external image/video/model asset enters a competition benchmark or public demo until its source, rights, intended use, and local checksum are recorded here.

## D1 - FOD-A (primary candidate)

- Name: Foreign Object Debris in Airports (FOD-A)
- Source repository: https://github.com/FOD-UNOmaha/FOD-data
- Paper: https://arxiv.org/abs/2110.03072
- Repository description: dataset of FOD designed for computer-vision applications
- Reported content: 31 FOD categories; >30,000 annotated instances; light and weather labels
- Repository license: **MIT**, copyright (c) 2020 FOD-UNOmaha
- Current official dataset version advertised by the source README: **2.1**
- Frozen acquisition target: **FOD-A 2.1 Pascal VOC, 300x300, reported archive size 412 MB**
- Official Google Drive file ID for that archive: `1RdErcq8PGRXZUOGauaACkQG44T-QyZ4x`
- Source recommendation: use Pascal VOC for experimentation; original 400x400 format is recommended for dataset extension
- Source-provided split: **train + validation** in the Pascal VOC version
- Original-paper experiments: used Pascal VOC v2.1 at 300x300 with the provided splits
- Planned use: primary training/validation/evaluation source for the FOD detector and robustness slices
- Acquisition automation: `.github/workflows/foda-probe.yml`
- Local/archive inspector: `scripts/foda_inspect.py`
- Parser/summary code: `src/aeroguard/datasets/foda.py`
- Status: **ACQUISITION/PROVENANCE PROBE ACTIVE**
- Required before benchmark use: record downloaded archive byte size + SHA-256, extracted annotation/image counts, class histogram, supplied split counts, and preserve the source license/citation
- Rights note: the repository carries an MIT license and links the dataset archive from its README. We will preserve the MIT notice and citation. If the archive itself contains narrower terms, those terms take precedence and must be recorded before training/redistribution.

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
