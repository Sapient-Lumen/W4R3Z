from pathlib import Path

from src.muc5.action_schema import Action, PASS, activate_jace, cast
from src.muc5.cards import CARD_COUNTERSPELL, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from src.muc5.counter_response import (
    GUARDED_COUNTER_AXIS,
    LEGACY_COUNTER_AXIS,
    claim_quarantine_rows,
    compare_counter_response_by_life,
    counter_response_gate_report,
    counter_response_specs,
    counter_response_stress_specs,
    rev0065_counter_response_arms,
)
from src.muc5.public_agents import PublicProfileAgent, make_public_agent
from src.muc5.terminal_decomposition import CF34_AGENT


def _obs(**overrides):
    base = {
        "frame": "RESPONSE",
        "player": 0,
        "starting_life": 20,
        "own_library_count": 20,
        "own_hand": {CARD_COUNTERSPELL: 1, CARD_JACE: 1, CARD_ISLAND: 3},
        "public_self": {"life": 20, "hand_count": 5, "islands_untapped": 2, "library_count": 20},
        "public_opponent": {"life": 20, "hand_count": 5, "overlord_ready": 0, "library_count": 20},
    }
    base.update(overrides)
    return base


def test_counter_guard_agent_is_factory_visible():
    agent = make_public_agent("counter_guard")
    assert isinstance(agent, PublicProfileAgent)
    assert agent.profile == "counter_guard"


def test_counter_guard_prioritizes_countering_overlord_over_passing():
    agent = PublicProfileAgent("counter_guard")
    obs = _obs()
    counter_overlord = cast(CARD_COUNTERSPELL, target_card=CARD_OVERLORD)
    assert agent.score_action(obs, counter_overlord) > agent.score_action(obs, PASS)


def test_counter_guard_avoids_low_library_brainstorm():
    agent = PublicProfileAgent("counter_guard")
    obs = _obs(frame="MAIN", own_library_count=4, public_self={"life": 20, "hand_count": 3, "islands_untapped": 4, "library_count": 4})
    brainstorm = activate_jace("zero")
    pass_action = PASS
    assert agent.score_action(obs, brainstorm) < agent.score_action(obs, pass_action)


def test_rev0065_arms_are_matched_counter_policy_swaps():
    arms = rev0065_counter_response_arms(Path("data/seed_decks.json"))
    assert len(arms) == 6
    assert {a.counter_policy_axis for a in arms} == {LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS}
    assert {a.threat_policy_axis for a in arms} == {"library_aware_threat_closure"}
    assert {a.size_axis for a in arms} == {"counter60_vs_threat40", "counter40_vs_threat40", "counter60_vs_threat60"}
    by_axis = {}
    for arm in arms:
        by_axis.setdefault(arm.size_axis, []).append(arm)
    for pair in by_axis.values():
        assert len(pair) == 2
        assert len({a.target.deck.counts().__repr__() for a in pair}) == 1
        assert len({a.opponent.deck.counts().__repr__() for a in pair}) == 1
        assert {a.target.agent_name for a in pair} == {CF34_AGENT, "counter_guard"}


def test_counter_response_specs_cover_seats_starting_players_and_life_totals():
    arms = rev0065_counter_response_arms(Path("data/seed_decks.json"))
    specs, meta = counter_response_specs(arms, simulator_revision="test", reps=2, life_totals=(20, 40))
    assert len(specs) == 6 * 2 * 2 * 2 * 2
    assert len(meta) == len(specs)
    assert {m["counter_policy_axis"] for m in meta.values()} == {LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS}
    assert {m["threat_policy_axis"] for m in meta.values()} == {"library_aware_threat_closure"}


def test_compare_counter_response_labels_rescue_candidate():
    rows = [
        {
            "size_axis": "counter60_vs_threat40",
            "starting_life": 20,
            "counter_policy_axis": LEGACY_COUNTER_AXIS,
            "target_mean_score_draw_half": 0.2,
            "library_out_win_share": 0.0,
        },
        {
            "size_axis": "counter60_vs_threat40",
            "starting_life": 20,
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "target_mean_score_draw_half": 0.65,
            "library_out_win_share": 0.5,
        },
    ]
    out = compare_counter_response_by_life(rows)
    assert out[0]["provisional_read"] == "counter_deck_rescue_candidate"


def test_claim_quarantine_attaches_counter_response_status():
    old = [
        {
            "size_axis": "counter60_vs_threat40",
            "starting_life": 20,
            "legacy_counter_score": 0.7,
            "closure_counter_score": 0.1,
            "closure_minus_legacy_counter_score_delta": -0.6,
        }
    ]
    response = [
        {
            "size_axis": "counter60_vs_threat40",
            "starting_life": 20,
            "public_counter_guard_score": 0.3,
            "guard_minus_legacy_counter_score_delta": 0.2,
        }
    ]
    out = claim_quarantine_rows(old, response)
    assert out[0]["quarantine_status"] == "quarantined_old_edge_threat_baseline_artifact"
    assert out[0]["counter_response_status"] == "no_current_counter_guard_rescue"


def test_counter_response_gate_requires_live_rows():
    report = counter_response_gate_report(
        {
            "games": 120,
            "truncations": 0,
            "python_errors": 0,
            "forensic_games": 120,
            "closure_feature_games": 120,
            "cpp_shadow_summary": {"mismatches": 0, "skipped_events": 0},
        },
        [
            {"counter_policy_axis": LEGACY_COUNTER_AXIS, "size_axis": "counter60_vs_threat40"},
            {"counter_policy_axis": GUARDED_COUNTER_AXIS, "size_axis": "counter40_vs_threat40"},
            {"counter_policy_axis": GUARDED_COUNTER_AXIS, "size_axis": "counter60_vs_threat60"},
        ],
    )
    assert report["passed"]


def test_counter_response_stress_specs_filter_candidate_cells():
    arms = rev0065_counter_response_arms(Path("data/seed_decks.json"))
    specs, meta = counter_response_stress_specs(
        arms,
        candidate_cells=(("counter60_vs_threat40", 40), ("counter60_vs_threat60", 20)),
        simulator_revision="test",
        reps=2,
    )
    # 2 cells * 2 policies * 2 seats * 2 starting players * 2 reps.
    assert len(specs) == 2 * 2 * 2 * 2 * 2
    assert len(meta) == len(specs)
    assert {m["stress_cell"] for m in meta.values()} == {
        "counter60_vs_threat40_life40",
        "counter60_vs_threat60_life20",
    }
    assert {m["counter_policy_axis"] for m in meta.values()} == {LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS}
