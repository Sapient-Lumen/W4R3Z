#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from random import Random
import sys
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.gameplay_map_elites import (
    GameplayEliteRecord,
    archive_summary,
    choose_parents,
    dedupe_candidates,
    gameplay_cell_id,
    mutate_candidate,
    random_candidate,
    seed_candidates_from_strategies,
    strategy_descriptor,
    update_archive,
)
from src.muc5.oracle_reporting import dump_json, flatten_score_rows, rectangular_rows, stage_seed_overlaps
from src.muc5.payoff import StrategyBundle, write_csv
from src.muc5.psro import (
    EmpiricalEvaluationConfig,
    EmpiricalGameEvaluator,
    FiniteOracleCandidate,
    evaluate_candidates_against_mixture,
    positive_mixture_support,
    strategy_signature,
)
from src.muc5.psro_catalog import (
    REV0092_ADMITTED_STRATEGY_ID,
    candidate_by_id,
    current_oracle_catalog,
    current_response_population,
    duplicate_signatures,
)

REVISION = "rev0095"
ADMITTED_ID = REV0092_ADMITTED_STRATEGY_ID
SUPPORT_TOLERANCE = 1e-3
MINIMUM_RESPONSE_GAIN = 0.02
SELECTION_GENERATIONS = 3
MUTATIONS_PER_GENERATION = 10
RANDOM_PER_GENERATION = 4
HOLDOUT_TOP_K = 5


