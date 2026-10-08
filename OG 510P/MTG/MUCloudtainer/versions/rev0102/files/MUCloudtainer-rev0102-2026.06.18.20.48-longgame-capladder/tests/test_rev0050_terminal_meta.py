from __future__ import annotations

from src.muc5.terminal_meta import (
    claim_ledger_rows,
    life_split_stability_rows,
    rank_disagreement_rows,
    terminal_meta_gate,
    terminal_meta_rank_rows,
)


def _rows():
    return [
        {"strategy0": "a", "strategy1": "b", "starting_life": 20, "p0_score": 1.0, "p1_score": 0.0, "p0_terminal_win": 1.0, "p1_terminal_win": 0.0, "is_truncation": False, "terminal_clean_game": True, "loss_reason": "player0_win"},
        {"strategy0": "b", "strategy1": "a", "starting_life": 20, "p0_score": 0.0, "p1_score": 1.0, "p0_terminal_win": 0.0, "p1_terminal_win": 1.0, "is_truncation": False, "terminal_clean_game": True, "loss_reason": "player1_win"},
        {"strategy0": "a", "strategy1": "b", "starting_life": 40, "p0_score": 0.5, "p1_score": 0.5, "p0_terminal_win": 0.0, "p1_terminal_win": 0.0, "is_truncation": False, "terminal_clean_game": True, "loss_reason": "decking_draw"},
        {"strategy0": "b", "strategy1": "a", "starting_life": 40, "p0_score": 0.5, "p1_score": 0.5, "p0_terminal_win": 0.0, "p1_terminal_win": 0.0, "is_truncation": False, "terminal_clean_game": True, "loss_reason": "decking_draw"},
    ]


def _aggregate():
    return [
        {"strategy0": "a", "strategy1": "b", "starting_life": 20, "games": 1, "p0_mean_score_draw_half": 1.0},
        {"strategy0": "b", "strategy1": "a", "starting_life": 20, "games": 1, "p0_mean_score_draw_half": 0.0},
        {"strategy0": "a", "strategy1": "b", "starting_life": 40, "games": 1, "p0_mean_score_draw_half": 0.5},
        {"strategy0": "b", "strategy1": "a", "starting_life": 40, "games": 1, "p0_mean_score_draw_half": 0.5},
    ]


def test_terminal_meta_rank_and_gate():
    meta = terminal_meta_rank_rows(_aggregate(), life_totals=(20, 40))
    assert {r["life_scope"] for r in meta} == {"all", "20", "40"}
    all_mass = sum(r["meta_rank_mass"] for r in meta if r["life_scope"] == "all")
    assert abs(all_mass - 1.0) < 1e-9
    gate = terminal_meta_gate(_rows(), _aggregate(), meta, min_raw_rows=4, min_aggregate_games=1)
    assert gate.passed
    assert gate.truncation_rows == 0


def test_life_stability_and_claim_ledger_shapes():
    life = life_split_stability_rows(_rows())
    assert {r["strategy"] for r in life} == {"a", "b"}
    assert all("abs_score_life_delta" in r for r in life)
    standings = [
        {"strategy": "a", "rank": 1, "mean_score_draw_half": 0.75},
        {"strategy": "b", "rank": 2, "mean_score_draw_half": 0.25},
    ]
    stat = [
        {"strategy": "a", "rank_by_lcb": 1, "games": 4, "score_lcb_95": 0.51, "mean_score_draw_half": 0.75, "claim_ready": True},
        {"strategy": "b", "rank_by_lcb": 2, "games": 4, "score_lcb_95": 0.10, "mean_score_draw_half": 0.25, "claim_ready": True},
    ]
    meta = terminal_meta_rank_rows(_aggregate(), life_totals=(20, 40))
    disagreements = rank_disagreement_rows(standings, stat, meta)
    ledger = claim_ledger_rows(standings, stat, meta, life)
    assert len(disagreements) == 2
    assert len(ledger) == 2
    assert {r["next_eval_hint"] for r in ledger}
