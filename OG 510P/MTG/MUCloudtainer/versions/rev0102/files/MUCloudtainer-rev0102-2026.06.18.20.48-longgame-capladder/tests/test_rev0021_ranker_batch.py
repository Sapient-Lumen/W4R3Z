from __future__ import annotations

from random import Random

from src.muc5.cpp_trace import check_public_traces_with_cpp, finalize_cpp_trace_batch, prepare_public_traces_for_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.decision import build_decision_frame
from src.muc5.engine import start_game
from src.muc5.public_agents import make_public_agent
from src.muc5.ranker_policy import LinearActionRankerAgent, load_linear_ranker_model, save_linear_ranker_model, zero_linear_ranker_model
from src.muc5.replay import record_public_decision_trace


def test_zero_linear_ranker_agent_chooses_legal_action(tmp_path):
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    state = start_game(deck, deck, seed=2101, record_log=False)
    frame = build_decision_frame(state)
    agent = LinearActionRankerAgent(zero_linear_ranker_model())
    idx = agent.choose_action_index(frame, Random(1))
    assert 0 <= idx < frame.action_count

    path = tmp_path / "ranker.json"
    save_linear_ranker_model(agent.model, path)
    loaded = load_linear_ranker_model(path)
    assert loaded.feature_names == agent.model.feature_names
    assert loaded.coefficients == agent.model.coefficients


def test_cpp_trace_prepare_finalize_roundtrip_small_trace():
    deck = DeckVector(40, 24, 6, 4, 3, 3)
    trace = record_public_decision_trace(
        deck,
        deck,
        make_public_agent("heuristic"),
        make_public_agent("patient"),
        seed=2102,
        transition_seed=3102,
        agent_seed=4102,
        starting_life=20,
        max_decisions=60,
        mulligan_policies=("land_band", "land_band"),
    )
    trace["trace_id"] = "rev0021_test_trace"
    prepared = prepare_public_traces_for_cpp([trace], revision="rev0021_test")
    assert prepared.trace_count == 1
    assert prepared.events > 0
    assert prepared.supported_events == prepared.events
    summary, rows = finalize_cpp_trace_batch(prepared)
    assert summary.python_replay_errors == 0
    assert summary.mismatches == 0
    assert summary.skipped_events == 0
    assert len(rows) == prepared.events


def test_check_public_traces_with_cpp_keeps_old_api():
    deck = DeckVector(40, 30, 0, 0, 10, 0)
    trace = record_public_decision_trace(
        deck,
        deck,
        make_public_agent("code_jace_ultimator_rev0020"),
        make_public_agent("patient"),
        seed=2103,
        transition_seed=3103,
        agent_seed=4103,
        starting_life=40,
        max_decisions=120,
        mulligan_policies=("keep_always", "keep_always"),
    )
    summary, _ = check_public_traces_with_cpp([trace], revision="rev0021_test")
    assert summary.python_replay_errors == 0
    assert summary.mismatches == 0
    assert summary.support_rate == 1.0
