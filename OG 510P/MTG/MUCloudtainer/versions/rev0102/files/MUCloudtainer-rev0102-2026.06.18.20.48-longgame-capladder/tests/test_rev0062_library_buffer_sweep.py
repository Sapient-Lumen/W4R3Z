from __future__ import annotations

from pathlib import Path

from src.muc5.deckspace import DeckVector
from src.muc5.library_buffer_sweep import (
    all_island_deck,
    compare_forensic_library_buffer_by_life,
    compare_library_buffer_by_life,
    library_buffer_gate_report,
    library_buffer_specs,
    rev0062_library_buffer_arms,
    scale_deck_to_legal_size,
)

ROOT = Path(__file__).resolve().parents[1]


def test_scale_deck_to_legal_size_preserves_positive_cards_and_legal_sizes():
    counter60 = DeckVector(60, 31, 16, 7, 5, 1)
    assert scale_deck_to_legal_size(counter60, 40) == DeckVector(40, 21, 10, 5, 3, 1)

    threat40 = DeckVector(40, 21, 7, 4, 2, 6)
    assert scale_deck_to_legal_size(threat40, 60) == DeckVector(60, 32, 10, 6, 3, 9)
    assert all_island_deck(40) == DeckVector(40, 40, 0, 0, 0, 0)
    assert all_island_deck(60) == DeckVector(60, 60, 0, 0, 0, 0)


def test_rev0062_specs_cover_legal_size_buffer_controls():
    arms = rev0062_library_buffer_arms(ROOT / "data" / "seed_decks.json")
    assert [a.arm_id for a in arms] == [
        "A_counter60_vs_threat40",
        "K_buffer40_vs_threat40",
        "J_buffer60_vs_threat40",
        "L_buffer60_vs_threat60",
        "M_counter40_vs_threat40",
        "N_counter60_vs_threat60",
        "O_buffer40_vs_threat60",
    ]
    specs, meta = library_buffer_specs(arms, simulator_revision="rev0062-test", life_totals=(20,), reps=1, base_seed=1)
    assert len(specs) == 28  # seven arms * two seats * two starting players * one rep
    assert {m["size_axis"] for m in meta.values()} == {
        "target60_opponent40",
        "target40_opponent40",
        "target60_opponent60",
        "target40_opponent60",
    }
    scaled_counter = next(m for m in meta.values() if m["arm_id"] == "M_counter40_vs_threat40")
    assert scaled_counter["target_deck_size"] == 40
    assert scaled_counter["target_overlord_count"] == 1
    scaled_threat = next(m for m in meta.values() if m["arm_id"] == "L_buffer60_vs_threat60")
    assert scaled_threat["opponent_deck_size"] == 60
    assert scaled_threat["opponent_overlord_count"] == 9


def test_compare_library_buffer_by_life_exposes_size_and_normalization_deltas():
    rows = [
        {"arm_id": "A_counter60_vs_threat40", "starting_life": 20, "target_mean_score_draw_half": 0.80, "library_out_win_share": 0.9},
        {"arm_id": "K_buffer40_vs_threat40", "starting_life": 20, "target_mean_score_draw_half": 0.30, "library_out_win_share": 1.0},
        {"arm_id": "J_buffer60_vs_threat40", "starting_life": 20, "target_mean_score_draw_half": 0.70, "library_out_win_share": 1.0},
        {"arm_id": "L_buffer60_vs_threat60", "starting_life": 20, "target_mean_score_draw_half": 0.20, "library_out_win_share": 1.0},
        {"arm_id": "M_counter40_vs_threat40", "starting_life": 20, "target_mean_score_draw_half": 0.55, "library_out_win_share": 0.5},
        {"arm_id": "N_counter60_vs_threat60", "starting_life": 20, "target_mean_score_draw_half": 0.35, "library_out_win_share": 0.5},
        {"arm_id": "O_buffer40_vs_threat60", "starting_life": 20, "target_mean_score_draw_half": 0.05, "library_out_win_share": 1.0},
    ]
    comp = compare_library_buffer_by_life(rows)[0]
    assert round(comp["passive_size_delta_buffer60_minus_buffer40_vs_threat40"], 6) == 0.40
    assert round(comp["opponent_size_normalization_drop_buffer60_threat40_minus_threat60"], 6) == 0.50
    assert round(comp["active_counterwall_value_at_40_counter40_minus_buffer40"], 6) == 0.25
    assert comp["provisional_read"] == "strong_60v40_passive_size_exploit"


def test_compare_forensic_library_buffer_by_life_reports_library_buffer_deltas():
    rows = [
        {"arm_id": "K_buffer40_vs_threat40", "starting_life": 20, "mean_focus_target_score": 0.30, "mean_target_library_buffer_final": -5},
        {"arm_id": "J_buffer60_vs_threat40", "starting_life": 20, "mean_focus_target_score": 0.70, "mean_target_library_buffer_final": 25},
        {"arm_id": "L_buffer60_vs_threat60", "starting_life": 20, "mean_focus_target_score": 0.20, "mean_target_library_buffer_final": -10},
    ]
    comp = compare_forensic_library_buffer_by_life(rows)[0]
    assert comp["passive_size_delta_final_library_buffer"] == 30
    assert comp["normalization_drop_final_library_buffer"] == 35


def test_library_buffer_gate_report_requires_arms_and_clean_rollout():
    rows = [{"arm_id": arm} for arm in (
        "A_counter60_vs_threat40",
        "K_buffer40_vs_threat40",
        "J_buffer60_vs_threat40",
        "L_buffer60_vs_threat60",
        "M_counter40_vs_threat40",
        "N_counter60_vs_threat60",
        "O_buffer40_vs_threat60",
    )]
    gate = library_buffer_gate_report({"games": 280, "truncations": 0, "python_errors": 0, "cpp_shadow_summary": {"mismatches": 0}}, rows)
    assert gate["passed"] is True
