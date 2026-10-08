from __future__ import annotations

import numpy as np

from src.muc5.confidence_floor import compare_matrix_self_floor, floor_from_estimates, require_no_seed_overlap
from src.muc5.psro import estimate_scores


def test_matrix_floor_distinguishes_self_diagonal_from_opponents() -> None:
    matrix = np.asarray(
        [
            [0.5, 0.7, 0.65],
            [0.3, 0.5, 0.4],
            [0.35, 0.6, 0.5],
        ]
    )
    comparison = compare_matrix_self_floor(matrix, ["a", "b", "c"], "a")
    assert comparison["self_diagonal_is_floor"] is True
    assert comparison["with_self"]["floor"] == 0.5
    assert comparison["without_self"]["floor"] == 0.65
    assert comparison["self_diagonal_floor_gap"] == 0.15000000000000002


def test_floor_from_estimates_uses_weakest_confidence_bound() -> None:
    estimates = [
        estimate_scores("focal", "opp_a", [1.0] * 40 + [0.0] * 10),
        estimate_scores("focal", "opp_b", [1.0] * 30 + [0.0] * 20),
    ]
    floor = floor_from_estimates("focal", estimates)
    assert floor.opponent_count == 2
    assert floor.weakest_mean_opponent == "opp_b"
    assert floor.weakest_ci_opponent in {"opp_a", "opp_b"}
    assert floor.total_games == 100
    assert floor.truncations == 0


def test_seed_overlap_audit_flags_cross_group_overlap() -> None:
    ok = require_no_seed_overlap([{"seed": 1}, {"seed": 2}], [{"seed": 3}])
    bad = require_no_seed_overlap([{"seed": 1}], [{"seed": 1}, {"seed": 2}])
    assert ok["passed"] is True
    assert bad["passed"] is False
    assert bad["overlap_count"] == 1
