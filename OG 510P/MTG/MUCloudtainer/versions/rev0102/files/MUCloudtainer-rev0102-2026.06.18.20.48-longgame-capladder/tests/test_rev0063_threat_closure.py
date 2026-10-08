from src.muc5.action_schema import Action, activate_jace, cast
from src.muc5.cards import CARD_OVERLORD
from src.muc5.public_agents import PublicProfileAgent, make_public_agent
from src.muc5.threat_closure import (
    attack_draw_cost,
    attack_face_damage,
    compare_threat_closure_by_life,
    rev0063_threat_closure_arms,
    threat_closure_specs,
)


def _attack(to_player: int, to_jace: int = 0) -> Action:
    return Action("ATTACK", {"to_player": to_player, "to_jace": to_jace})


def test_threat_closure_agent_is_factory_visible():
    agent = make_public_agent("threat_closure")
    assert isinstance(agent, PublicProfileAgent)
    assert agent.profile == "threat_closure"


def test_threat_closure_attack_guard_avoids_pre_damage_selfdeck():
    agent = PublicProfileAgent("threat_closure")
    obs = {
        "frame": "ATTACK",
        "own_library_count": 1,
        "public_self": {"library_count": 1, "life": 40, "hand_count": 2},
        "public_opponent": {"life": 5, "jace_loyalty": None},
        "starting_life": 40,
    }
    assert agent.score_action(obs, _attack(1)) < agent.score_action(obs, Action("PASS", {}))


def test_threat_closure_prefers_small_surviving_lethal_attack():
    agent = PublicProfileAgent("threat_closure")
    obs = {
        "frame": "ATTACK",
        "own_library_count": 8,
        "public_self": {"library_count": 8, "life": 40, "hand_count": 2},
        "public_opponent": {"life": 10, "jace_loyalty": None},
        "starting_life": 40,
    }
    two = agent.score_action(obs, _attack(2))
    three = agent.score_action(obs, _attack(3))
    one = agent.score_action(obs, _attack(1))
    assert two > one
    assert two > three


def test_threat_closure_deprioritizes_low_library_jace_zero():
    agent = PublicProfileAgent("threat_closure")
    obs = {
        "frame": "MAIN",
        "own_library_count": 4,
        "public_self": {"library_count": 4, "life": 20, "hand_count": 5},
        "public_opponent": {"life": 20, "jace_loyalty": None},
        "starting_life": 20,
    }
    assert agent.score_action(obs, activate_jace("zero")) < agent.score_action(obs, cast(CARD_OVERLORD, mode="full_cost"))


def test_threat_closure_arms_and_specs_are_balanced():
    arms = rev0063_threat_closure_arms("data/seed_decks.json")
    assert len(arms) == 6
    assert {a.policy_axis for a in arms} == {"legacy_threat_rush", "library_aware_threat_closure"}
    specs, meta = threat_closure_specs(arms, simulator_revision="rev0063", life_totals=(20,), reps=1, max_decisions=30)
    assert len(specs) == len(arms) * 2 * 2
    assert all(gid in meta for gid in [s.game_id for s in specs])
    assert {m["target_seat"] for m in meta.values()} == {0, 1}


def test_attack_helpers_and_comparison_rows():
    assert attack_draw_cost(_attack(2, 1)) == 6
    assert attack_face_damage(_attack(3)) == 15
    rows = [
        {"target_size_axis": "buffer40_vs_threat40", "policy_axis": "legacy_threat_rush", "starting_life": 40, "mean_target_score": 1.0, "mean_threat_jace_zero_actions": 8, "mean_threat_declared_attackers_to_player": 1},
        {"target_size_axis": "buffer40_vs_threat40", "policy_axis": "library_aware_threat_closure", "starting_life": 40, "mean_target_score": 0.25, "mean_threat_jace_zero_actions": 1, "mean_threat_declared_attackers_to_player": 8},
    ]
    comp = compare_threat_closure_by_life(rows)
    assert comp[0]["closure_guard_target_score_delta_guarded_minus_legacy"] == -0.75
    assert comp[0]["provisional_read"] == "guard_reduces_inert_edge"
