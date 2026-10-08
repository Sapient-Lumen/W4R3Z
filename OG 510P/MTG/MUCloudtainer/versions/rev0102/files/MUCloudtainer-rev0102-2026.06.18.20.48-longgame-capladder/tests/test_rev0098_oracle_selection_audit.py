from __future__ import annotations

from pathlib import Path

from src.muc5.oracle_selection_audit import (
    audit_oracle_selection_bias,
    default_branch_specs,
    read_score_rows,
    strategy_bundle_from_score_row,
    summarize_branch,
    top_holdout_strategy_rows,
)

ROOT = Path(__file__).resolve().parents[1]


def test_branch_specs_cover_four_response_oracles() -> None:
    specs = default_branch_specs()
    assert [spec.revision for spec in specs] == ["rev0094", "rev0095", "rev0096", "rev0097"]
    assert {spec.holdout_stage for spec in specs} == {"holdout"}
    assert any("generation0_training" in spec.screen_stages for spec in specs)


def test_selection_bias_audit_detects_learned_optimism_without_promotion() -> None:
    audit = audit_oracle_selection_bias(ROOT)
    aggregate = audit["aggregate"]
    assert aggregate["branches"] == 4
    assert aggregate["no_branch_cleared_holdout_ci_threshold"] is True
    assert aggregate["branch_best_screen_not_heldout_count"] >= 1
    assert aggregate["worst_branch_best_screen_to_holdout_gap_branch"] == "learned_response_rev0097"
    worst = aggregate["worst_mean_optimism_pair"]
    assert worst["branch_id"] == "learned_response_rev0097"
    assert worst["mean_optimism"] > 0.25


def test_top_holdout_rows_are_reconstructible_strategy_bundles() -> None:
    rows = top_holdout_strategy_rows(ROOT)
    assert {row["branch_id"] for row in rows} == {
        "finite_catalog_rev0094",
        "gameplay_map_elites_rev0095",
        "frozen_mlp_rev0096",
        "learned_response_rev0097",
    }
    strategies = [strategy_bundle_from_score_row(row) for row in rows]
    assert all(strategy.deck.size in {40, 60} for strategy in strategies)
    assert all(strategy.agent_name for strategy in strategies)


def test_summarize_branch_pairs_screen_to_holdout() -> None:
    spec = next(spec for spec in default_branch_specs() if spec.revision == "rev0096")
    rows = read_score_rows(ROOT, spec)
    summary, pairs = summarize_branch(spec, rows)
    assert summary["screen_rows"] == 40
    assert summary["holdout_rows"] == 5
    assert len(pairs) == 5
    assert summary["best_holdout_mean"] < 0.5
