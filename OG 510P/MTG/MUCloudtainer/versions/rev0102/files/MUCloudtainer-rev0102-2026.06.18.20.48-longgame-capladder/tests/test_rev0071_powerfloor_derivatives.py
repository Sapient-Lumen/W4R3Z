from __future__ import annotations

import csv
from pathlib import Path

from src.muc5.cpp_rollout import (
    CppShadowTransitionRow,
    PreparedCppShadowRollout,
    sample_prepared_cpp_shadow_rollout,
)
from src.muc5.evidence_derivatives import summarize_cpp_batch_trace_rows, summarize_ranker_training_dataset
from src.muc5.evidence_index import build_evidence_index
from src.muc5.population_frontier import aggregate_population_summary_rows, population_precision_gate_rows
from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.threat_response import CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS


def _row(i: int) -> CppShadowTransitionRow:
    return CppShadowTransitionRow(
        game_id="g",
        step=i,
        player=0,
        frame="MAIN",
        main_phase="precombat",
        pending_choice_kind="none",
        stack_depth=0,
        action_kind="PASS",
        action="PASS",
        supported_by_cpp=True,
        skipped_reason="",
        cpp_match=None,
        case_id=f"case{i}",
    )


def test_sample_prepared_cpp_shadow_rollout_reindexes_even_sample() -> None:
    prepared = PreparedCppShadowRollout(
        revision="revtest",
        game_rows=({"winner": "0", "is_truncation": False, "decisions": 10},),
        records=tuple(f"record{i}" for i in range(10)),  # type: ignore[arg-type]
        expected_signatures=tuple(f"sig{i}" for i in range(10)),
        record_row_indices=tuple(range(10)),
        transition_rows=tuple(_row(i) for i in range(10)),
        python_errors=(),
    )
    sampled = sample_prepared_cpp_shadow_rollout(prepared, max_records=4)
    assert sampled.game_rows == prepared.game_rows
    assert sampled.record_row_indices == (0, 1, 2, 3)
    assert sampled.expected_signatures == ("sig0", "sig3", "sig6", "sig9")
    assert [r.case_id for r in sampled.transition_rows] == ["case0", "case3", "case6", "case9"]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_evidence_derivatives_turn_missing_derivative_blocker_into_archive_candidate(tmp_path: Path) -> None:
    root = tmp_path
    (root / "data").mkdir()
    raw = root / "data" / ("rev0021_" + "ranker_training_dataset.csv")
    _write_csv(
        raw,
        [
            {
                "game_index": 0,
                "decision_id": "d0",
                "step": 1,
                "player": 0,
                "agent_name": "agentA",
                "starting_player": 0,
                "starting_life": 20,
                "action_index": 0,
                "action_count": 2,
                "chosen": 1,
                "action": "PASS",
                "kind_pass": 1.0,
                "kind_cast": 0.0,
            },
            {
                "game_index": 0,
                "decision_id": "d0",
                "step": 1,
                "player": 0,
                "agent_name": "agentA",
                "starting_player": 0,
                "starting_life": 20,
                "action_index": 1,
                "action_count": 2,
                "chosen": 0,
                "action": "PLAY_ISLAND",
                "kind_pass": 0.0,
                "kind_cast": 0.0,
            },
        ],
    )
    [before] = build_evidence_index(root, min_bytes=10)
    assert before.retention_class == "blocked_missing_compact_derivative"
    summary = summarize_ranker_training_dataset(raw)
    (root / "data" / "rev0021_ranker_summary.json").write_text("{}\n", encoding="utf-8")
    [after] = build_evidence_index(root, min_bytes=10)
    assert summary["rows"] == 2
    assert summary["chosen_rows"] == 1
    assert after.retention_class == "evidence_archive_candidate"


def test_cpp_batch_trace_derivative_counts_mismatches_and_support(tmp_path: Path) -> None:
    raw = tmp_path / "trace.csv"
    _write_csv(
        raw,
        [
            {
                "trace_id": "t0",
                "step": 1,
                "player": 0,
                "frame": "MAIN",
                "main_phase": "precombat",
                "pending_choice_kind": "none",
                "stack_depth": 0,
                "action_kind": "PASS",
                "action": "PASS",
                "supported_by_cpp": "True",
                "skipped_reason": "",
                "python_pre_fingerprint_ok": "True",
                "python_post_fingerprint_ok": "True",
                "cpp_match": "True",
                "case_id": "c0",
            },
            {
                "trace_id": "t0",
                "step": 2,
                "player": 0,
                "frame": "MAIN",
                "main_phase": "precombat",
                "pending_choice_kind": "none",
                "stack_depth": 0,
                "action_kind": "CAST",
                "action": "CAST",
                "supported_by_cpp": "True",
                "skipped_reason": "",
                "python_pre_fingerprint_ok": "True",
                "python_post_fingerprint_ok": "True",
                "cpp_match": "False",
                "case_id": "c1",
            },
        ],
    )
    summary = summarize_cpp_batch_trace_rows(raw)
    assert summary["rows"] == 2
    assert summary["supported_by_cpp_rows"] == 2
    assert summary["cpp_mismatch_rows"] == 1
    assert summary["action_kind_counts"]["PASS"] == 1


def test_population_gate_can_reach_precision_and_then_quarantine_low_floor() -> None:
    rows: list[dict[str, object]] = []
    for counter in (LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS):
        for threat in (CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS):
            rows.append(
                {
                    "size_axis": "cellA",
                    "starting_life": 20,
                    "counter_policy_axis": counter,
                    "threat_policy_axis": threat,
                    "target_mean_score_draw_half": 0.55 if counter == GUARDED_COUNTER_AXIS else 0.30,
                    "target_score_lcb_95": 0.25 if counter == GUARDED_COUNTER_AXIS else 0.05,
                    "target_score_ucb_95": 0.75 if counter == GUARDED_COUNTER_AXIS else 0.55,
                    "games": 24,
                }
            )
    [row] = population_precision_gate_rows(
        rows,
        row_policies=(LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS),
        column_policies=(CLOSURE_THREAT_AXIS, PRESSURE_THREAT_AXIS),
        min_games_per_cell=24,
        max_ci_width=0.60,
        conservative_floor_threshold=0.50,
        iterations=200,
    )
    assert row["precision_ok"] is True
    assert row["status"] == "quarantined_low_security_floor"
    assert row["gate_passed"] is False


def test_aggregate_population_summary_rows_recomputes_weighted_ci_without_overwrite() -> None:
    rows = [
        {
            "starting_life": 20,
            "size_axis": "small",
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.25,
            "games": 8,
            "source_revision": "revA",
        },
        {
            "starting_life": 20,
            "size_axis": "large",
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "threat_policy_axis": CLOSURE_THREAT_AXIS,
            "target_mean_score_draw_half": 0.75,
            "games": 24,
            "source_revision": "revB",
        },
    ]
    [pooled] = aggregate_population_summary_rows(rows, context_axes=("starting_life",))
    assert pooled["games"] == 32
    assert pooled["source_rows"] == 2
    assert abs(float(pooled["target_mean_score_draw_half"]) - 0.625) < 1e-12
    assert pooled["pooled_size_axes"] == "large;small"
    assert pooled["pooled_source_revisions"] == "revA;revB"
    assert float(pooled["target_score_ucb_95"]) - float(pooled["target_score_lcb_95"]) < 0.50
