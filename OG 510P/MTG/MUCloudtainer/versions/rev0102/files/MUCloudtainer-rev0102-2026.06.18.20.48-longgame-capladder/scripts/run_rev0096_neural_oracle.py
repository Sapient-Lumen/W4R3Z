#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.neural_oracle import (
    candidate_catalog_rows,
    deck_sources_from_population_and_gme,
    duplicate_candidate_ids,
    neural_model_audit,
    neural_response_candidates,
)
from src.muc5.oracle_reporting import dump_json, flatten_score_rows, rectangular_rows, stage_counts, stage_seed_overlaps
from src.muc5.payoff import write_csv
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator, evaluate_candidates_against_mixture, positive_mixture_support, strategy_signature
from src.muc5.psro_catalog import REV0092_ADMITTED_STRATEGY_ID, candidate_by_id, current_oracle_catalog, current_response_population

REVISION = "rev0096"
ADMITTED_ID = REV0092_ADMITTED_STRATEGY_ID
SUPPORT_TOLERANCE = 1e-3
MINIMUM_RESPONSE_GAIN = 0.02
MAX_DECK_SOURCES = 5
HOLDOUT_TOP_K = 5


def carry_forward_evidence_catalog(data: Path) -> dict[str, object]:
    latest = find_tiering_catalog(ROOT)
    if latest is None:
        raise SystemExit("no evidence tiering catalog found to carry forward")
    catalog = load_tiering_catalog(latest)
    catalog = json.loads(json.dumps(catalog))
    catalog["source_cube"] = ROOT.name
    catalog["carried_forward_in_revision"] = REVISION
    catalog["revision_note"] = (
        "Same immutable rev0072 cold sidecar; rev0096 adds compact frozen-MLP "
        "neural-oracle challenge outputs and shared oracle-reporting helpers only."
    )
    out_path = data / "rev0096_evidence_tiering_catalog.json"
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
    base_catalog = current_oracle_catalog(ROOT, population)
    admitted = candidate_by_id(base_catalog, ADMITTED_ID)
    expanded_population = [*population, admitted.strategy]
    expanded_ids = [strategy.strategy_id for strategy in expanded_population]
    expanded_payload = json.loads((data / "rev0092_psro_expanded_game.json").read_text(encoding="utf-8"))
    expanded_mixture = tuple(float(weight) for weight in expanded_payload["solver"]["column_mixture"])
    support = positive_mixture_support(expanded_population, expanded_mixture, tolerance=SUPPORT_TOLERANCE)
    if support.strategy_ids != (ADMITTED_ID,):
        raise AssertionError(f"rev0096 expected admitted response as effective sole support, found {support.strategy_ids}")

    deck_sources = deck_sources_from_population_and_gme(
        population,
        admitted.strategy,
        gme_archive_path=data / "rev0095_gameplay_map_elites_archive.csv",
        gme_limit=8,
    )
    forbidden = {strategy_signature(strategy) for strategy in expanded_population}
    candidates = neural_response_candidates(deck_sources, max_decks=MAX_DECK_SOURCES, forbidden_signatures=forbidden)
    duplicates = duplicate_candidate_ids(expanded_population, candidates)
    model_audit = neural_model_audit()

    evaluator = EmpiricalGameEvaluator()
    selection_config = EmpiricalEvaluationConfig(reps=1, max_decisions=900, base_seed=9601000)
    holdout_config = EmpiricalEvaluationConfig(reps=6, max_decisions=900, base_seed=9602000)
    confirmation_config = EmpiricalEvaluationConfig(reps=8, max_decisions=900, base_seed=9603000)

    selection, selection_pairs, selection_rows = evaluate_candidates_against_mixture(
        candidates,
        expanded_population,
        expanded_mixture,
        selection_config,
        evaluator=evaluator,
        stage="rev0096_neural_selection",
        support_tolerance=SUPPORT_TOLERANCE,
    )
    holdout_candidates_by_id = {candidate.strategy.strategy_id: candidate for candidate in candidates}
    holdout_candidates = [holdout_candidates_by_id[str(row["candidate_strategy"])] for row in selection[:HOLDOUT_TOP_K]]
    holdout, holdout_pairs, holdout_rows = evaluate_candidates_against_mixture(
        holdout_candidates,
        expanded_population,
        expanded_mixture,
        holdout_config,
        evaluator=EmpiricalGameEvaluator(),
        stage="rev0096_neural_holdout",
        support_tolerance=SUPPORT_TOLERANCE,
    )
    threshold = 0.5 + MINIMUM_RESPONSE_GAIN + support.max_score_error_from_pruning
    for row in selection:
        row["challenge_threshold_with_pruning_bound"] = threshold
        row["selection_response_pass"] = int(row["truncations"]) == 0 and float(row["mixture_ci_low"]) > threshold
        row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
    for row in holdout:
        row["challenge_threshold_with_pruning_bound"] = threshold
        row["holdout_response_pass"] = int(row["truncations"]) == 0 and float(row["mixture_ci_low"]) > threshold
        row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
    holdout.sort(key=lambda row: (bool(row["holdout_response_pass"]), float(row["mixture_mean_score"])), reverse=True)

    confirmation_candidates = [holdout_candidates_by_id[str(row["candidate_strategy"])] for row in holdout if bool(row["holdout_response_pass"])]
    confirmation: list[dict[str, object]] = []
    confirmation_pairs = []
    confirmation_rows: list[dict[str, object]] = []
    if confirmation_candidates:
        confirmation, confirmation_pairs, confirmation_rows = evaluate_candidates_against_mixture(
            confirmation_candidates,
            expanded_population,
            expanded_mixture,
            confirmation_config,
            evaluator=EmpiricalGameEvaluator(),
            stage="rev0096_neural_confirmation",
            support_tolerance=SUPPORT_TOLERANCE,
        )
        for row in confirmation:
            row["challenge_threshold_with_pruning_bound"] = threshold
            row["confirmation_response_pass"] = int(row["truncations"]) == 0 and float(row["mixture_ci_low"]) > threshold
            row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
        confirmation.sort(key=lambda row: (bool(row["confirmation_response_pass"]), float(row["mixture_mean_score"])), reverse=True)

    confirmed_response = next((row for row in confirmation if bool(row.get("confirmation_response_pass"))), None)
    best_selection = selection[0] if selection else None
    best_holdout = holdout[0] if holdout else None
    game_rows = [*selection_rows, *holdout_rows, *confirmation_rows]
    score_rows = [
        *flatten_score_rows(selection, stage="selection"),
        *flatten_score_rows(holdout, stage="holdout"),
        *flatten_score_rows(confirmation, stage="confirmation"),
    ]
    seed_overlaps = stage_seed_overlaps(game_rows)
    counts_by_stage = stage_counts(game_rows)
    total_truncations = sum(bool(row.get("truncation")) for row in game_rows)
    evidence_catalog = carry_forward_evidence_catalog(data)

    if confirmed_response is not None:
        status = "neural_oracle_confirmed_candidate_for_future_psro_round"
    elif best_holdout is not None and float(best_holdout["mixture_mean_score"]) > 0.5:
        status = "neural_oracle_found_point_estimate_only_not_confirmed"
    else:
        status = "neural_oracle_no_holdout_response"

    summary = {
        "revision": REVISION,
        "schema": "muc5.rev0096_neural_oracle.v1",
        "status": status,
        "strategic_policy_promoted": False,
        "target": {
            "expanded_population_strategy_ids": expanded_ids,
            "effective_support": support.as_dict(),
            "support_tolerance": SUPPORT_TOLERANCE,
            "minimum_response_gain": MINIMUM_RESPONSE_GAIN,
            "challenge_threshold_with_pruning_bound": threshold,
        },
        "model_audit": model_audit,
        "deck_sources": [source.as_dict() for source in deck_sources],
        "configs": {
            "max_deck_sources": MAX_DECK_SOURCES,
            "holdout_top_k": HOLDOUT_TOP_K,
            "selection": selection_config.as_dict(),
            "holdout": holdout_config.as_dict(),
            "confirmation": confirmation_config.as_dict(),
        },
        "candidate_count": len(candidates),
        "duplicates_against_expanded_population": duplicates,
        "selection": selection,
        "holdout": holdout,
        "confirmation": confirmation,
        "confirmed_response": confirmed_response,
        "best_selection": best_selection,
        "best_holdout": best_holdout,
        "stage_game_rows": counts_by_stage,
        "game_rows": len(game_rows),
        "score_rows": len(score_rows),
        "seed_overlap_counts": seed_overlaps,
        "truncations": total_truncations,
        "pair_estimates": {
            "selection": [estimate.as_dict() for estimate in selection_pairs],
            "holdout": [estimate.as_dict() for estimate in holdout_pairs],
            "confirmation": [estimate.as_dict() for estimate in confirmation_pairs],
        },
        "evidence_catalog": evidence_catalog,
        "interpretation": (
            "rev0096 reactivates the dormant rev0023 frozen MLP action-ranker as a bounded PSRO response oracle. "
            "It tests neural pilots against the current effective support without training a new black-box policy or promoting a strategy."
        ),
    }
    audit = {
        "revision": REVISION,
        "schema": "muc5.rev0096_neural_oracle_audit.v1",
        "passed": (
            support.strategy_ids == (ADMITTED_ID,)
            and model_audit.get("feature_count") == 81
            and int(model_audit.get("hidden_size", 0)) > 0
            and len(deck_sources) >= MAX_DECK_SOURCES
            and len(candidates) >= 20
            and len(holdout) == min(HOLDOUT_TOP_K, len(candidates))
            and not duplicates
            and total_truncations == 0
            and all(int(value) == 0 for value in seed_overlaps.values())
            and summary["strategic_policy_promoted"] is False
            and evidence_catalog.get("core_validation", {}).get("passed") is True
        ),
        "checks": {
            "effective_support": support.as_dict(),
            "model_audit": model_audit,
            "deck_source_count": len(deck_sources),
            "candidate_count": len(candidates),
            "holdout_candidates": [row["candidate_strategy"] for row in holdout],
            "best_selection_candidate": None if best_selection is None else best_selection["candidate_strategy"],
            "best_selection_mean": None if best_selection is None else best_selection["mixture_mean_score"],
            "best_holdout_candidate": None if best_holdout is None else best_holdout["candidate_strategy"],
            "best_holdout_mean": None if best_holdout is None else best_holdout["mixture_mean_score"],
            "best_holdout_ci_low": None if best_holdout is None else best_holdout["mixture_ci_low"],
            "confirmed_response": confirmed_response,
            "duplicates_against_expanded_population": duplicates,
            "stage_game_rows": counts_by_stage,
            "game_rows": len(game_rows),
            "score_rows": len(score_rows),
            "seed_overlap_counts": seed_overlaps,
            "truncations": total_truncations,
            "status": status,
            "evidence_catalog": evidence_catalog,
        },
    }

    write_csv(data / "rev0096_neural_oracle_games.csv", rectangular_rows(game_rows))
    write_csv(data / "rev0096_neural_oracle_scores.csv", rectangular_rows(score_rows))
    write_csv(data / "rev0096_neural_oracle_catalog.csv", rectangular_rows(candidate_catalog_rows(candidates, sources=deck_sources)))
    write_csv(data / "rev0096_neural_oracle_deck_sources.csv", rectangular_rows(source.as_dict() for source in deck_sources))
    dump_json(data / "rev0096_neural_oracle_summary.json", summary)
    dump_json(data / "rev0096_neural_oracle_audit.json", audit)
    print(json.dumps({"summary": summary, "audit": audit}, indent=2, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
