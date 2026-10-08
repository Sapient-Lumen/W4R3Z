from __future__ import annotations

from src.muc5.terminal_decomposition import compare_decomposition_by_life, decomposition_gate_report, sample_transition_rows


def test_compare_decomposition_by_life_reports_effects_and_read():
    rows = [
        {"arm_id": "A_original_size_skew", "starting_life": 20, "target_mean_score_draw_half": 0.75, "library_out_win_share": 0.90},
        {"arm_id": "B_pilot_swap_size_skew", "starting_life": 20, "target_mean_score_draw_half": 0.35, "library_out_win_share": 1.00},
        {"arm_id": "C_equalized_40v40", "starting_life": 20, "target_mean_score_draw_half": 0.42, "library_out_win_share": 1.00},
        {"arm_id": "D_equalized_60v60", "starting_life": 20, "target_mean_score_draw_half": 0.58, "library_out_win_share": 0.80},
    ]
    comp = compare_decomposition_by_life(rows)
    assert len(comp) == 1
    assert comp[0]["original_minus_pilot_swap"] == 0.40
    assert abs(comp[0]["equalized_60v60_minus_40v40"] - 0.16) < 1e-12
    assert comp[0]["provisional_read"] == "edge_follows_counterwall_deck_shell_more_than_cf34_pilot"


def test_sample_transition_rows_keeps_mismatches_before_stride_sample():
    rows = [
        {"case_id": "a", "supported_by_cpp": True, "cpp_match": True},
        {"case_id": "b", "supported_by_cpp": True, "cpp_match": False},
        {"case_id": "c", "supported_by_cpp": False, "cpp_match": None},
        {"case_id": "d", "supported_by_cpp": True, "cpp_match": True},
    ]
    sample = sample_transition_rows(rows, limit=3)
    assert [r["case_id"] for r in sample[:2]] == ["b", "c"]
    assert len(sample) == 3


def test_decomposition_gate_report_is_revision_agnostic():
    summary = {
        "games": 384,
        "truncations": 0,
        "python_errors": 0,
        "cpp_shadow_summary": {"mismatches": 0, "skipped_events": 0},
        "cpp_trace_summary": {"mismatches": 0},
    }
    rows = [
        {"arm_id": "A_original_size_skew"},
        {"arm_id": "B_pilot_swap_size_skew"},
        {"arm_id": "C_equalized_40v40"},
        {"arm_id": "D_equalized_60v60"},
    ]
    replay = [{"passed": True} for _ in range(12)]
    gate = decomposition_gate_report(summary, replay, rows, min_games=384, min_replay_passed=12)
    assert gate["passed"] is True
    assert gate["errors"] == []
