"""Deterministic parameter sweeps for risky DHT guesses.

The live network will be noisy.  Before SAM/I2P transport exists, this module
keeps the chaos boring and repeatable: vary captured-family fraction, disjoint
path count, and family caps, then report whether a lookup front is likely to be
captured by the first fast window.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product


class SweepDecisionKind(str, Enum):
    ACCEPT_PRESSURE = "accept_pressure"
    CONTINUE_FAST_WINDOW_CAPTURED = "continue_fast_window_captured"
    CONTINUE_NOT_ENOUGH_FAMILIES = "continue_not_enough_families"


@dataclass(frozen=True)
class SweepScenario:
    captured_families: int
    honest_families: int
    paths: int
    max_per_family: int
    fast_window_size: int

    def validate(self) -> None:
        if self.captured_families < 0 or self.honest_families < 0:
            raise ValueError("family counts must be non-negative")
        if self.captured_families + self.honest_families <= 0:
            raise ValueError("at least one family is required")
        if self.paths <= 0 or self.max_per_family <= 0 or self.fast_window_size <= 0:
            raise ValueError("paths, max_per_family, and fast_window_size must be positive")


@dataclass(frozen=True)
class SweepPoint:
    scenario: SweepScenario
    selected_families: tuple[str, ...]
    fast_window_families: tuple[str, ...]
    captured_fast_fraction: float
    decision: SweepDecisionKind

    @property
    def selected_family_count(self) -> int:
        return len(set(self.selected_families))


@dataclass(frozen=True)
class SweepReport:
    points: tuple[SweepPoint, ...]

    @property
    def captured_points(self) -> tuple[SweepPoint, ...]:
        return tuple(point for point in self.points if point.decision is SweepDecisionKind.CONTINUE_FAST_WINDOW_CAPTURED)

    @property
    def worst_point(self) -> SweepPoint:
        return max(self.points, key=lambda point: (point.captured_fast_fraction, -point.selected_family_count))

    def by_captured_families(self) -> dict[int, list[SweepPoint]]:
        out: dict[int, list[SweepPoint]] = {}
        for point in self.points:
            out.setdefault(point.scenario.captured_families, []).append(point)
        return out


def evaluate_sweep_scenario(scenario: SweepScenario, *, min_families: int = 3, max_fast_captured_fraction: float = 0.67) -> SweepPoint:
    scenario.validate()
    captured_families = [f"captured-{idx}" for idx in range(scenario.captured_families)]
    honest_families = [f"honest-{idx}" for idx in range(scenario.honest_families)]
    families = captured_families + honest_families
    # Captured families are placed first and repeated up to the family cap to
    # model the scary fast-window: the adversary is not everywhere, but when a
    # captured family is allowed multiple slots it can fill the first replies.
    selection_order = (
        [family for family in captured_families for _ in range(scenario.max_per_family)]
        + [family for family in honest_families for _ in range(scenario.max_per_family)]
    )
    selected: list[str] = []
    counts: dict[str, int] = {}
    for family in selection_order:
        if counts.get(family, 0) >= scenario.max_per_family:
            continue
        counts[family] = counts.get(family, 0) + 1
        selected.append(family)
        if len(selected) >= scenario.paths:
            break

    fast = tuple(selected[: scenario.fast_window_size])
    captured_fast = sum(1 for family in fast if family.startswith("captured-"))
    captured_fraction = captured_fast / len(fast) if fast else 0.0
    if captured_fraction > max_fast_captured_fraction:
        decision = SweepDecisionKind.CONTINUE_FAST_WINDOW_CAPTURED
    elif len(set(selected)) < min_families:
        decision = SweepDecisionKind.CONTINUE_NOT_ENOUGH_FAMILIES
    else:
        decision = SweepDecisionKind.ACCEPT_PRESSURE
    return SweepPoint(scenario, tuple(selected), fast, captured_fraction, decision)


def run_capture_sweep(
    *,
    captured_family_options: tuple[int, ...] = (0, 1, 2, 3),
    honest_family_options: tuple[int, ...] = (1, 2, 4),
    path_options: tuple[int, ...] = (3, 5, 7),
    family_cap_options: tuple[int, ...] = (1, 2),
    fast_window_size: int = 3,
) -> SweepReport:
    points = [
        evaluate_sweep_scenario(SweepScenario(captured, honest, paths, cap, min(fast_window_size, paths)))
        for captured, honest, paths, cap in product(captured_family_options, honest_family_options, path_options, family_cap_options)
        if captured + honest > 0
    ]
    return SweepReport(tuple(points))
