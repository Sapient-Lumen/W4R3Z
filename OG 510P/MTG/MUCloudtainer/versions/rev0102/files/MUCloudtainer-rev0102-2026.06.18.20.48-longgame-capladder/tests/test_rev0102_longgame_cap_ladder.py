from __future__ import annotations

from pathlib import Path

from src.muc5.longgame import (
    cap_ladder_summary,
    classify_nonterminal_snapshot,
    evaluate_focal_pair_with_snapshots,
    longgame_snapshot,
    run_cap_ladder_cell,
)
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator
from src.muc5.transfer_stress import rev0092_admitted_strategy, rev0101_transfer_stress_panel

ROOT = Path(__file__).resolve().parents[1]


def _counter_axis():
    return next(entry.strategy for entry in rev0101_transfer_stress_panel() if entry.strategy.strategy_id == "ood_counter_jace40")


def test_rev0102_snapshot_classification_is_counts_only() -> None:
    snapshot = {
        "loss_reason": "max_decisions_reached",
        "diagnostic_focal_advantage": 0.0,
        "focal_library_count": 3,
        "opponent_library_count": 4,
    }
    assert classify_nonterminal_snapshot(snapshot) == "balanced_control_cap"
    snapshot["opponent_library_count"] = 1
    assert classify_nonterminal_snapshot(snapshot) == "library_edge_cap"


def test_rev0102_focal_pair_snapshot_rows_are_balanced_and_nonleaking() -> None:
    target = rev0092_admitted_strategy(ROOT)
    opponent = _counter_axis()
    evaluator = EmpiricalGameEvaluator()
    estimate, rows = evaluate_focal_pair_with_snapshots(
        evaluator,
        target,
        opponent,
        EmpiricalEvaluationConfig(life_totals=(20,), reps=1, max_decisions=800, base_seed=102021),
        stage="unit_rev0102_axis",
    )
    assert estimate.games == 4
    assert len(rows) == 4
    assert {int(row["orientation"]) for row in rows} == {0, 1}
    assert {int(row["starting_player"]) for row in rows} == {0, 1}
    assert all(row["hidden_identity_leakage_guard"] == "counts_only_no_hand_or_library_identities" for row in rows)
    forbidden = {"focal_hand", "opponent_hand", "focal_library", "opponent_library"}
    assert all(not (forbidden & set(row.keys())) for row in rows)


def test_rev0102_cap_ladder_replays_same_seed_across_caps() -> None:
    target = rev0092_admitted_strategy(ROOT)
    opponent = _counter_axis()
    evaluator = EmpiricalGameEvaluator()
    rows = run_cap_ladder_cell(
        evaluator,
        target,
        opponent,
        original_stage="rev0101_ood_stress",
        ladder_stage="unit_rev0102_cap_ladder",
        base_seed=10101010,
        starting_life=40,
        rep=14,
        orientation=1,
        starting_player=0,
        max_decision_caps=(20, 25),
    )
    assert len(rows) == 2
    assert {row["seed"] for row in rows} == {30921518}
    assert [row["max_decisions"] for row in rows] == [20, 25]
    summary = cap_ladder_summary(rows)
    assert summary["rows"] == 2
    assert summary["caps"] == [20, 25]
