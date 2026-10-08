from random import Random

import pytest

from src.muc5.agents import HeuristicAgent, play_agent_game, play_public_agent_game
from src.muc5.cards import CARD_JACE
from src.muc5.decision import PublicHeuristicAgent, build_decision_frame, apply_decision_index
from src.muc5.deckspace import DeckVector
from src.muc5.engine import PendingChoice, start_game
from src.muc5.fairness import audit_observation_shape, all_checks_pass
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.payoff import mulligan_strategy_bundles, play_strategy_pair


def test_jace_plus2_pending_choice_is_redacted_for_non_actor():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    state = start_game(deck, deck, seed=9009, mulligan_policy=POLICY_LAND_BAND)
    state.pending_choice = PendingChoice(0, "jace_plus2", {"target_player": 1, "seen_top_card": CARD_JACE, "resume": "MAIN"})
    actor_obs = state.observation(0)
    non_actor_obs = state.observation(1)
    assert actor_obs["pending_choice_data"]["seen_top_card"] == CARD_JACE
    assert non_actor_obs["pending_choice_data"]["redacted"] is True
    assert "seen_top_card" not in non_actor_obs["pending_choice_data"]
    assert all_checks_pass(audit_observation_shape(state, 0))
    assert all_checks_pass(audit_observation_shape(state, 1))


def test_decision_frame_fastpath_rejects_stale_reuse():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    state = start_game(deck, deck, seed=9010, mulligan_policy=POLICY_LAND_BAND)
    frame = build_decision_frame(state)
    idx = PublicHeuristicAgent().choose_action_index(frame, Random(1))
    apply_decision_index(state, frame, idx, Random(1))
    with pytest.raises(ValueError):
        apply_decision_index(state, frame, idx, Random(1))


def test_public_agent_game_runs_without_omniscient_agent_interface():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    _, result = play_public_agent_game(deck, deck, PublicHeuristicAgent(), PublicHeuristicAgent(), seed=9011, max_decisions=30, record_log=False)
    assert result.decisions >= 1


def test_payoff_pair_supports_seat_specific_mulligan_policies():
    bundles = mulligan_strategy_bundles("data/seed_decks.json")
    left = next(b for b in bundles if b.strategy_id.endswith("keep_always"))
    right = next(b for b in bundles if b.strategy_id.endswith("land_band_business"))
    row = play_strategy_pair(left, right, seed=9012, starting_player=0, starting_life=20, max_decisions=40)
    assert row["mulligan0"] == "keep_always"
    assert row["mulligan1"] == "land_band_business"
    assert "is_truncation" in row
