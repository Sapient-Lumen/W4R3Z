from __future__ import annotations

from src.muc5.action_schema import cast
from src.muc5.cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD
from src.muc5.public_agents import PublicProfileAgent, make_public_agent
from src.muc5.threat_response import (
    CLOSURE_THREAT_AXIS,
    PRESSURE_THREAT_AXIS,
    compare_threat_response_by_life,
    rev0066_threat_response_arms,
    summarize_counter_ownership_rows,
)


def _response_obs(player: int, controller: int, target_card: str = CARD_OVERLORD):
    return {
        "player": player,
        "frame": "RESPONSE",
        "starting_life": 20,
        "own_hand": {CARD_COUNTERSPELL: 1, CARD_FORCE: 1},
        "own_library_count": 20,
        "public_self": {"life": 20, "hand_count": 4, "library_count": 20, "islands_untapped": 5},
        "public_opponent": {"life": 20, "hand_count": 4, "library_count": 20, "islands_untapped": 5},
        "stack": [{"spell_id": 7, "controller": controller, "card": target_card, "mode": "normal", "params": {}}],
    }


def test_guarded_public_profiles_penalize_self_countering() -> None:
    action = cast(CARD_COUNTERSPELL, target_id=7, target_card=CARD_OVERLORD)
    for profile in ("threat_closure", "threat_pressure", "counter_guard"):
        scorer = PublicProfileAgent(profile)
        own_score = scorer.score_action(_response_obs(player=1, controller=1), action)
        opposing_score = scorer.score_action(_response_obs(player=1, controller=0), action)
        assert own_score < -800.0
        assert opposing_score > 20.0


def test_threat_pressure_alias_loads() -> None:
    assert make_public_agent("threat_pressure").name.endswith("threat_pressure_rev0012")
    assert make_public_agent("public_threat_pressure").name.endswith("threat_pressure_rev0012")


def test_rev0066_arms_have_matched_threat_axes() -> None:
    arms = rev0066_threat_response_arms("data/seed_decks.json")
    axes = {(a.size_axis, a.threat_policy_axis) for a in arms}
    for size_axis in ("counter40_vs_threat40", "counter60_vs_threat40", "counter60_vs_threat60"):
        assert (size_axis, CLOSURE_THREAT_AXIS) in axes
        assert (size_axis, PRESSURE_THREAT_AXIS) in axes
    assert all(a.target.agent_name == "counter_guard" for a in arms)


def test_compare_threat_response_classifies_pressure_effect() -> None:
    rows = [
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": CLOSURE_THREAT_AXIS, "starting_life": 40, "target_mean_score_draw_half": 0.70},
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": PRESSURE_THREAT_AXIS, "starting_life": 40, "target_mean_score_draw_half": 0.35},
    ]
    out = compare_threat_response_by_life(rows)
    assert out[0]["provisional_read"] == "threat_pressure_refutes_counter_rescue"


def test_ownership_summary_counts_rates() -> None:
    rows = [
        {"axis": "a", "selected_own_spell_counters": 0, "threat_selected_own_spell_counters": 0},
        {"axis": "a", "selected_own_spell_counters": 2, "threat_selected_own_spell_counters": 1},
    ]
    out = summarize_counter_ownership_rows(rows, group_keys=("axis",))
    assert out[0]["sum_selected_own_spell_counters"] == 2
    assert out[0]["threat_own_spell_counter_rate_per_game"] == 0.5
