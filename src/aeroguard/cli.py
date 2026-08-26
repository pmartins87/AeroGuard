from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from .agent import run_agent
from .fixture import generate_fixture
from .vision import attach_persistence, build_reference, crop_with_margin, detect_candidates


def _decision_color(decision: str) -> tuple[int, int, int]:
    return {
        "close": (80, 180, 80),
        "reinspect": (0, 190, 255),
        "human_review": (50, 50, 230),
    }.get(decision, (220, 220, 220))


def _draw_event(frame, candidate, decision: str):
    annotated = frame.copy()
    color = _decision_color(decision)
    x, y, w, h = candidate.bbox
    cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
    label = f"{decision} p={candidate.persistence} c={candidate.contrast:.1f}"
    cv2.putText(
        annotated,
        label,
        (x, max(18, y - 7)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        color,
        1,
        cv2.LINE_AA,
    )
    return annotated


def analyze_video(
    input_path: str | Path,
    output_json: str | Path,
    *,
    output_video: str | Path | None = None,
    evidence_dir: str | Path | None = None,
) -> dict:
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open input video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = None
    if output_video is not None:
        output_video = Path(output_video)
        output_video.parent.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(
            str(output_video),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        if not writer.isOpened():
            raise RuntimeError(f"failed to open output video writer: {output_video}")

    evidence_path = Path(evidence_dir) if evidence_dir is not None else None
    if evidence_path is not None:
        evidence_path.mkdir(parents=True, exist_ok=True)

    frames = []
    while len(frames) < 20:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
        if writer is not None:
            writer.write(frame)
    if len(frames) < 5:
        cap.release()
        if writer is not None:
            writer.release()
        raise RuntimeError("input must contain at least 5 frames")
    reference = build_reference(frames)

    history: list[list] = []
    traces = []
    frame_index = len(frames)
    evidence_counter = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        raw = detect_candidates(frame, reference, frame_index)
        current = [attach_persistence(c, history) for c in raw]
        annotated = frame.copy()
        for candidate in current:
            if candidate.persistence < 2:
                continue
            trace = run_agent(candidate)
            trace_dict = trace.to_dict()
            traces.append(trace_dict)
            annotated = _draw_event(annotated, candidate, trace.decision)

            if evidence_path is not None and trace.decision in {"reinspect", "human_review"}:
                crop = crop_with_margin(frame, candidate)
                crop_name = f"event_{evidence_counter:04d}_f{frame_index}_{trace.decision}.jpg"
                cv2.imwrite(str(evidence_path / crop_name), crop)
                trace_dict["evidence_crop"] = crop_name
                evidence_counter += 1

        if writer is not None:
            writer.write(annotated)
        history.append(current)
        history = history[-6:]
        frame_index += 1

    cap.release()
    if writer is not None:
        writer.release()

    payload = {
        "schema": "aeroguard.trace.v1",
        "input": str(input_path),
        "opencv_version": cv2.__version__,
        "annotated_video": str(output_video) if output_video is not None else None,
        "evidence_dir": str(evidence_path) if evidence_path is not None else None,
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
    p_analyze.add_argument("--output-video", default="artifacts/annotated.mp4")
    p_analyze.add_argument("--evidence-dir", default="artifacts/evidence")

    p_demo = sub.add_parser("demo")
    p_demo.add_argument("--video", default="artifacts/fixture.mp4")
    p_demo.add_argument("--output-json", default="artifacts/events.json")
    p_demo.add_argument("--output-video", default="artifacts/annotated.mp4")
    p_demo.add_argument("--evidence-dir", default="artifacts/evidence")

    args = parser.parse_args()
    if args.command == "generate-fixture":
        path = generate_fixture(args.output)
        print(path)
    elif args.command == "analyze":
        payload = analyze_video(
            args.input,
            args.output_json,
            output_video=args.output_video,
            evidence_dir=args.evidence_dir,
        )
        print(json.dumps({"events": len(payload["events"]), "output": args.output_json}))
    elif args.command == "demo":
        generate_fixture(args.video)
        payload = analyze_video(
            args.video,
            args.output_json,
            output_video=args.output_video,
            evidence_dir=args.evidence_dir,
        )
        print(json.dumps({"events": len(payload["events"]), "output": args.output_json}))


if __name__ == "__main__":
    main()
