#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.confidence_floor import (
    compare_matrix_self_floor,
    floor_from_estimates,
    opponent_estimate_rows,
    require_no_seed_overlap,
)
from src.muc5.evaluation_design import audit_balanced_focal_rows, expected_games_per_pair, pair_symmetry_rows
from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.oracle_reporting import dump_json, rectangular_rows, stage_counts
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator
from src.muc5.psro_catalog import REV0092_ADMITTED_STRATEGY_ID, candidate_by_id, current_oracle_catalog, current_response_population

REVISION = "rev0100"
INCUMBENT_STAGE = "rev0100_incumbent_confidence_floor"
SELF_STAGE = "rev0100_self_control"
CONFIG = EmpiricalEvaluationConfig(life_totals=(20, 40), reps=30, max_decisions=700, base_seed=10001000)
MATRIX_SOURCE = "data/rev0099_expanded_matrix_cells.csv"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rev0099_matrix(data: Path) -> tuple[np.ndarray, list[str]]:
    path = ROOT / MATRIX_SOURCE
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    n = 1 + max(int(row["row_index"]) for row in rows)
    matrix = np.full((n, n), np.nan, dtype=np.float64)
    strategy_ids = [""] * n
    for row in rows:
        i = int(row["row_index"])
        j = int(row["column_index"])
        matrix[i, j] = float(row["row_score"])
        strategy_ids[i] = row["row_strategy"]
    if np.isnan(matrix).any() or any(not strategy_id for strategy_id in strategy_ids):
        raise ValueError("rev0099 matrix source is incomplete")
    return matrix, strategy_ids


def carry_forward_evidence_catalog(data: Path) -> dict[str, object]:
    candidates = sorted(data.glob("rev*_evidence_tiering_catalog.json"))
    candidates = [path for path in candidates if path.name != "rev0100_evidence_tiering_catalog.json"]
    latest = candidates[-1] if candidates else find_tiering_catalog(ROOT)
    if latest is None:
        raise SystemExit("no evidence tiering catalog found")
    catalog = json.loads(json.dumps(load_tiering_catalog(latest)))
    catalog["source_cube"] = ROOT.name
    catalog["carried_forward_in_revision"] = REVISION
    catalog["revision_note"] = (
        "Same immutable cold-evidence sidecar; rev0100 adds compact confidence-floor evidence "
        "for the admitted response and self-diagonal floor disambiguation."
    )
    out_path = data / "rev0100_evidence_tiering_catalog.json"
    dump_json(out_path, catalog)
    validation = validate_core_tiering(ROOT, catalog)
    if validation.get("passed") is not True:
        raise SystemExit(f"carried-forward evidence catalog failed core validation: {validation}")
    return {
        "catalog_path": out_path.name,
        "prior_catalog_path": latest.name,
        "summary": catalog.get("summary", {}),
        "core_validation": validation,
    }


