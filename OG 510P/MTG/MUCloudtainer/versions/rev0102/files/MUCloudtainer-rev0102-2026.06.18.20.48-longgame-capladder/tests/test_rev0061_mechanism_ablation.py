from __future__ import annotations

from pathlib import Path

from src.muc5.deckspace import DeckVector
from src.muc5.mechanism_ablation import (
    compare_forensic_ablation_by_life,
    compare_mechanism_ablation_by_life,
    mechanism_ablation_gate_report,
    mechanism_ablation_specs,
    all_island_buffer_deck,
    replace_counterspell_with_islands,
    replace_jace_and_counterspell_with_islands,
    replace_jace_with_islands,
    rev0061_mechanism_ablation_arms,
)

ROOT = Path(__file__).resolve().parents[1]


def test_jace_and_counterspell_ablation_decks_preserve_size_and_counts():
    deck = DeckVector(60, 31, 16, 7, 5, 1)
    no_jace = replace_jace_with_islands(deck)
    assert no_jace == DeckVector(60, 36, 16, 7, 0, 1)
    assert no_jace.size == deck.size
    assert no_jace.counterspell == deck.counterspell
    assert no_jace.force == deck.force

    no_counter = replace_counterspell_with_islands(deck)
    assert no_counter == DeckVector(60, 47, 0, 7, 5, 1)
    assert no_counter.jace == deck.jace

    no_both = replace_jace_and_counterspell_with_islands(deck)
    assert no_both == DeckVector(60, 52, 0, 7, 0, 1)
    assert all_island_buffer_deck(60) == DeckVector(60, 60, 0, 0, 0, 0)


def test_rev0061_ablation_specs_have_expected_arms_and_target_meta():
    arms = rev0061_mechanism_ablation_arms(ROOT / "data" / "seed_decks.json")
    assert [a.arm_id for a in arms] == [
        "A_original_size_skew",
        "G_target_no_jace60",
        "H_target_no_counterspell60",
        "I_target_no_jace_no_counterspell60",
        "J_target_all_island60",
    ]
    specs, meta = mechanism_ablation_specs(arms, simulator_revision="rev0061-test", life_totals=(20,), reps=1, base_seed=1)
    assert len(specs) == 20  # five arms * two seats * two starting players * one rep
    no_jace_meta = [m for m in meta.values() if m["arm_id"] == "G_target_no_jace60"][0]
    assert no_jace_meta["target_jace_count"] == 0
    assert no_jace_meta["target_counterspell_count"] == 16
    no_counter_meta = [m for m in meta.values() if m["arm_id"] == "H_target_no_counterspell60"][0]
    assert no_counter_meta["target_counterspell_count"] == 0
    assert no_counter_meta["target_jace_count"] == 5


def test_compare_mechanism_ablation_by_life_and_gate():
    rows = [
        {"arm_id": "A_original_size_skew", "starting_life": 20, "target_mean_score_draw_half": 0.75, "library_out_win_share": 0.80},
        {"arm_id": "G_target_no_jace60", "starting_life": 20, "target_mean_score_draw_half": 0.67, "library_out_win_share": 0.70},
        {"arm_id": "H_target_no_counterspell60", "starting_life": 20, "target_mean_score_draw_half": 0.25, "library_out_win_share": 0.20},
        {"arm_id": "I_target_no_jace_no_counterspell60", "starting_life": 20, "target_mean_score_draw_half": 0.10, "library_out_win_share": 0.10},
        {"arm_id": "J_target_all_island60", "starting_life": 20, "target_mean_score_draw_half": 0.66, "library_out_win_share": 1.00},
    ]
    comp = compare_mechanism_ablation_by_life(rows)
    assert comp[0]["anchor_minus_no_counterspell"] == 0.50
    assert comp[0]["provisional_read"] == "passive_library_buffer_alone_is_competitive"

    gate = mechanism_ablation_gate_report({"games": 192, "truncations": 0, "python_errors": 0, "cpp_shadow_summary": {"mismatches": 0}}, rows)
    assert gate["passed"] is True


def test_compare_forensic_ablation_by_life_reports_feature_drops():
    rows = [
        {"arm_id": "A_original_size_skew", "starting_life": 20, "mean_focus_target_score": 0.75, "mean_target_library_buffer_final": 20, "mean_target_activate_jace_zero": 5, "mean_target_cast_counterspell": 8},
        {"arm_id": "G_target_no_jace60", "starting_life": 20, "mean_focus_target_score": 0.62, "mean_target_library_buffer_final": 12, "mean_target_activate_jace_zero": 0, "mean_target_cast_counterspell": 8},
        {"arm_id": "H_target_no_counterspell60", "starting_life": 20, "mean_focus_target_score": 0.25, "mean_target_library_buffer_final": -5, "mean_target_activate_jace_zero": 3, "mean_target_cast_counterspell": 0},
        {"arm_id": "J_target_all_island60", "starting_life": 20, "mean_focus_target_score": 0.65, "mean_target_library_buffer_final": 30, "mean_target_activate_jace_zero": 0, "mean_target_cast_counterspell": 0},
    ]
    comp = compare_forensic_ablation_by_life(rows)
    assert comp[0]["anchor_minus_no_counterspell_score"] == 0.50
    assert comp[0]["no_jace_target_jace_zero"] == 0
    assert comp[0]["no_counterspell_target_counterspell"] == 0
