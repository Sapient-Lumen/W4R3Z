from __future__ import annotations

from src.muc5.action_hard_racing import HardFrameOnlineRacingSummary, collect_hard_frame_online_racing
from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.strategy_sets import outcome_ranker_probe_bundles


def test_rev0043_summary_dataclass_roundtrip() -> None:
    s = HardFrameOnlineRacingSummary(
        revision="revtest",
        behavior_games=1,
        behavior_decisions=2,
        choice_frames_seen=2,
        candidate_frames_seen=1,
        frames_with_disagreement=1,
        selected_situations=1,
        high_action_selected=1,
        subset_situations=1,
        candidate_actions=3,
        branch_games=5,
        base_rollouts_per_action=1,
        max_extra_rollouts_per_situation=2,
        adaptive_extra_rollouts=2,
        early_stops=1,
        branch_terminal_games=5,
        branch_truncations=0,
        cpp_checked_transitions=10,
        cpp_skipped_transitions=0,
        cpp_mismatches=0,
        mean_action_count=5.0,
        mean_branched_action_count=3.0,
        mean_rollouts_per_action=1.6,
        decisive_situations=1,
        decisive_per_100_rollouts=20.0,
        mean_best_minus_chosen=0.5,
        behavior_chosen_best_rate=0.0,
        mean_label_confidence_proxy=0.6,
        mean_selected_screen_score=0.5,
        mean_vote_entropy_proxy=0.5,
        mean_profile_spread=0.5,
        mean_ranker_spread=0.5,
        ranker_revision="rev0034",
        ranker_available_frames_seen=1,
        tool_status={},
        mismatch_examples=(),
        skipped_examples=(),
    )
    d = s.as_dict()
    assert d["revision"] == "revtest"
    assert d["decisive_per_100_rollouts"] == 20.0


def test_rev0043_tiny_online_racing_runs() -> None:
    bundles = outcome_ranker_probe_bundles("data/seed_decks.json")[:2]
    specs = build_action_counterfactual_specs(bundles, life_totals=(20,), base_seed=4304399, max_decisions=120, limit_games=2)
    selected, candidates, branches, allocations, votes, transitions, summary = collect_hard_frame_online_racing(
        specs,
        revision="revtest43",
        max_behavior_frames=40,
        max_situations=1,
        branch_action_budget=3,
        max_actions_per_frame=2,
        base_rollouts_per_action=1,
        max_extra_rollouts_per_situation=1,
        branch_max_decisions=80,
        min_unique_screen_votes=1,
    )
    assert summary.behavior_games == 2
    assert summary.cpp_mismatches == 0
    assert summary.cpp_skipped_transitions == 0
    assert len(allocations) == summary.branch_games
    assert len(transitions) == summary.cpp_checked_transitions
    if summary.selected_situations:
        assert selected
        assert candidates
        assert branches