def main() -> None:
    data = ROOT / "data"
    population = current_response_population(data / "seed_decks.json")
    catalog = current_oracle_catalog(ROOT, population)
    admitted = candidate_by_id(catalog, REV0092_ADMITTED_STRATEGY_ID).strategy
    evaluator = EmpiricalGameEvaluator()

    estimates = []
    game_rows: list[dict[str, object]] = []
    for opponent in population:
        estimate, rows = evaluator.evaluate_focal_pair(admitted, opponent, CONFIG, stage=INCUMBENT_STAGE)
        estimates.append(estimate)
        game_rows.extend(rows)

    self_estimate, self_rows = evaluator.evaluate_focal_pair(admitted, admitted, CONFIG, stage=SELF_STAGE)
    game_rows.extend(self_rows)

    estimate_rows = opponent_estimate_rows(estimates, stage=INCUMBENT_STAGE) + opponent_estimate_rows([self_estimate], stage=SELF_STAGE)
    floor_summary = floor_from_estimates(admitted.strategy_id, estimates)
    balance = audit_balanced_focal_rows(game_rows, expected_life_totals=CONFIG.life_totals, expected_reps=CONFIG.reps)
    pair_symmetry = pair_symmetry_rows(game_rows)
    seed_overlap = require_no_seed_overlap([row for row in game_rows if row["stage"] == INCUMBENT_STAGE], self_rows)
    matrix, strategy_ids = read_rev0099_matrix(data)
    matrix_self_comparison = compare_matrix_self_floor(matrix, strategy_ids, admitted.strategy_id)
    evidence_catalog = carry_forward_evidence_catalog(data)

    strategy_rows: list[dict[str, object]] = []
    for strategy in [*population, admitted]:
        strategy_rows.append(
            {
                "strategy_id": strategy.strategy_id,
                "deck_name": strategy.deck_name,
                "deck_size": strategy.deck.size,
                "agent_name": strategy.agent_name,
                "mulligan_policy": str(strategy.mulligan_policy),
                "deck_json": json.dumps(strategy.deck.counts(), sort_keys=True),
                "role": "admitted_response" if strategy.strategy_id == admitted.strategy_id else "incumbent_opponent",
            }
        )

    write_csv(data / "rev0100_confidence_floor_games.csv", rectangular_rows(game_rows))
    write_csv(data / "rev0100_confidence_floor_pair_estimates.csv", rectangular_rows(estimate_rows))
    write_csv(data / "rev0100_confidence_floor_pair_symmetry.csv", rectangular_rows(pair_symmetry))
    write_csv(data / "rev0100_confidence_floor_strategies.csv", rectangular_rows(strategy_rows))

    expected_rows = (len(population) + 1) * expected_games_per_pair(CONFIG.life_totals, CONFIG.reps)
    truncations = sum(1 for row in game_rows if bool(row.get("truncation")))
    confidence_floor_cleared = bool(floor_summary.passed_over_half_by_ci_low)
    audit_checks = {
        "incumbent_opponents": len(population),
        "expected_rows": expected_rows,
        "game_rows": len(game_rows),
        "games_per_pair": expected_games_per_pair(CONFIG.life_totals, CONFIG.reps),
        "truncations": truncations,
        "balance_passed": balance["passed"],
        "seed_overlap_passed": seed_overlap["passed"],
        "self_diagonal_is_rev0099_floor": matrix_self_comparison["self_diagonal_is_floor"],
        "rev0099_floor_with_self": matrix_self_comparison["with_self"]["floor"],
        "rev0099_floor_without_self": matrix_self_comparison["without_self"]["floor"],
        "rev0099_self_diagonal_floor_gap": matrix_self_comparison["self_diagonal_floor_gap"],
        "rev0100_min_incumbent_mean": floor_summary.min_mean_score,
        "rev0100_min_incumbent_ci_low": floor_summary.min_ci_low,
        "rev0100_weakest_mean_opponent": floor_summary.weakest_mean_opponent,
        "rev0100_weakest_ci_opponent": floor_summary.weakest_ci_opponent,
        "confidence_floor_cleared": confidence_floor_cleared,
        "self_control_mean": self_estimate.mean_score,
        "self_control_ci_low": self_estimate.ci_low,
        "self_control_ci_high": self_estimate.ci_high,
        "core_tiering_passed": evidence_catalog["core_validation"].get("passed") is True,
    }
    audit_passed = (
        len(game_rows) == expected_rows
        and truncations == 0
        and bool(balance["passed"])
        and bool(seed_overlap["passed"])
        and matrix_self_comparison["self_diagonal_is_floor"] is True
        and evidence_catalog["core_validation"].get("passed") is True
    )

    summary = {
        "schema": "muc5.rev0100_confidence_floor.v1",
        "revision": REVISION,
        "status": "admitted_response_confidence_floor_audited",
        "strategic_policy_promoted": False,
        "stage": INCUMBENT_STAGE,
        "self_control_stage": SELF_STAGE,
        "config": CONFIG.as_dict(),
        "target_strategy": admitted.as_dict(),
        "incumbent_population": [strategy.as_dict() for strategy in population],
        "floor_summary": floor_summary.as_dict(),
        "self_control": self_estimate.as_dict(),
        "matrix_self_floor_comparison": matrix_self_comparison,
        "balance_audit": balance,
        "seed_overlap_audit": seed_overlap,
        "stage_counts": stage_counts(game_rows),
        "max_pair_seat_gap_abs": max(abs(float(row.get("seat1_minus_seat0") or 0.0)) for row in pair_symmetry) if pair_symmetry else 0.0,
        "max_pair_start_gap_abs": max(abs(float(row.get("focal_starts_minus_draws") or 0.0)) for row in pair_symmetry) if pair_symmetry else 0.0,
        "audit_checks": audit_checks,
        "evidence_catalog": evidence_catalog,
        "audit_passed": audit_passed,
        "confidence_floor_cleared": confidence_floor_cleared,
        "interpretation": (
            "rev0100 separates the matrix self-diagonal convention from opponent-floor evidence and remeasures the admitted "
            "response against each incumbent at higher per-pair resolution. This is a confidence audit for the current PSRO "
            "target, not a general strategic promotion."
        ),
    }
    audit = {
        "schema": "muc5.rev0100_confidence_floor_audit.v1",
        "revision": REVISION,
        "passed": audit_passed,
        "confidence_floor_cleared": confidence_floor_cleared,
        "checks": audit_checks,
        "balance_audit": balance,
        "seed_overlap_audit": seed_overlap,
    }
    dump_json(data / "rev0100_confidence_floor_summary.json", summary)
    dump_json(data / "rev0100_confidence_floor_audit.json", audit)
    print(json.dumps({"audit_passed": audit_passed, "checks": audit_checks}, indent=2, sort_keys=True))
    if not audit_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
