from __future__ import annotations

from src.muc5.terminal_life_cell_replicate import (
    dimension_stability_rows,
    holdout_cell_rows,
    life_cell_replication_agenda,
    life_cell_replication_gate,
    replication_comparison_rows,
)


def test_life_cell_replication_agenda_prefers_claim_candidates():
    rows = [
        {"target":"a","opponent":"b","starting_life":20,"games":208,"mean_score_draw_half":0.63,"score_lcb_95":0.54,"score_ucb_95":0.72,"cell_signal":"life_cell_claim_candidate"},
        {"target":"a","opponent":"b","starting_life":40,"games":208,"mean_score_draw_half":0.78,"score_lcb_95":0.69,"score_ucb_95":0.87,"cell_signal":"life_cell_claim_candidate"},
        {"target":"x","opponent":"y","starting_life":20,"games":20,"mean_score_draw_half":0.90,"score_lcb_95":0.40,"score_ucb_95":1.0,"cell_signal":"uncertain_life_cell"},
    ]
    agenda = life_cell_replication_agenda(rows, top_n_cells=2)
    assert len(agenda) == 2
    assert {a["starting_life"] for a in agenda} == {20, 40}
    assert all(a["agenda_reason"] == "independent_holdout_replication" for a in agenda)


def test_holdout_and_comparison_labels():
    holdout = holdout_cell_rows([
        {"target":"a","opponent":"b","starting_life":20,"games":128,"mean_score_draw_half":0.70,"score_lcb_95":0.58,"score_ucb_95":0.82,"terminal_win_rate":0.7,"terminal_win_lcb_95":0.5,"terminal_win_ucb_95":0.8,"truncations":0},
    ])
    assert holdout[0]["holdout_label"] == "holdout_replicated_candidate"
    comp = replication_comparison_rows([
        {"target":"a","opponent":"b","starting_life":20,"games":208,"mean_score_draw_half":0.63,"score_lcb_95":0.54,"score_ucb_95":0.72,"cell_signal":"life_cell_claim_candidate"},
    ], holdout)
    assert comp[0]["combined_games"] == 336
    assert comp[0]["replication_label"] == "replicated_life_cell_claim_candidate"


def test_dimension_stability_and_gate():
    dim = dimension_stability_rows([
        {"target":"a","opponent":"b","starting_life":20,"dimension":"target_seat","value":"0","games":64,"mean_score_draw_half":0.65},
        {"target":"a","opponent":"b","starting_life":20,"dimension":"target_seat","value":"1","games":64,"mean_score_draw_half":0.60},
    ])
    assert dim and dim[0]["dimension_label"] == "dimension_stable_smoke"
    gate = life_cell_replication_gate(
        raw_rows=[{"is_truncation":False,"loss_reason":""}] * 192,
        holdout_rows=[{"holdout_games":96}, {"holdout_games":96}],
        comparison_rows=[{"replication_label":"replicated_life_cell_claim_candidate"}],
        revision="revtest",
        cpp_summary={"skipped_events":0,"mismatches":0},
        replay_results=[{"passed":True}],
        min_raw_rows=160,
        min_holdout_games_per_cell=96,
    )
    assert gate["passed"] is True
