# R2 scene-quality guardrails

Status: full-corpus OpenCV 5 profile complete; severe acquisition-failure gate integrated into the video pipeline.

## Why this exists

AeroGuard must not turn unusable visual evidence into a confident safety escalation. Before candidate extraction, each frame is measured for basic acquisition quality. If the frame is severely degraded, the system requests reacquisition, skips detection/escalation for that frame and breaks temporal persistence across the missing evidence.

This is deliberately a **narrow safety guardrail**. It is not a learned FOD-confidence score and it does not claim that every frame passing the gate is sufficient for reliable FOD detection.

## Real-data profile

Workflow `foda-scene-quality-profile`, run `33042687798`, profiled all **33,793 FOD-A images** using the pinned OpenCV 5 environment. The artifact digest is:

`sha256:4c22ac2829455dca48832fd5a2b4fb4d0c794947cda22c507654262d11b78120`

Observed corpus extrema / reference statistics:

| Metric | Observed minimum | Median / mean where useful | Observed maximum |
|---|---:|---:|---:|
| mean luma | 63.3054 | median 154.4400 | 239.5970 |
| p95-p05 dynamic range | 9.0 | median 46.0 | 199.0 |
| Laplacian variance | 10.4301 | median 113.9781 | 1853.2569 |
| dark-pixel fraction (<=31) | 0.0 or near-zero | mean 0.001823 | 0.166822 |
| highlight-clipped fraction (>=250) | 0.0 or near-zero | mean 0.001119 | 0.062233 |
| grayscale entropy (bits) | 3.62281 | median 5.77890 | 7.59227 |

The source categorization metadata uses light indices `0=Bright`, `1=Dim`, `2=Dark`. Even the `Dark` subset remains visually informative by these simple measurements; ordinary dark imagery must therefore not be treated as a failure by itself.

## Frozen v1 reacquisition policy

`SceneQualityPolicy` currently uses:

- `mean_luma >= 60.0`
- `dynamic_range >= 5.0`
- `laplacian_variance >= 9.0`
- `entropy_bits >= 2.5`
- `dark_fraction <= 0.18`
- `clipped_high_fraction <= 0.07`

The thresholds sit beyond the observed FOD-A support and intentionally target only severe failures. Dynamic-range and entropy thresholds are additionally loose enough that the deterministic synthetic fixture remains usable; the gate should not confuse a deliberately simple test scene with sensor failure.

The workflow gates the policy against the entire FOD-A corpus so a future threshold change cannot silently reject in-distribution benchmark images.

## Runtime behavior

For every frame after reference creation:

1. OpenCV measures luma distribution, dynamic range, Laplacian variance, dark/highlight clipping fractions and histogram entropy.
2. `assess_scene_quality` returns `usable` plus explicit reasons.
3. If unusable, the JSON trace records `action: reacquire` and the annotated output displays a reacquisition notice.
4. Candidate extraction and agent escalation are skipped for that frame.
5. Temporal history receives an empty observation so persistence cannot bridge across missing visual evidence.

A dedicated integration test uses an all-black video and requires all post-reference frames to be marked for reacquisition with zero FOD events.

## What this proves and what it does not

It proves that AeroGuard has a deterministic, inspectable failure mode for gross visual-acquisition failures and that the policy is compatible with the full current FOD-A corpus.

It does **not** prove robustness to every blur, rain, occlusion, glare, compression artifact or domain shift. Those claims require targeted validation data. Learned-detector confidence calibration will be performed separately on the frozen validation split after the first trained checkpoint exists.
