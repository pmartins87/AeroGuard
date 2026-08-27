#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import cv2

from aeroguard.agent import run_agent
from aeroguard.benchmarking import runtime_fingerprint, sha256_file, timing_summary
from aeroguard.scene_quality import measure_scene_quality
from aeroguard.vision import attach_persistence, build_reference, detect_candidates


def run_once(video_path: Path, reference_frames: int) -> dict:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {video_path}")

    seed_frames = []
    while len(seed_frames) < reference_frames:
        ok, frame = cap.read()
        if not ok:
            break
        seed_frames.append(frame)
    if len(seed_frames) < 5:
        cap.release()
        raise RuntimeError("benchmark input requires at least 5 reference frames")

    reference = build_reference(seed_frames)
    history: list[list] = []
    frame_index = len(seed_frames)
    processed = 0
    candidates = 0
    agent_events = 0
    stage_ms: list[float] = []

    t_run = time.perf_counter_ns()
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t0 = time.perf_counter_ns()
        measure_scene_quality(frame)
        raw = detect_candidates(frame, reference, frame_index)
        current = [attach_persistence(candidate, history) for candidate in raw]
        for candidate in current:
            if candidate.persistence >= 2:
                run_agent(candidate)
                agent_events += 1
        t1 = time.perf_counter_ns()
        stage_ms.append((t1 - t0) / 1_000_000.0)
        candidates += len(current)
        history.append(current)
        history = history[-6:]
        frame_index += 1
        processed += 1
    elapsed_ms = (time.perf_counter_ns() - t_run) / 1_000_000.0
    cap.release()

    if processed == 0:
        raise RuntimeError("benchmark input contains no measurable frames")
    return {
        "processed_frames": processed,
        "candidates": candidates,
        "agent_events": agent_events,
        "elapsed_ms": elapsed_ms,
        "ms_per_frame": elapsed_ms / processed,
        "frames_per_second": processed / (elapsed_ms / 1000.0),
        "opencv_stage_ms": timing_summary(stage_ms),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark the deterministic AeroGuard OpenCV core workload.")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-frames", type=int, default=20)
    parser.add_argument("--warmup-runs", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    if args.reference_frames < 5:
        raise ValueError("reference-frames must be >= 5")
    if args.warmup_runs < 0 or args.repeats <= 0:
        raise ValueError("warmup-runs must be >= 0 and repeats must be > 0")
    if not args.video.is_file():
        raise FileNotFoundError(args.video)

    for _ in range(args.warmup_runs):
        run_once(args.video, args.reference_frames)

    runs = [run_once(args.video, args.reference_frames) for _ in range(args.repeats)]
    frame_counts = {run["processed_frames"] for run in runs}
    if len(frame_counts) != 1:
        raise AssertionError(f"non-deterministic processed frame count: {sorted(frame_counts)}")

    ms_per_frame = [float(run["ms_per_frame"]) for run in runs]
    fps = [float(run["frames_per_second"]) for run in runs]
    payload = {
        "schema": "aeroguard.benchmark.opencv_core.v1",
        "workload": {
            "name": "aeroguard_classic_scene_quality_detection_agent",
            "description": "video decode -> reference -> scene quality -> OpenCV candidate extraction -> persistence -> bounded agent",
            "reference_frames": args.reference_frames,
            "warmup_runs": args.warmup_runs,
            "measured_repeats": args.repeats,
        },
        "input": {
            "path": str(args.video),
            "sha256": sha256_file(args.video),
            "processed_frames_per_repeat": runs[0]["processed_frames"],
        },
        "runtime": runtime_fingerprint(),
        "summary": {
            "ms_per_frame": timing_summary(ms_per_frame),
            "frames_per_second": timing_summary(fps),
            "candidate_counts": [run["candidates"] for run in runs],
            "agent_event_counts": [run["agent_events"] for run in runs],
        },
        "runs": runs,
        "claim_policy": "This harness is reproducibility infrastructure. Competition performance claims require the same frozen input and configuration on comparable Graviton4 vanilla OpenCV 5 and COOL runs; learned-detector mode will be added after the trained ONNX artifact exists.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "input_sha256": payload["input"]["sha256"],
        "p50_ms_per_frame": payload["summary"]["ms_per_frame"]["p50_ms"],
        "p95_ms_per_frame": payload["summary"]["ms_per_frame"]["p95_ms"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
