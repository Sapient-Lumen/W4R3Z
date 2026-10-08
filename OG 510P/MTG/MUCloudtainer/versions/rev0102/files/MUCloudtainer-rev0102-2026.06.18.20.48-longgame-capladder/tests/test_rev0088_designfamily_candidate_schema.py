from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.population_candidate_gate import (
    candidate_evidence_contract_rows,
    candidate_gate_component_rows,
    candidate_gate_groups,
    summarize_candidate_evidence_contract,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def _delta(design: str, comparison: str = "same_score") -> dict[str, object]:
    return {
        "complete_pair": True,
        "sampling_design": design,
        "comparison": comparison,
        "candidate_minus_baseline_score": "0" if comparison == "same_score" else "-1",
        "baseline_mechanism": "life_total",
        "candidate_mechanism": "life_total",
    }


def test_gate_family_expands_for_new_sampling_designs() -> None:
    rows = []
    for design in ("selected_cell_seed_disjoint_holdout", "adaptive_candidate_transfer_seedpaired", "new_holdout_design"):
        rows.extend(_delta(design) for _ in range(4))
    groups = candidate_gate_groups(rows)
    labels = [group["label"] for group in groups]
    assert labels == ["overall", "transfer_panel", "design:new_holdout_design", "selected_cell_holdout"]

    components = candidate_gate_component_rows(rows)
    assert len(components) == 8
    assert {int(row["family_tests_used"]) for row in components} == {4}
    assert {row["label"] for row in components if row["group_kind"] == "sampling_design"} == {
        "selected_cell_holdout",
        "transfer_panel",
        "design:new_holdout_design",
    }


def test_candidate_evidence_contract_fails_missing_or_truthy_pool_flags() -> None:
    deltas = [_delta("adaptive_candidate_transfer_seedpaired")]
    games = [
        {
            "counter_policy_axis": "candidate",
            "sampling_design": "adaptive_candidate_transfer_seedpaired",
            "pair_key": "p1",
            "broad_pool_eligible": "False",
            "candidate_pool_eligible": "False",
            "adaptive_selection_source": "revX",
            "adaptive_selection_reason": "selected",
        },
        {
            "counter_policy_axis": "candidate",
            "sampling_design": "adaptive_candidate_transfer_seedpaired",
            "pair_key": "p2",
            "broad_pool_eligible": "true",
            "candidate_pool_eligible": "False",
            "adaptive_selection_source": "revX",
            "adaptive_selection_reason": "selected",
        },
        {
            "counter_policy_axis": "candidate",
            "sampling_design": "adaptive_candidate_transfer_seedpaired",
            "pair_key": "p3",
            "broad_pool_eligible": "False",
            "adaptive_selection_source": "revX",
            "adaptive_selection_reason": "selected",
        },
    ]
    rows = candidate_evidence_contract_rows(deltas, games)
    pool = next(row for row in rows if row["contract"] == "game_pool_flags_explicit_false")
    assert pool["missing_field_rows"] == 1
    assert pool["nonconforming_rows"] == 2
    assert pool["hard_fail"] is True
    summary = summarize_candidate_evidence_contract(rows, paired_delta_rows=len(deltas), game_rows=len(games), sampling_design_groups=2, family_tests_used=2)
    assert summary.passed is False
    assert summary.hard_fail_rows >= 1


def test_actual_rev0088_candidate_schema_contract_passes_and_keeps_stabilizer_blocked() -> None:
    summary = json.loads((DATA / "rev0088_candidate_designfamily_summary.json").read_text(encoding="utf-8"))
    gate = summary["candidate_gate"]
    contract = summary["evidence_contract"]
    assert summary["revision"] == "rev0088"
    assert summary["input_revision"] == "rev0084"
    assert summary["sampling_design_groups"] == 3
    assert summary["family_tests_used"] == 3
    assert summary["component_rows"] == 6
    assert gate["score_hard_fail_rows"] == 1
    assert gate["mechanism_hard_fail_rows"] == 2
    assert gate["candidate_pool_eligible"] is False
    assert gate["broad_pool_eligible"] is False
    assert contract["passed"] is True
    assert contract["hard_fail_rows"] == 0

    with (DATA / "rev0088_candidate_designfamily_schema_rows.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    assert {row["hard_fail"] for row in rows} == {"False"}
    family = next(row for row in rows if row["contract"] == "sampling_designs_have_family_rows")
    assert family["family_tests_used"] == "3"
    assert family["missing_design_groups"] == ""
