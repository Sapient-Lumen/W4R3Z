from random import Random
import json

from src.muc5.action_schema import choose, activate_jace, cast
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE
from src.muc5.decision import build_decision_frame
from src.muc5.engine import GameState, PlayerState, StackSpell, apply_action, legal_actions
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace
from src.muc5.deckspace import DeckVector
from src.muc5.decision import PublicHeuristicAgent


def test_jace_plus2_seen_top_card_persists_after_leave_choice_without_public_leak():
    state = GameState(
        players=[
            PlayerState(library=[CARD_ISLAND], jace_loyalty=3),
            PlayerState(library=[CARD_ISLAND, CARD_FORCE]),
        ],
        active_player=0,
        frame="MAIN",
    )

    apply_action(state, activate_jace("plus2", target_player="opponent"), Random(91))
    actor_info = state.information_state(0)
    non_actor_info = state.information_state(1)

    assert actor_info["known_top_cards"] == {"1": CARD_FORCE}
    assert any(ev["kind"] == "SAW_TOP_CARD" and ev["card"] == CARD_FORCE for ev in actor_info["private_events"])
    assert CARD_FORCE not in json.dumps(non_actor_info, sort_keys=True)

    apply_action(state, choose("jace_plus2", put="leave"), Random(91))
    resolved_info = state.information_state(0)
    assert state.pending_choice is None
    assert resolved_info["known_top_cards"] == {"1": CARD_FORCE}
    assert any(ev["kind"] == "JACE_PLUS2_ORDER" and ev["put"] == "leave" for ev in resolved_info["public_events"])


def test_jace_plus2_bottom_clears_top_card_knowledge():
    state = GameState(
        players=[
            PlayerState(library=[CARD_ISLAND], jace_loyalty=3),
            PlayerState(library=[CARD_ISLAND, CARD_FORCE]),
        ],
        active_player=0,
        frame="MAIN",
    )

    apply_action(state, activate_jace("plus2", target_player="opponent"), Random(92))
    assert state.information_state(0)["known_top_cards"] == {"1": CARD_FORCE}
    apply_action(state, choose("jace_plus2", put="bottom"), Random(92))
    assert state.information_state(0)["known_top_cards"] == {}
    assert state.players[1].library[0] == CARD_FORCE


def test_force_pitch_card_is_public_exile_identity_and_event():
    state = GameState(
        players=[
            PlayerState(hand={CARD_FORCE: 1, CARD_COUNTERSPELL: 1}, life=20),
            PlayerState(),
        ],
        active_player=1,
        priority_player=0,
        frame="RESPONSE",
        stack=[StackSpell(1, 1, CARD_JACE)],
    )
    action = next(a for a in legal_actions(state) if a.kind == "CAST" and a.params.get("card") == CARD_FORCE and a.params.get("payment") == "pitch")
    apply_action(state, action, Random(93))

    opponent_obs = state.observation(1)
    assert opponent_obs["public_opponent"]["exile"][CARD_COUNTERSPELL] == 1
    assert any(ev["kind"] == "FORCE_PITCH_PAYMENT" and ev["pitch_card"] == CARD_COUNTERSPELL for ev in state.public_events)


def test_decision_frame_carries_replay_checked_information_state_fingerprint():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    trace = record_public_decision_trace(
        deck,
        deck,
        PublicHeuristicAgent(),
        PublicHeuristicAgent(),
        seed=9101,
        transition_seed=9102,
        agent_seed=9103,
        max_decisions=20,
    )
    assert trace["events"]
    assert "information_state_fingerprint" in trace["events"][0]
    assert trace["events"][0]["information_state_schema"] == "muc5.information_state.v1"
    result = replay_public_decision_trace(trace)
    assert result.passed, result.errors

    tampered = dict(trace)
    tampered["events"] = [dict(event) for event in trace["events"]]
    tampered["events"][0]["information_state_fingerprint"] = "not-the-real-info-hash"
    drift = replay_public_decision_trace(tampered)
    assert not drift.passed
    assert "information_state_fingerprint" in drift.errors[0]
