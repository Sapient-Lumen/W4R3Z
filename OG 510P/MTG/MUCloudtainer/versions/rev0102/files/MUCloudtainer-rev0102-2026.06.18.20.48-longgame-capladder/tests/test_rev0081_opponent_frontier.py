from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    population_column_frontier_rows,
    summarize_population_column_frontier,
)
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS
from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)


def _read_csv(name: str) -> list[dict[str, object]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def test_column_frontier_outputs_all_requested_threat_columns_and_fails_closed_on_missing_policy() -> None:
    rows = [
        {
            "counter_policy_axis": LEGACY_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "games": 64,
            "target_mean_score_draw_half": 0.55,
        },
        {
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "games": 64,
            "target_mean_score_draw_half": 0.70,
        },
        # PRESSURE_THREAT_AXIS intentionally lacks the guarded row.
        {
            "counter_policy_axis": LEGACY_COUNTER_AXIS,
            "threat_policy_axis": PRESSURE_THREAT_AXIS,
            "games": 64,
            "target_mean_score_draw_half": 0.80,
        },
    ]
    frontier = population_column_frontier_rows(
        rows,
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        context_axes=(),
        min_games_per_cell=16,
        max_ci_width=1.0,
        conservative_floor_threshold=0.30,
        alpha=0.05,
    )
    assert [row["threat_policy_axis"] for row in frontier] == [CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS]
    closure = frontier[0]
    pressure = frontier[1]
    assert closure["complete"] is True
    assert closure["status"] == "candidate_counter_answer_for_threat_column"
    assert closure["best_response_row_policy_by_lcb"] == GUARDED_COUNTER_AXIS
    assert pressure["complete"] is False
    assert pressure["status"] == "incomplete_opponent_column"
    assert pressure["column_answer_passed"] is False
    assert GUARDED_COUNTER_AXIS in str(pressure["missing_row_policies"])


def test_actual_rev0081_opponent_frontier_resolves_all_low_floor_axes_without_promoting() -> None:
    summary = json.loads((DATA / "rev0081_opponent_frontier_summary.json").read_text(encoding="utf-8"))
    assert summary["eligible_summary_game_rows"] == 1152
    assert summary["adaptive_summary_rows_excluded"] == 18
    assert summary["frontier_rows"] == 36
    assert summary["global_frontier_rows"] == 3
    assert summary["mandatory_frontier_rows"] == 18
    assert summary["mandatory_column_answer_passed_rows"] == 0
    assert summary["frontier_summary"]["column_answer_passed_rows"] == 0
    assert summary["frontier_summary"]["status_counts"] == {"no_credible_counter_answer_for_threat_column": 36}
    assert summary["weak_threat_axis_count"] == 3
    assert summary["max_ci_width_observed"] <= 0.60
    assert summary["min_games_per_observed_column_cell"] >= 24


def test_frontier_csv_has_every_layer_threat_combination() -> None:
    rows = _read_csv("rev0081_opponent_frontier_familywise.csv")
    assert len(rows) == 36
    layer_counts: dict[str, int] = {}
    threat_counts: dict[str, int] = {}
    for row in rows:
        layer_counts[row["hierarchy_layer"]] = layer_counts.get(row["hierarchy_layer"], 0) + 1
        threat_counts[row["threat_policy_axis"]] = threat_counts.get(row["threat_policy_axis"], 0) + 1
    assert layer_counts == {"global": 3, "by_life": 6, "by_size": 9, "by_size_life": 18}
    assert set(threat_counts) == set(COLUMN_POLICIES)
    assert set(threat_counts.values()) == {12}


def test_frontier_summarizer_tracks_threat_and_layer_status_counts() -> None:
    rows = _read_csv("rev0081_opponent_frontier_familywise.csv")
    summary = summarize_population_column_frontier(rows)
    assert summary["rows"] == 36
    assert summary["column_answer_passed_rows"] == 0
    assert summary["hierarchy_layer_status_counts"]["global"] == {"no_credible_counter_answer_for_threat_column": 3}
    assert summary["hierarchy_layer_status_counts"]["by_size_life"] == {"no_credible_counter_answer_for_threat_column": 18}
    assert summary["worst_threat_policy_axis"] == "library_aware_threat_closure_targetguarded"
    assert summary["worst_size_axis"] == "counter40_vs_threat40"
    assert str(summary["worst_starting_life"]) == "20"
