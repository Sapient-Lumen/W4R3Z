#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evaluation_design import audit_balanced_focal_rows, expected_games_per_pair, pair_symmetry_rows
from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.oracle_reporting import dump_json, rectangular_rows, stage_counts
from src.muc5.payoff import StrategyBundle, write_csv
from src.muc5.population_frontier import zero_sum_maximin
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator, build_symmetric_empirical_game
from src.muc5.psro_catalog import REV0092_ADMITTED_STRATEGY_ID, candidate_by_id, current_oracle_catalog, current_response_population

REVISION = "rev0099"
STAGE = "rev0099_expanded_matrix_refresh"
CONFIG = EmpiricalEvaluationConfig(life_totals=(20, 40), reps=10, max_decisions=700, base_seed=9909900)


def expanded_population(data: Path) -> list[StrategyBundle]:
    population = current_response_population(data / "seed_decks.json")
    catalog = current_oracle_catalog(ROOT, population)
    admitted = candidate_by_id(catalog, REV0092_ADMITTED_STRATEGY_ID).strategy
    ids = {strategy.strategy_id for strategy in population}
    if admitted.strategy_id in ids:
        raise ValueError("admitted strategy already present in base population")
    return [*population, admitted]


def matrix_rows(matrix: np.ndarray, strategies: list[StrategyBundle]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i, row_strategy in enumerate(strategies):
        for j, column_strategy in enumerate(strategies):
            rows.append(
                {
                    "row_index": i,
                    "column_index": j,
                    "row_strategy": row_strategy.strategy_id,
                    "column_strategy": column_strategy.strategy_id,
                    "row_score": float(matrix[i, j]),
                    "column_score": float(1.0 - matrix[i, j]),
                    "diagonal": i == j,
                }
            )
    return rows


def strategy_rows(matrix: np.ndarray, strategies: list[StrategyBundle], solution) -> list[dict[str, object]]:
    row_mix = list(solution.row_strategy)
    col_mix = list(solution.column_strategy)
    rows: list[dict[str, object]] = []
    for i, strategy in enumerate(strategies):
        rows.append(
            {
                "strategy_index": i,
                "strategy_id": strategy.strategy_id,
                "deck_name": strategy.deck_name,
                "deck_size": strategy.deck.size,
                "agent_name": strategy.agent_name,
                "mulligan_policy": str(strategy.mulligan_policy),
                "deck_json": json.dumps(strategy.deck.counts(), sort_keys=True),
                "row_mixture_weight": float(row_mix[i]),
                "column_mixture_weight": float(col_mix[i]),
                "effective_row_support_1e_3": float(row_mix[i]) > 1e-3,
                "effective_column_support_1e_3": float(col_mix[i]) > 1e-3,
                "pure_floor_vs_population": float(np.min(matrix[i, :])),
                "pure_ceiling_vs_population": float(np.max(matrix[i, :])),
                "mean_vs_population": float(np.mean(matrix[i, :])),
                "best_response_score_against_strategy_as_column": float(np.max(matrix[:, i])),
            }
        )
    rows.sort(key=lambda row: (float(row["row_mixture_weight"]), float(row["pure_floor_vs_population"])), reverse=True)
    return rows


def pair_estimate_rows(estimates) -> list[dict[str, object]]:
    out = []
    for estimate in estimates:
        payload = estimate.as_dict()
        payload["stage"] = STAGE
        out.append(payload)
    return out


def carry_forward_evidence_catalog(data: Path) -> dict[str, object]:
    candidates = sorted(data.glob("rev*_evidence_tiering_catalog.json"))
    candidates = [path for path in candidates if path.name != "rev0099_evidence_tiering_catalog.json"]
    latest = candidates[-1] if candidates else find_tiering_catalog(ROOT)
    if latest is None:
        raise SystemExit("no evidence tiering catalog found")
    catalog = json.loads(json.dumps(load_tiering_catalog(latest)))
    catalog["source_cube"] = ROOT.name
    catalog["carried_forward_in_revision"] = REVISION
    catalog["revision_note"] = (
        "Same immutable cold-evidence sidecar; rev0099 adds compact balanced evaluation-design "
        "helpers and a bounded expanded-population matrix refresh only."
    )
    out_path = data / "rev0099_evidence_tiering_catalog.json"
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
    strategies = expanded_population(data)
    evaluator = EmpiricalGameEvaluator()
    matrix, estimates, game_rows = build_symmetric_empirical_game(strategies, CONFIG, evaluator=evaluator, stage=STAGE)
    solution = zero_sum_maximin(matrix)
    balance = audit_balanced_focal_rows(game_rows, expected_life_totals=CONFIG.life_totals, expected_reps=CONFIG.reps)
    pair_symmetry = pair_symmetry_rows(game_rows)
    matrix_csv_rows = matrix_rows(matrix, strategies)
    strategy_csv_rows = strategy_rows(matrix, strategies, solution)
    estimates_csv_rows = pair_estimate_rows(estimates)
    write_csv(data / "rev0099_expanded_matrix_games.csv", rectangular_rows(game_rows))
    write_csv(data / "rev0099_expanded_matrix_cells.csv", rectangular_rows(matrix_csv_rows))
    write_csv(data / "rev0099_expanded_matrix_pair_estimates.csv", rectangular_rows(estimates_csv_rows))
    write_csv(data / "rev0099_expanded_matrix_strategy_summary.csv", rectangular_rows(strategy_csv_rows))
    write_csv(data / "rev0099_pair_symmetry_summary.csv", rectangular_rows(pair_symmetry))

    antisymmetry_error = float(np.max(np.abs(matrix + matrix.T - 1.0)))
    diagonal_error = float(np.max(np.abs(np.diag(matrix) - 0.5)))
    expected_pairs = len(strategies) * (len(strategies) - 1) // 2
    expected_rows = expected_pairs * expected_games_per_pair(CONFIG.life_totals, CONFIG.reps)
    truncations = sum(1 for row in game_rows if bool(row.get("truncation")))
    admitted_index = [strategy.strategy_id for strategy in strategies].index(REV0092_ADMITTED_STRATEGY_ID)
    admitted_summary = strategy_csv_rows[[row["strategy_id"] for row in strategy_csv_rows].index(REV0092_ADMITTED_STRATEGY_ID)]
    support_ids = [row["strategy_id"] for row in strategy_csv_rows if bool(row["effective_row_support_1e_3"])]
    evidence_catalog = carry_forward_evidence_catalog(data)

    audit_checks = {
        "strategy_count": len(strategies),
        "expected_pair_count": expected_pairs,
        "pair_estimates": len(estimates),
        "game_rows": len(game_rows),
        "expected_game_rows": expected_rows,
        "truncations": truncations,
        "balance_passed": balance["passed"],
        "antisymmetry_error": antisymmetry_error,
        "diagonal_error": diagonal_error,
        "solver_gap": float(solution.exploitability_upper_value - solution.guaranteed_value),
        "admitted_row_mixture_weight": float(strategy_csv_rows[[row["strategy_id"] for row in strategy_csv_rows].index(REV0092_ADMITTED_STRATEGY_ID)]["row_mixture_weight"]),
        "admitted_pure_floor": float(admitted_summary["pure_floor_vs_population"]),
        "support_ids": support_ids,
        "core_tiering_passed": evidence_catalog["core_validation"].get("passed") is True,
    }
    passed = (
        audit_checks["strategy_count"] == 9
        and audit_checks["pair_estimates"] == expected_pairs
        and audit_checks["game_rows"] == expected_rows
        and truncations == 0
        and bool(balance["passed"])
        and antisymmetry_error <= 1e-12
        and diagonal_error <= 1e-12
        and evidence_catalog["core_validation"].get("passed") is True
    )
    summary = {
        "schema": "muc5.rev0099_expanded_matrix_refresh.v1",
        "revision": REVISION,
        "status": "balanced_expanded_population_matrix_refreshed",
        "strategic_policy_promoted": False,
        "config": CONFIG.as_dict(),
        "stage": STAGE,
        "population": [strategy.as_dict() for strategy in strategies],
        "solver": {
            "method": solution.solution_method,
            "guaranteed_value": solution.guaranteed_value,
            "restricted_best_response_value": solution.exploitability_upper_value,
            "solver_gap": solution.exploitability_upper_value - solution.guaranteed_value,
            "row_mixture": list(solution.row_strategy),
            "column_mixture": list(solution.column_strategy),
        },
        "effective_support_1e_3": support_ids,
        "admitted_response_summary": admitted_summary,
        "balance_audit": balance,
        "stage_counts": stage_counts(game_rows),
        "max_pair_seat_gap_abs": max(abs(float(row.get("seat1_minus_seat0") or 0.0)) for row in pair_symmetry) if pair_symmetry else 0.0,
        "max_pair_start_gap_abs": max(abs(float(row.get("focal_starts_minus_draws") or 0.0)) for row in pair_symmetry) if pair_symmetry else 0.0,
        "audit_checks": audit_checks,
        "evidence_catalog": evidence_catalog,
        "passed": passed,
        "interpretation": (
            "rev0099 centralizes balanced focal-pair evaluation design and refreshes the nine-strategy empirical matrix. "
            "The result is a measurement/audit repair, not a strategic promotion; support and floors remain exploratory sample estimates."
        ),
    }
    dump_json(data / "rev0099_expanded_matrix_refresh_summary.json", summary)
    dump_json(
        data / "rev0099_expanded_matrix_refresh_audit.json",
        {
            "schema": "muc5.rev0099_expanded_matrix_refresh_audit.v1",
            "revision": REVISION,
            "passed": passed,
            "checks": audit_checks,
            "balance_audit": balance,
        },
    )
    print(json.dumps({"passed": passed, "audit_checks": audit_checks, "support_ids": support_ids}, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
