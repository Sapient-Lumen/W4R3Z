from __future__ import annotations

from random import Random

from src.muc5.decision import build_decision_frame
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.imitation import action_ranker_feature_names
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from src.muc5.ranker_policy import MLPActionRankerAgent, MLPActionRankerModel
from src.muc5.strategy_sets import mlp_ranker_probe_bundles, mulligan_policy_gate_bundles


def zero_mlp_model() -> MLPActionRankerModel:
    names = action_ranker_feature_names()
    hidden = 3
    return MLPActionRankerModel(
        model_id="test_zero_mlp",
        feature_names=names,
        hidden_weights=tuple(tuple(0.0 for _ in range(hidden)) for _ in names),
        hidden_bias=(0.0, 0.0, 0.0),
        output_weights=(0.0, 0.0, 0.0),
        output_bias=0.0,
        activation="relu",
        source_revision="test",
    )


def test_mlp_ranker_model_scores_and_agent_picks_legal_index():
    deck = DeckVector(40, 22, 8, 6, 3, 1)
    state = start_game(deck, deck, seed=232301, record_log=False)
    frame = build_decision_frame(state)
    model = zero_mlp_model()
    agent = MLPActionRankerAgent(model)
    idx = agent.choose_action_index(frame, Random(2323))
    assert 0 <= idx < frame.action_count
    assert isinstance(model.score_action(frame, frame.legal_actions[idx]), float)


def test_rev0023_strategy_sets_keep_mulligan_axis_visible():
    bundles = mulligan_policy_gate_bundles("data/seed_decks.json")
    assert len(bundles) == 9
    policies = {b.mulligan_policy for b in bundles}
    assert policies == {POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS}
    shells = {b.strategy_id.rsplit("_", 1)[0] for b in bundles}
    assert len(shells) == 3


def test_rev0023_mlp_probe_population_contains_mlp_and_baselines():
    bundles = mlp_ranker_probe_bundles("data/seed_decks.json")
    agents = {b.agent_name for b in bundles}
    assert "mlp_ranker_rev0023" in agents
    assert "mlp_ranker_blend_threat_rev0023" in agents
    assert "linear_ranker_rev0021" in agents
    assert "counter_happy" in agents
    assert len(bundles) == 8
