from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS
from src.muc5.population_candidate_transfer import (
    candidate_transfer_arms,
    paired_candidate_delta_rows,
    paired_candidate_transfer_specs,
    summarize_candidate_transfer_rows,
)
from src.muc5.population_counterprobe import REPAIR_COUNTER_AXIS
from src.muc5.threat_response import CLOSURE_THREAT_AXIS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_candidate_transfer_specs_seed_pair_guard_and_candidate() -> None:
    arms = candidate_transfer_arms(
        DATA / "seed_decks.json",
        threat_axes=(CLOSURE_THREAT_AXIS,),
        size_axes=("counter40_vs_threat40",),
    )
    assert {arm.counter_policy_axis for arm in arms} == {GUARDED_COUNTER_AXIS, REPAIR_COUNTER_AXIS}
    specs, meta = paired_candidate_transfer_specs(arms, simulator_revision="unit", life_totals=(20,), reps=3, base_seed=123456)
    assert len(specs) == 2 * 1 * 1 * 1 * 2 * 2 * 3
    by_pair: dict[str, dict[str, int]] = {}
    for spec in specs:
        item = meta[spec.game_id]
        assert item["broad_pool_eligible"] is False
        assert item["candidate_pool_eligible"] is False
        assert spec.starting_life == 20
        by_pair.setdefault(item["pair_key"], {})[item["counter_policy_axis"]] = spec.seed
    assert len(by_pair) == 2 * 2 * 3
    for seeds in by_pair.values():
        assert set(seeds) == {GUARDED_COUNTER_AXIS, REPAIR_COUNTER_AXIS}
        assert seeds[GUARDED_COUNTER_AXIS] == seeds[REPAIR_COUNTER_AXIS]


def test_candidate_transfer_summary_quarantines_negative_transfer() -> None:
    rows = [
        {"pair_key": "a", "complete_pair": True, "counter_policy_axis": GUARDED_COUNTER_AXIS, "focus_target_score": 1.0},
        {"pair_key": "a", "complete_pair": True, "counter_policy_axis": REPAIR_COUNTER_AXIS, "focus_target_score": 0.0},
        {"pair_key": "b", "complete_pair": True, "counter_policy_axis": GUARDED_COUNTER_AXIS, "focus_target_score": 0.0},
        {"pair_key": "b", "complete_pair": True, "counter_policy_axis": REPAIR_COUNTER_AXIS, "focus_target_score": 0.0},
    ]
    deltas = paired_candidate_delta_rows(rows)
    summary = summarize_candidate_transfer_rows(deltas)
    assert summary.status == "candidate_quarantined_negative_transfer"
    assert summary.guard_better_pairs == 1
    assert summary.same_score_pairs == 1
    assert summary.candidate_dominates_pairwise is False


def test_actual_rev0084_candidate_transfer_keeps_stabilizer_quarantined() -> None:
    summary = json.loads((DATA / "rev0084_candidate_transfer_summary.json").read_text(encoding="utf-8"))
    assert summary["games"] == 480
    assert summary["complete_pairs"] == 240
    assert summary["python_errors"] == 0
    assert summary["terminal_summary"]["truncation_rows"] == 0
    assert summary["cpp_shadow_checked_events"] == 14000
    assert summary["cpp_shadow_mismatches"] == 0
    assert summary["candidate_axis"] == REPAIR_COUNTER_AXIS
    assert summary["baseline_axis"] == GUARDED_COUNTER_AXIS
    assert summary["candidate_broad_pool_eligible"] is False
    assert summary["candidate_pool_eligible"] is False
    assert summary["status"] == "candidate_quarantined_transfer_or_holdout_risk"
    assert summary["overall_summary"]["status"] == "candidate_quarantined_negative_transfer"
    assert summary["overall_summary"]["candidate_better_pairs"] < summary["overall_summary"]["guard_better_pairs"]
    assert summary["overall_summary"]["candidate_mean_delta"] < 0.0
    assert summary["holdout_summary"]["status"] == "candidate_quarantined_negative_transfer"
    assert summary["transfer_summary"]["status"] == "candidate_quarantined_negative_transfer"

    with (DATA / "rev0084_candidate_transfer_games.csv").open(newline="", encoding="utf-8") as handle:
        games = list(csv.DictReader(handle))
    assert len(games) == 480
    assert {row["broad_pool_eligible"] for row in games} == {"False"}
    assert {row["candidate_pool_eligible"] for row in games} == {"False"}
    assert {row["source_revision"] for row in games} == {"rev0084"}

    with (DATA / "rev0084_candidate_transfer_paired_deltas.csv").open(newline="", encoding="utf-8") as handle:
        deltas = list(csv.DictReader(handle))
    assert len(deltas) == 240
    assert {row["complete_pair"] for row in deltas} == {"True"}
