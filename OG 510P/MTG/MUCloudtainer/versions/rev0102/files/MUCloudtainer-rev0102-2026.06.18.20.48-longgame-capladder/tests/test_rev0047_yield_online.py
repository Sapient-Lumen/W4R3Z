from __future__ import annotations

from src.muc5.action_yield_collect import collect_yield_screen_online_counterfactuals
from src.muc5.action_yield_screen import YieldScreenModel
from src.muc5.ranker_policy import train_linear_action_ranker_from_candidate_rows
from src.muc5.imitation import action_ranker_feature_names
from src.muc5.strategy_sets import yield_counterfactual_action_ranker_bundles


def _dummy_yield_model() -> YieldScreenModel:
    names = ("action_count", "screen_unique_votes", "screen_vote_entropy_proxy", "profile_spread", "ranker_spread", "screen_score", "starting_life_40", "starting_player")
    return YieldScreenModel(
        revision="test",
        feature_names=names,
        mean=tuple(0.0 for _ in names),
        scale=tuple(1.0 for _ in names),
        coef=tuple(0.0 for _ in names),
        intercept=0.0,
        train_rows=0,
        holdout_rows=0,
        metrics={},
        source_files=(),
    )


def test_yield_online_empty_specs_are_auditable():
    pool, ranks, selected, candidates, branches, allocations, votes, cpp_rows, summary = collect_yield_screen_online_counterfactuals(
        [],
        yield_model=_dummy_yield_model(),
        revision="revtest",
        selected_situations=2,
    )
    assert pool == []
    assert ranks == []
    assert selected == []
    assert candidates == []
    assert branches == []
    assert allocations == []
    assert votes == []
    assert cpp_rows == []
    assert summary.revision == "revtest"
    assert summary.cpp_mismatches == 0


def test_generic_linear_ranker_training_helper_on_tiny_rows():
    names = list(action_ranker_feature_names())
    rows = []
    for sid in ["s0", "s1", "s2", "s3"]:
        for idx in [0, 1]:
            row = {name: 0.0 for name in names}
            row.update({
                "situation_id": sid,
                "action_index": idx,
                "mean_actor_score": float(idx),
                "is_best_action": int(idx == 1),
                "label_confidence_proxy": 0.8,
                "branched_subset": 0,
                "branch_rollouts": 2,
                "screen_unique_votes": 2,
                "situation_best_margin": 1.0,
            })
            row[names[0]] = float(idx)
            rows.append(row)
    model, metrics, coef_rows, pred_rows = train_linear_action_ranker_from_candidate_rows(
        rows,
        model_id="tiny_test_ranker",
        source_revision="revtest",
        seed=7,
    )
    assert model.model_id == "tiny_test_ranker"
    assert len(model.feature_names) == len(names)
    assert metrics["training_rows"] > 0
    assert coef_rows
    assert pred_rows


def test_rev0047_strategy_panel_names_are_generic_counterfactual_aliases():
    bundles = yield_counterfactual_action_ranker_bundles("data/seed_decks.json")
    names = {b.agent_name for b in bundles}
    assert "counterfactual_linear_ranker_rev0047" in names
    assert "counterfactual_ranker_blend_counter_rev0047" in names
    assert "counterfactual_ranker_blend_threat_rev0047" in names
