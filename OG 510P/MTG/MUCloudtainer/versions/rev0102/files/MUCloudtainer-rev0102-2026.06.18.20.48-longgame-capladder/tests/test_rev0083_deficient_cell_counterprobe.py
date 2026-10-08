from __future__ import annotations

import csv
import json
from pathlib import Path

from src.muc5.counter_response import GUARDED_COUNTER_AXIS, LEGACY_COUNTER_AXIS
from src.muc5.deckspace import DeckVector
from src.muc5.population_counterprobe import (
    REPAIR_COUNTER_AXIS,
    deficient_cell_counterprobe_arms,
    paired_deficient_cell_specs,
    summarize_counterprobe_rescue,
)
from src.muc5.public_agents import make_public_agent

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_counter_life20_stabilizer_registered_as_public_agent() -> None:
    agent = make_public_agent("counter_life20_stabilizer")
    assert agent.name == "public_counter_life20_stabilizer_rev0012"


def test_paired_deficient_cell_specs_use_same_seed_grid_by_policy() -> None:
    arms = deficient_cell_counterprobe_arms(DATA / "seed_decks.json")
    specs, meta = paired_deficient_cell_specs(arms, simulator_revision="unit", reps=2, base_seed=123000)
    assert {arm.counter_policy_axis for arm in arms} == {LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS, REPAIR_COUNTER_AXIS}
    assert len(specs) == 3 * 2 * 2 * 2
    by_policy: dict[str, list[int]] = {}
    for spec in specs:
        axis = meta[spec.game_id]["counter_policy_axis"]
        by_policy.setdefault(axis, []).append(spec.seed)
        assert spec.starting_life == 20
        assert spec.deck0.size in {40}
        assert spec.deck1.size in {40}
    assert sorted(by_policy) == sorted([LEGACY_COUNTER_AXIS, GUARDED_COUNTER_AXIS, REPAIR_COUNTER_AXIS])
    seeds = {axis: sorted(values) for axis, values in by_policy.items()}
    assert seeds[LEGACY_COUNTER_AXIS] == seeds[GUARDED_COUNTER_AXIS] == seeds[REPAIR_COUNTER_AXIS]


def test_counterprobe_rescue_summary_distinguishes_certification_limited_from_deficient() -> None:
    rows = [
        {
            "counter_policy_axis": LEGACY_COUNTER_AXIS,
            "games": 64,
            "target_mean_score_draw_half": 0.20,
            "target_score_lcb_familywise_probe": 0.0,
            "target_score_ucb_familywise_probe": 0.39,
        },
        {
            "counter_policy_axis": GUARDED_COUNTER_AXIS,
            "games": 64,
            "target_mean_score_draw_half": 0.48,
            "target_score_lcb_familywise_probe": 0.29,
            "target_score_ucb_familywise_probe": 0.67,
        },
        {
            "counter_policy_axis": REPAIR_COUNTER_AXIS,
            "games": 64,
            "target_mean_score_draw_half": 0.55,
            "target_score_lcb_familywise_probe": 0.36,
            "target_score_ucb_familywise_probe": 0.74,
        },
    ]
    summary = summarize_counterprobe_rescue(rows, threshold=0.50)
    assert summary["status"] == "candidate_counter_repair_certification_limited"
    assert summary["counter_set_deficient_even_by_upper_bound"] is False
    assert summary["candidate_certified"] is False


def test_actual_rev0083_counterprobe_keeps_targeted_rows_out_of_broad_pool() -> None:
    summary = json.loads((DATA / "rev0083_deficient_cell_counterprobe_summary.json").read_text())
    assert summary["games"] == 192
    assert summary["seed_balance_complete_rows"] == 64
    assert summary["cpp_shadow_mismatches"] == 0
    assert summary["terminal_summary"]["truncation_rows"] == 0
    assert summary["broad_pool_eligible"] is False
    assert summary["status"] == "candidate_counter_repair_certification_limited"
    assert summary["candidate_axis"] == REPAIR_COUNTER_AXIS
    assert summary["candidate_mean"] >= 0.50
    assert summary["candidate_lcb"] < 0.50
    assert summary["paired_outcome_summary"]["rows"] == 64
    assert summary["paired_outcome_summary"]["candidate_mean_delta"] == 0.0

    with (DATA / "rev0083_deficient_cell_counterprobe_games.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 192
    assert {row["broad_pool_eligible"] for row in rows} == {"False"}
    assert {row["sampling_design"] for row in rows} == {"targeted_counterprobe_same_seed_grid"}

    with (DATA / "rev0083_deficient_cell_counterprobe_paired_outcome_delta.csv").open(newline="", encoding="utf-8") as handle:
        paired = list(csv.DictReader(handle))
    assert len(paired) == 64
    counts: dict[str, int] = {}
    for row in paired:
        counts[row["comparison"]] = counts.get(row["comparison"], 0) + 1
    assert counts.get("candidate_better", 0) == counts.get("guard_better", 0)
