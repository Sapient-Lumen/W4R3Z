from __future__ import annotations

import json
from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.evidence_tiering import CATALOG_FORMAT, find_tiering_catalog, catalog_row_count
from src.muc5.population_frontier import (
    exact_support_enumeration_maximin,
    exact_two_row_maximin,
    population_precision_gate_rows,
    zero_sum_maximin,
)
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS


def test_exact_two_row_maximin_solves_two_by_three_game_without_iteration_noise() -> None:
    result = exact_two_row_maximin([[0.2, 0.9, 0.2], [0.8, 0.1, 0.4]])
    assert result.solution_method == "exact_two_row"
    assert result.iterations == 0
    assert abs(result.row_strategy[0] - 0.3) < 1e-12
    assert abs(result.guaranteed_value - 0.34) < 1e-12
    assert abs(result.exploitability_upper_value - 0.34) < 1e-12
    assert abs(sum(result.column_strategy) - 1.0) < 1e-12


def test_zero_sum_maximin_uses_exact_support_enumeration_for_small_larger_games() -> None:
    result = zero_sum_maximin(
        [
            [0.8, 0.2, 0.4],
            [0.3, 0.7, 0.5],
            [0.6, 0.4, 0.9],
        ],
    )
    assert result.solution_method == "exact_support_enumeration"
    assert result.iterations == 0
    assert abs(result.guaranteed_value - 0.5) < 1e-12
    assert abs(result.exploitability_upper_value - 0.5) < 1e-12
    assert abs(sum(result.row_strategy) - 1.0) < 1e-12
    assert abs(sum(result.column_strategy) - 1.0) < 1e-12


def test_zero_sum_maximin_can_still_use_fictitious_play_when_exact_support_is_disabled() -> None:
    result = zero_sum_maximin(
        [
            [0.8, 0.2, 0.4],
            [0.3, 0.7, 0.5],
            [0.6, 0.4, 0.9],
        ],
        iterations=200,
        max_exact_cells=0,
    )
    assert result.solution_method == "fictitious_play"
    assert result.iterations == 200


def test_exact_support_enumeration_rejects_missing_values_fail_closed() -> None:
    try:
        exact_support_enumeration_maximin([[0.1, 0.2], [0.3, float("nan")], [0.4, 0.5]])
    except ValueError as exc:
        assert "missing or non-finite" in str(exc)
    else:  # pragma: no cover - test must fail closed.
        raise AssertionError("exact support enumeration accepted a non-finite payoff matrix")


def test_population_gate_reports_exact_solver_for_current_two_policy_surface() -> None:
    rows = []
    for counter in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS):
        for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS):
            rows.append(
                {
                    "scope": "demo",
                    "counter_policy_axis": counter,
                    "threat_policy_axis": threat,
                    "target_mean_score_draw_half": 0.60 if counter == GUARDED_COUNTER_AXIS else 0.30,
                    "target_score_lcb_95": 0.20 if counter == GUARDED_COUNTER_AXIS else 0.05,
                    "target_score_ucb_95": 0.80 if counter == GUARDED_COUNTER_AXIS else 0.55,
                    "games": 24,
                }
            )
    [gate] = population_precision_gate_rows(
        rows,
        context_axes=("scope",),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        min_games_per_cell=24,
        max_ci_width=0.70,
        conservative_floor_threshold=0.50,
    )
    assert gate["mixed_solution_method"] == "exact_two_row"
    assert gate["status"] == "quarantined_low_security_floor"


def test_evidence_tiering_catalog_discovery_prefers_latest_revision(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    old = data / "rev0072_evidence_tiering_catalog.json"
    new = data / "rev0073_evidence_tiering_catalog.json"
    payload = {
        "format": CATALOG_FORMAT,
        "records": [
            {"path": "data/raw.csv", "row_count": 7},
        ],
    }
    old.write_text(json.dumps({**payload, "records": [{"path": "data/raw.csv", "row_count": 3}]}) + "\n", encoding="utf-8")
    new.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    assert find_tiering_catalog(tmp_path) == new
    assert catalog_row_count(tmp_path, "data/raw.csv") == 7
