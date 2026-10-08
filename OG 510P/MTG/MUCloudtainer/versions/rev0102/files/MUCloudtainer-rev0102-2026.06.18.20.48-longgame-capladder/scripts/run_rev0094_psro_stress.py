#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter
import json
import math
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.payoff import StrategyBundle, write_csv
from src.muc5.psro import (
    EmpiricalEvaluationConfig,
    EmpiricalGameEvaluator,
    FiniteOracleCandidate,
    evaluate_candidates_against_mixture,
    positive_mixture_support,
)
from src.muc5.psro_catalog import (
    REV0092_ADMITTED_STRATEGY_ID,
    candidate_by_id,
    current_oracle_catalog,
    current_response_population,
    duplicate_signatures,
    incumbent_population_candidates,
)

REVISION = "rev0094"
ADMITTED_ID = REV0092_ADMITTED_STRATEGY_ID
SUPPORT_TOLERANCE = 1e-3
MINIMUM_RESPONSE_GAIN = 0.02


def rectangular_rows(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    material = [dict(row) for row in rows]
    fields = sorted({key for row in material for key in row})
    return [{key: row.get(key, "") for key in fields} for row in material]


def flatten_score_rows(rows: Sequence[Mapping[str, object]], *, stage: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        flat = {key: value for key, value in row.items() if key not in {"opponent_scores", "deck", "mixture_support"}}
        flat["stage"] = stage
        flat["opponent_scores_json"] = json.dumps(row.get("opponent_scores", {}), sort_keys=True)
        flat["deck_json"] = json.dumps(row.get("deck", {}), sort_keys=True)
        flat["mixture_support_json"] = json.dumps(row.get("mixture_support", {}), sort_keys=True)
        out.append(flat)
    return out


def stage_seed_overlaps(rows: Sequence[Mapping[str, object]]) -> dict[str, int]:
    seeds_by_stage: dict[str, set[int]] = {}
    for row in rows:
        seeds_by_stage.setdefault(str(row["stage"]), set()).add(int(row["seed"]))
    stages = sorted(seeds_by_stage)
    return {
        f"{left}|{right}": len(seeds_by_stage[left] & seeds_by_stage[right])
        for i, left in enumerate(stages)
        for right in stages[i + 1 :]
    }


def outcome_interval(values: Sequence[float]) -> dict[str, float]:
    if not values:
        raise ValueError("need values")
    mean = sum(values) / len(values)
    if len(values) <= 1:
        se = 0.5
    else:
        se = math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1)) / math.sqrt(len(values))
    return {
        "mean": mean,
        "standard_error": se,
        "ci_low": max(0.0, mean - 1.96 * se),
        "ci_high": min(1.0, mean + 1.96 * se),
    }


