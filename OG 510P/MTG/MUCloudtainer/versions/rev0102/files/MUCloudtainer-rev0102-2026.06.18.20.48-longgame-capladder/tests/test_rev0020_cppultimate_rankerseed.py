from __future__ import annotations

import copy
from collections import Counter
from random import Random

from src.muc5.action_schema import activate_jace
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.cpp_transition import (
    cpp_transition_signatures,
    is_supported_transition,
    state_signature,
    transition_record_from_state_action,
    with_jace_ultimate_shuffle_transport,
)
from src.muc5.engine import GameState, PlayerState, apply_action, legal_actions


def test_cpp_transition_supports_jace_ultimate_with_explicit_shuffle_transport() -> None:
    p0 = PlayerState(life=20, hand=Counter(), jace_loyalty=12)
    p1 = PlayerState(
        life=20,
        library=[CARD_ISLAND, CARD_FORCE, CARD_OVERLORD],
        hand=Counter({CARD_COUNTERSPELL: 1, CARD_JACE: 1}),
    )
    state = GameState(
        players=[p0, p1],
        active_player=0,
        frame="MAIN",
        starting_life=20,
        record_log=False,
        starting_deck_counts=[{CARD_JACE: 1}, {CARD_ISLAND: 1, CARD_FORCE: 1, CARD_OVERLORD: 1, CARD_COUNTERSPELL: 1, CARD_JACE: 1}],
    )
    action = activate_jace("ultimate", target_player="opponent")
    assert action in legal_actions(state)
    assert not is_supported_transition(state, action)  # no RNG/shuffle transcript on the legal menu action

    pre = copy.deepcopy(state)
    apply_action(state, action, Random(20020), validate=True)
    transported = with_jace_ultimate_shuffle_transport(pre, action, state)
    assert is_supported_transition(pre, transported)

    record = transition_record_from_state_action(pre, transported, "rev0020_direct_jace_ultimate")
    got = cpp_transition_signatures([record], force_build=True)[0]
    assert got == state_signature(state)
    assert state.players[1].total_hand() == 0
    assert state.players[1].total_library() == 2
    assert sum(state.players[1].exile.values()) == 3


def test_action_imitation_rows_are_public_feature_aligned() -> None:
    from src.muc5.deckspace import DeckVector
    from src.muc5.imitation import action_ranker_feature_names, collect_action_imitation_rows
    from src.muc5.public_agents import make_public_agent

    d = DeckVector(40, 24, 6, 4, 3, 3)
    agent = make_public_agent("heuristic")
    rows, summary = collect_action_imitation_rows([(d, d, agent, agent, 0, 20, ("keep_always", "keep_always"))], seed_base=22020, max_decisions=8)
    assert summary.games == 1
    assert summary.decisions > 0
    assert summary.rows >= summary.decisions
    assert summary.chosen_rows == summary.decisions
    features = action_ranker_feature_names()
    assert "ctx_frame_main" in features
    assert "jace_ultimate" in features
    for row in rows[:20]:
        for feature in features:
            assert feature in row
        assert row["chosen"] in {0, 1}
