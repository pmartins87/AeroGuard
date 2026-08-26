from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


@dataclass(frozen=True)
class Candidate:
    frame_index: int
    x: int
    y: int
    w: int
    h: int
    area: int
    contrast: float
    persistence: int = 1

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    def to_dict(self) -> dict:
        return asdict(self)


Decision = Literal["close", "reinspect", "human_review"]


@dataclass(frozen=True)
class AgentStep:
    step: int
    tool: str
    reason: str
    result: dict

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EventTrace:
    candidate: Candidate
    decision: Decision
    steps: tuple[AgentStep, ...]

    def to_dict(self) -> dict:
        return {
            "candidate": self.candidate.to_dict(),
            "decision": self.decision,
            "steps": [step.to_dict() for step in self.steps],
        }
