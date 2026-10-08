from src.muc5.payoff import StrategyBundle
from src.muc5.deckspace import DeckVector
from src.muc5.terminal_life_cell_claim import (
    focused_life_cell_specs,
    life_cell_agenda_from_matchup_claim,
    life_cell_claim_gate,
    life_cell_summary_rows,
)


def _deck():
    return DeckVector(40, 24, 8, 4, 2, 2)


def test_life_cell_agenda_splits_life_sensitive_claim():
    claims = [{
        "target": "a",
        "opponent": "b",
        "claim_label": "life_sensitive_matchup_claim_candidate",
        "games": 160,
        "avg_score": 0.7,
        "total_score_lcb_95": 0.59,
        "life_delta_high_minus_low": 0.2,
        "abs_life_delta": 0.2,
    }]
    cells = [
        {"target": "a", "opponent": "b", "starting_life": 20, "games": 80, "mean_score_draw_half": 0.6, "score_lcb_95": 0.45, "score_ucb_95": 0.75, "terminal_win_rate": 0.6, "cell_signal": "uncertain"},
        {"target": "a", "opponent": "b", "starting_life": 40, "games": 80, "mean_score_draw_half": 0.8, "score_lcb_95": 0.65, "score_ucb_95": 0.95, "terminal_win_rate": 0.8, "cell_signal": "favored"},
    ]
    agenda = life_cell_agenda_from_matchup_claim(claims, cells)
    assert [r["starting_life"] for r in agenda] == [20, 40]
    assert agenda[0]["agenda_reason"] == "needs_life_cell_confirmation"
    assert agenda[1]["agenda_reason"] == "verify_strong_life_cell"


def test_focused_life_cell_specs_count_and_life():
    strategies = [
        StrategyBundle("a", "da", _deck(), "counter_happy", "land_band"),
        StrategyBundle("b", "db", _deck(), "threat_rush", "land_band_business"),
    ]
    agenda = [{"target": "a", "opponent": "b", "starting_life": 20}]
    specs = focused_life_cell_specs(strategies, agenda, simulator_revision="test", reps=3, base_seed=5)
    assert len(specs) == 12  # 2 target seats * 2 starting players * 3 reps
    assert {s.starting_life for s in specs} == {20}
    assert all("_c00_" in s.game_id for s in specs)


def test_life_cell_summary_and_gate():
    rows = []
    for i in range(160):
        rows.append({
            "focus_target": "a",
            "focus_opponent": "b",
            "starting_life": 20,
            "focus_target_score": 1.0 if i < 100 else 0.0,
            "focus_target_terminal_win": 1.0 if i < 100 else 0.0,
            "is_truncation": False,
            "loss_reason": "",
        })
    agenda = [{"target": "a", "opponent": "b", "starting_life": 20, "previous_games": 80, "previous_score": 0.55, "previous_score_lcb_95": 0.4}]
    cells = life_cell_summary_rows(rows, agenda)
    assert cells[0]["games"] == 160
    assert cells[0]["cell_signal"] == "life_cell_claim_candidate"
    gate = life_cell_claim_gate(rows, cells, cells, revision="test", cpp_summary={"skipped_events": 0, "mismatches": 0}, min_rows=100, min_new_cell_games=100, min_cumulative_cell_games=100)
    assert gate["passed"] is True
    assert gate["claim_cell_count"] == 1