def candidate_catalog_rows(candidates: Sequence[FiniteOracleCandidate], *, generation_by_id: Mapping[str, int]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for candidate in candidates:
        strategy = candidate.strategy
        desc = strategy_descriptor(strategy)
        row = candidate.as_dict()
        row.update(
            {
                "generation": int(generation_by_id.get(strategy.strategy_id, -1)),
                "cell_id": gameplay_cell_id(strategy),
                **{f"desc_{key}": value for key, value in desc.items()},
            }
        )
        out.append(row)
    return out


def carry_forward_evidence_catalog(data: Path) -> dict[str, object]:
    latest = find_tiering_catalog(ROOT)
    if latest is None:
        raise SystemExit("no evidence tiering catalog found to carry forward")
    catalog = load_tiering_catalog(latest)
    catalog = json.loads(json.dumps(catalog))
    catalog["source_cube"] = ROOT.name
    catalog["carried_forward_in_revision"] = REVISION
    catalog["revision_note"] = (
        "Same immutable rev0072 cold sidecar; rev0095 adds compact gameplay-driven "
        "MAP-Elites oracle outputs only."
    )
    out_path = data / "rev0095_evidence_tiering_catalog.json"
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


def build_generation_zero(
    expanded_population: Sequence[StrategyBundle],
    base_catalog: Sequence[FiniteOracleCandidate],
    *,
    forbidden_signatures: set[tuple[object, ...]],
) -> list[FiniteOracleCandidate]:
    seed_strategies = [*expanded_population, *(candidate.strategy for candidate in base_catalog)]
    seeds = seed_candidates_from_strategies(seed_strategies, prefix="gme_seed")
    # Re-evaluate the old static map proposals as generation-zero seeds, but do
    # not inherit their static archive quality.  Gameplay decides archive cells.
    relabeled_static: list[FiniteOracleCandidate] = []
    for index, candidate in enumerate(base_catalog, 1):
        strategy = StrategyBundle(
            strategy_id=f"gme_static_{index:02d}_{candidate.strategy.strategy_id}",
            deck_name=candidate.strategy.deck_name,
            deck=candidate.strategy.deck,
            agent_name=candidate.strategy.agent_name,
            mulligan_policy=candidate.strategy.mulligan_policy,
        )
        relabeled_static.append(
            FiniteOracleCandidate(
                strategy=strategy,
                oracle_family="gameplay_map_elites_static_seed",
                source=f"static catalog proposal {candidate.strategy.strategy_id}; quality reset and remeasured by gameplay",
            )
        )
    return dedupe_candidates([*seeds, *relabeled_static], forbidden_signatures=forbidden_signatures)


def main() -> None:
    data = ROOT / "data"
    rng = Random(95095)

    population = current_response_population(data / "seed_decks.json")
    base_catalog = current_oracle_catalog(ROOT, population)
    admitted = candidate_by_id(base_catalog, ADMITTED_ID)
    expanded_population: list[StrategyBundle] = [*population, admitted.strategy]
    expanded_ids = [strategy.strategy_id for strategy in expanded_population]
    expanded_payload = json.loads((data / "rev0092_psro_expanded_game.json").read_text(encoding="utf-8"))
    expanded_mixture = tuple(float(weight) for weight in expanded_payload["solver"]["column_mixture"])
    support = positive_mixture_support(expanded_population, expanded_mixture, tolerance=SUPPORT_TOLERANCE)
    if support.strategy_ids != (ADMITTED_ID,):
        raise AssertionError(f"rev0095 expected admitted response as effective sole support, found {support.strategy_ids}")

    forbidden_signatures = {strategy_signature(strategy) for strategy in expanded_population}
    all_candidates: dict[str, FiniteOracleCandidate] = {}
    generation_by_id: dict[str, int] = {}
    archive: dict[str, GameplayEliteRecord] = {}
    evaluator = EmpiricalGameEvaluator()
    selection_config = EmpiricalEvaluationConfig(reps=1, max_decisions=900, base_seed=9501000)
    holdout_config = EmpiricalEvaluationConfig(reps=6, max_decisions=900, base_seed=9502000)
    confirmation_config = EmpiricalEvaluationConfig(reps=8, max_decisions=900, base_seed=9503000)

    generation_batches: list[dict[str, object]] = []
    game_rows: list[dict[str, object]] = []
    score_rows: list[dict[str, object]] = []
    selection_pair_estimates = []

    gen0 = build_generation_zero(expanded_population, base_catalog, forbidden_signatures=forbidden_signatures)
    # Keep the first batch bounded; the archive should become generative quickly.
    batch = gen0[:18]
    seen_signatures = set(forbidden_signatures)
    seen_ids: set[str] = set()

    for generation in range(SELECTION_GENERATIONS):
        if generation > 0:
            parents = choose_parents(archive, all_candidates, rng, count=MUTATIONS_PER_GENERATION)
            proposals: list[FiniteOracleCandidate] = []
            for index, parent in enumerate(parents, 1):
                proposals.append(mutate_candidate(parent, rng, generation=generation, index=index, prefix="gme"))
            for index in range(1, RANDOM_PER_GENERATION + 1):
                proposals.append(random_candidate(rng, generation=generation, index=100 + index, prefix="gme"))
            batch = dedupe_candidates(proposals, forbidden_signatures=seen_signatures)
        batch = [candidate for candidate in batch if candidate.strategy.strategy_id not in seen_ids]
        batch = batch[: (18 if generation == 0 else MUTATIONS_PER_GENERATION + RANDOM_PER_GENERATION)]
        if not batch:
            break
        for candidate in batch:
            all_candidates[candidate.strategy.strategy_id] = candidate
            generation_by_id[candidate.strategy.strategy_id] = generation
            seen_signatures.add(strategy_signature(candidate.strategy))
            seen_ids.add(candidate.strategy.strategy_id)
        selection, pair_estimates, rows = evaluate_candidates_against_mixture(
            batch,
            expanded_population,
            expanded_mixture,
            selection_config,
            evaluator=evaluator,
            stage=f"rev0095_gme_selection_g{generation}",
            support_tolerance=SUPPORT_TOLERANCE,
        )
        changed = update_archive(archive, all_candidates, selection, generation=generation)
        generation_batches.append(
            {
                "generation": generation,
                "evaluated_candidates": len(batch),
                "new_or_replaced_elites": len(changed),
                "archive_cells_after_generation": len(archive),
                "best_generation_candidate": selection[0]["candidate_strategy"] if selection else None,
                "best_generation_mean": selection[0]["mixture_mean_score"] if selection else None,
                "best_generation_ci_low": selection[0]["mixture_ci_low"] if selection else None,
            }
        )
        selection_pair_estimates.extend(pair_estimates)
        game_rows.extend(rows)
        score_rows.extend(flatten_score_rows(selection, stage=f"selection_g{generation}"))

    elite_records = sorted(
        archive.values(),
        key=lambda record: (record.quality, record.ci_low, -record.truncations, record.strategy_id),
        reverse=True,
    )
    holdout_candidates = [all_candidates[record.strategy_id] for record in elite_records[:HOLDOUT_TOP_K]]
    holdout, holdout_pairs, holdout_rows = evaluate_candidates_against_mixture(
        holdout_candidates,
        expanded_population,
        expanded_mixture,
        holdout_config,
        evaluator=EmpiricalGameEvaluator(),
        stage="rev0095_gme_holdout",
        support_tolerance=SUPPORT_TOLERANCE,
    )
    threshold = 0.5 + MINIMUM_RESPONSE_GAIN + support.max_score_error_from_pruning
    for row in holdout:
        row["challenge_threshold_with_pruning_bound"] = threshold
        row["holdout_response_pass"] = int(row["truncations"]) == 0 and float(row["mixture_ci_low"]) > threshold
        row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
    holdout.sort(key=lambda row: (bool(row["holdout_response_pass"]), float(row["mixture_mean_score"])), reverse=True)
    game_rows.extend(holdout_rows)
    score_rows.extend(flatten_score_rows(holdout, stage="holdout"))

    confirmation_candidates = [all_candidates[str(row["candidate_strategy"])] for row in holdout if bool(row["holdout_response_pass"])]
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
            stage="rev0095_gme_confirmation",
            support_tolerance=SUPPORT_TOLERANCE,
        )
        for row in confirmation:
            row["challenge_threshold_with_pruning_bound"] = threshold
            row["confirmation_response_pass"] = int(row["truncations"]) == 0 and float(row["mixture_ci_low"]) > threshold
            row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
        confirmation.sort(key=lambda row: (bool(row["confirmation_response_pass"]), float(row["mixture_mean_score"])), reverse=True)
        game_rows.extend(confirmation_rows)
        score_rows.extend(flatten_score_rows(confirmation, stage="confirmation"))

    confirmed_response = next((row for row in confirmation if bool(row.get("confirmation_response_pass"))), None)
    best_holdout = holdout[0] if holdout else None
    best_archive = elite_records[0] if elite_records else None
    seed_overlaps = stage_seed_overlaps(game_rows)
    stage_counts = Counter(str(row["stage"]) for row in game_rows)
    total_truncations = sum(bool(row.get("truncation")) for row in game_rows)
    duplicates = duplicate_signatures(expanded_population, list(all_candidates.values()))
    evidence_catalog = carry_forward_evidence_catalog(data)

    if confirmed_response is not None:
        status = "generative_oracle_confirmed_candidate_for_future_psro_round"
    elif best_holdout is not None and float(best_holdout["mixture_mean_score"]) > 0.5:
        status = "generative_oracle_found_point_estimate_only_not_confirmed"
    else:
        status = "generative_oracle_no_holdout_response"

    summary = {
        "revision": REVISION,
        "schema": "muc5.rev0095_gameplay_map_elites.v1",
        "status": status,
        "strategic_policy_promoted": False,
        "target": {
            "expanded_population_strategy_ids": expanded_ids,
            "effective_support": support.as_dict(),
            "support_tolerance": SUPPORT_TOLERANCE,
            "minimum_response_gain": MINIMUM_RESPONSE_GAIN,
            "challenge_threshold_with_pruning_bound": threshold,
        },
        "configs": {
            "selection": selection_config.as_dict(),
            "holdout": holdout_config.as_dict(),
            "confirmation": confirmation_config.as_dict(),
            "selection_generations": SELECTION_GENERATIONS,
            "mutations_per_generation": MUTATIONS_PER_GENERATION,
            "random_per_generation": RANDOM_PER_GENERATION,
            "holdout_top_k": HOLDOUT_TOP_K,
        },
        "archive_summary": archive_summary(archive),
        "generation_batches": generation_batches,
        "evaluated_candidates": len(all_candidates),
        "archive_cells": len(archive),
        "duplicates_against_expanded_population": duplicates,
        "best_archive_elite": None if best_archive is None else best_archive.as_dict(),
        "holdout": holdout,
        "confirmed_response": confirmed_response,
        "confirmation": confirmation,
        "stage_game_rows": dict(sorted(stage_counts.items())),
        "game_rows": len(game_rows),
        "score_rows": len(score_rows),
        "seed_overlap_counts": seed_overlaps,
        "truncations": total_truncations,
        "pair_estimates": {
            "selection": [estimate.as_dict() for estimate in selection_pair_estimates],
            "holdout": [estimate.as_dict() for estimate in holdout_pairs],
            "confirmation": [estimate.as_dict() for estimate in confirmation_pairs],
        },
        "evidence_catalog": evidence_catalog,
        "interpretation": (
            "rev0095 is the first gameplay-driven generative MAP-Elites oracle. "
            "Cells are selected by actual rollout score against the effective PSRO support, not by the old static archive quality. "
            "This is an oracle-shaping and stress experiment, not a promotion gate."
        ),
    }
    audit = {
        "revision": REVISION,
        "schema": "muc5.rev0095_gameplay_map_elites_audit.v1",
        "passed": (
            support.strategy_ids == (ADMITTED_ID,)
            and len(all_candidates) >= 24
            and len(archive) >= 6
            and len(holdout) == min(HOLDOUT_TOP_K, len(archive))
            and not duplicates
            and total_truncations == 0
            and all(int(value) == 0 for value in seed_overlaps.values())
            and summary["strategic_policy_promoted"] is False
            and evidence_catalog.get("core_validation", {}).get("passed") is True
        ),
        "checks": {
            "effective_support": support.as_dict(),
            "evaluated_candidates": len(all_candidates),
            "archive_cells": len(archive),
            "holdout_candidates": [row["candidate_strategy"] for row in holdout],
            "best_holdout_candidate": None if best_holdout is None else best_holdout["candidate_strategy"],
            "best_holdout_mean": None if best_holdout is None else best_holdout["mixture_mean_score"],
            "best_holdout_ci_low": None if best_holdout is None else best_holdout["mixture_ci_low"],
            "confirmed_response": confirmed_response,
            "duplicates_against_expanded_population": duplicates,
            "stage_game_rows": dict(sorted(stage_counts.items())),
            "game_rows": len(game_rows),
            "score_rows": len(score_rows),
            "seed_overlap_counts": seed_overlaps,
            "truncations": total_truncations,
            "status": status,
            "evidence_catalog": evidence_catalog,
        },
    }

    write_csv(data / "rev0095_gameplay_map_elites_games.csv", rectangular_rows(game_rows))
    write_csv(data / "rev0095_gameplay_map_elites_scores.csv", rectangular_rows(score_rows))
    write_csv(data / "rev0095_gameplay_map_elites_archive.csv", rectangular_rows(record.as_dict() for record in elite_records))
    write_csv(
        data / "rev0095_gameplay_map_elites_catalog.csv",
        rectangular_rows(candidate_catalog_rows(list(all_candidates.values()), generation_by_id=generation_by_id)),
    )
    dump_json(data / "rev0095_gameplay_map_elites_summary.json", summary)
    dump_json(data / "rev0095_gameplay_map_elites_audit.json", audit)
    print(json.dumps({"summary": summary, "audit": audit}, indent=2, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
