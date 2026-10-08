from src.muc5.terminal_cell_confirm import cell_confluence_agenda_from_retest, cell_confirmation_rows, cell_confirmation_gate


def test_confluence_agenda_prefers_favored_cells():
    cells = [
        {"target":"A","opponent":"B","starting_life":20,"games":32,"mean_score_draw_half":0.75,"score_lcb_95":0.55,"cell_signal":"favored"},
        {"target":"A","opponent":"B","starting_life":40,"games":32,"mean_score_draw_half":0.70,"score_lcb_95":0.52,"cell_signal":"favored"},
        {"target":"C","opponent":"D","starting_life":20,"games":32,"mean_score_draw_half":0.55,"score_lcb_95":0.31,"cell_signal":"uncertain"},
        {"target":"C","opponent":"D","starting_life":40,"games":32,"mean_score_draw_half":0.50,"score_lcb_95":0.26,"cell_signal":"uncertain"},
    ]
    agenda = cell_confluence_agenda_from_retest(cells, top_n=1)
    assert agenda[0]["target"] == "A"
    assert agenda[0]["agenda_reason"] == "both_lives_favored"


def test_confirmation_gate_accepts_terminal_clean_favored_panel():
    cells = [
        {"target":"A","opponent":"B","starting_life":20,"games":48,"mean_score_draw_half":0.72,"score_lcb_95":0.55,"score_ucb_95":0.90,"cell_signal":"favored"},
        {"target":"A","opponent":"B","starting_life":40,"games":48,"mean_score_draw_half":0.69,"score_lcb_95":0.52,"score_ucb_95":0.86,"cell_signal":"favored"},
    ]
    conf = cell_confirmation_rows(cells, [{"target":"A","opponent":"B","previous_avg_score":0.70,"previous_life_delta_high_minus_low":0.0}])
    assert conf[0]["confirmation_label"] == "confirmed_stable_favored"
    rows = [{"is_truncation": False, "loss_reason": "player_0_lost"} for _ in range(250)]
    gate = cell_confirmation_gate(rows, [{"target":"A","opponent":"B"}], conf, revision="test", cpp_summary={"mismatches":0,"skipped_events":0}, min_rows=200, min_cell_games=48)
    assert gate.passed
    assert gate.favored_or_confirmed_cells == 1
