# Dataset and Media Provenance Ledger

Rule: no external image/video/model asset enters a competition benchmark or public demo until its source, rights, intended use, and local checksum are recorded here.

## D1 - FOD-A (primary candidate)

- Name: Foreign Object Debris in Airports (FOD-A)
- Source repository: https://github.com/FOD-UNOmaha/FOD-data
- Paper: https://arxiv.org/abs/2110.03072
- Reported content: 31 FOD categories; >30,000 annotated instances; light and weather labels
- Formats advertised: original 400x400 and Pascal VOC 300x300 versions
- Repository license: MIT
- Planned use: primary training/validation/evaluation source for the FOD detector and robustness slices
- Status: **APPROVED FOR ACQUISITION; archive-level provenance still to be recorded after download**
- Required before redistribution: verify that the downloaded dataset archive is covered by the repository license/terms and record its checksum

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
