# FOD-A provenance audit — 2026-08-26

Purpose: freeze the facts directly observed from the downloadable GitHub Actions provenance artifact and supersede any earlier provisional/manual dataset counts.

## Immutable source target

- Dataset: FOD-A
- Upstream repository: `https://github.com/FOD-UNOmaha/FOD-data`
- Upstream advertised version/format: **v2.1 Pascal VOC, 300x300**
- Google Drive file ID: `1RdErcq8PGRXZUOGauaACkQG44T-QyZ4x`
- Downloaded archive SHA-256: **`408af3ac5be8af399367a7a846c6bd720727391c2d89de17985321c27468dd87`**
- Downloaded archive bytes: **431,758,527**

Upstream README independently confirms the same Google Drive file ID and identifies it as FOD-A v2.1 Pascal VOC at 300x300 resolution.

## Directly observed corpus facts

From the archived `foda_manifest.json` produced by the successful provenance workflow:

- Pascal VOC annotation XMLs: **33,793**
- images represented by non-empty annotations: **33,793**
- annotated objects: **34,472**
- source labels: **31**
- image dimensions observed: **300x300**

### Raw class histogram

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

### Bounding-box area profile

Computed from all 34,472 preserved fractional boxes:

- minimum: ~21.41 px²
- p10: ~217.73 px²
- p25: ~842.08 px²
- median: ~3,250.88 px²
- p75: ~9,261.23 px²
- p90: ~19,337.69 px²
- p95: ~27,386.08 px²
- maximum: ~77,785.68 px²
- area < 1,024 px²: **9,852 / 34,472 = 28.58%**
- area < 256 px²: **3,718 / 34,472 = 10.79%**
- area < 64 px²: **776 / 34,472 = 2.25%**

Small-object performance remains an important evaluation slice, but the verified fraction below 1,024 px² is **28.58%**, not the earlier provisional 46.43%.

## Source split discovery

The successful split-discovery probe found the source files:

- `VOC2007/ImageSets/Main/trainval.txt`
- `VOC2007/ImageSets/Main/test.txt`

It also found categorization metadata under `ImageSets/Main/CategorizationData/`.

The upstream README calls the Pascal VOC package a provided train/validation split, while the physical VOC package uses standard `trainval.txt` / `test.txt` filenames. AeroGuard will preserve the physical source files exactly and treat `test.txt` as held out until the new audit records member counts, hashes, overlap, and annotation coverage.

## Correction record

Earlier project documentation contained provisional counts of **18,742 images / 31,493 objects** and a different 31-label taxonomy. Those values are inconsistent with the downloadable provenance artifact for the frozen archive SHA above and are therefore **superseded**.

The corrected values in this document come from the retained GitHub Actions artifact generated from the frozen official archive. This correction is intentionally preserved rather than hidden: provenance mistakes discovered before training are a reason to strengthen the audit pipeline.

## Next gate

The dataset inspector has now been upgraded so the next `foda-probe` run will record:

- exact `trainval.txt` count + SHA-256;
- exact `test.txt` count + SHA-256;
- duplicate-ID guard;
- trainval/test overlap;
- union coverage against all annotation XML IDs;
- missing or extra split IDs.

No learned benchmark is considered valid until that split audit passes.