def admitted_stress_from_incumbent_rows(incumbent_scores: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in incumbent_scores:
        challenger_mean = float(row["mixture_mean_score"])
        # In a two-player constant-sum panel against a single opponent, the
        # admitted strategy's score is the complement of the challenger's score.
        out.append(
            {
                "incumbent_strategy": row["candidate_strategy"],
                "incumbent_mean_score_vs_admitted": challenger_mean,
                "incumbent_ci_low_vs_admitted": row["mixture_ci_low"],
                "incumbent_ci_high_vs_admitted": row["mixture_ci_high"],
                "admitted_mean_score_vs_incumbent": 1.0 - challenger_mean,
                "admitted_ci_low_vs_incumbent": 1.0 - float(row["mixture_ci_high"]),
                "admitted_ci_high_vs_incumbent": 1.0 - float(row["mixture_ci_low"]),
                "games": row["games"],
                "truncations": row["truncations"],
            }
        )
    out.sort(key=lambda item: float(item["admitted_mean_score_vs_incumbent"]))
    return out


def main() -> None:
    data = ROOT / "data"
    population = current_response_population(data / "seed_decks.json")
    base_catalog = current_oracle_catalog(ROOT, population)
    admitted = candidate_by_id(base_catalog, ADMITTED_ID)
    expanded_population: list[StrategyBundle] = [*population, admitted.strategy]
    expanded_strategy_ids = [strategy.strategy_id for strategy in expanded_population]

    expanded_payload = json.loads((data / "rev0092_psro_expanded_game.json").read_text())
    expanded_mixture = tuple(float(weight) for weight in expanded_payload["solver"]["column_mixture"])
    if expanded_payload.get("admitted_strategy", {}).get("strategy_id") != ADMITTED_ID:
        raise AssertionError("rev0094 stress expected the rev0092 admitted candidate")
    if len(expanded_mixture) != len(expanded_population):
        raise AssertionError("expanded mixture and reconstructed population size disagree")

    support = positive_mixture_support(expanded_population, expanded_mixture, tolerance=SUPPORT_TOLERANCE)
    if support.strategy_ids != (ADMITTED_ID,):
        raise AssertionError(f"expected effective support to isolate admitted candidate, found {support.strategy_ids}")

    # Candidate catalog for the second PSRO-style challenge: existing population
    # controls test whether the admitted strategy is already exploitable, while
    # nonduplicate oracle proposals test whether a second expansion is warranted.
    challenge_catalog = incumbent_population_candidates(population) + [
        candidate for candidate in base_catalog if candidate.strategy.strategy_id != ADMITTED_ID
    ]
    duplicates = duplicate_signatures(expanded_population, challenge_catalog)
    nonduplicate_catalog = [candidate for candidate in challenge_catalog if candidate.strategy.strategy_id not in duplicates]

    evaluator = EmpiricalGameEvaluator()
    selection_config = EmpiricalEvaluationConfig(reps=2, max_decisions=900, base_seed=9401000)
    holdout_config = EmpiricalEvaluationConfig(reps=6, max_decisions=900, base_seed=9402000)
    incumbent_config = EmpiricalEvaluationConfig(reps=6, max_decisions=900, base_seed=9403000)

    selection, selection_pairs, selection_rows = evaluate_candidates_against_mixture(
        challenge_catalog,
        expanded_population,
        expanded_mixture,
        selection_config,
        evaluator=evaluator,
        stage="rev0094_challenge_selection",
        support_tolerance=SUPPORT_TOLERANCE,
    )
    eligible_selection = [row for row in selection if not bool(row["duplicate_of_population"])]
    selected_ids = [str(row["candidate_strategy"]) for row in eligible_selection[:4]]
    by_id = {candidate.strategy.strategy_id: candidate for candidate in challenge_catalog}
    holdout_candidates = [by_id[strategy_id] for strategy_id in selected_ids]
    holdout, holdout_pairs, holdout_rows = evaluate_candidates_against_mixture(
        holdout_candidates,
        expanded_population,
        expanded_mixture,
        holdout_config,
        evaluator=evaluator,
        stage="rev0094_challenge_holdout",
        support_tolerance=SUPPORT_TOLERANCE,
    )

    threshold = 0.5 + MINIMUM_RESPONSE_GAIN + support.max_score_error_from_pruning
    for row in selection:
        row["challenge_threshold_with_pruning_bound"] = threshold
        row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
    for row in holdout:
        row["challenge_threshold_with_pruning_bound"] = threshold
        row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
        row["holdout_response_pass"] = (
            not bool(row["duplicate_of_population"])
            and int(row["truncations"]) == 0
            and float(row["mixture_ci_low"]) > threshold
        )
    holdout.sort(key=lambda row: (bool(row["holdout_response_pass"]), float(row["mixture_mean_score"])), reverse=True)
    confirmed_response = next((row for row in holdout if bool(row["holdout_response_pass"])), None)

    incumbent_controls = incumbent_population_candidates(population)
    incumbent_scores, incumbent_pairs, incumbent_rows = evaluate_candidates_against_mixture(
        incumbent_controls,
        expanded_population,
        expanded_mixture,
        incumbent_config,
        evaluator=EmpiricalGameEvaluator(),
        stage="rev0094_incumbent_stress",
        support_tolerance=SUPPORT_TOLERANCE,
    )
    stress_rows = admitted_stress_from_incumbent_rows(incumbent_scores)
    worst_stress = min(stress_rows, key=lambda row: float(row["admitted_mean_score_vs_incumbent"]))
    best_incumbent_challenger = max(stress_rows, key=lambda row: float(row["incumbent_mean_score_vs_admitted"]))

    game_rows = [*selection_rows, *holdout_rows, *incumbent_rows]
    score_rows = [
        *flatten_score_rows(selection, stage="selection"),
        *flatten_score_rows(holdout, stage="holdout"),
        *flatten_score_rows(incumbent_scores, stage="incumbent_stress"),
    ]
    overlaps = stage_seed_overlaps(game_rows)
    stage_counts = Counter(str(row["stage"]) for row in game_rows)
    total_truncations = sum(bool(row.get("truncation")) for row in game_rows)
    status = "second_oracle_no_confirmed_response"
    if confirmed_response is not None:
        status = "second_oracle_candidate_confirmed_for_future_expansion"
    elif float(best_incumbent_challenger["incumbent_mean_score_vs_admitted"]) > 0.5:
        status = "incumbent_vulnerability_seen_but_not_confirmed"

    payload = {
        "revision": REVISION,
        "schema": "muc5.rev0094_psro_stress.v1",
        "status": status,
        "strategic_policy_promoted": False,
        "admitted_strategy": admitted.strategy.as_dict(),
        "expanded_population_strategy_ids": expanded_strategy_ids,
        "source_expanded_solver": expanded_payload["solver"],
        "effective_support": support.as_dict(),
        "support_tolerance": SUPPORT_TOLERANCE,
        "minimum_response_gain": MINIMUM_RESPONSE_GAIN,
        "challenge_threshold_with_pruning_bound": threshold,
        "configs": {
            "selection": selection_config.as_dict(),
            "holdout": holdout_config.as_dict(),
            "incumbent_stress": incumbent_config.as_dict(),
        },
        "catalog": {
            "challenge_candidates": len(challenge_catalog),
            "nonduplicate_candidates": len(nonduplicate_catalog),
            "duplicate_controls": duplicates,
            "selected_for_holdout": selected_ids,
            "candidate_catalog_file": "data/rev0094_psro_challenge_catalog.csv",
        },
        "selection_top5": selection[:5],
        "holdout": holdout,
        "confirmed_response": confirmed_response,
        "incumbent_stress": {
            "rows": stress_rows,
            "worst_admitted_score_vs_incumbent": worst_stress,
            "best_incumbent_challenger_vs_admitted": best_incumbent_challenger,
            "admitted_min_mean_score_vs_incumbents": float(worst_stress["admitted_mean_score_vs_incumbent"]),
            "admitted_min_ci_low_vs_incumbents": min(float(row["admitted_ci_low_vs_incumbent"]) for row in stress_rows),
            "all_incumbent_mean_scores_below_half": all(float(row["incumbent_mean_score_vs_admitted"]) < 0.5 for row in stress_rows),
        },
        "stage_game_rows": dict(sorted(stage_counts.items())),
        "game_rows": len(game_rows),
        "seed_overlap_counts": overlaps,
        "truncations": total_truncations,
        "pair_estimates": {
            "selection": [estimate.as_dict() for estimate in selection_pairs],
            "holdout": [estimate.as_dict() for estimate in holdout_pairs],
            "incumbent_stress": [estimate.as_dict() for estimate in incumbent_pairs],
        },
        "interpretation": (
            "This is a stress/challenge panel for the rev0092 admitted response, not a promotion gate. "
            "The effective expanded-game mixture is almost entirely the admitted strategy; tiny solver residue is "
            "pruned with an explicit payoff error bound before evaluating second-oracle responses."
        ),
    }

    audit = {
        "revision": REVISION,
        "schema": "muc5.rev0094_psro_stress_audit.v1",
        "passed": (
            support.strategy_ids == (ADMITTED_ID,)
            and support.max_score_error_from_pruning < SUPPORT_TOLERANCE
            and len(challenge_catalog) == 23
            and len(nonduplicate_catalog) == 15
            and len(holdout) == 4
            and confirmed_response is None
            and float(worst_stress["admitted_mean_score_vs_incumbent"]) > 0.55
            and all(float(row["incumbent_mean_score_vs_admitted"]) < 0.5 for row in stress_rows)
            and total_truncations == 0
            and all(value == 0 for value in overlaps.values())
        ),
        "checks": {
            "effective_support": support.as_dict(),
            "challenge_candidates": len(challenge_catalog),
            "nonduplicate_candidates": len(nonduplicate_catalog),
            "duplicate_controls": duplicates,
            "holdout_candidates": selected_ids,
            "confirmed_response": confirmed_response,
            "admitted_min_mean_score_vs_incumbents": float(worst_stress["admitted_mean_score_vs_incumbent"]),
            "admitted_min_ci_low_vs_incumbents": min(float(row["admitted_ci_low_vs_incumbent"]) for row in stress_rows),
            "best_incumbent_challenger_mean": float(best_incumbent_challenger["incumbent_mean_score_vs_admitted"]),
            "stage_game_rows": dict(sorted(stage_counts.items())),
            "game_rows": len(game_rows),
            "seed_overlap_counts": overlaps,
            "truncations": total_truncations,
            "status": status,
        },
    }

    write_csv(data / "rev0094_psro_challenge_games.csv", rectangular_rows(game_rows))
    write_csv(data / "rev0094_psro_challenge_scores.csv", rectangular_rows(score_rows))
    write_csv(data / "rev0094_psro_challenge_catalog.csv", rectangular_rows(candidate.as_dict() for candidate in challenge_catalog))
    write_csv(data / "rev0094_psro_incumbent_stress.csv", rectangular_rows(stress_rows))
    (data / "rev0094_psro_stress_summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    (data / "rev0094_psro_stress_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"summary": payload, "audit": audit}, indent=2, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
