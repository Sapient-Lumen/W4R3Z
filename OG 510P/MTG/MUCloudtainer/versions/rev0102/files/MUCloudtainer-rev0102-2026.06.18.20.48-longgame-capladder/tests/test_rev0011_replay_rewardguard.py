from random import Random

from src.muc5.decision import PublicHeuristicAgent, PublicRandomAgent
from src.muc5.deckspace import DeckVector
from src.muc5.engine import start_game
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, state_fingerprint
from src.muc5.reward_guard import reward_packet_from_state, audit_reward_packet, audit_payoff_like_row
from src.muc5.mulligan import POLICY_LAND_BAND


def sample_deck() -> DeckVector:
    return DeckVector(40, 24, 6, 4, 3, 3)


def test_public_decision_trace_replays_exactly() -> None:
    deck = sample_deck()
    trace = record_public_decision_trace(
        deck,
        deck,
        PublicHeuristicAgent(),
        PublicRandomAgent(),
        seed=111,
        transition_seed=222,
        agent_seed=333,
        starting_life=20,
        max_decisions=80,
        mulligan_policy=POLICY_LAND_BAND,
    )
    result = replay_public_decision_trace(trace)
    assert result.passed, result.errors
    assert result.checked_steps == len(trace["events"])
    assert result.final_fingerprint == trace["final"]["fingerprint"]


def test_replay_detects_tampering() -> None:
    deck = sample_deck()
    trace = record_public_decision_trace(deck, deck, PublicHeuristicAgent(), PublicHeuristicAgent(), seed=7, max_decisions=20)
    assert trace["events"]
    tampered = dict(trace)
    tampered["events"] = [dict(ev) for ev in trace["events"]]
    first = tampered["events"][0]
    if first["legal_action_count"] > 1:
        first["action_index"] = (int(first["action_index"]) + 1) % int(first["legal_action_count"])
    else:
        first["post_fingerprint"] = "not-the-real-hash"
    result = replay_public_decision_trace(tampered)
    assert not result.passed
    assert result.errors


def test_state_fingerprint_changes_after_action() -> None:
    deck = sample_deck()
    state = start_game(deck, deck, seed=5, record_log=False)
    before = state_fingerprint(state)
    from src.muc5.decision import build_decision_frame, apply_decision_index

    frame = build_decision_frame(state)
    apply_decision_index(state, frame, 0, Random(5))
    after = state_fingerprint(state)
    assert before != after


def test_reward_guard_flags_truncation_for_training() -> None:
    deck = sample_deck()
    state = start_game(deck, deck, seed=9, record_log=False)
    state.frame = "GAME_OVER"
    state.loss_reason = "max_decisions_reached"
    packet = reward_packet_from_state(state, 0)
    ok, errors = audit_reward_packet(packet)
    assert not ok
    assert any("truncation" in e for e in errors)
    ok2, errors2 = audit_reward_packet(packet, allow_truncation_training_reward=True)
    assert ok2, errors2


def test_payoff_like_row_guard() -> None:
    ok, errors = audit_payoff_like_row({"is_truncation": "True", "p0_terminal_win": "False", "p1_terminal_win": "False", "p0_score": "0.5", "p1_score": "0.5"})
    assert ok, errors
    bad, bad_errors = audit_payoff_like_row({"is_truncation": "True", "p0_terminal_win": "True", "p0_score": "1.4"})
    assert not bad
    assert len(bad_errors) >= 2
