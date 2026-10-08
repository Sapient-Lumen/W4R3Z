from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.population_frontier import COUNTER_POPULATION, THREAT_POPULATION
from src.muc5.population_power import (
    complete_panel_games_per_cell_for_axes,
    hoeffding_full_width,
    population_precision_power_ladder_rows,
    required_games_for_hoeffding_width,
    summarize_power_ladder_rows,
)
from src.muc5.population_sampling import global_pool_source_rows
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)


def _read_csv(name: str) -> list[dict[str, object]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _source_rows(include_rev0080: bool) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    sources = [
        ("rev0069", "rev0069_population_frontier_arm_summary.csv"),
        ("rev0070", "rev0070_population_precision_arm_summary.csv"),
    ]
    if include_rev0080:
        sources.append(("rev0080", "rev0080_size_ladder_arm_summary.csv"))
    for revision, name in sources:
        for row in _read_csv(name):
            item = dict(row)
            item["source_revision"] = revision
            rows.append(item)
    return rows


def test_required_games_and_complete_panel_increment_math() -> None:
    per_cell_alpha = 0.05 / 6.0
    required = required_games_for_hoeffding_width(0.60, alpha=per_cell_alpha)
    assert required == 31
    assert hoeffding_full_width(required, alpha=per_cell_alpha) <= 0.60
    assert hoeffding_full_width(required - 1, alpha=per_cell_alpha) > 0.60
    assert complete_panel_games_per_cell_for_axes(()) == 24
    assert complete_panel_games_per_cell_for_axes(("starting_life",)) == 12
    assert complete_panel_games_per_cell_for_axes(("size_axis",)) == 8
    assert complete_panel_games_per_cell_for_axes(("size_axis", "starting_life")) == 4


def test_power_ladder_identifies_five_reps_before_rev0080_and_zero_after() -> None:
    layers = (
        ("global", (), True),
        ("by_life", ("starting_life",), True),
        ("by_size", ("size_axis",), True),
        ("by_size_life", ("size_axis", "starting_life"), False),
    )
    before = population_precision_power_ladder_rows(
        global_pool_source_rows(_source_rows(include_rev0080=False)),
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=layers,
        min_games_per_cell=24,
        max_ci_width=0.60,
        alpha=0.05,
    )
    after = population_precision_power_ladder_rows(
        global_pool_source_rows(_source_rows(include_rev0080=True)),
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=layers,
        min_games_per_cell=24,
        max_ci_width=0.60,
        alpha=0.05,
    )
    before_summary = summarize_power_ladder_rows(before)
    after_summary = summarize_power_ladder_rows(after)
    assert before_summary["mandatory_max_complete_panel_reps_needed"] == 1
    assert before_summary["max_complete_panel_reps_needed"] == 5
    assert before_summary["precision_blocked_rows"] == 3
    assert before_summary["underpowered_rows"] == 6
    assert after_summary["mandatory_max_complete_panel_reps_needed"] == 0
    assert after_summary["max_complete_panel_reps_needed"] == 0
    assert after_summary["precision_blocked_rows"] == 0
    assert after_summary["underpowered_rows"] == 0


def test_actual_rev0080_summary_clears_power_blockers_without_promoting() -> None:
    summary = json.loads((DATA / "rev0080_size_ladder_power_summary.json").read_text(encoding="utf-8"))
    assert summary["games"] == 720
    assert summary["post_gate_passed_cells"] == 0
    assert summary["pre_all_layer_complete_panel_reps_needed"] == 5
    assert summary["post_all_layer_complete_panel_reps_needed"] == 0
    assert summary["post_power_summary"]["precision_blocked_rows"] == 0
    assert summary["post_power_summary"]["underpowered_rows"] == 0
    assert summary["hierarchy_summary"]["status_counts"] == {"quarantined_low_security_floor": 12}
    assert summary["cpp_shadow_records_checked"] == 15000
    assert summary["cpp_shadow_summary"]["mismatches"] == 0


def test_unknown_complete_panel_revisions_fail_closed_until_whitelisted() -> None:
    rows = [
        {
            "source_revision": "rev9999",
            "counter_policy_axis": counter,
            "threat_policy_axis": threat,
            "size_axis": "synthetic",
            "starting_life": 20,
            "games": 100,
            "target_mean_score_draw_half": 0.9,
            "target_score_lcb_95": 0.8,
            "target_score_ucb_95": 1.0,
        }
        for counter in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS)
        for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS)
    ]
    assert global_pool_source_rows(rows) == []
