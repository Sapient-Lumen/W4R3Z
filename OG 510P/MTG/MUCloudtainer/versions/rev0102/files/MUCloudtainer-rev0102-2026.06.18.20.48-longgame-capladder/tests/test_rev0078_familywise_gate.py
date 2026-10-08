from __future__ import annotations

import csv
from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    aggregate_population_summary_rows,
    population_familywise_gate_rows,
    population_familywise_interval_rows,
    population_precision_gate_rows,
    summarize_population_precision_gate,
)
from src.muc5.population_sampling import global_pool_source_rows
from src.muc5.statgate import hoeffding_interval
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)


def _near_threshold_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for counter in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS):
        for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS):
            mean = 0.25 if counter == LEGACY_COUNTER_AXIS else 0.533
            games = 2000
            ci = hoeffding_interval(mean, games, alpha=0.05)
            rows.append(
                {
                    "scope": "demo",
                    "counter_policy_axis": counter,
                    "threat_policy_axis": threat,
                    "target_mean_score_draw_half": mean,
                    "target_score_lcb_95": ci.low,
                    "target_score_ucb_95": ci.high,
                    "games": games,
                }
            )
    return rows


def _actual_summary_rows() -> list[dict[str, object]]:
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


def test_familywise_interval_rows_split_alpha_across_matrix_cells() -> None:
    rows = _near_threshold_rows()
    adjusted = population_familywise_interval_rows(
        rows,
        context_axes=("scope",),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        alpha=0.05,
    )
    assert len(adjusted) == 4
    assert {row["interval_family_cell_count"] for row in adjusted} == {4}
    assert {row["interval_per_cell_alpha"] for row in adjusted} == {0.0125}
    guarded = [row for row in adjusted if row["counter_policy_axis"] == GUARDED_COUNTER_AXIS]
    assert all(float(row["target_score_lcb_familywise"]) < float(row["target_score_lcb_95"]) for row in guarded)
    assert all(float(row["target_score_ucb_familywise"]) > float(row["target_score_ucb_95"]) for row in guarded)


def test_familywise_gate_can_block_an_unadjusted_near_threshold_candidate() -> None:
    ordinary = population_precision_gate_rows(
        _near_threshold_rows(),
        context_axes=("scope",),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        min_games_per_cell=100,
        max_ci_width=0.20,
        conservative_floor_threshold=0.50,
    )
    familywise = population_familywise_gate_rows(
        _near_threshold_rows(),
        context_axes=("scope",),
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        min_games_per_cell=100,
        max_ci_width=0.20,
        conservative_floor_threshold=0.50,
        alpha=0.05,
    )
    assert ordinary[0]["status"] == "candidate_promotable"
    assert ordinary[0]["gate_passed"] is True
    assert familywise[0]["status"] == "quarantined_low_security_floor"
    assert familywise[0]["gate_passed"] is False
    assert float(familywise[0]["conservative_pure_security_lcb"]) < float(ordinary[0]["conservative_pure_security_lcb"])


def test_actual_eligible_population_familywise_gate_strengthens_existing_quarantine() -> None:
    eligible = global_pool_source_rows(_actual_summary_rows())
    pooled = aggregate_population_summary_rows(eligible, context_axes=())
    ordinary = population_precision_gate_rows(
        pooled,
        context_axes=(),
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        min_games_per_cell=24,
        max_ci_width=0.60,
        conservative_floor_threshold=0.50,
    )
    familywise = population_familywise_gate_rows(
        pooled,
        context_axes=(),
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        min_games_per_cell=24,
        max_ci_width=0.60,
        conservative_floor_threshold=0.50,
        alpha=0.05,
    )
    ordinary_summary = summarize_population_precision_gate(ordinary)
    familywise_summary = summarize_population_precision_gate(familywise)
    assert ordinary_summary["gate_passed_cells"] == 0
    assert familywise_summary["gate_passed_cells"] == 0
    assert familywise[0]["status"] == "quarantined_low_security_floor"
    assert familywise[0]["interval_family_cell_count"] == 6
    assert float(familywise_summary["best_conservative_pure_security_lcb"]) < float(ordinary_summary["best_conservative_pure_security_lcb"])
    assert float(familywise_summary["max_ci_width_observed"]) > float(ordinary_summary["max_ci_width_observed"])
