from __future__ import annotations

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace
from src.muc5.mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS


def test_cpp_trace_checker_replays_public_trace() -> None:
    deck0 = DeckVector(40, 22, 8, 6, 3, 1)
    deck1 = DeckVector(40, 20, 4, 8, 5, 3)
    trace = record_public_decision_trace(
        deck0,
        deck1,
        make_public_agent("heuristic"),
        make_public_agent("threat_rush"),
        seed=191919,
        transition_seed=191919,
        agent_seed=291919,
        starting_player=0,
        starting_life=20,
        max_decisions=80,
        mulligan_policies=(POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS),
    )
    trace["trace_id"] = "test_trace"
    summary, rows = check_public_traces_with_cpp([trace], revision="test")
    assert summary.traces == 1
    assert summary.events == len(trace["events"])
    assert summary.python_replay_errors == 0
    assert summary.mismatches == 0
    assert rows
    assert summary.supported_events > 0
    assert summary.cpp_match_rate_on_supported == 1.0


def test_cpp_trace_checker_marks_tampered_trace_as_python_error() -> None:
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    trace = record_public_decision_trace(
        deck,
        deck,
        make_public_agent("heuristic"),
        make_public_agent("heuristic"),
        seed=191920,
        transition_seed=191920,
        agent_seed=291920,
        starting_player=0,
        starting_life=20,
        max_decisions=20,
        mulligan_policies=(POLICY_LAND_BAND, POLICY_LAND_BAND),
    )
    trace["trace_id"] = "tampered_trace"
    if trace["events"]:
        trace["events"][0]["legal_actions"] = ["BROKEN"]
    summary, _rows = check_public_traces_with_cpp([trace], revision="test")
    assert summary.python_replay_errors >= 1
