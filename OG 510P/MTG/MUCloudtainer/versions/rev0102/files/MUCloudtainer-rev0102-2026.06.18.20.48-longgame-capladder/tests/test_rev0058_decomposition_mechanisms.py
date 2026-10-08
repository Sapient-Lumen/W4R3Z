from __future__ import annotations

from pathlib import Path

from src.muc5.terminal_decomposition import (
    decomposition_specs,
    proportional_counterwall_40,
    proportional_overlord_60,
    rev0058_decomposition_arms,
)
from src.muc5.terminal_mechanisms import (
    annotate_target_mechanism,
    loss_loser,
    mechanism_profile_rows,
    target_summary_rows,
    terminal_mechanism,
)


ROOT = Path(__file__).resolve().parents[1]


def test_terminal_mechanism_parser_and_annotation():
    assert loss_loser("player_1_draw_from_empty_library") == 1
    assert terminal_mechanism("player_1_draw_from_empty_library") == "library_out"
    assert terminal_mechanism("player_0_life_total_zero_or_less") == "life_total"
    row = annotate_target_mechanism(
        {
            "focus_target_score": 1.0,
            "focus_target_seat": 0,
            "loss_reason": "player_1_draw_from_empty_library",
        }
    )
    assert row["focus_target_result"] == "target_win"
    assert row["focus_terminal_mechanism"] == "library_out"
    assert row["focus_terminal_loser_role"] == "opponent"
    assert row["focus_is_library_out_win"] is True


def test_mechanism_and_target_summaries_are_grouped():
    rows = [
        {"arm_id": "A", "starting_life": 20, "focus_target_score": 1.0, "focus_target_seat": 0, "loss_reason": "player_1_draw_from_empty_library", "decisions": 10, "turn_number": 5},
        {"arm_id": "A", "starting_life": 20, "focus_target_score": 0.0, "focus_target_seat": 0, "loss_reason": "player_0_life_total_zero_or_less", "decisions": 12, "turn_number": 6},
    ]
    profile = mechanism_profile_rows(rows, group_keys=("arm_id", "starting_life"))
    assert {r["terminal_mechanism"] for r in profile} == {"library_out", "life_total"}
    summary = target_summary_rows(rows, group_keys=("arm_id", "starting_life"))
    assert summary[0]["games"] == 2
    assert summary[0]["target_library_out_wins"] == 1
    assert summary[0]["target_terminal_wins"] == 1


def test_rev0058_decomposition_arms_and_specs_contract():
    assert proportional_counterwall_40().size == 40
    assert proportional_overlord_60().size == 60
    arms = rev0058_decomposition_arms(ROOT / "data" / "seed_decks.json")
    assert [a.arm_id for a in arms] == [
        "A_original_size_skew",
        "B_pilot_swap_size_skew",
        "C_equalized_40v40",
        "D_equalized_60v60",
        "E_same_deck_counter60_pilot",
        "F_same_deck_overlord40_pilot",
    ]
    specs, meta = decomposition_specs(arms[:2], simulator_revision="test", life_totals=(20,), reps=2, base_seed=100)
    assert len(specs) == 16  # 2 arms * 1 life * 2 target seats * 2 starting players * 2 reps
    assert len(meta) == len(specs)
    assert {m["target_seat"] for m in meta.values()} == {0, 1}
    assert all(s.simulator_revision == "test" for s in specs)
