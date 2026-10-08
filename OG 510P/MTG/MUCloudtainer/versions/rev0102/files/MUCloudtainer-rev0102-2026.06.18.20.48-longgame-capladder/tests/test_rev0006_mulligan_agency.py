from random import Random

from src.muc5.action_schema import Action
from src.muc5.cards import CARD_ISLAND, CARD_JACE
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.env import MUC5SlotEnv
from src.muc5.mulligan import (
    MULLIGAN_KEEP,
    MULLIGAN_TAKE,
    POLICY_LAND_BAND,
    MulliganPolicy,
    RuleMulliganAgent,
    legal_bottom_actions,
    legal_mulligan_actions,
    london_mulligan_agent_opening_hand,
)


def seed_deck() -> DeckVector:
    return DeckVector(40, 24, 6, 4, 3, 3)


def test_mulligan_keep_or_take_actions_are_explicit():
    hand = {CARD_ISLAND: 2, CARD_JACE: 5}
    actions = legal_mulligan_actions(hand, mulligans_taken=0)
    assert MULLIGAN_KEEP in actions
    assert MULLIGAN_TAKE in actions


def test_bottom_actions_are_card_specific():
    hand = {CARD_ISLAND: 2, CARD_JACE: 1}
    actions = legal_bottom_actions(hand)
    assert Action("MULLIGAN_BOTTOM", {"card": CARD_ISLAND}) in actions
    assert Action("MULLIGAN_BOTTOM", {"card": CARD_JACE}) in actions


def test_rule_mulligan_agent_logs_keep_and_bottom_decisions():
    # Top seven are all Jace, forcing land_band to mulligan once. The next seven
    # are six Islands + one Jace, so the agent keeps and bottoms an excess Island.
    library = [CARD_ISLAND] * 26 + [CARD_ISLAND] * 6 + [CARD_JACE] + [CARD_JACE] * 7
    rng = Random(6)
    hand, result, events = london_mulligan_agent_opening_hand(
        library,
        rng,
        RuleMulliganAgent(MulliganPolicy(POLICY_LAND_BAND, max_mulligans=1)),
        player=0,
    )
    assert result.mulligans_taken == 1
    assert result.kept_hand_size == 6
    assert result.decision_count == len(events) == 3
    assert events[0].action == "MULLIGAN_TAKE"
    assert events[1].action == "MULLIGAN_KEEP"
    assert events[2].stage == "bottom"
    assert sum(hand.values()) == 6
    assert len(library) == 34


def test_start_game_accepts_mulligan_agents_and_records_decision_log():
    d = seed_deck()
    agent = RuleMulliganAgent(POLICY_LAND_BAND)
    state = start_game(d, d, seed=19, mulligan_agents=(agent, agent))
    assert len(state.mulligan_log) == 2
    assert state.mulligan_decision_log
    assert all("action" in row for row in state.mulligan_decision_log)


def test_slot_env_accepts_mulligan_agents():
    d = seed_deck()
    agent = RuleMulliganAgent(POLICY_LAND_BAND)
    env = MUC5SlotEnv(d, d, max_action_slots=64, mulligan_agents=(agent, agent))
    obs = env.reset(seed=21)
    assert env.state is not None
    assert env.state.mulligan_decision_log
    assert "self_mulligans_taken" in obs.feature_names
