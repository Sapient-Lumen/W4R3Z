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
from src.muc5.oracle_reporting import dump_json, rectangular_rows, stage_counts
from src.muc5.agents import play_public_agent_game
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator, stable_seed
from src.muc5.transfer_stress import (
    audit_transfer_stress_panel,
    estimate_panel_rows,
    family_summary_rows,
    rev0092_admitted_strategy,
    rev0101_transfer_stress_panel,
    summarize_transfer_stress,
)

REV = "rev0101"
CODENAME = "transferstress-oodpanel"
DATA = ROOT / "data"

STRESS_CONFIG = EmpiricalEvaluationConfig(
    life_totals=(20, 40),
    reps=20,
    max_decisions=1400,
    base_seed=10101010,
    confidence_z=1.96,
)
SELF_CONTROL_CONFIG = EmpiricalEvaluationConfig(
    life_totals=(20, 40),
    reps=20,
    max_decisions=1400,
    base_seed=10101910,
    confidence_z=1.96,
)
THRESHOLD = 0.5
RESCUE_MAX_DECISIONS = 1600



def rescue_truncated_cells(
    evaluator: EmpiricalGameEvaluator,
    target,
    panel,
    truncated_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Rerun only the exact truncated cells with a larger cap.

    The deterministic seed does not include max_decisions, so preserving the
    original stage/base/opponent/life/rep/orientation/start tuple replays the
    same shuffled game.  This avoids rerunning a whole 160-row pair just to
    learn whether a single long game was an operational cap artifact.
    """

    if not truncated_rows:
        return []
    by_id = {entry.strategy.strategy_id: entry for entry in panel}
    rescue_rows: list[dict[str, object]] = []
    for original in truncated_rows:
        opponent_id = str(original["opponent_strategy"])
        entry = by_id[opponent_id]
        life = int(original["starting_life"])
        rep = int(original["rep"])
        orientation = int(original["orientation"])
        starting_player = int(original["starting_player"])
        seat0, seat1 = (target, entry.strategy) if orientation == 0 else (entry.strategy, target)
        focal_player = 0 if orientation == 0 else 1
        seed = stable_seed(
            STRESS_CONFIG.base_seed,
            "rev0101_ood_stress",
            target.strategy_id,
            entry.strategy.strategy_id,
            life,
            rep,
            orientation,
            starting_player,
        )
        state, result = play_public_agent_game(
            seat0.deck,
            seat1.deck,
            evaluator.agent(seat0, 0),  # type: ignore[arg-type]
            evaluator.agent(seat1, 1),  # type: ignore[arg-type]
            seed=seed,
            transition_seed=seed,
            agent_seed=seed + 1000003,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=RESCUE_MAX_DECISIONS,
            mulligan_agents=(evaluator.mulligan(seat0, 0), evaluator.mulligan(seat1, 1)),  # type: ignore[arg-type]
            record_log=False,
            episode_id=f"rev0101_truncation_rescue:{target.strategy_id}:{entry.strategy.strategy_id}:{life}:{rep}:{orientation}:{starting_player}",
        )
        score = 0.5 if result.winner is None else (1.0 if result.winner == focal_player else 0.0)
        rescue_rows.append(
            {
                "stage": "rev0101_truncation_rescue",
                "focal_strategy": target.strategy_id,
                "opponent_strategy": entry.strategy.strategy_id,
                "strategy0": seat0.strategy_id,
                "strategy1": seat1.strategy_id,
                "focal_player": focal_player,
                "starting_player": starting_player,
                "starting_life": life,
                "rep": rep,
                "orientation": orientation,
                "seed": seed,
                "score": score,
                "winner": "None" if result.winner is None else result.winner,
                "loss_reason": result.loss_reason,
                "truncation": result.loss_reason == "max_decisions_reached",
                "decisions": result.decisions,
                "turn_number": state.turn_number,
                "interface": "public_decision_frame+information_state",
                "stress_family": entry.stress_family,
                "opponent_agent_name": entry.strategy.agent_name,
                "opponent_mulligan_policy": str(entry.strategy.mulligan_policy),
                "opponent_deck_name": entry.strategy.deck_name,
                "opponent_deck_size": entry.strategy.deck.size,
                "source_revision": REV,
                "original_max_decisions": STRESS_CONFIG.max_decisions,
                "rescue_max_decisions": RESCUE_MAX_DECISIONS,
            }
        )
    return rescue_rows

def write_csv(path: Path, rows: Iterable[Mapping[str, object]], *, fallback_fields: Sequence[str] = ()) -> None:
    material = rectangular_rows(rows)
    fields = list(material[0].keys()) if material else list(fallback_fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in material:
            writer.writerow(row)


def main() -> None:
    target = rev0092_admitted_strategy(ROOT)
    panel = rev0101_transfer_stress_panel()
    panel_audit = audit_transfer_stress_panel(panel, root=ROOT, focal=target)
    if not panel_audit["passed"]:
        raise SystemExit(f"transfer stress panel failed audit: {json.dumps(panel_audit, sort_keys=True)}")

    evaluator = EmpiricalGameEvaluator()
    estimates = []
    game_rows: list[dict[str, object]] = []
    for entry in panel:
        estimate, rows = evaluator.evaluate_focal_pair(
            target,
            entry.strategy,
            STRESS_CONFIG,
            stage="rev0101_ood_stress",
        )
        estimates.append(estimate)
        for row in rows:
            row["stress_family"] = entry.stress_family
            row["opponent_agent_name"] = entry.strategy.agent_name
            row["opponent_mulligan_policy"] = str(entry.strategy.mulligan_policy)
            row["opponent_deck_name"] = entry.strategy.deck_name
            row["opponent_deck_size"] = entry.strategy.deck.size
            row["source_revision"] = REV
        game_rows.extend(rows)

    self_estimate, self_rows = evaluator.evaluate_focal_pair(
        target,
        target,
        SELF_CONTROL_CONFIG,
        stage="rev0101_self_control",
    )
    for row in self_rows:
        row["stress_family"] = "self_control"
        row["opponent_agent_name"] = target.agent_name
        row["opponent_mulligan_policy"] = str(target.mulligan_policy)
        row["opponent_deck_name"] = target.deck_name
        row["opponent_deck_size"] = target.deck.size
        row["source_revision"] = REV

    truncated_rows = [row for row in game_rows if bool(row.get("truncation"))]
    rescue_rows = rescue_truncated_cells(evaluator, target, panel, truncated_rows)
    rescue_remaining = [row for row in rescue_rows if bool(row.get("truncation"))]

    design_audit = audit_balanced_focal_rows(
        game_rows,
        expected_life_totals=STRESS_CONFIG.life_totals,
        expected_reps=STRESS_CONFIG.reps,
    )
    self_design_audit = audit_balanced_focal_rows(
        self_rows,
        expected_life_totals=SELF_CONTROL_CONFIG.life_totals,
        expected_reps=SELF_CONTROL_CONFIG.reps,
    )
    seed_audit = require_no_seed_overlap(game_rows, self_rows)
    rescue_seed_audit = require_no_seed_overlap(rescue_rows, self_rows) if rescue_rows else {"passed": True, "group_seed_counts": [0, 0], "overlap_count": 0, "overlaps": []}
    summary = summarize_transfer_stress(target.strategy_id, panel, estimates, threshold=THRESHOLD)
    estimate_rows = estimate_panel_rows(estimates, panel, stage="rev0101_ood_stress")
    family_rows = family_summary_rows(estimates, panel, threshold=THRESHOLD)
    symmetry = pair_symmetry_rows([*game_rows, *self_rows])
    catalog_rows = [entry.as_dict() for entry in panel]
    self_estimate_row = estimate_row(self_estimate, stage="rev0101_self_control")

    weakest_rows = sorted(estimate_rows, key=lambda row: (float(row["ci_low"]), float(row["mean_score"])))[:3]
    status = (
        "ood_confidence_floor_survives_fixed_panel"
        if summary.confidence_floor_cleared
        else "ood_mean_floor_survives_but_truncation_or_confidence_floor_remains_open"
        if summary.min_mean_score > THRESHOLD
        else "ood_mean_floor_breached_fixed_panel"
    )
    audit_payload = {
        "schema": "muc5.rev0101.transfer_stress_audit.v1",
        "revision": REV,
        "codename": CODENAME,
        "passed": bool(
            panel_audit["passed"]
            and design_audit["passed"]
            and self_design_audit["passed"]
            and seed_audit["passed"]
            and rescue_seed_audit["passed"]
            and (not truncated_rows or len(rescue_rows) == len(truncated_rows))
            and self_estimate.truncations == 0
        ),
        "panel_audit": panel_audit,
        "design_audit": design_audit,
        "self_design_audit": self_design_audit,
        "seed_audit": seed_audit,
        "rescue_seed_audit": rescue_seed_audit,
        "truncation_rescue": {
            "attempted": bool(truncated_rows),
            "original_truncated_rows": len(truncated_rows),
            "rescue_rows": len(rescue_rows),
            "remaining_truncations_after_rescue": len(rescue_remaining),
            "rescue_max_decisions": RESCUE_MAX_DECISIONS,
        },
        "summary": summary.as_dict(),
        "self_control": self_estimate_row,
        "stage_counts": stage_counts([*game_rows, *self_rows]),
        "status": status,
    }
    summary_payload = {
        "schema": "muc5.rev0101.transfer_stress_summary.v1",
        "revision": REV,
        "codename": CODENAME,
        "focus": "out-of-distribution transfer stress for the admitted PSRO response after rev0100 confidence-floor evidence",
        "target_strategy": target.strategy_id,
        "target_deck": target.deck.counts(),
        "target_agent": target.agent_name,
        "target_mulligan": str(target.mulligan_policy),
        "stress_config": STRESS_CONFIG.as_dict(),
        "self_control_config": SELF_CONTROL_CONFIG.as_dict(),
        "summary": summary.as_dict(),
        "self_control": self_estimate_row,
        "weakest_rows_by_ci_low": weakest_rows,
        "family_summary": family_rows,
        "panel_audit": panel_audit,
        "design_audit_passed": design_audit["passed"],
        "self_design_audit_passed": self_design_audit["passed"],
        "seed_audit_passed": seed_audit["passed"],
        "rescue_seed_audit_passed": rescue_seed_audit["passed"],
        "truncation_rescue": {
            "attempted": bool(truncated_rows),
            "original_truncated_rows": len(truncated_rows),
            "rescue_rows": len(rescue_rows),
            "remaining_truncations_after_rescue": len(rescue_remaining),
            "rescue_max_decisions": RESCUE_MAX_DECISIONS,
        },
        "mean_floor_above_half_ignoring_truncation_gate": bool(summary.min_mean_score > THRESHOLD),
        "total_game_rows": len(game_rows) + len(self_rows),
        "ood_game_rows": len(game_rows),
        "self_control_rows": len(self_rows),
        "status": status,
        "strategic_policy_promoted": False,
        "read": (
            "This fixed OOD panel is a falsification and transfer audit for the current admitted PSRO response. "
            "It is deliberately outside the original eight-incumbent confidence floor and does not promote a strategy."
        ),
    }

    write_csv(DATA / "rev0101_transfer_stress_panel.csv", catalog_rows)
    write_csv(DATA / "rev0101_transfer_stress_games.csv", game_rows)
    write_csv(DATA / "rev0101_transfer_stress_pair_estimates.csv", estimate_rows)
    write_csv(DATA / "rev0101_transfer_stress_family_summary.csv", family_rows)
    write_csv(DATA / "rev0101_transfer_stress_pair_symmetry.csv", symmetry)
    write_csv(DATA / "rev0101_transfer_stress_self_control.csv", [self_estimate_row])
    write_csv(DATA / "rev0101_transfer_stress_truncation_rescue.csv", rescue_rows)
    dump_json(DATA / "rev0101_transfer_stress_summary.json", summary_payload)
    dump_json(DATA / "rev0101_transfer_stress_audit.json", audit_payload)
    print(json.dumps(summary_payload, indent=2, sort_keys=True))
    if not audit_payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
