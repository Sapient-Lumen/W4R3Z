#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.confidence_floor import estimate_row, require_no_seed_overlap
from src.muc5.evaluation_design import audit_balanced_focal_rows, pair_symmetry_rows
from src.muc5.longgame import (
    cap_ladder_summary,
    evaluate_focal_pair_with_snapshots,
    run_cap_ladder_cell,
    summarize_longgame_axis,
)
from src.muc5.oracle_reporting import dump_json, rectangular_rows
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator
from src.muc5.transfer_stress import rev0092_admitted_strategy, rev0101_transfer_stress_panel

REV = "rev0102"
CODENAME = "longgame-capladder"
DATA = ROOT / "data"
OOD_STAGE = "rev0101_ood_stress"
REV0101_BASE_SEED = 10101010
COUNTER_AXIS_ID = "ood_counter_jace40"
CAPS = (1400, 1600, 2400, 3200, 5000)
AXIS_CONFIG = EmpiricalEvaluationConfig(
    life_totals=(20, 40),
    reps=24,
    max_decisions=3200,
    base_seed=10201020,
    confidence_z=1.96,
)
THRESHOLD = 0.5


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], *, fallback_fields: Sequence[str] = ()) -> None:
    material = rectangular_rows(rows)
    fields = list(material[0].keys()) if material else list(fallback_fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in material:
            writer.writerow(row)


def strategy_by_id(strategy_id: str):
    matches = [entry.strategy for entry in rev0101_transfer_stress_panel() if entry.strategy.strategy_id == strategy_id]
    if not matches:
        raise ValueError(f"unknown stress-panel strategy {strategy_id!r}")
    return matches[0]


def main() -> None:
    target = rev0092_admitted_strategy(ROOT)
    counter_axis = strategy_by_id(COUNTER_AXIS_ID)
    evaluator = EmpiricalGameEvaluator()

    rev0101_rows = read_csv_rows(DATA / "rev0101_transfer_stress_games.csv")
    truncated_source_rows = [
        row for row in rev0101_rows
        if row.get("opponent_strategy") == COUNTER_AXIS_ID and str(row.get("truncation", "")).lower() == "true"
    ]
    if not truncated_source_rows:
        raise SystemExit("expected at least one rev0101 truncated row on the counter/Jace axis")

    cap_rows: list[dict[str, object]] = []
    for source in truncated_source_rows:
        cap_rows.extend(
            run_cap_ladder_cell(
                evaluator,
                target,
                counter_axis,
                original_stage=OOD_STAGE,
                ladder_stage="rev0102_cap_ladder",
                base_seed=REV0101_BASE_SEED,
                starting_life=int(source["starting_life"]),
                rep=int(source["rep"]),
                orientation=int(source["orientation"]),
                starting_player=int(source["starting_player"]),
                max_decision_caps=CAPS,
            )
        )
    cap_summary = cap_ladder_summary(cap_rows)

    axis_estimate, axis_rows = evaluate_focal_pair_with_snapshots(
        evaluator,
        target,
        counter_axis,
        AXIS_CONFIG,
        stage="rev0102_counter_jace_axis_refresh",
    )
    axis_summary = summarize_longgame_axis(axis_estimate, axis_rows, max_decisions=AXIS_CONFIG.max_decisions, threshold=THRESHOLD)
    axis_pair = estimate_row(axis_estimate, stage="rev0102_counter_jace_axis_refresh")
    axis_pair.update(axis_summary.as_dict())

    design_audit = audit_balanced_focal_rows(
        axis_rows,
        expected_life_totals=AXIS_CONFIG.life_totals,
        expected_reps=AXIS_CONFIG.reps,
    )
    seed_audit = require_no_seed_overlap(axis_rows, cap_rows)
    symmetry_rows = pair_symmetry_rows(axis_rows)
    snapshot_leakage_violations = [
        row for row in [*axis_rows, *cap_rows]
        if row.get("hidden_identity_leakage_guard") != "counts_only_no_hand_or_library_identities"
    ]
    cap_max_rows = [row for row in cap_rows if int(row["max_decisions"]) == max(CAPS)]
    cap_max_remaining = [row for row in cap_max_rows if row.get("loss_reason") == "max_decisions_reached"]
    status = (
        "counter_jace_axis_confidence_floor_cleared_and_cap_resolved"
        if axis_summary.confidence_floor_cleared and not cap_max_remaining
        else "counter_jace_axis_still_open_due_to_confidence_or_persistent_cap"
    )

    audit_payload = {
        "schema": "muc5.rev0102.longgame_cap_ladder_audit.v1",
        "revision": REV,
        "codename": CODENAME,
        "passed": bool(
            design_audit["passed"]
            and seed_audit["passed"]
            and len(snapshot_leakage_violations) == 0
            and len(cap_rows) == len(truncated_source_rows) * len(CAPS)
            and axis_summary.games == 192
        ),
        "status": status,
        "design_audit": design_audit,
        "seed_audit": seed_audit,
        "snapshot_leakage_violations": len(snapshot_leakage_violations),
        "cap_ladder_summary": cap_summary,
        "axis_summary": axis_summary.as_dict(),
        "strategic_policy_promoted": False,
    }
    summary_payload = {
        "schema": "muc5.rev0102.longgame_cap_ladder_summary.v1",
        "revision": REV,
        "codename": CODENAME,
        "focus": "counter-control/Jace long-game cap ladder and high-cap axis refresh for the admitted PSRO response",
        "target_strategy": target.strategy_id,
        "opponent_strategy": COUNTER_AXIS_ID,
        "target_deck": target.deck.counts(),
        "opponent_deck": counter_axis.deck.counts(),
        "axis_config": AXIS_CONFIG.as_dict(),
        "cap_ladder_caps": list(CAPS),
        "rev0101_truncated_source_rows": len(truncated_source_rows),
        "cap_ladder": cap_summary,
        "axis_summary": axis_summary.as_dict(),
        "axis_pair_estimate": axis_pair,
        "design_audit_passed": design_audit["passed"],
        "seed_audit_passed": seed_audit["passed"],
        "snapshot_leakage_violations": len(snapshot_leakage_violations),
        "status": status,
        "strategic_policy_promoted": False,
        "read": (
            "rev0102 turns the rev0101 counter-control/Jace cap caveat into executable evidence. "
            "The ordinary payoff convention is unchanged: cap rows score 0.5. Snapshot diagnostics are counts-only and non-adjudicatory."
        ),
    }

    write_csv(DATA / "rev0102_longgame_cap_ladder_rows.csv", cap_rows)
    write_csv(DATA / "rev0102_counter_jace_axis_games.csv", axis_rows)
    write_csv(DATA / "rev0102_counter_jace_axis_pair_estimate.csv", [axis_pair])
    write_csv(DATA / "rev0102_counter_jace_axis_pair_symmetry.csv", symmetry_rows)
    dump_json(DATA / "rev0102_longgame_cap_ladder_summary.json", summary_payload)
    dump_json(DATA / "rev0102_longgame_cap_ladder_audit.json", audit_payload)
    print(json.dumps(summary_payload, indent=2, sort_keys=True))
    if not audit_payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
