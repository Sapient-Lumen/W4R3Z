"""Larger deterministic adversarial sweeps for early DHT guesses.

Live I2P transport will be noisy.  rev0014 adds a grid that stays boring and
reproducible: vary captured-family share, false-provider share, stale-head
share, and latency advantage, then classify whether a local policy should accept
or continue.  This is not a simulator of the real network; it is a pressure map
for guesses that are easy to fool with optimistic unit examples.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product

from .ids import DOMAIN, sha256

SWEEP_GRID_DOMAIN = DOMAIN + b":sweep-grid-v1:"


class SweepGridDecisionKind(str, Enum):
    ACCEPT_LOW_PRESSURE = "accept_low_pressure"
    CONTINUE_CAPTURE_PRESSURE = "continue_capture_pressure"
    CONTINUE_FALSE_PROVIDER_PRESSURE = "continue_false_provider_pressure"
    CONTINUE_STALE_HEAD_PRESSURE = "continue_stale_head_pressure"
    CONTINUE_FAST_WINDOW_CAPTURE = "continue_fast_window_capture"
    QUARANTINE_COMBINED_PRESSURE = "quarantine_combined_pressure"


@dataclass(frozen=True)
class SweepGridScenario:
    family_count: int
    captured_families: int
    false_provider_fraction: float
    stale_head_fraction: float
    latency_advantage_ms: int
    fast_window_size: int = 4

    def validate(self) -> None:
        if self.family_count <= 0 or self.captured_families < 0 or self.captured_families > self.family_count:
            raise ValueError("invalid family/capture counts")
        if not (0 <= self.false_provider_fraction <= 1) or not (0 <= self.stale_head_fraction <= 1):
            raise ValueError("fractions must be between 0 and 1")
        if self.fast_window_size <= 0:
            raise ValueError("fast_window_size must be positive")

    @property
    def captured_fraction(self) -> float:
        return self.captured_families / self.family_count


@dataclass(frozen=True)
class SweepGridPolicy:
    max_capture_fraction: float = 0.34
    max_false_provider_fraction: float = 0.10
    max_stale_head_fraction: float = 0.34
    max_fast_captured_fraction: float = 0.50
    quarantine_score: int = 3

    def validate(self) -> None:
        for value in (self.max_capture_fraction, self.max_false_provider_fraction, self.max_stale_head_fraction, self.max_fast_captured_fraction):
            if not (0 <= value <= 1):
                raise ValueError("policy fractions must be between 0 and 1")
        if self.quarantine_score <= 0:
            raise ValueError("quarantine score must be positive")


@dataclass(frozen=True)
class SweepGridPoint:
    scenario: SweepGridScenario
    decision: SweepGridDecisionKind
    risk_score: int
    captured_fraction: float
    fast_captured_fraction: float
    transcript_digest: bytes


@dataclass(frozen=True)
class SweepGridSummary:
    points: tuple[SweepGridPoint, ...]
    decision_counts: dict[str, int]
    worst_points: tuple[SweepGridPoint, ...]
    transcript_digest: bytes


def _fast_captured_fraction(scenario: SweepGridScenario) -> float:
    # A captured latency advantage should distort the *first answers* more than
    # the whole graph.  This small formula is intentionally conservative rather
    # than realistic: if captured nodes are faster, assume they overfill the fast
    # window before slower honest families answer.
    if scenario.captured_families == 0:
        return 0.0
    advantage_boost = min(1.0, max(0, scenario.latency_advantage_ms) / 200)
    base = scenario.captured_fraction
    return min(1.0, base + (1.0 - base) * advantage_boost)


def evaluate_sweep_grid_point(scenario: SweepGridScenario, *, policy: SweepGridPolicy | None = None) -> SweepGridPoint:
    scenario.validate()
    policy = policy or SweepGridPolicy()
    policy.validate()
    fast_capture = _fast_captured_fraction(scenario)
    risks = {
        "capture": scenario.captured_fraction > policy.max_capture_fraction,
        "false": scenario.false_provider_fraction > policy.max_false_provider_fraction,
        "stale": scenario.stale_head_fraction > policy.max_stale_head_fraction,
        "fast": fast_capture > policy.max_fast_captured_fraction,
    }
    risk_score = sum(1 for value in risks.values() if value)
    if risk_score >= policy.quarantine_score:
        decision = SweepGridDecisionKind.QUARANTINE_COMBINED_PRESSURE
    elif risks["fast"]:
        decision = SweepGridDecisionKind.CONTINUE_FAST_WINDOW_CAPTURE
    elif risks["false"]:
        decision = SweepGridDecisionKind.CONTINUE_FALSE_PROVIDER_PRESSURE
    elif risks["stale"]:
        decision = SweepGridDecisionKind.CONTINUE_STALE_HEAD_PRESSURE
    elif risks["capture"]:
        decision = SweepGridDecisionKind.CONTINUE_CAPTURE_PRESSURE
    else:
        decision = SweepGridDecisionKind.ACCEPT_LOW_PRESSURE
    digest = sha256(
        SWEEP_GRID_DOMAIN
        + b":point:"
        + str((scenario.family_count, scenario.captured_families, scenario.false_provider_fraction, scenario.stale_head_fraction, scenario.latency_advantage_ms, scenario.fast_window_size, decision.value, risk_score)).encode("ascii")
    )
    return SweepGridPoint(scenario, decision, risk_score, scenario.captured_fraction, fast_capture, digest)


def run_sweep_grid(
    *,
    family_counts: tuple[int, ...] = (4, 8),
    captured_family_counts: tuple[int, ...] = (0, 1, 2, 4),
    false_provider_fractions: tuple[float, ...] = (0.0, 0.1, 0.25),
    stale_head_fractions: tuple[float, ...] = (0.0, 0.25, 0.5),
    latency_advantages_ms: tuple[int, ...] = (0, 80, 200),
    policy: SweepGridPolicy | None = None,
) -> SweepGridSummary:
    policy = policy or SweepGridPolicy()
    points: list[SweepGridPoint] = []
    for family_count, captured, false_fraction, stale_fraction, latency in product(family_counts, captured_family_counts, false_provider_fractions, stale_head_fractions, latency_advantages_ms):
        if captured > family_count:
            continue
        points.append(evaluate_sweep_grid_point(
            SweepGridScenario(family_count, captured, false_fraction, stale_fraction, latency),
            policy=policy,
        ))
    decision_counts: dict[str, int] = {}
    for point in points:
        decision_counts[point.decision.value] = decision_counts.get(point.decision.value, 0) + 1
    worst = tuple(sorted(points, key=lambda point: (-point.risk_score, -point.fast_captured_fraction, -point.scenario.false_provider_fraction, -point.scenario.stale_head_fraction))[:5])
    digest = sha256(SWEEP_GRID_DOMAIN + b":summary:" + b"".join(point.transcript_digest for point in points))
    return SweepGridSummary(tuple(points), decision_counts, worst, digest)
