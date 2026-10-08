from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.population_pair_forensics import (
    binomial_tail_at_least,
    paired_sign_summary,
    pair_integrity_rows,
    summarize_pair_integrity,
    tie_mechanism_summary,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_exact_binomial_tail_and_familywise_status() -> None:
    assert abs(binomial_tail_at_least(13, 15) - 0.003692626953125) < 1e-15
    rows = [
        {"complete_pair": True, "comparison": "guard_better", "candidate_minus_baseline_score": -1.0}
        for _ in range(13)
    ] + [
        {"complete_pair": True, "comparison": "candidate_better", "candidate_minus_baseline_score": 1.0}
        for _ in range(2)
    ]
    summary = paired_sign_summary(rows, label="unit", family_tests=3)
    assert summary.non_tie_pairs == 15
    assert summary.guard_better_pairs == 13
    assert summary.negative_transfer_familywise_supported is True
    assert summary.status == "candidate_quarantined_exact_sign_negative_transfer"


def test_pair_integrity_catches_seed_or_context_mismatch() -> None:
    rows = [
        {
            "pair_key": "p0",
            "counter_policy_axis": "public_counter_guard",
            "seed": 1,
            "transition_seed": 1,
            "agent_seed": 2,
            "paired_seed": 1,
            "sampling_design": "x",
            "size_axis": "s",
            "starting_life": 20,
            "target_seat": 0,
            "starting_player": 0,
            "rep": 0,
            "threat_policy_axis": "t",
            "broad_pool_eligible": False,
            "candidate_pool_eligible": False,
        },
        {
            "pair_key": "p0",
            "counter_policy_axis": "public_counter_life20_stabilizer",
            "seed": 99,
            "transition_seed": 1,
            "agent_seed": 2,
            "paired_seed": 1,
            "sampling_design": "x",
            "size_axis": "s",
            "starting_life": 40,
            "target_seat": 0,
            "starting_player": 0,
            "rep": 0,
            "threat_policy_axis": "t",
            "broad_pool_eligible": False,
            "candidate_pool_eligible": False,
        },
    ]
    integrity = pair_integrity_rows(rows)
    assert integrity[0]["complete_pair"] is True
    assert integrity[0]["seed_mismatch"] is True
    assert integrity[0]["context_mismatch"] is True
    summary = summarize_pair_integrity(integrity)
    assert summary.passed is False
    assert summary.seed_mismatches == 1
    assert summary.context_mismatches == 1


def test_tie_mechanism_forensics_warns_on_non_equivalent_ties() -> None:
    rows = [
        {
            "complete_pair": True,
            "comparison": "same_score",
            "baseline_mechanism": "life_total",
            "candidate_mechanism": "library_out",
            "baseline_loss_reason": "life",
            "candidate_loss_reason": "library",
        },
        {
            "complete_pair": True,
            "comparison": "same_score",
            "baseline_mechanism": "life_total",
            "candidate_mechanism": "life_total",
            "baseline_loss_reason": "life",
            "candidate_loss_reason": "life",
        },
    ]
    summary = tie_mechanism_summary(rows, label="unit")
    assert summary.same_score_pairs == 2
    assert summary.same_score_mechanism_flip_pairs == 1
    assert summary.life_to_library_flips == 1
    assert summary.tie_equivalence_warning is True


def test_actual_rev0085_pair_forensics_refines_rev0084_quarantine() -> None:
    summary = json.loads((DATA / "rev0085_pair_integrity_summary.json").read_text(encoding="utf-8"))
    assert summary["input_revision"] == "rev0084"
    assert summary["games"] == 480
    assert summary["paired_delta_rows"] == 240
    assert summary["pair_integrity"]["passed"] is True
    assert summary["pair_integrity"]["complete_pairs"] == 240
    assert summary["pair_integrity"]["seed_mismatches"] == 0
    assert summary["pair_integrity"]["context_mismatches"] == 0
    assert summary["overall_same_score_pairs"] == 207
    assert summary["overall_same_score_mechanism_flip_pairs"] == 18
    assert summary["tie_equivalence_warning"] is True
    assert summary["transfer_familywise_negative_supported"] is True
    assert summary["holdout_familywise_negative_supported"] is False
    assert summary["overall_familywise_negative_supported"] is False
    assert summary["candidate_dominance_supported_primary_rows"] == 0
    assert summary["negative_transfer_supported_primary_rows"] == 1
    assert summary["status"] == "candidate_quarantined_transfer_panel_exact_sign_negative_transfer"

    with (DATA / "rev0085_primary_sign_tests.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["label"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"overall", "selected_cell_holdout", "transfer_panel"}
    assert abs(float(rows["transfer_panel"]["one_sided_p_candidate_worse"]) - 0.003692626953125) < 1e-15
    assert abs(float(rows["overall"]["one_sided_p_candidate_worse"]) - 0.01754101668484509) < 1e-15
