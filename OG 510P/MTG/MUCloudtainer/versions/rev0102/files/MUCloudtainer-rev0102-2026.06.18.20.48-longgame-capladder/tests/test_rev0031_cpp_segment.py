from __future__ import annotations

from src.muc5.cpp_segment import cpp_segment_tool_status, build_nochoice_segment_specs, run_nochoice_segment_cpp_panel
from src.muc5.payoff import load_seed_decks
from src.muc5.strategy_sets import repeated_counterfactual_mulligan_gate_bundles


def test_cpp_segment_tool_builds():
    status = cpp_segment_tool_status().as_dict()
    assert status["usable"] is True
    assert status["gpp"]


def test_nochoice_segment_panel_smoke():
    strategies = repeated_counterfactual_mulligan_gate_bundles("data/seed_decks.json")[:3]
    specs = build_nochoice_segment_specs(strategies, life_totals=(20,), limit_pairs=2, base_seed=9310000, max_decisions=120)
    game_rows, segment_rows, summary = run_nochoice_segment_cpp_panel(specs, revision="test")
    assert len(game_rows) == 2
    assert summary.segments == len(segment_rows)
    assert summary.cpp_segment_mismatches == 0
    assert summary.skipped_events == 0
    assert summary.cpp_match_rate_on_checked_segments == 1.0
