from __future__ import annotations

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_label_compare import collect_matched_action_label_comparison
from src.muc5.cpp_segment import build_nochoice_segment_specs
from src.muc5.cpp_segment_benchmark import benchmark_cpp_segment_vs_one_action
from src.muc5.strategy_sets import mapelite_mulligan_variant_bundles, outcome_ranker_probe_bundles


def test_matched_label_comparison_uses_same_situations_and_actions():
    strategies = outcome_ranker_probe_bundles("data/seed_decks.json")[:2]
    specs = build_action_counterfactual_specs(
        strategies,
        life_totals=(20,),
        base_seed=937000,
        max_decisions=240,
        limit_games=2,
    )
    candidate_rows, branch_rows, comparison_rows, transition_rows, summary = collect_matched_action_label_comparison(
        specs,
        revision="rev0037_test",
        max_situations=2,
        max_actions_per_frame=3,
        sample_high_action_frames=True,
        branch_action_budget=4,
        budget_rng_seed=937,
        fixed_rollouts_per_action=2,
        adaptive_base_rollouts_per_action=1,
        branch_max_decisions=180,
    )
    assert summary.sampled_situations >= 1
    assert summary.cpp_mismatches == 0
    assert summary.cpp_skipped_transitions == 0
    assert len(comparison_rows) == summary.sampled_situations
    methods = {row["method"] for row in candidate_rows}
    assert methods == {"fixed_equal", "adaptive_race"}
    for row in comparison_rows:
        sid = row["situation_id"]
        fixed_actions = {r["action"] for r in candidate_rows if r["situation_id"] == sid and r["method"] == "fixed_equal"}
        adaptive_actions = {r["action"] for r in candidate_rows if r["situation_id"] == sid and r["method"] == "adaptive_race"}
        assert fixed_actions == adaptive_actions
    assert len(branch_rows) >= summary.sampled_situations * 2
    assert len(transition_rows) >= len(branch_rows)


def test_cpp_segment_benchmark_smoke():
    strategies = mapelite_mulligan_variant_bundles("data/rev0014_map_elites_archive.csv", limit_cells=1)[:2]
    specs = build_nochoice_segment_specs(
        strategies,
        simulator_revision="rev0037_test",
        life_totals=(20,),
        reps=1,
        base_seed=937500,
        max_decisions=120,
        limit_pairs=2,
    )
    game_rows, segment_rows, summary = benchmark_cpp_segment_vs_one_action(specs, revision="rev0037_test")
    assert len(game_rows) == len(specs)
    assert summary.segment_mismatches == 0
    assert summary.skipped_events == 0
    assert summary.forced_actions >= summary.segments
    assert len(segment_rows) == summary.segments
