from __future__ import annotations

from src.muc5.truncation_rescue import annotate_rescued_rows, summarize_rescue, truncation_by_pair, truncation_by_strategy


def test_truncation_rescue_annotation_and_summary() -> None:
    baseline = [
        {"simulator_revision": "revX", "strategy0": "a", "strategy1": "b", "starting_life": 20, "starting_player": 0, "seed": 1, "is_truncation": True, "decisions": 380, "loss_reason": "max_decisions_reached", "winner": "None", "p0_score": 0.5, "p1_score": 0.5},
        {"simulator_revision": "revX", "strategy0": "b", "strategy1": "a", "starting_life": 20, "starting_player": 1, "seed": 2, "is_truncation": False, "decisions": 120, "loss_reason": "decking", "winner": "1", "p0_score": 0.0, "p1_score": 1.0},
    ]
    final = [
        {"simulator_revision": "revY", "strategy0": "a", "strategy1": "b", "starting_life": 20, "starting_player": 0, "seed": 1, "is_truncation": False, "decisions": 611, "loss_reason": "combat_damage", "winner": "0", "p0_score": 1.0, "p1_score": 0.0},
        {"simulator_revision": "revY", "strategy0": "b", "strategy1": "a", "starting_life": 20, "starting_player": 1, "seed": 2, "is_truncation": False, "decisions": 120, "loss_reason": "decking", "winner": "1", "p0_score": 0.0, "p1_score": 1.0},
    ]
    rows = annotate_rescued_rows(baseline, final, revision="revTest", baseline_max_decisions=380, final_max_decisions=900)
    assert rows[0]["simulator_revision"] == "revTest"
    assert rows[0]["baseline_is_truncation"] is True
    assert rows[0]["resolved_from_truncation"] is True
    assert rows[0]["truncation_rescue_status"] == "resolved_terminal"
    assert rows[1]["truncation_rescue_status"] == "already_terminal"
    summary = summarize_rescue(rows, revision="revTest", baseline_max_decisions=380, final_max_decisions=900)
    assert summary.baseline_truncations == 1
    assert summary.final_truncations == 0
    assert summary.resolved_truncations == 1
    assert summary.rescued_terminal_rate == 1.0
    by_strategy = truncation_by_strategy(rows)
    assert {r["strategy"] for r in by_strategy} == {"a", "b"}
    by_pair = truncation_by_pair(rows)
    assert len(by_pair) == 2
