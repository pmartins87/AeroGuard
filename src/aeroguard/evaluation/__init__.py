"""Competition-facing evaluation primitives."""

from .detection import Box, DetectionMetrics, evaluate_boxes, intersection_over_union

__all__ = ["Box", "DetectionMetrics", "evaluate_boxes", "intersection_over_union"]
