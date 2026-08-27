#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aeroguard.agent_scenarios import evaluate_agent_scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the frozen deterministic Agentic Vision scenario suite.")
    parser.add_argument("--output", type=Path, default=Path("artifacts/agent_scenarios.json"))
    args = parser.parse_args()

    result = evaluate_agent_scenarios()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("total", "passed", "failed", "task_success_rate")}, indent=2))
    if result["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
