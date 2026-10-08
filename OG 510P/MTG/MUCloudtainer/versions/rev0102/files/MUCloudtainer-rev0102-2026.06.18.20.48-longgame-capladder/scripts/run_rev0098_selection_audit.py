#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.oracle_reporting import dump_json, flatten_score_rows, rectangular_rows, stage_counts, stage_seed_overlaps
from src.muc5.oracle_selection_audit import (
    audit_oracle_selection_bias,
    strategy_bundle_from_score_row,
    top_holdout_strategy_rows,
)
from src.muc5.payoff import StrategyBundle, write_csv
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator
from src.muc5.psro_catalog import REV0092_ADMITTED_STRATEGY_ID, candidate_by_id, current_oracle_catalog, current_response_population

REVISION = "rev0098"
SUPPORT_TOLERANCE = 1e-3
FRONTIER_REPS = 12


def carry_forward_evidence_catalog(data: Path) -> dict[str, object]:
    candidates = sorted((ROOT / "data").glob("rev*_evidence_tiering_catalog.json"))
    candidates = [path for path in candidates if path.name != "rev0098_evidence_tiering_catalog.json"]
    latest = candidates[-1] if candidates else find_tiering_catalog(ROOT)
    if latest is None:
        raise SystemExit("no evidence tiering catalog found to carry forward")
    catalog = load_tiering_catalog(latest)
    catalog = json.loads(json.dumps(catalog))
    catalog["source_cube"] = ROOT.name
    catalog["carried_forward_in_revision"] = REVISION
    catalog["revision_note"] = (
        "Same immutable rev0072 cold sidecar; rev0098 adds compact cross-oracle "
        "selection-bias audit outputs and a bounded common-target frontier retest only."
    )
    out_path = data / "rev0098_evidence_tiering_catalog.json"
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


