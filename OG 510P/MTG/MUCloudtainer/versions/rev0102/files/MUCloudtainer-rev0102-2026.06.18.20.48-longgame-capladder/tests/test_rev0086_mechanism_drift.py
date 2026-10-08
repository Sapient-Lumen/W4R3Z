from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.population_pair_forensics import (
    mechanism_drift_summary,
    mechanism_flip_direction,
    same_score_mechanism_flip_rows,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_mechanism_drift_summary_detects_familywise_library_shift() -> None:
    rows = [
        {
            "complete_pair": True,
            "comparison": "same_score",
            "baseline_mechanism": "life_total",
            "candidate_mechanism": "library_out",
        }
        for _ in range(9)
    ] + [
        {
            "complete_pair": True,
            "comparison": "same_score",
            "baseline_mechanism": "library_out",
            "candidate_mechanism": "life_total",
        }
    ]
    summary = mechanism_drift_summary(rows, label="unit", family_tests=3)
    assert summary.same_score_mechanism_flip_pairs == 10
    assert summary.life_to_library_flips == 9
    assert summary.library_to_life_flips == 1
    assert abs(summary.one_sided_p_candidate_library_shift - 0.0107421875) < 1e-15
    assert summary.candidate_library_shift_familywise_supported is True
    assert summary.status == "candidate_same_score_shift_toward_library_out_supported"


def test_same_score_flip_rows_are_compact_and_exclude_same_mechanism_ties() -> None:
    rows = [
        {
            "pair_key": "p0",
            "complete_pair": True,
            "comparison": "same_score",
            "baseline_mechanism": "life_total",
            "candidate_mechanism": "library_out",
            "starting_life": "20",
            "target_seat": "1",
            "starting_player": "0",
            "rep": "7",
            "paired_seed": "123",
            "baseline_score": "1.0",
            "candidate_score": "1.0",
        },
        {
            "pair_key": "p1",
            "complete_pair": True,
            "comparison": "same_score",
            "baseline_mechanism": "library_out",
            "candidate_mechanism": "library_out",
        },
        {
            "pair_key": "p2",
            "complete_pair": True,
            "comparison": "guard_better",
            "baseline_mechanism": "life_total",
            "candidate_mechanism": "library_out",
        },
    ]
    flips = same_score_mechanism_flip_rows(rows)
    assert len(flips) == 1
    assert flips[0]["pair_key"] == "p0"
    assert flips[0]["mechanism_direction"] == "life_to_library"
    assert flips[0]["starting_life"] == 20
    assert mechanism_flip_direction(rows[1]) == "same_mechanism"


def test_actual_rev0086_mechanism_drift_tightens_tie_contract() -> None:
    summary = json.loads((DATA / "rev0086_mechanism_drift_summary.json").read_text(encoding="utf-8"))
    assert summary["revision"] == "rev0086"
    assert summary["input_revision"] == "rev0084"
    assert summary["paired_delta_rows"] == 240
    assert summary["overall_same_score_pairs"] == 207
    assert summary["overall_score_and_mechanism_equivalent_pairs"] == 189
    assert summary["overall_same_score_mechanism_flip_pairs"] == 18
    assert summary["overall_life_to_library_flips"] == 16
    assert summary["overall_library_to_life_flips"] == 2
    assert abs(summary["overall_one_sided_p_candidate_library_shift"] - 0.0006561279296875) < 1e-15
    assert summary["overall_candidate_library_shift_familywise_supported"] is True
    assert summary["holdout_candidate_library_shift_familywise_supported"] is True
    assert summary["transfer_candidate_library_shift_familywise_supported"] is False
    assert summary["candidate_library_shift_supported_primary_rows"] == 2
    assert summary["candidate_life_shift_supported_primary_rows"] == 0
    assert summary["candidate_broad_pool_eligible"] is False
    assert summary["candidate_pool_eligible"] is False
    assert summary["status"] == "candidate_quarantined_score_tie_library_out_drift"

    with (DATA / "rev0086_primary_mechanism_drift.csv").open(newline="", encoding="utf-8") as handle:
        primary = {row["label"]: row for row in csv.DictReader(handle)}
    assert set(primary) == {"overall", "selected_cell_holdout", "transfer_panel"}
    assert primary["overall"]["candidate_library_shift_familywise_supported"] == "True"
    assert primary["transfer_panel"]["candidate_library_shift_familywise_supported"] == "False"

    with (DATA / "rev0086_same_score_mechanism_flips.csv").open(newline="", encoding="utf-8") as handle:
        flips = list(csv.DictReader(handle))
    assert len(flips) == 18
    directions = {row["mechanism_direction"] for row in flips}
    assert directions == {"life_to_library", "library_to_life"}
