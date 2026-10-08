from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np

from .psro import PairEstimate


@dataclass(frozen=True)
class FloorSummary:
    """Confidence-floor summary for one focal strategy.

    Matrix diagonals are useful conventions for zero-sum solving, but they are
    not opponent evidence.  This helper keeps the two notions separate so a
    self-play diagonal cannot hide or distort the floor against real challengers.
    """

    focal_strategy: str
    opponent_count: int
    total_games: int
    min_mean_score: float
    min_ci_low: float
    max_ci_high: float
    weakest_mean_opponent: str
    weakest_ci_opponent: str
    truncations: int
    passed_over_half_by_ci_low: bool
    threshold: float = 0.5

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def estimate_row(estimate: PairEstimate, *, stage: str) -> dict[str, object]:
    payload = estimate.as_dict()
    payload["stage"] = stage
    payload["score_excess_over_half"] = float(estimate.mean_score - 0.5)
    payload["ci_low_excess_over_half"] = float(estimate.ci_low - 0.5)
    payload["ci_high_excess_over_half"] = float(estimate.ci_high - 0.5)
    return payload


def floor_from_estimates(
    focal_strategy: str,
    estimates: Sequence[PairEstimate],
    *,
    threshold: float = 0.5,
) -> FloorSummary:
    """Return the weakest opponent floor across non-self pair estimates."""

    material = [estimate for estimate in estimates if estimate.focal_strategy != estimate.opponent_strategy]
    if not material:
        raise ValueError("at least one non-self estimate is required")
    means = np.asarray([estimate.mean_score for estimate in material], dtype=np.float64)
    ci_lows = np.asarray([estimate.ci_low for estimate in material], dtype=np.float64)
    ci_highs = np.asarray([estimate.ci_high for estimate in material], dtype=np.float64)
    weakest_mean_index = int(np.argmin(means))
    weakest_ci_index = int(np.argmin(ci_lows))
    truncations = int(sum(estimate.truncations for estimate in material))
    return FloorSummary(
        focal_strategy=str(focal_strategy),
        opponent_count=len(material),
        total_games=int(sum(estimate.games for estimate in material)),
        min_mean_score=float(means[weakest_mean_index]),
        min_ci_low=float(ci_lows[weakest_ci_index]),
        max_ci_high=float(np.max(ci_highs)),
        weakest_mean_opponent=material[weakest_mean_index].opponent_strategy,
        weakest_ci_opponent=material[weakest_ci_index].opponent_strategy,
        truncations=truncations,
        passed_over_half_by_ci_low=bool(float(ci_lows[weakest_ci_index]) > float(threshold) and truncations == 0),
        threshold=float(threshold),
    )


def matrix_row_floor(
    matrix: Sequence[Sequence[float]],
    strategy_ids: Sequence[str],
    focal_strategy: str,
    *,
    include_self: bool,
) -> dict[str, object]:
    """Summarize a row floor from a score matrix with explicit self handling."""

    ids = list(strategy_ids)
    if focal_strategy not in ids:
        raise ValueError(f"unknown focal strategy {focal_strategy!r}")
    focal_index = ids.index(focal_strategy)
    values: list[tuple[str, float]] = []
    for index, opponent_id in enumerate(ids):
        if not include_self and index == focal_index:
            continue
        values.append((opponent_id, float(matrix[focal_index][index])))
    if not values:
        raise ValueError("matrix row floor has no values after self filtering")
    opponent_id, value = min(values, key=lambda item: item[1])
    return {
        "focal_strategy": focal_strategy,
        "include_self": bool(include_self),
        "opponent_count": len(values),
        "floor": value,
        "floor_opponent": opponent_id,
        "ceiling": max(score for _, score in values),
        "mean": float(sum(score for _, score in values) / len(values)),
    }


def compare_matrix_self_floor(
    matrix: Sequence[Sequence[float]],
    strategy_ids: Sequence[str],
    focal_strategy: str,
) -> dict[str, object]:
    """Expose the self-diagonal ambiguity from a matrix row."""

    with_self = matrix_row_floor(matrix, strategy_ids, focal_strategy, include_self=True)
    without_self = matrix_row_floor(matrix, strategy_ids, focal_strategy, include_self=False)
    return {
        "schema": "muc5.matrix_self_floor_comparison.v1",
        "focal_strategy": focal_strategy,
        "with_self": with_self,
        "without_self": without_self,
        "self_diagonal_is_floor": bool(with_self["floor_opponent"] == focal_strategy),
        "self_diagonal_floor_gap": float(without_self["floor"] - with_self["floor"]),
    }


def opponent_estimate_rows(estimates: Iterable[PairEstimate], *, stage: str) -> list[dict[str, object]]:
    return [estimate_row(estimate, stage=stage) for estimate in estimates]


def require_no_seed_overlap(*row_groups: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Audit deterministic seed namespaces across row groups."""

    seen: dict[int, int] = {}
    overlaps: list[dict[str, object]] = []
    counts: list[int] = []
    for group_index, rows in enumerate(row_groups):
        seeds: set[int] = set()
        for row in rows:
            seed = int(row["seed"])
            seeds.add(seed)
            previous = seen.get(seed)
            if previous is not None and previous != group_index:
                overlaps.append({"seed": seed, "first_group": previous, "second_group": group_index})
            seen[seed] = group_index
        counts.append(len(seeds))
    return {
        "schema": "muc5.seed_overlap_audit.v1",
        "passed": not overlaps,
        "group_seed_counts": counts,
        "overlap_count": len(overlaps),
        "overlaps": overlaps[:20],
    }
