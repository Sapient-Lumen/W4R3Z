#!/usr/bin/env python3
"""Shared deterministic numeric helpers for generated scientific benchmarks.

Keep only representation-neutral mechanics here. Scientific models, constants,
acceptance thresholds, and interpretation remain in their owning benchmark.
"""
from __future__ import annotations

import math
from typing import Any


def stable_number(value: float) -> float:
    """Return a compact deterministic float while retaining small errors."""
    return float(f"{value:.15g}")


def log_log_slope(rows: list[dict[str, Any]], x_key: str, y_key: str) -> float:
    """Return the ordinary-least-squares slope in natural-log coordinates."""
    points = [(math.log(float(row[x_key])), math.log(float(row[y_key]))) for row in rows]
    mean_x = sum(x for x, _ in points) / len(points)
    mean_y = sum(y for _, y in points) / len(points)
    denominator = sum((x - mean_x) ** 2 for x, _ in points)
    if denominator <= 0:
        raise ValueError("degenerate log-log fit")
    return sum((x - mean_x) * (y - mean_y) for x, y in points) / denominator


def linear_slope(rows: list[dict[str, Any]], x_key: str, y_key: str) -> float:
    """Return the ordinary-least-squares slope in the supplied coordinates."""
    points = [(float(row[x_key]), float(row[y_key])) for row in rows]
    mean_x = sum(x for x, _ in points) / len(points)
    mean_y = sum(y for _, y in points) / len(points)
    denominator = sum((x - mean_x) ** 2 for x, _ in points)
    if denominator <= 0:
        raise ValueError("degenerate linear fit")
    return sum((x - mean_x) * (y - mean_y) for x, y in points) / denominator
