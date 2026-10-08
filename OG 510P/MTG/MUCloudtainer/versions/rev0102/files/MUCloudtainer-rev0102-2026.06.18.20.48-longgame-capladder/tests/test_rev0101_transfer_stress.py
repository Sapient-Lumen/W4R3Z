from __future__ import annotations

from pathlib import Path

from src.muc5.evaluation_design import audit_balanced_focal_rows
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator
from src.muc5.psro_catalog import REV0092_ADMITTED_STRATEGY_ID, current_response_population
from src.muc5.transfer_stress import (
    audit_transfer_stress_panel,
    estimate_panel_rows,
    family_summary_rows,
    rev0092_admitted_strategy,
    rev0101_transfer_stress_panel,
    summarize_transfer_stress,
)
from src.muc5.psro import strategy_signature

ROOT = Path(__file__).resolve().parents[1]


def test_rev0101_panel_is_legal_unique_and_not_target_duplicate() -> None:
    target = rev0092_admitted_strategy(ROOT)
    panel = rev0101_transfer_stress_panel()
    audit = audit_transfer_stress_panel(panel, root=ROOT, focal=target)
    assert audit["passed"], audit
    assert audit["entries"] >= 12
    assert audit["families"]["branch_frontier"] >= 4
    assert audit["families"]["counter_control"] >= 4
    assert not audit["duplicate_focal"]
    assert target.strategy_id == REV0092_ADMITTED_STRATEGY_ID
    population_signatures = {strategy_signature(strategy) for strategy in current_response_population(ROOT / "data" / "seed_decks.json")}
    assert all(strategy_signature(entry.strategy) not in population_signatures for entry in panel)


def test_rev0101_transfer_summary_uses_nonself_opponents() -> None:
    target = rev0092_admitted_strategy(ROOT)
    panel = rev0101_transfer_stress_panel()[:2]
    evaluator = EmpiricalGameEvaluator()
    config = EmpiricalEvaluationConfig(life_totals=(20,), reps=1, max_decisions=700, base_seed=110011)
    estimates = []
    rows = []
    for entry in panel:
        estimate, game_rows = evaluator.evaluate_focal_pair(target, entry.strategy, config, stage="unit_rev0101")
        estimates.append(estimate)
        rows.extend(game_rows)
    summary = summarize_transfer_stress(target.strategy_id, panel, estimates)
    assert summary.panel_size == 2
    assert summary.total_games == 8
    assert 0.0 <= summary.min_mean_score <= 1.0
    assert summary.weakest_ci_opponent in {entry.strategy.strategy_id for entry in panel}
    design = audit_balanced_focal_rows(rows, expected_life_totals=(20,), expected_reps=1)
    assert design["passed"], design


def test_rev0101_transfer_rows_carry_family_metadata() -> None:
    target = rev0092_admitted_strategy(ROOT)
    panel = rev0101_transfer_stress_panel()[:3]
    evaluator = EmpiricalGameEvaluator()
    config = EmpiricalEvaluationConfig(life_totals=(20,), reps=1, max_decisions=700, base_seed=110021)
    estimates = [evaluator.evaluate_focal_pair(target, entry.strategy, config, stage="unit_rev0101")[0] for entry in panel]
    rows = estimate_panel_rows(estimates, panel, stage="unit_rev0101")
    families = family_summary_rows(estimates, panel)
    assert len(rows) == 3
    assert {row["stage"] for row in rows} == {"unit_rev0101"}
    assert all("stress_family" in row and "rationale" in row for row in rows)
    assert families
    assert all("confidence_floor_cleared" in row for row in families)
