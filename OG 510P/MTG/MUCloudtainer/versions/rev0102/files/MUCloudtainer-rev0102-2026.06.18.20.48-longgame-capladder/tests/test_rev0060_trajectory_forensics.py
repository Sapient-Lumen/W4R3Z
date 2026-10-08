from __future__ import annotations

from pathlib import Path

from src.muc5.action_schema import Action, cast
from src.muc5.cpp_rollout import CppShadowGameSpec, prepare_cpp_shadow_rollout
from src.muc5.payoff import load_seed_decks
from src.muc5.terminal_decomposition import CF34_AGENT, CF34_MULLIGAN, THREAT_AGENT, THREAT_MULLIGAN
from src.muc5.trajectory_forensics import (
    metric_deltas_by_arm,
    summarize_forensic_rows,
    update_action_counters,
    validate_forensics_against_game_row,
)

ROOT = Path(__file__).resolve().parents[1]


def test_action_feature_counters_and_summary_delta():
    counters = {k: 0 for k in (
        "pass_actions",
        "play_island_actions",
        "cast_jace",
        "cast_overlord_impending",
        "cast_overlord_full_cost",
        "cast_counterspell",
        "cast_force_pitch",
        "cast_force_mana",
        "activate_jace_plus2_self",
        "activate_jace_plus2_opponent",
        "activate_jace_zero",
        "activate_jace_minus1",
        "activate_jace_ultimate_self",
        "activate_jace_ultimate_opponent",
        "attack_actions",
        "attack_to_player_total",
        "attack_to_jace_total",
        "block_actions",
        "block_player_attackers_total",
        "block_jace_attackers_total",
        "discard_choices",
        "cleanup_discard_choices",
        "jace_plus2_leave_choices",
        "jace_plus2_bottom_choices",
        "jace_brainstorm_putback_choices",
        "jace_legend_choices",
        "nonpass_actions",
    )}
    update_action_counters(counters, cast("ForceOfWill", payment="pitch", target_id=3, target_card="JaceTheMindSculptor"))
    update_action_counters(counters, Action("ATTACK", {"to_player": 2, "to_jace": 1}))
    assert counters["cast_force_pitch"] == 1
    assert counters["attack_to_player_total"] == 2
    assert counters["attack_to_jace_total"] == 1

    rows = [
        {"arm_id": "A_original_size_skew", "focus_target_score": 1.0, "decisions": 10, "turn_number": 5, "target_library_buffer_final": 20, "focus_terminal_mechanism": "library_out", "focus_terminal_loser_role": "opponent"},
        {"arm_id": "B_pilot_swap_size_skew", "focus_target_score": 0.0, "decisions": 12, "turn_number": 6, "target_library_buffer_final": -10, "focus_terminal_mechanism": "library_out", "focus_terminal_loser_role": "target"},
    ]
    summary = summarize_forensic_rows(rows, group_keys=("arm_id",))
    delta = metric_deltas_by_arm(summary)
    assert {r["arm_id"]: r["games"] for r in summary} == {"A_original_size_skew": 1, "B_pilot_swap_size_skew": 1}
    assert any(r["metric"] == "mean_target_library_buffer_final" and r["left_minus_right"] == 30 for r in delta)


def test_forensics_validation_accepts_legacy_decision_overcount():
    forensic = {
        "winner": "0",
        "loss_reason": "player_1_attempted_to_draw_from_empty_library",
        "starting_life": 20,
        "starting_player": 0,
        "p0_score": 1.0,
        "p1_score": 0.0,
        "decisions": 42,
        "applied_decisions": 42,
        "legacy_terminal_row_decisions": 43,
    }
    stored = {
        "winner": "0",
        "loss_reason": "player_1_attempted_to_draw_from_empty_library",
        "starting_life": "20",
        "starting_player": "0",
        "p0_score": "1.0",
        "p1_score": "0.0",
        "decisions": "43",
    }
    assert validate_forensics_against_game_row(forensic, stored) == []


def test_forensics_validation_accepts_corrected_decision_count():
    forensic = {
        "winner": "0",
        "loss_reason": "player_1_attempted_to_draw_from_empty_library",
        "starting_life": 20,
        "starting_player": 0,
        "p0_score": 1.0,
        "p1_score": 0.0,
        "decisions": 42,
        "applied_decisions": 42,
        "legacy_terminal_row_decisions": 43,
    }
    stored = {
        "winner": "0",
        "loss_reason": "player_1_attempted_to_draw_from_empty_library",
        "starting_life": "20",
        "starting_player": "0",
        "p0_score": "1.0",
        "p1_score": "0.0",
        "decisions": "42",
    }
    assert validate_forensics_against_game_row(forensic, stored) == []


def test_cpp_shadow_game_row_decisions_equal_applied_transition_count():
    decks = load_seed_decks(ROOT / "data" / "seed_decks.json")
    spec = CppShadowGameSpec(
        game_id="rev0060_decision_count_contract",
        strategy0="cf34_counter_wall",
        strategy1="pub_threat_overlord",
        deck0_name="sixty_counterwall_jace",
        deck1_name="forty_overlord_impending",
        deck0=decks["sixty_counterwall_jace"],
        deck1=decks["forty_overlord_impending"],
        agent0=CF34_AGENT,
        agent1=THREAT_AGENT,
        mulligan0=CF34_MULLIGAN,
        mulligan1=str(THREAT_MULLIGAN),
        seed=5959000,
        starting_player=0,
        starting_life=20,
        max_decisions=900,
        simulator_revision="rev0060-test",
    )
    prepared = prepare_cpp_shadow_rollout([spec], revision="rev0060-test")
    assert len(prepared.game_rows) == 1
    assert prepared.game_rows[0]["winner"] != "None"
    assert int(prepared.game_rows[0]["decisions"]) == len(prepared.transition_rows)
