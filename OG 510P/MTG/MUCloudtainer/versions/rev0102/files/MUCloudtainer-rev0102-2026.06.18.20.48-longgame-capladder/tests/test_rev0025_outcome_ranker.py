from random import Random

from src.muc5.deckspace import DeckVector
from src.muc5.mulligan import POLICY_LAND_BAND
from src.muc5.outcome_training import collect_outcome_weighted_action_rows, outcome_weight_for_score
from src.muc5.public_agents import make_public_agent
from src.muc5.ranker_policy import LinearActionRankerAgent, zero_linear_ranker_model
from src.muc5.decision import build_decision_frame
from src.muc5.engine import start_game


def test_outcome_weight_rule_keeps_truncations_out_of_training_signal():
    assert outcome_weight_for_score(1.0, terminal=True) == 1.0
    assert outcome_weight_for_score(0.0, terminal=True) == 0.15
    assert outcome_weight_for_score(0.5, terminal=False) == 0.0


def test_collect_outcome_rows_public_shape_and_weights():
    deck = DeckVector(40, 24, 4, 4, 8, 0)
    rows, summary = collect_outcome_weighted_action_rows(
        [(deck, deck, make_public_agent("threat_rush"), make_public_agent("counter_happy"), 0, 20, (POLICY_LAND_BAND, POLICY_LAND_BAND))],
        seed_base=252500,
        max_decisions=80,
    )
    assert rows
    assert summary.games == 1
    assert summary.rows >= summary.chosen_rows
    assert {"actor_terminal_score", "outcome_weight", "terminal", "chosen"}.issubset(rows[0].keys())
    assert all(float(r["outcome_weight"]) >= 0.0 for r in rows)
    # Public feature rows must not carry raw hidden libraries or opponent hand.
    forbidden = {"opponent_hand", "library", "players"}
    assert not forbidden.intersection(rows[0].keys())


def test_zero_outcome_ranker_agent_chooses_legal_slot():
    deck = DeckVector(40, 22, 8, 6, 3, 1)
    state = start_game(deck, deck, seed=252501, starting_life=20, record_log=False)
    frame = build_decision_frame(state)
    agent = LinearActionRankerAgent(zero_linear_ranker_model("rev0025_zero"), name="zero_outcome_ranker_test")
    idx = agent.choose_action_index(frame, Random(2525))
    assert 0 <= idx < frame.action_count
