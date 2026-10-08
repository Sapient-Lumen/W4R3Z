from src.muc5.terminal_matchup_claim import concrete_claim_agenda_from_confirmation, matchup_claim_rows, target_dimension_rows, matchup_claim_gate


def test_concrete_claim_agenda_prefers_favored_cell():
    rows = [
        {"target": "a", "opponent": "b", "confirmation_label": "field_watch", "avg_score": 0.70, "min_score": 0.62, "games": 96, "abs_life_delta": 0.02, "confluence_rank": 2},
        {"target": "c", "opponent": "d", "confirmation_label": "favored_cell_signal", "avg_score": 0.66, "min_score": 0.60, "games": 96, "abs_life_delta": 0.01, "confluence_rank": 1},
    ]
    agenda = concrete_claim_agenda_from_confirmation(rows, top_n=1)
    assert agenda[0]["target"] == "c"
    assert agenda[0]["dossier_rank"] == 1


def test_matchup_claim_rows_can_label_candidate():
    agenda = [{"target": "a", "opponent": "b", "dossier_rank": 1, "source_confirmation_label": "favored_cell_signal"}]
    cells = [
        {"target": "a", "opponent": "b", "starting_life": 20, "games": 96, "mean_score_draw_half": 0.66, "score_lcb_95": 0.54, "terminal_win_rate": 0.66},
        {"target": "a", "opponent": "b", "starting_life": 40, "games": 96, "mean_score_draw_half": 0.70, "score_lcb_95": 0.58, "terminal_win_rate": 0.70},
    ]
    dims = [
        {"target": "a", "opponent": "b", "dimension": "target_seat", "mean_score_draw_half": 0.68},
        {"target": "a", "opponent": "b", "dimension": "target_seat", "mean_score_draw_half": 0.66},
        {"target": "a", "opponent": "b", "dimension": "starting_player", "mean_score_draw_half": 0.69},
        {"target": "a", "opponent": "b", "dimension": "starting_player", "mean_score_draw_half": 0.65},
    ]
    claims = matchup_claim_rows(cells, dims, agenda, min_total_games=160, min_life_games=80)
    assert claims[0]["claim_label"] == "concrete_matchup_claim_candidate"
    assert claims[0]["games"] == 192


def test_dimension_rows_and_gate():
    rows = []
    for life in (20, 40):
        for seat in (0, 1):
            rows.append({"focus_target": "a", "focus_opponent": "b", "starting_life": life, "focus_target_seat": seat, "starting_player": 0, "focus_target_score": 1.0, "focus_target_terminal_win": 1.0, "is_truncation": False})
    dims = target_dimension_rows(rows, [{"target": "a", "opponent": "b"}])
    assert any(r["dimension"] == "all" and r["games"] == 4 for r in dims)
    gate = matchup_claim_gate(rows, [{"claim_label": "concrete_matchup_claim_candidate"}], revision="revtest", cpp_summary={"skipped_events": 0, "mismatches": 0}, min_rows=4)
    assert gate["passed"] is True