def unique_frontier_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Keep one best-holdout row per concrete strategy signature.

    Separate oracle branches may rediscover the same deck/pilot/mulligan.  The
    audit wants branch provenance, but the retest should not spend budget twice
    on a literal duplicate policy.
    """

    out: list[dict[str, object]] = []
    seen: dict[tuple[object, ...], dict[str, object]] = {}
    for row in rows:
        strategy = strategy_bundle_from_score_row(row)
        sig = (*strategy.deck.as_tuple(), strategy.agent_name, str(strategy.mulligan_policy))
        if sig in seen:
            seen[sig]["merged_branch_ids"] = str(seen[sig].get("merged_branch_ids", seen[sig]["branch_id"])) + "," + str(row["branch_id"])
            continue
        payload = dict(row)
        payload["merged_branch_ids"] = str(row["branch_id"])
        seen[sig] = payload
        out.append(payload)
    return out


def run_frontier_retest(data: Path) -> dict[str, object]:
    population = current_response_population(data / "seed_decks.json")
    catalog = current_oracle_catalog(ROOT, population)
    admitted = candidate_by_id(catalog, REV0092_ADMITTED_STRATEGY_ID).strategy
    challenger_rows = unique_frontier_rows(top_holdout_strategy_rows(ROOT))
    retest_candidates: list[tuple[str, str, StrategyBundle]] = []
    for row in challenger_rows:
        strategy = strategy_bundle_from_score_row(row, strategy_id_prefix="retest_")
        retest_candidates.append((str(row["branch_id"]), str(row["branch_family"]), strategy))
    retest_candidates.append(
        (
            "admitted_self_control",
            "same concrete deck/pilot/mulligan as the target response",
            StrategyBundle(
                strategy_id="retest_admitted_self_control",
                deck_name=admitted.deck_name,
                deck=admitted.deck,
                agent_name=admitted.agent_name,
                mulligan_policy=admitted.mulligan_policy,
            ),
        )
    )

    config = EmpiricalEvaluationConfig(life_totals=(20, 40), reps=FRONTIER_REPS, max_decisions=700, base_seed=9809800)
    evaluator = EmpiricalGameEvaluator()
    score_rows: list[dict[str, object]] = []
    game_rows: list[dict[str, object]] = []
    pair_estimates = []
    for branch_id, branch_family, strategy in retest_candidates:
        estimate, rows = evaluator.evaluate_focal_pair(
            strategy,
            admitted,
            config,
            stage=f"rev0098_frontier_retest_{branch_id}",
        )
        pair_estimates.append(estimate)
        score_rows.append(
            {
                "branch_id": branch_id,
                "branch_family": branch_family,
                "candidate_strategy": strategy.strategy_id,
                "target_strategy": admitted.strategy_id,
                "agent_name": strategy.agent_name,
                "mulligan_policy": str(strategy.mulligan_policy),
                "deck_size": strategy.deck.size,
                "deck_json": json.dumps(strategy.deck.counts(), sort_keys=True),
                "games": estimate.games,
                "mean_score": estimate.mean_score,
                "standard_error": estimate.standard_error,
                "ci_low": estimate.ci_low,
                "ci_high": estimate.ci_high,
                "truncations": estimate.truncations,
                "clear_half_by_ci_low": estimate.ci_low > 0.5,
                "duplicate_of_target_components": (
                    strategy.deck.as_tuple() == admitted.deck.as_tuple()
                    and strategy.agent_name == admitted.agent_name
                    and str(strategy.mulligan_policy) == str(admitted.mulligan_policy)
                ),
            }
        )
        for row in rows:
            row = dict(row)
            row["branch_id"] = branch_id
            row["branch_family"] = branch_family
            game_rows.append(row)

    score_rows.sort(key=lambda row: (float(row["mean_score"]), float(row["ci_low"])), reverse=True)
    write_csv(data / "rev0098_frontier_retest_scores.csv", rectangular_rows(score_rows))
    write_csv(data / "rev0098_frontier_retest_games.csv", rectangular_rows(game_rows))
    best_challenger = next((row for row in score_rows if row["branch_id"] != "admitted_self_control"), None)
    self_control = next((row for row in score_rows if row["branch_id"] == "admitted_self_control"), None)
    return {
        "config": config.as_dict(),
        "target_strategy": admitted.as_dict(),
        "candidate_count_including_self_control": len(score_rows),
        "game_rows": len(game_rows),
        "stage_game_rows": stage_counts(game_rows),
        "seed_overlap_counts": stage_seed_overlaps(game_rows),
        "truncations": sum(int(row["truncation"]) for row in game_rows),
        "score_rows": score_rows,
        "pair_estimates": [estimate.as_dict() for estimate in pair_estimates],
        "best_challenger": best_challenger,
        "self_control": self_control,
        "no_challenger_clears_half_by_ci_low": all(
            not bool(row["clear_half_by_ci_low"]) for row in score_rows if row["branch_id"] != "admitted_self_control"
        ),
    }


def main() -> None:
    data = ROOT / "data"
    selection = audit_oracle_selection_bias(ROOT)
    branch_rows = selection["branches"]
    pair_rows = selection["candidate_pairs"]
    write_csv(data / "rev0098_oracle_selection_branch_summary.csv", rectangular_rows(branch_rows))
    write_csv(data / "rev0098_oracle_selection_candidate_pairs.csv", rectangular_rows(pair_rows))

    frontier = run_frontier_retest(data)
    evidence_catalog = carry_forward_evidence_catalog(data)

    audit_checks = {
        "branch_count": len(branch_rows),
        "candidate_pair_count": len(pair_rows),
        "no_branch_cleared_holdout_ci_threshold": selection["aggregate"]["no_branch_cleared_holdout_ci_threshold"],
        "frontier_game_rows": frontier["game_rows"],
        "frontier_truncations": frontier["truncations"],
        "frontier_seed_overlaps": frontier["seed_overlap_counts"],
        "frontier_no_challenger_clears_half_by_ci_low": frontier["no_challenger_clears_half_by_ci_low"],
    }
    passed = (
        audit_checks["branch_count"] == 4
        and audit_checks["candidate_pair_count"] >= 10
        and audit_checks["no_branch_cleared_holdout_ci_threshold"] is True
        and audit_checks["frontier_game_rows"] == int(frontier["candidate_count_including_self_control"]) * FRONTIER_REPS * 8
        and audit_checks["frontier_truncations"] == 0
        and all(int(value) == 0 for value in frontier["seed_overlap_counts"].values())
        and audit_checks["frontier_no_challenger_clears_half_by_ci_low"] is True
        and evidence_catalog["core_validation"].get("passed") is True
    )
    summary = {
        "schema": "muc5.rev0098_selection_audit_frontier_retest.v1",
        "revision": REVISION,
        "status": "selection_bias_audited_frontier_retest_complete_no_population_admission",
        "strategic_policy_promoted": False,
        "selection_bias": selection,
        "frontier_retest": frontier,
        "evidence_catalog": evidence_catalog,
        "audit_checks": audit_checks,
        "passed": passed,
        "interpretation": (
            "Across rev0094-rev0097 response-oracle branches, screen winners routinely shrink on holdout; "
            "a common-target retest finds no challenger with a confidence lower bound above 0.5."
        ),
    }
    dump_json(data / "rev0098_oracle_selection_audit_summary.json", summary)
    dump_json(
        data / "rev0098_oracle_selection_audit.json",
        {
            "schema": "muc5.rev0098_oracle_selection_audit.v1",
            "revision": REVISION,
            "passed": passed,
            "checks": audit_checks,
            "summary_file": "data/rev0098_oracle_selection_audit_summary.json",
        },
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
