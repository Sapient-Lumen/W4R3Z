from __future__ import annotations

import csv
from pathlib import Path

from src.muc5.population_frontier import (
    COUNTER_POPULATION,
    THREAT_POPULATION,
    aggregate_population_summary_rows,
    population_precision_gate_rows,
    summarize_population_precision_gate,
)
from src.muc5.population_sampling import (
    COMPLETE_POPULATION_PANEL,
    TARGETED_STRATUM_CHALLENGE,
    adaptive_pooling_guard,
    global_pool_source_rows,
    sampling_frame_for_row,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ROW_POLICIES = tuple(axis for axis, _agent, _note in COUNTER_POPULATION)
COLUMN_POLICIES = tuple(axis for axis, _agent, _note in THREAT_POPULATION)


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


def _global_gate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    pooled = aggregate_population_summary_rows(rows, context_axes=())
    return population_precision_gate_rows(
        pooled,
        context_axes=(),
        row_policies=ROW_POLICIES,
        column_policies=COLUMN_POLICIES,
        min_games_per_cell=24,
        max_ci_width=0.60,
        conservative_floor_threshold=0.50,
    )


def test_sampling_frame_classifier_excludes_targeted_challenge_from_global_pool() -> None:
    assert sampling_frame_for_row({"source_revision": "rev0069"}) == COMPLETE_POPULATION_PANEL
    assert sampling_frame_for_row({"source_revision": "rev0070"}) == COMPLETE_POPULATION_PANEL
    assert sampling_frame_for_row({"source_revision": "rev0075"}) == TARGETED_STRATUM_CHALLENGE
    assert sampling_frame_for_row({"source_revision": "rev0099", "stress_selection_rule": "posthoc"}) == TARGETED_STRATUM_CHALLENGE


def test_actual_population_summary_split_keeps_adaptive_rows_out_of_broad_pool() -> None:
    rows = _actual_summary_rows()
    guard = adaptive_pooling_guard(rows)
    eligible = global_pool_source_rows(rows)
    assert guard["sampling_frame_counts"] == {
        COMPLETE_POPULATION_PANEL: 72,
        TARGETED_STRATUM_CHALLENGE: 18,
    }
    assert guard["global_pool_guard_passed"] is True
    assert len(eligible) == 72
    assert sum(int(row["games"]) for row in eligible) == 432


def test_naive_adaptive_pool_would_materially_shift_global_lcb_but_still_not_promote() -> None:
    rows = _actual_summary_rows()
    eligible_gate = _global_gate(global_pool_source_rows(rows))
    naive_gate = _global_gate(rows)
    eligible_summary = summarize_population_precision_gate(eligible_gate)
    naive_summary = summarize_population_precision_gate(naive_gate)

    assert eligible_summary["gate_passed_cells"] == 0
    assert naive_summary["gate_passed_cells"] == 0
    assert eligible_gate[0]["status"] == "quarantined_low_security_floor"
    assert naive_gate[0]["status"] == "quarantined_low_security_floor"
    # The post-hoc challenge was selected from promising underpowered strata; if
    # it is incorrectly pooled as if it were a normal population panel, the broad
    # conservative floor moves materially upward.
    assert float(naive_summary["best_conservative_pure_security_lcb"]) - float(eligible_summary["best_conservative_pure_security_lcb"]) > 0.10
