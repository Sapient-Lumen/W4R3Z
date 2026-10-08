from __future__ import annotations

from src.muc5.action_schema import cast
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD
from src.muc5.public_agents import PublicProfileAgent, make_public_agent
from src.muc5.response_matrix import (
    CLOSURE_THREAT_AXIS,
    PRESSURE_THREAT_AXIS,
    SURGE_THREAT_AXIS,
    THREAT_SURGE_AGENT,
    compare_response_matrix_by_life,
    rev0067_response_matrix_arms,
)


def _response_obs(player: int, controller: int, target_card: str = CARD_COUNTERSPELL):
    return {
        "player": player,
        "frame": "RESPONSE",
        "starting_life": 20,
        "own_hand": {CARD_COUNTERSPELL: 1, CARD_FORCE: 1, CARD_JACE: 1, CARD_OVERLORD: 1},
        "own_library_count": 24,
        "public_self": {"life": 20, "hand_count": 4, "library_count": 24, "islands_untapped": 5},
        "public_opponent": {"life": 20, "hand_count": 4, "library_count": 24, "islands_untapped": 5},
        "stack": [{"spell_id": 7, "controller": controller, "card": target_card, "mode": "normal", "params": {}}],
    }


def test_threat_surge_alias_loads() -> None:
    assert make_public_agent(THREAT_SURGE_AGENT).name.endswith("threat_surge_rev0012")
    assert make_public_agent("public_threat_surge").name.endswith("threat_surge_rev0012")


def test_threat_surge_penalizes_self_counter_and_protects_stack() -> None:
    action = cast(CARD_COUNTERSPELL, target_id=7, target_card=CARD_COUNTERSPELL)
    scorer = PublicProfileAgent("threat_surge")
    own_score = scorer.score_action(_response_obs(player=1, controller=1), action)
    opposing_counter_score = scorer.score_action(_response_obs(player=1, controller=0), action)
    assert own_score < -850.0
    assert opposing_counter_score > 150.0


def test_rev0067_arms_cover_three_threat_axes() -> None:
    arms = rev0067_response_matrix_arms("data/seed_decks.json")
    axes = {(a.size_axis, a.threat_policy_axis) for a in arms}
    for size_axis in ("counter40_vs_threat40", "counter60_vs_threat40", "counter60_vs_threat60"):
        assert (size_axis, CLOSURE_THREAT_AXIS) in axes
        assert (size_axis, PRESSURE_THREAT_AXIS) in axes
        assert (size_axis, SURGE_THREAT_AXIS) in axes
    assert all(a.target.agent_name == "counter_guard" for a in arms)


def test_compare_response_matrix_classifies_surge_refutation() -> None:
    rows = [
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": CLOSURE_THREAT_AXIS, "starting_life": 40, "target_mean_score_draw_half": 0.70},
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": PRESSURE_THREAT_AXIS, "starting_life": 40, "target_mean_score_draw_half": 0.62},
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": SURGE_THREAT_AXIS, "starting_life": 40, "target_mean_score_draw_half": 0.35},
    ]
    out = compare_response_matrix_by_life(rows)
    assert out[0]["best_threat_axis_for_this_cell"] == SURGE_THREAT_AXIS
    assert out[0]["provisional_read"] == "threat_surge_refutes_counter_guard"


def test_compare_response_matrix_marks_missing_policy_incomplete() -> None:
    rows = [
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": CLOSURE_THREAT_AXIS, "starting_life": 40, "target_mean_score_draw_half": 0.70},
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": PRESSURE_THREAT_AXIS, "starting_life": 40, "target_mean_score_draw_half": 0.62},
    ]
    out = compare_response_matrix_by_life(rows)
    assert out[0]["provisional_read"] == "incomplete_matrix"
    assert out[0]["counter_score_vs_surge"] is None
    assert out[0]["best_threat_axis_for_this_cell"] is None
    assert out[0]["missing_threat_policy_axes"] == [SURGE_THREAT_AXIS]
