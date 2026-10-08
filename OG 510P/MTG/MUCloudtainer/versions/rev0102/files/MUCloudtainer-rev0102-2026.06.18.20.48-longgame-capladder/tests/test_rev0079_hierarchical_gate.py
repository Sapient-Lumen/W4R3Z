from __future__ import annotations

import csv
from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    population_hierarchical_familywise_gate_rows,
    summarize_population_hierarchical_gate,
)
from src.muc5.population_sampling import global_pool_source_rows
from src.muc5.statgate import hoeffding_interval
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)


def _source_rows() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for revision, name in (
        ("rev0069", "rev0069_population_frontier_arm_summary.csv"),
        ("rev0070", "rev0070_population_precision_arm_summary.csv"),
        ("rev0075", "rev0075_stratum_challenge_arm_summary.csv"),
    ):
        with (DATA / name).open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                row["source_revision"] = revision
                out.append(row)
    return out


def _simpson_style_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for size_axis, guarded_mean in (("large_good", 0.90), ("small_bad", 0.45)):
        for counter in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS):
            for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS):
                mean = guarded_mean if counter == GUARDED_COUNTER_AXIS else 0.20
                games = 10_000
                ci = hoeffding_interval(mean, games, alpha=0.0125)
                rows.append(
                    {
                        "size_axis": size_axis,
                        "counter_policy_axis": counter,
                        "threat_policy_axis": threat,
                        "target_mean_score_draw_half": mean,
                        "target_score_lcb_95": ci.low,
                        "target_score_ucb_95": ci.high,
                        "games": games,
                    }
                )
    return rows


def test_hierarchical_gate_blocks_aggregate_only_simpson_style_promotion() -> None:
    rows = _simpson_style_rows()
    gate_rows = population_hierarchical_familywise_gate_rows(
        rows,
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        layers=(
            ("global", (), True),
            ("by_size", ("size_axis",), True),
        ),
        min_games_per_cell=1000,
        max_ci_width=0.10,
        conservative_floor_threshold=0.50,
        alpha=0.05,
    )
    summary = summarize_population_hierarchical_gate(gate_rows)
    global_rows = [row for row in gate_rows if row["hierarchy_layer"] == "global"]
    size_rows = [row for row in gate_rows if row["hierarchy_layer"] == "by_size"]
    assert len(global_rows) == 1
    assert global_rows[0]["status"] == "candidate_promotable"
    assert any(row["size_axis"] == "small_bad" and row["status"] == "quarantined_low_security_floor" for row in size_rows)
    assert summary["mandatory_all_passed"] is False
    assert summary["mandatory_gate_passed_rows"] == 2


def test_actual_eligible_population_hierarchy_exposes_size_precision_and_fine_underpower() -> None:
    eligible = global_pool_source_rows(_source_rows())
    gate_rows = population_hierarchical_familywise_gate_rows(
        eligible,
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        layers=(
            ("global", (), True),
            ("by_life", ("starting_life",), True),
            ("by_size", ("size_axis",), True),
            ("by_size_life", ("size_axis", "starting_life"), False),
        ),
        min_games_per_cell=24,
        max_ci_width=0.60,
        conservative_floor_threshold=0.50,
        alpha=0.05,
    )
    summary = summarize_population_hierarchical_gate(gate_rows)
    assert len(gate_rows) == 12
    assert summary["gate_passed_cells"] == 0
    assert summary["mandatory_all_passed"] is False
    assert summary["hierarchy_layers"] == {"global": 1, "by_life": 2, "by_size": 3, "by_size_life": 6}
    assert summary["hierarchy_layer_status_counts"]["global"] == {"quarantined_low_security_floor": 1}
    assert summary["hierarchy_layer_status_counts"]["by_life"] == {"quarantined_low_security_floor": 2}
    assert summary["hierarchy_layer_status_counts"]["by_size"] == {"precision_target_not_met": 3}
    assert summary["hierarchy_layer_status_counts"]["by_size_life"] == {"underpowered_min_games": 6}
