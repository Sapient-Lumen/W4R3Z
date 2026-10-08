from __future__ import annotations

from random import Random

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_hard_frame import collect_hard_frame_hybrid_comparison, hard_frame_screen_score
from src.muc5.strategy_sets import outcome_ranker_probe_bundles


def test_hard_frame_screen_score_prefers_high_disagreement_high_action():
    easy, easy_bonus, easy_reason = hard_frame_screen_score(
        action_count=2,
        unique_votes=1,
        vote_entropy_proxy=0.0,
        profile_spread=0.0,
        ranker_spread=0.0,
        high_action_threshold=5,
    )
    hard, hard_bonus, hard_reason = hard_frame_screen_score(
        action_count=12,
        unique_votes=4,
        vote_entropy_proxy=0.6,
        profile_spread=0.5,
        ranker_spread=0.4,
        high_action_threshold=5,
    )
    assert 0.0 <= easy <= 1.0
    assert 0.0 <= hard <= 1.0
    assert hard > easy
    assert easy_bonus == 0.0
    assert hard_bonus == 1.0
    assert "high_action" in hard_reason
    assert "public_disagreement" in hard_reason


def test_collect_hard_frame_hybrid_comparison_smoke():
    bundles = outcome_ranker_probe_bundles("data/seed_decks.json")
    specs = build_action_counterfactual_specs(
        bundles[:4],
        life_totals=(20,),
        base_seed=410499,
        max_decisions=180,
        limit_games=4,
    )
    selected, candidates, methods, branches, votes, transitions, summary = collect_hard_frame_hybrid_comparison(
        specs,
        revision="rev0041_test",
        screen_agent_names=("counter_happy", "threat_rush", "patient"),
        max_behavior_frames=40,
        max_situations=2,
        high_action_threshold=4,
        max_actions_per_frame=2,
        branch_action_budget=4,
        branch_rollouts_per_action=1,
        branch_max_decisions=100,
        ranker_revision="rev0034",
    )
    assert summary.selected_situations >= 1
    assert selected
    assert candidates
    assert methods
    assert branches
    assert votes
    assert transitions
    assert summary.cpp_mismatches == 0
    assert {"unscreened_budget", "screened_vote_budget", "hybrid_vote_diverse_ranker"}.issubset({str(r["method"]) for r in methods})
