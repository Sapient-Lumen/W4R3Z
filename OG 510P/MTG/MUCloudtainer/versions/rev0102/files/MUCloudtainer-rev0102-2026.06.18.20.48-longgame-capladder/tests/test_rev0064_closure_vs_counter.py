from pathlib import Path

from src.muc5.closure_vs_counter import (
    annotate_closure_vs_counter_rows,
    closure_vs_counter_gate_report,
    closure_vs_counter_specs,
    compare_closure_vs_counter_by_life,
    compare_closure_vs_counter_features_by_life,
    rev0064_closure_vs_counter_arms,
)
from src.muc5.threat_closure import THREAT_CLOSURE_AGENT, THREAT_RUSH_AGENT

ROOT = Path(__file__).resolve().parents[1]


def test_rev0064_arms_are_matched_policy_pairs() -> None:
    arms = rev0064_closure_vs_counter_arms(ROOT / "data" / "seed_decks.json")
    assert len(arms) == 6
    by_axis = {}
    for arm in arms:
        by_axis.setdefault(arm.size_axis, []).append(arm)
    assert set(by_axis) == {"counter60_vs_threat40", "counter40_vs_threat40", "counter60_vs_threat60"}
    for axis, axis_arms in by_axis.items():
        assert {a.opponent.agent_name for a in axis_arms} == {THREAT_RUSH_AGENT, THREAT_CLOSURE_AGENT}
        assert len({a.target.deck.size for a in axis_arms}) == 1
        assert len({a.opponent.deck.size for a in axis_arms}) == 1
        assert len({str(a.target.mulligan_policy) for a in axis_arms}) == 1
        assert len({str(a.opponent.mulligan_policy) for a in axis_arms}) == 1


def test_rev0064_specs_balance_seat_start_life_and_seed_ids() -> None:
    arms = rev0064_closure_vs_counter_arms(ROOT / "data" / "seed_decks.json")[:2]
    specs, meta = closure_vs_counter_specs(arms, simulator_revision="testrev", life_totals=(20,), reps=2, base_seed=1000)
    assert len(specs) == 2 * 1 * 2 * 2 * 2
    assert len(meta) == len(specs)
    assert len({s.seed for s in specs}) == len(specs)
    assert {m["target_seat"] for m in meta.values()} == {0, 1}
    assert {m["threat_seat"] for m in meta.values()} == {0, 1}
    assert {m["threat_policy_axis"] for m in meta.values()} == {"legacy_threat_rush", "library_aware_threat_closure"}


def test_rev0064_annotation_and_comparison_helpers() -> None:
    rows = [
        {"cpp_shadow_game_id": "g1", "p0_score": 1.0, "p1_score": 0.0, "loss_reason": "player_1_attempted_to_draw_from_empty_library", "decisions": 10, "turn_number": 5},
        {"cpp_shadow_game_id": "g2", "p0_score": 0.0, "p1_score": 1.0, "loss_reason": "player_0_life_total_zero_or_less", "decisions": 8, "turn_number": 4},
    ]
    meta = {
        "g1": {"target_seat": 0, "arm_id": "A_legacy_counter60_vs_threat40", "starting_life": 20, "size_axis": "counter60_vs_threat40", "threat_policy_axis": "legacy_threat_rush", "target_deck_size": 60, "opponent_deck_size": 40, "target": "counter", "opponent": "threat"},
        "g2": {"target_seat": 0, "arm_id": "A_closure_counter60_vs_threat40", "starting_life": 20, "size_axis": "counter60_vs_threat40", "threat_policy_axis": "library_aware_threat_closure", "target_deck_size": 60, "opponent_deck_size": 40, "target": "counter", "opponent": "threat"},
    }
    annotated = annotate_closure_vs_counter_rows(rows, meta)
    assert annotated[0]["focus_is_library_out_win"] is True
    assert annotated[1]["focus_target_result"] == "target_loss"
    summary_rows = [
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": "legacy_threat_rush", "starting_life": 20, "target_mean_score_draw_half": 0.8, "library_out_win_share": 1.0},
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": "library_aware_threat_closure", "starting_life": 20, "target_mean_score_draw_half": 0.4, "library_out_win_share": 0.0},
    ]
    comparison = compare_closure_vs_counter_by_life(summary_rows)[0]
    assert comparison["closure_minus_legacy_counter_score_delta"] == -0.4
    assert comparison["provisional_read"] == "counter_edge_mostly_legacy_threat_artifact"


def test_rev0064_gate_requires_cells_and_policy_coverage() -> None:
    summary = {
        "games": 144,
        "truncations": 0,
        "python_errors": 0,
        "closure_feature_games": 144,
        "cpp_shadow_summary": {"mismatches": 0, "skipped_events": 0},
    }
    feature_rows = []
    for axis in ("counter60_vs_threat40", "counter40_vs_threat40", "counter60_vs_threat60"):
        for policy in ("legacy_threat_rush", "library_aware_threat_closure"):
            feature_rows.append({"size_axis": axis, "threat_policy_axis": policy})
    assert closure_vs_counter_gate_report(summary, feature_rows)["passed"] is True
    assert closure_vs_counter_gate_report({**summary, "games": 30}, feature_rows)["passed"] is False


def test_rev0064_feature_comparison_adapter_uses_size_axis() -> None:
    rows = [
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": "legacy_threat_rush", "starting_life": 40, "mean_target_score": 0.7, "mean_threat_score": 0.3, "mean_threat_selfdeck_on_attack_trigger": 0.1, "mean_threat_selfdeck_on_overlord_cast": 0.0, "mean_threat_selfdeck_on_jace_zero": 0.5, "mean_threat_jace_zero_actions": 4.0, "mean_threat_declared_attackers_to_player": 1.0, "threat_selfdeck_losses": 7},
        {"size_axis": "counter60_vs_threat40", "threat_policy_axis": "library_aware_threat_closure", "starting_life": 40, "mean_target_score": 0.2, "mean_threat_score": 0.8, "mean_threat_selfdeck_on_attack_trigger": 0.0, "mean_threat_selfdeck_on_overlord_cast": 0.0, "mean_threat_selfdeck_on_jace_zero": 0.0, "mean_threat_jace_zero_actions": 0.0, "mean_threat_declared_attackers_to_player": 2.0, "threat_selfdeck_losses": 1},
    ]
    comparison = compare_closure_vs_counter_features_by_life(rows)[0]
    assert comparison["closure_threat_selfdeck_event_rate"] == 0.0
    assert comparison["legacy_threat_selfdeck_event_rate"] == 0.6
    assert comparison["provisional_read"] == "closure_guard_reduces_selfdeck_and_counter_score"
