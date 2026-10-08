from __future__ import annotations

from random import Random

from src.muc5.code_policy import code_policy_catalog, make_code_policy_agent, smoke_lint_code_policy
from src.muc5.decision import build_decision_frame
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.public_agents import make_public_agent, PublicProfileAgent


def test_code_policy_agents_choose_legal_indices():
    deck = DeckVector(40, 20, 8, 6, 4, 2)
    state = start_game(deck, deck, seed=1313, starting_life=20, record_log=False)
    frame = build_decision_frame(state)
    assert frame.action_count > 0
    for item in code_policy_catalog():
        agent = make_code_policy_agent(item["policy_id"])
        idx = agent.choose_action_index(frame, Random(7))
        assert 0 <= idx < frame.action_count
        assert agent.name == item["policy_id"]


def test_code_policy_factory_is_wired_through_public_agent_factory():
    agent = make_public_agent("code_jace_lock_rev0013")
    assert agent.name == "code_jace_lock_rev0013"


def test_public_agent_choice_effect_scoring_refactor():
    # Rev0013 fixes a public-agent typo where CHOOSE_FOR_EFFECT actions were not scored.
    agent = PublicProfileAgent("heuristic")
    obs = {"frame": "CHOICE", "player": 0, "own_hand": {}, "public_self": {}, "public_opponent": {}, "starting_life": 20}
    island_discard = type("A", (), {"kind": "CHOOSE_FOR_EFFECT", "params": {"effect": "discard", "discard": "Island"}})()
    force_discard = type("A", (), {"kind": "CHOOSE_FOR_EFFECT", "params": {"effect": "discard", "discard": "ForceOfWill"}})()
    assert agent.score_action(obs, island_discard) > agent.score_action(obs, force_discard)


def test_smoke_lint_code_policy_contract():
    deck = DeckVector(40, 20, 8, 6, 4, 2)
    frames = [build_decision_frame(start_game(deck, deck, seed=21 + i, starting_life=20, record_log=False)) for i in range(2)]
    ok, errors = smoke_lint_code_policy(make_code_policy_agent("code_overlord_clock_rev0013"), frames)
    assert ok, errors
