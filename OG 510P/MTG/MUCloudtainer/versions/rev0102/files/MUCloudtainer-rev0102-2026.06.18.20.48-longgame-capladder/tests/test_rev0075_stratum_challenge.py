from __future__ import annotations

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.population_frontier import population_gate_bool, summarize_population_precision_gate
from src.muc5.population_stratum_challenge import select_underpowered_candidate_cells
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS


def test_gate_bool_does_not_treat_false_csv_strings_as_passed() -> None:
    rows = [
        {"status": "underpowered_min_games", "gate_passed": "False", "conservative_pure_security_lcb": "0.1", "max_ci_width_observed": "0.4"},
        {"status": "candidate_promotable", "gate_passed": "True", "conservative_pure_security_lcb": "0.6", "max_ci_width_observed": "0.2"},
    ]
    assert population_gate_bool("False") is False
    assert population_gate_bool("True") is True
    assert summarize_population_precision_gate(rows)["gate_passed_cells"] == 1


def test_select_underpowered_candidate_cells_deduplicates_high_mean_strata() -> None:
    rows = [
        {
            "source_revision": "rev0069",
            "size_axis": "counter40_vs_threat40",
            "starting_life": "40",
            "status": "underpowered_min_games",
            "mean_pure_security_value": "0.75",
            "mean_best_pure_row_policy": GUARDED_COUNTER_AXIS,
        },
        {
            "source_revision": "rev0070",
            "size_axis": "counter40_vs_threat40",
            "starting_life": "40",
            "status": "underpowered_min_games",
            "mean_pure_security_value": "0.50",
            "mean_best_pure_row_policy": GUARDED_COUNTER_AXIS,
        },
        {
            "source_revision": "rev0070",
            "size_axis": "counter60_vs_threat60",
            "starting_life": "20",
            "status": "underpowered_min_games",
            "mean_pure_security_value": "0.25",
            "mean_best_pure_row_policy": LEGACY_COUNTER_AXIS,
        },
    ]
    selected = select_underpowered_candidate_cells(rows, min_mean_floor=0.50, required_best_policy=GUARDED_COUNTER_AXIS)
    assert selected == (("counter40_vs_threat40", 40),)


def test_select_underpowered_candidate_cells_ignores_non_underpowered_rows() -> None:
    rows = [
        {
            "size_axis": "counter40_vs_threat40",
            "starting_life": "40",
            "status": "quarantined_low_security_floor",
            "mean_pure_security_value": "0.75",
            "mean_best_pure_row_policy": GUARDED_COUNTER_AXIS,
        }
    ]
    assert select_underpowered_candidate_cells(rows, min_mean_floor=0.50, required_best_policy=GUARDED_COUNTER_AXIS) == ()


def test_population_aggregation_normalizes_string_and_int_starting_life_contexts() -> None:
    from src.muc5.population_frontier import aggregate_population_summary_rows, population_cells_from_summary_rows

    rows = []
    for counter in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS):
        for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS):
            rows.append({
                "size_axis": "counter40_vs_threat40",
                "starting_life": "40",
                "counter_policy_axis": counter,
                "threat_policy_axis": threat,
                "target_mean_score_draw_half": 0.25,
                "games": 4,
            })
            rows.append({
                "size_axis": "counter40_vs_threat40",
                "starting_life": 40,
                "counter_policy_axis": counter,
                "threat_policy_axis": threat,
                "target_mean_score_draw_half": 0.75,
                "games": 4,
            })
    pooled = aggregate_population_summary_rows(rows, context_axes=("size_axis", "starting_life"))
    assert len(pooled) == 4
    assert {row["starting_life"] for row in pooled} == {40}
    [cell] = population_cells_from_summary_rows(
        pooled,
        context_axes=("size_axis", "starting_life"),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
    )
    assert cell.complete
    assert cell.min_games == 8
