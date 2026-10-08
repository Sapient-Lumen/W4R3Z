from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_rev0058_decomposition_outputs_are_present_and_gated():
    summary = json.loads((ROOT / "data" / "rev0058_decomposition_summary.json").read_text())
    assert summary["revision"] == "rev0058"
    assert summary["games"] == 192
    assert summary["decomposition_gate"]["passed"] is True
    assert summary["terminal_clean_summary"]["terminal_clean"] is True
    assert summary["cpp_shadow_summary"]["mismatches"] == 0
    assert summary["cpp_shadow_summary"]["skipped_events"] == 0
    assert summary["cpp_trace_summary"]["mismatches"] == 0
    assert summary["replay_passed"] == 8
    assert summary["raw_cpp_transition_rows_generated_but_not_shipped"] > 50000
    assert (ROOT / "data" / "rev0058_decomposition_cpp_transition_sample.csv").exists()
    assert not (ROOT / "data" / "rev0058_decomposition_cpp_transitions.csv").exists()


def test_rev0058_decomposition_directional_read_is_encoded():
    rows = list(csv.DictReader((ROOT / "data" / "rev0058_decomposition_comparisons.csv").open()))
    by_life = {int(r["starting_life"]): r for r in rows}
    assert set(by_life) == {20, 40}
    for row in by_life.values():
        assert float(row["original_score"]) > 0.65
        assert float(row["pilot_swap_score"]) < 0.40
        assert row["provisional_read"] == "edge_follows_counterwall_deck_shell_more_than_cf34_pilot"
