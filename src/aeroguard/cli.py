from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from .agent import run_agent
from .fixture import generate_fixture
from .vision import attach_persistence, build_reference, detect_candidates


def analyze_video(input_path: str | Path, output_json: str | Path) -> dict:
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open input video: {input_path}")

    frames = []
    while len(frames) < 20:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    if len(frames) < 5:
        raise RuntimeError("input must contain at least 5 frames")
    reference = build_reference(frames)

    history: list[list] = []
    traces = []
    frame_index = len(frames)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        raw = detect_candidates(frame, reference, frame_index)
        current = [attach_persistence(c, history) for c in raw]
        for candidate in current:
            if candidate.persistence >= 2:
                traces.append(run_agent(candidate).to_dict())
        history.append(current)
        history = history[-6:]
        frame_index += 1
    cap.release()

    payload = {
        "schema": "aeroguard.trace.v1",
        "input": str(input_path),
        "opencv_version": cv2.__version__,
        "events": traces,
    }
    output_json = Path(output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(prog="aeroguard")
    sub = parser.add_subparsers(dest="command", required=True)

    p_fixture = sub.add_parser("generate-fixture")
    p_fixture.add_argument("--output", default="artifacts/fixture.mp4")

    p_analyze = sub.add_parser("analyze")
    p_analyze.add_argument("--input", required=True)
    p_analyze.add_argument("--output-json", default="artifacts/events.json")

    p_demo = sub.add_parser("demo")
    p_demo.add_argument("--video", default="artifacts/fixture.mp4")
    p_demo.add_argument("--output-json", default="artifacts/events.json")

    args = parser.parse_args()
    if args.command == "generate-fixture":
        path = generate_fixture(args.output)
        print(path)
    elif args.command == "analyze":
        payload = analyze_video(args.input, args.output_json)
        print(json.dumps({"events": len(payload["events"]), "output": args.output_json}))
    elif args.command == "demo":
        generate_fixture(args.video)
        payload = analyze_video(args.video, args.output_json)
        print(json.dumps({"events": len(payload["events"]), "output": args.output_json}))


if __name__ == "__main__":
    main()
