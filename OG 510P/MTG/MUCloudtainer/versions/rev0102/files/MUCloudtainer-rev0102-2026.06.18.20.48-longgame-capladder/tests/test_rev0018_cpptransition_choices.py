from __future__ import annotations

import copy
from collections import Counter
from random import Random

from src.muc5.action_schema import PASS, activate_jace, choose
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.cpp_transition import cpp_transition_signatures, state_signature, transition_record_from_state_action
from src.muc5.engine import GameState, PendingChoice, PlayerState, StackSpell, apply_action


def _state() -> GameState:
    return GameState(players=[PlayerState(life=20), PlayerState(life=20)], record_log=False, starting_life=20)


def _assert_cpp_matches_python(state: GameState, action) -> None:
    expected = copy.deepcopy(state)
    apply_action(expected, action, Random(999), validate=True)
    record = transition_record_from_state_action(state, action, "unit")
    [actual] = cpp_transition_signatures([record])
    assert actual == state_signature(expected)


def test_rev0018_cpp_resolves_overlord_into_pending_discard_with_exact_library_order() -> None:
    state = _state()
    state.frame = "RESPONSE"
    state.pre_stack_frame = "MAIN"
    state.priority_player = 1
    state.consecutive_passes = 1
    state.stack = [StackSpell(1, 0, CARD_OVERLORD, "full_cost")]
    state.next_spell_id = 2
    state.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE]
    _assert_cpp_matches_python(state, PASS)


def test_rev0018_cpp_jace_brainstorm_activation_and_putback_choice() -> None:
    state = _state()
    state.players[0].jace_loyalty = 3
    state.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE]
    _assert_cpp_matches_python(state, activate_jace("zero"))

    # Now test the actual putback transition separately with exact ordered library
    # transport. The top of the library is list[-1].
    state2 = _state()
    state2.players[0].hand = Counter({CARD_ISLAND: 2, CARD_JACE: 1, CARD_FORCE: 1})
    state2.players[0].library = [CARD_COUNTERSPELL, CARD_OVERLORD]
    state2.pending_choice = PendingChoice(0, "jace_brainstorm_putback", {"resume": "MAIN"})
    _assert_cpp_matches_python(state2, choose("jace_brainstorm_putback", first_draw=CARD_JACE, second_draw=CARD_ISLAND))


def test_rev0018_cpp_jace_plus2_bottom_moves_top_card_to_bottom() -> None:
    state = _state()
    state.players[0].library = [CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE]
    state.pending_choice = PendingChoice(0, "jace_plus2", {"target_player": 0, "seen_top_card": CARD_FORCE, "resume": "MAIN"})
    _assert_cpp_matches_python(state, choose("jace_plus2", put="bottom"))
