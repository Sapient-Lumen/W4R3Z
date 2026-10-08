from __future__ import annotations

from pathlib import Path

from src.muc5.ranker_policy import counterfactual_ranker_model_path, load_counterfactual_ranker_agent
from src.muc5.public_agents import make_public_agent
from src.muc5.strategy_sets import scaled_counterfactual_action_ranker_bundles
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.decision import build_decision_frame

ROOT = Path(__file__).resolve().parents[1]


def test_rev0034_generic_counterfactual_model_path():
    assert counterfactual_ranker_model_path("rev0034").name == "rev0034_counterfactual_action_ranker_model.json"
    assert counterfactual_ranker_model_path("0034").name == "rev0034_counterfactual_action_ranker_model.json"


def test_rev0034_strategy_bundle_panel_names():
    bundles = scaled_counterfactual_action_ranker_bundles(ROOT / "data" / "seed_decks.json")
    agents = {b.agent_name for b in bundles}
    assert "counterfactual_linear_ranker_rev0034" in agents
    assert "counterfactual_ranker_blend_counter_rev0034" in agents
    assert len(bundles) == 8


def test_rev0034_public_agent_factory_after_model_exists():
    path = ROOT / "data" / "rev0034_counterfactual_action_ranker_model.json"
    if not path.exists():
        # Allows pytest to run before the rev0034 build script; the archive audit
        # requires the model after generation.
        return
    agent = make_public_agent("counterfactual_linear_ranker_rev0034")
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    state = start_game(deck, deck, seed=34034, mulligan_policy="land_band", record_log=False)
    frame = build_decision_frame(state)
    idx = agent.choose_action_index(frame, __import__("random").Random(1))
    assert 0 <= idx < frame.action_count
    direct = load_counterfactual_ranker_agent("rev0034")
    idx2 = direct.choose_action_index(frame, __import__("random").Random(1))
    assert 0 <= idx2 < frame.action_count
