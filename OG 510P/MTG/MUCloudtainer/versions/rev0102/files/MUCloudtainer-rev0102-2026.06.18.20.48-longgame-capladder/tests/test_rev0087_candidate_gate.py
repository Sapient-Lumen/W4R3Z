from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.population_candidate_gate import build_candidate_gate, candidate_gate_component_rows, candidate_pool_leak_rows

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_candidate_gate_blocks_score_or_mechanism_hard_failures() -> None:
    rows = []
    for idx in range(12):
        rows.append(
            {
                "complete_pair": True,
                "sampling_design": "adaptive_candidate_transfer_seedpaired",
                "comparison": "guard_better" if idx < 11 else "candidate_better",
                "candidate_minus_baseline_score": "-1" if idx < 11 else "1",
                "baseline_mechanism": "life_total",
                "candidate_mechanism": "life_total",
            }
        )
    for idx in range(12):
        rows.append(
            {
                "complete_pair": True,
                "sampling_design": "selected_cell_seed_disjoint_holdout",
                "comparison": "same_score",
                "candidate_minus_baseline_score": "0",
                "baseline_mechanism": "life_total" if idx < 11 else "library_out",
                "candidate_mechanism": "library_out" if idx < 11 else "life_total",
            }
        )
    components = candidate_gate_component_rows(rows, primary_family_tests=3)
    hard = {(row["label"], row["component"]) for row in components if row["hard_fail"]}
    assert ("transfer_panel", "paired_score_transfer") in hard
    assert ("selected_cell_holdout", "same_score_mechanism_drift") in hard


def test_pool_leak_rows_parse_false_strings_and_catch_true_leak() -> None:
    games = [
        {
            "counter_policy_axis": "candidate",
            "sampling_design": "adaptive",
            "size_axis": "s",
            "broad_pool_eligible": "False",
            "candidate_pool_eligible": "False",
        },
        {
            "counter_policy_axis": "candidate",
            "sampling_design": "adaptive",
            "size_axis": "s",
            "broad_pool_eligible": "true",
            "candidate_pool_eligible": "0",
        },
    ]
    leaks = candidate_pool_leak_rows(games, candidate_axis="candidate")
    assert len(leaks) == 1
    assert leaks[0]["broad_pool_eligible_rows"] == 1
    assert leaks[0]["candidate_pool_eligible_rows"] == 0
    assert leaks[0]["hard_fail"] is True


def test_actual_rev0087_candidate_firewall_rejects_stabilizer() -> None:
    summary = json.loads((DATA / "rev0087_candidate_gate_summary.json").read_text(encoding="utf-8"))
    gate = summary["candidate_gate"]
    assert summary["revision"] == "rev0087"
    assert summary["input_revision"] == "rev0084"
    assert gate["paired_delta_rows"] == 240
    assert gate["game_rows"] == 480
    assert gate["primary_component_rows"] == 6
    assert gate["score_hard_fail_rows"] == 1
    assert gate["mechanism_hard_fail_rows"] == 2
    assert gate["pool_leak_fail_rows"] == 0
    assert gate["score_gate_passed"] is False
    assert gate["mechanism_gate_passed"] is False
    assert gate["pool_leak_gate_passed"] is True
    assert gate["candidate_pool_eligible"] is False
    assert gate["broad_pool_eligible"] is False
    assert set(gate["hard_fail_reasons"]) == {
        "score_tie_mechanism_drift_familywise_supported",
        "score_transfer_familywise_negative",
    }
    assert gate["status"] == "candidate_rejected_score_and_mechanism_firewall"

    with (DATA / "rev0087_candidate_gate_component_rows.csv").open(newline="", encoding="utf-8") as handle:
        components = list(csv.DictReader(handle))
    assert len(components) == 6
    hard = {(row["label"], row["component"], row["hard_fail_reason"]) for row in components if row["hard_fail"] == "True"}
    assert ("transfer_panel", "paired_score_transfer", "score_transfer_familywise_negative") in hard
    assert ("overall", "same_score_mechanism_drift", "score_tie_mechanism_drift_familywise_supported") in hard
    assert ("selected_cell_holdout", "same_score_mechanism_drift", "score_tie_mechanism_drift_familywise_supported") in hard

    with (DATA / "rev0087_candidate_gate_leak_audit.csv").open(newline="", encoding="utf-8") as handle:
        leaks = list(csv.DictReader(handle))
    assert len(leaks) == 8
    assert sum(int(row["broad_pool_eligible_rows"]) for row in leaks) == 0
    assert sum(int(row["candidate_pool_eligible_rows"]) for row in leaks) == 0
