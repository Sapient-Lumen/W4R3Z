from random import Random
from collections import Counter

from src.muc5.action_schema import Action, activate_jace, choose, cast, PASS
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.engine import GameState, PlayerState, apply_action, legal_actions, StackSpell
from src.muc5.invariants import assert_card_conservation


def test_overlord_attack_triggers_resolve_one_at_a_time():
    # top of library is list[-1]. Two attacking Overlords should not let the
    # player see all four cards before making the first discard choice.
    p0 = PlayerState(
        life=20,
        library=[CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_ISLAND],
        hand=Counter(),
        overlord_ready=2,
    )
    p1 = PlayerState(life=20, library=[], hand=Counter())
    state = GameState(
        players=[p0, p1],
        active_player=0,
        frame="ATTACK",
        starting_deck_counts=[
            {CARD_ISLAND: 1, CARD_COUNTERSPELL: 1, CARD_FORCE: 1, CARD_JACE: 1, CARD_OVERLORD: 2},
            {},
        ],
        record_log=False,
    )

    apply_action(state, Action("ATTACK", {"to_player": 2, "to_jace": 0}), Random(1))
    assert state.pending_choice is not None
    assert state.pending_choice.kind == "discard"
    assert state.pending_choice.data["overlord_triggers_remaining"] == 1
    assert state.players[0].hand == {CARD_ISLAND: 1, CARD_JACE: 1}
    assert state.players[0].library == [CARD_COUNTERSPELL, CARD_FORCE]

    apply_action(state, choose("discard", discard=CARD_ISLAND), Random(1))
    assert state.pending_choice is not None
    assert state.pending_choice.kind == "discard"
    assert state.pending_choice.data["overlord_triggers_remaining"] == 0
    assert state.players[0].hand[CARD_JACE] == 1
    assert state.players[0].hand[CARD_FORCE] == 1
    assert state.players[0].hand[CARD_COUNTERSPELL] == 1
    assert CARD_ISLAND in state.players[0].graveyard
    assert_card_conservation(state)


def test_jace_minus1_targets_specific_overlord_creature_state():
    p0 = PlayerState(life=20, hand=Counter(), jace_loyalty=3)
    p1 = PlayerState(life=20, hand=Counter(), overlord_ready=1, overlord_sick=1, overlord_tapped=1, impending_1=1)
    state = GameState(
        players=[p0, p1],
        active_player=0,
        frame="MAIN",
        starting_deck_counts=[{CARD_JACE: 1}, {CARD_OVERLORD: 4}],
        record_log=False,
    )
    compact = [a.compact() for a in legal_actions(state)]
    assert any("target_state=ready" in c for c in compact)
    assert any("target_state=sick" in c for c in compact)
    assert any("target_state=tapped" in c for c in compact)
    assert not any("impending" in c for c in compact)

    apply_action(state, activate_jace("minus1", target_player="opponent", target_state="tapped"), Random(2))
    assert state.players[1].overlord_ready == 1
    assert state.players[1].overlord_sick == 1
    assert state.players[1].overlord_tapped == 0
    assert state.players[1].impending_1 == 1
    assert state.players[1].hand[CARD_OVERLORD] == 1
    assert_card_conservation(state)


def test_counter_war_force_protects_jace_from_counterspell():
    # Stack before resolution (bottom to top): Jace, Counterspell targeting Jace,
    # Force targeting Counterspell. After both players pass through resolutions,
    # Force should counter Counterspell, then Jace should resolve.
    p0 = PlayerState(life=20, hand=Counter(), islands_tapped=4)
    p1 = PlayerState(life=20, hand=Counter(), islands_tapped=2)
    state = GameState(
        players=[p0, p1],
        active_player=0,
        priority_player=0,
        frame="RESPONSE",
        stack=[
            StackSpell(1, 0, CARD_JACE),
            StackSpell(2, 1, CARD_COUNTERSPELL, params={"target_id": 1}),
            StackSpell(3, 0, CARD_FORCE, mode="pitch", params={"target_id": 2}),
        ],
        next_spell_id=4,
        pre_stack_frame="MAIN",
        starting_deck_counts=[{CARD_ISLAND: 4, CARD_JACE: 1, CARD_FORCE: 1}, {CARD_ISLAND: 2, CARD_COUNTERSPELL: 1}],
        record_log=False,
    )
    apply_action(state, PASS, Random(3))
    apply_action(state, PASS, Random(3))
    assert [s.spell_id for s in state.stack] == [1]
    assert state.players[0].graveyard[CARD_FORCE] == 1
    assert state.players[1].graveyard[CARD_COUNTERSPELL] == 1

    apply_action(state, PASS, Random(3))
    apply_action(state, PASS, Random(3))
    assert state.players[0].jace_loyalty == 3
    assert not state.stack
    assert_card_conservation(state)
