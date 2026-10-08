from src.muc5.terminal_matchup import life_flip_gate, life_flip_matchups_from_target_pairs, life_flip_retest_rows


def test_life_flip_matchups_select_biggest_split():
    rows = [
        {"target": "a", "opponent": "b", "starting_life": 20, "games": 8, "mean_score_draw_half": 0.2},
        {"target": "a", "opponent": "b", "starting_life": 40, "games": 8, "mean_score_draw_half": 0.8},
        {"target": "a", "opponent": "c", "starting_life": 20, "games": 8, "mean_score_draw_half": 0.4},
        {"target": "a", "opponent": "c", "starting_life": 40, "games": 8, "mean_score_draw_half": 0.5},
    ]
    selected = life_flip_matchups_from_target_pairs(rows, top_n=1)
    assert selected[0]["target"] == "a"
    assert selected[0]["opponent"] == "b"
    assert abs(selected[0]["previous_life_delta_high_minus_low"] - 0.6) < 1e-12


def test_life_flip_retest_label_confirmed():
    cells = [
        {"matchup_index": 0, "target": "a", "opponent": "b", "starting_life": 20, "games": 16, "mean_score_draw_half": 0.25},
        {"matchup_index": 0, "target": "a", "opponent": "b", "starting_life": 40, "games": 16, "mean_score_draw_half": 0.75},
    ]
    prev = [{"previous_life_delta_high_minus_low": 0.5}]
    flips = life_flip_retest_rows(cells, prev)
    assert flips[0]["life_flip_label"] == "confirmed_life_split_signal"


def test_life_flip_gate_rejects_truncation():
    game_rows = [{"is_truncation": True, "loss_reason": "max_decisions_reached"}]
    gate = life_flip_gate(game_rows, [], [], revision="x", cpp_summary={"mismatches": 0, "skipped_events": 0}, min_rows=1)
    assert not gate.passed
    assert "truncation" in gate.errors[0]
