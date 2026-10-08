from src.muc5.terminal_deep import (
    annotate_focus_rows,
    deep_claim_gate,
    deep_target_summary_rows,
    strategy_ids_from_claims,
    targeted_strategy_pair_specs,
)
from src.muc5.strategy_sets import terminal_clean_yield_ranker_bundles


def test_strategy_ids_from_claims_prefers_agenda_labels():
    claims = [
        {"strategy": "a", "claim_label": "terminal_clean_signal_only", "meta_rank_mass": 0.9, "mean_score_draw_half": 0.8, "meta_rank": 1},
        {"strategy": "b", "claim_label": "life_sensitive_candidate", "meta_rank_mass": 0.1, "mean_score_draw_half": 0.6, "meta_rank": 2},
        {"strategy": "c", "claim_label": "robust_candidate", "meta_rank_mass": 0.2, "mean_score_draw_half": 0.7, "meta_rank": 3},
    ]
    assert strategy_ids_from_claims(claims, top_n=2) == ["b", "c"]


def test_targeted_specs_include_only_pairs_touching_target():
    strategies = terminal_clean_yield_ranker_bundles("data/seed_decks.json")
    specs = targeted_strategy_pair_specs(strategies, target_ids=[strategies[0].strategy_id], simulator_revision="revtest", reps=1, life_totals=(20,), max_decisions=10)
    assert specs
    assert all(s.strategy0 == strategies[0].strategy_id or s.strategy1 == strategies[0].strategy_id for s in specs)
    # 8 left/right ordered pairs touching one target = 15, times 2 starting players.
    assert len(specs) == 30


def test_deep_summaries_and_gate():
    rows = []
    for i in range(100):
        rows.append({
            "strategy0": "a", "strategy1": "b", "starting_life": 20 if i % 2 == 0 else 40,
            "p0_score": 1.0, "p1_score": 0.0, "p0_terminal_win": 1.0, "p1_terminal_win": 0.0,
            "is_truncation": False, "loss_reason": "terminal",
        })
    summary = deep_target_summary_rows(rows, target_ids=["a"], previous_claim_rows=[])
    assert summary[0]["strategy"] == "a"
    assert summary[0]["games"] == 100
    assert summary[0]["deep_claim_label"] in {"deep_robust_signal", "deep_life_sensitive_signal", "deep_field_signal"}
    gate = deep_claim_gate(rows, revision="revtest", target_ids=["a"], cpp_summary={"mismatches": 0, "skipped_events": 0}, min_rows=50, min_target_games=50)
    assert gate.passed
    annotated = annotate_focus_rows(rows[:1], ["a"])
    assert annotated[0]["focus_kind"] == "target_as_p0"
