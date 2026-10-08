#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.gameplay_map_elites import strategy_descriptor
from src.muc5.learned_response_oracle import (
    default_registry_path,
    duplicate_candidate_ids,
    learned_deck_sources,
    learned_feature_names,
    learned_response_candidates,
    sampled_learned_models,
    write_registry,
)
from src.muc5.oracle_reporting import dump_json, flatten_score_rows, rectangular_rows, stage_counts, stage_seed_overlaps
from src.muc5.payoff import StrategyBundle, write_csv
from src.muc5.psro import EmpiricalEvaluationConfig, EmpiricalGameEvaluator, evaluate_candidates_against_mixture, positive_mixture_support, strategy_signature
from src.muc5.psro_catalog import REV0092_ADMITTED_STRATEGY_ID, candidate_by_id, current_oracle_catalog, current_response_population

REVISION = "rev0097"
ADMITTED_ID = REV0092_ADMITTED_STRATEGY_ID
SUPPORT_TOLERANCE = 1e-3
MINIMUM_RESPONSE_GAIN = 0.02
G0_MODELS_PER_PROFILE = 3
LEARNED_PROFILES = ("threat_pressure", "threat_surge")
G1_CHILDREN = 8
FINAL_PARENT_KEEP = 3
FINAL_DECKS = 2
HOLDOUT_TOP_K = 5


def carry_forward_evidence_catalog(data: Path) -> dict[str, object]:
    candidates = sorted((ROOT / "data").glob("rev*_evidence_tiering_catalog.json"))
    candidates = [path for path in candidates if path.name != "rev0097_evidence_tiering_catalog.json"]
    latest = candidates[-1] if candidates else find_tiering_catalog(ROOT)
    if latest is None:
        raise SystemExit("no evidence tiering catalog found to carry forward")
    catalog = load_tiering_catalog(latest)
    catalog = json.loads(json.dumps(catalog))
    catalog["source_cube"] = ROOT.name
    catalog["carried_forward_in_revision"] = REVISION
    catalog["revision_note"] = (
        "Same immutable rev0072 cold sidecar; rev0097 adds compact learned-response "
        "oracle outputs, agent registry, and information-state feature tests only."
    )
    out_path = data / "rev0097_evidence_tiering_catalog.json"
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


def candidate_by_agent_best(rows: list[dict[str, object]]) -> dict[str, float]:
    best: dict[str, float] = {}
    for row in rows:
        agent = str(row.get("agent_name", ""))
        if not agent:
            continue
        score = float(row.get("mixture_mean_score", 0.0))
        best[agent] = max(score, best.get(agent, -1.0))
    return best


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
        raise AssertionError(f"rev0097 expected admitted response as effective sole support, found {support.strategy_ids}")

    forbidden = {strategy_signature(strategy) for strategy in expanded_population}
    decks = learned_deck_sources(gme_archive_path=data / "rev0095_gameplay_map_elites_archive.csv", limit=FINAL_DECKS)

    # Generation 0: cheap direct-response training screen on the best gameplay-derived deck.
    g0_models = sampled_learned_models(profiles=LEARNED_PROFILES, generation0_per_profile=G0_MODELS_PER_PROFILE)
    write_registry(
        default_registry_path(),
        g0_models,
        metadata={
            "stage": "generation0_training",
            "target_strategy_id": ADMITTED_ID,
            "feature_count": len(learned_feature_names()),
        },
    )
    g0_candidates = learned_response_candidates(g0_models, decks[:1], forbidden_signatures=forbidden)
    training_config = EmpiricalEvaluationConfig(reps=1, max_decisions=1400, base_seed=9701000)
    g0_selection, g0_pairs, g0_game_rows = evaluate_candidates_against_mixture(
        g0_candidates,
        expanded_population,
        expanded_mixture,
        training_config,
        evaluator=EmpiricalGameEvaluator(),
        stage="rev0097_learned_g0_training",
        support_tolerance=SUPPORT_TOLERANCE,
    )
    parent_scores = candidate_by_agent_best(g0_selection)

    # Generation 1: recenter around the best rollout-scored parents and evaluate
    # the final compact oracle set across the top two deck sources.
    g1_models = sampled_learned_models(
        profiles=LEARNED_PROFILES,
        generation0_per_profile=G0_MODELS_PER_PROFILE,
        generation1_children=G1_CHILDREN,
        parent_scores=parent_scores,
    )
    for model in g0_models:
        object.__setattr__(model, "training_score", parent_scores.get(model.normalized_id()))
        object.__setattr__(model, "training_games", sum(int(row.get("games", 0)) for row in g0_selection if row.get("agent_name") == model.normalized_id()))
    for model in g1_models:
        object.__setattr__(model, "training_score", parent_scores.get(str(model.parent_agent_id), None))
        object.__setattr__(model, "training_games", 0)
    final_parent_ids = [agent for agent, _score in sorted(parent_scores.items(), key=lambda item: item[1], reverse=True)[:FINAL_PARENT_KEEP]]
    final_parents = [model for model in g0_models if model.normalized_id() in final_parent_ids]
    final_models = [*g1_models, *final_parents]
    write_registry(
        default_registry_path(),
        [*g0_models, *g1_models],
        metadata={
            "stage": "generation1_final",
            "target_strategy_id": ADMITTED_ID,
            "feature_names": list(learned_feature_names()),
            "generation0_parent_scores": parent_scores,
            "final_model_ids": [model.normalized_id() for model in final_models],
            "deck_signatures": [deck.as_tuple() for deck in decks],
        },
    )
    candidates = learned_response_candidates(final_models, decks, forbidden_signatures=forbidden)
    duplicates = duplicate_candidate_ids(expanded_population, candidates)

    selection_config = EmpiricalEvaluationConfig(reps=1, max_decisions=1400, base_seed=9702000)
    holdout_config = EmpiricalEvaluationConfig(reps=4, max_decisions=1400, base_seed=9703000)
    confirmation_config = EmpiricalEvaluationConfig(reps=6, max_decisions=1400, base_seed=9704000)

    selection, selection_pairs, selection_rows = evaluate_candidates_against_mixture(
        candidates,
        expanded_population,
        expanded_mixture,
        selection_config,
        evaluator=EmpiricalGameEvaluator(),
        stage="rev0097_learned_selection",
        support_tolerance=SUPPORT_TOLERANCE,
    )
    by_id = {candidate.strategy.strategy_id: candidate for candidate in candidates}
    holdout_candidates = [by_id[str(row["candidate_strategy"])] for row in selection[:HOLDOUT_TOP_K]]
    holdout, holdout_pairs, holdout_rows = evaluate_candidates_against_mixture(
        holdout_candidates,
        expanded_population,
        expanded_mixture,
        holdout_config,
        evaluator=EmpiricalGameEvaluator(),
        stage="rev0097_learned_holdout",
        support_tolerance=SUPPORT_TOLERANCE,
    )

    threshold = 0.5 + MINIMUM_RESPONSE_GAIN + support.max_score_error_from_pruning
    for rows, flag_name in ((g0_selection, "training_response_pass"), (selection, "selection_response_pass"), (holdout, "holdout_response_pass")):
        for row in rows:
            row["challenge_threshold_with_pruning_bound"] = threshold
            row[flag_name] = int(row["truncations"]) == 0 and float(row["mixture_ci_low"]) > threshold
            row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
    holdout.sort(key=lambda row: (bool(row["holdout_response_pass"]), float(row["mixture_mean_score"]), float(row["mixture_ci_low"])), reverse=True)

    confirmation_candidates = [by_id[str(row["candidate_strategy"])] for row in holdout if bool(row["holdout_response_pass"])]
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
            stage="rev0097_learned_confirmation",
            support_tolerance=SUPPORT_TOLERANCE,
        )
        for row in confirmation:
            row["challenge_threshold_with_pruning_bound"] = threshold
            row["confirmation_response_pass"] = int(row["truncations"]) == 0 and float(row["mixture_ci_low"]) > threshold
            row["excess_over_self_response"] = float(row["mixture_mean_score"]) - 0.5
        confirmation.sort(key=lambda row: (bool(row["confirmation_response_pass"]), float(row["mixture_mean_score"]), float(row["mixture_ci_low"])), reverse=True)

    confirmed_response = next((row for row in confirmation if bool(row.get("confirmation_response_pass"))), None)
    best_training = g0_selection[0] if g0_selection else None
    best_selection = selection[0] if selection else None
    best_holdout = holdout[0] if holdout else None
    game_rows = [*g0_game_rows, *selection_rows, *holdout_rows, *confirmation_rows]
    score_rows = [
        *flatten_score_rows(g0_selection, stage="generation0_training"),
        *flatten_score_rows(selection, stage="selection"),
        *flatten_score_rows(holdout, stage="holdout"),
        *flatten_score_rows(confirmation, stage="confirmation"),
    ]
    total_truncations = sum(bool(row.get("truncation")) for row in game_rows)
    seed_overlaps = stage_seed_overlaps(game_rows)
    counts_by_stage = stage_counts(game_rows)
    evidence_catalog = carry_forward_evidence_catalog(data)

    if confirmed_response is not None:
        status = "learned_response_oracle_confirmed_candidate_for_future_psro_round"
    elif best_holdout is not None and float(best_holdout["mixture_mean_score"]) > 0.5:
        status = "learned_response_oracle_found_point_estimate_only_not_confirmed"
    else:
        status = "learned_response_oracle_no_holdout_response"

    registry_payload = json.loads(default_registry_path().read_text(encoding="utf-8"))
    registry_agents = registry_payload.get("agents", {}) if isinstance(registry_payload, dict) else {}
    deck_rows = [
        {
            "deck_index": index,
            "deck_signature": deck.as_tuple(),
            "deck_size": deck.size,
            **{f"deck_{key}": value for key, value in deck.counts().items()},
        }
        for index, deck in enumerate(decks, 1)
    ]
    catalog_rows = []
    for candidate in candidates:
        row = candidate.as_dict()
        row.update({f"desc_{key}": value for key, value in strategy_descriptor(candidate.strategy).items()})
        catalog_rows.append(row)
    registry_rows = []
    for agent_id, row in sorted(registry_agents.items()):
        flat = {"agent_id": agent_id, "base_profile": row.get("base_profile"), "generation": row.get("generation"), "parent_agent_id": row.get("parent_agent_id"), "training_score": row.get("training_score"), "training_games": row.get("training_games"), "source": row.get("source")}
        weights = row.get("weights", {}) if isinstance(row, dict) else {}
        for name in learned_feature_names():
            flat[f"w_{name}"] = float(weights.get(name, 0.0)) if isinstance(weights, dict) else 0.0
        registry_rows.append(flat)

    summary = {
        "revision": REVISION,
        "schema": "muc5.rev0097_learned_response_oracle.v1",
        "status": status,
        "strategic_policy_promoted": False,
        "target": {
            "expanded_population_strategy_ids": expanded_ids,
            "effective_support": support.as_dict(),
            "support_tolerance": SUPPORT_TOLERANCE,
            "minimum_response_gain": MINIMUM_RESPONSE_GAIN,
            "challenge_threshold_with_pruning_bound": threshold,
        },
        "learner": {
            "type": "rollout-searched linear information-state action scorer",
            "feature_count": len(learned_feature_names()),
            "feature_names": list(learned_feature_names()),
            "generation0_models": len(g0_models),
            "generation1_children": len(g1_models),
            "final_models": [model.normalized_id() for model in final_models],
            "final_parent_keep": FINAL_PARENT_KEEP,
            "registry_path": default_registry_path().name,
            "generation0_parent_scores": parent_scores,
        },
        "configs": {
            "training": training_config.as_dict(),
            "selection": selection_config.as_dict(),
            "holdout": holdout_config.as_dict(),
            "confirmation": confirmation_config.as_dict(),
            "holdout_top_k": HOLDOUT_TOP_K,
            "final_decks": FINAL_DECKS,
        },
        "deck_sources": deck_rows,
        "training_candidate_count": len(g0_candidates),
        "candidate_count": len(candidates),
        "duplicates_against_expanded_population": duplicates,
        "generation0_training": g0_selection,
        "selection": selection,
        "holdout": holdout,
        "confirmation": confirmation,
        "confirmed_response": confirmed_response,
        "best_training": best_training,
        "best_selection": best_selection,
        "best_holdout": best_holdout,
        "stage_game_rows": counts_by_stage,
        "game_rows": len(game_rows),
        "score_rows": len(score_rows),
        "seed_overlap_counts": seed_overlaps,
        "truncations": total_truncations,
        "pair_estimates": {
            "generation0_training": [estimate.as_dict() for estimate in g0_pairs],
            "selection": [estimate.as_dict() for estimate in selection_pairs],
            "holdout": [estimate.as_dict() for estimate in holdout_pairs],
            "confirmation": [estimate.as_dict() for estimate in confirmation_pairs],
        },
        "evidence_catalog": evidence_catalog,
        "interpretation": (
            "rev0097 trains a small registry-backed information-state action scorer by direct rollout search against the current effective PSRO support. "
            "It is a learned response-oracle probe, not a strategic-promotion gate."
        ),
    }
    checks = {
        "support_is_admitted_response": support.strategy_ids == (ADMITTED_ID,),
        "registry_schema": registry_payload.get("schema") == "muc5.rev0097_learned_response_agent_registry.v1",
        "registry_agent_count": len(registry_agents),
        "registry_agent_count_matches_models": len(registry_agents) == len(g0_models) + len(g1_models),
        "feature_count": len(learned_feature_names()),
        "feature_count_positive": len(learned_feature_names()) >= 40,
        "training_candidate_count": len(g0_candidates),
        "candidate_count": len(candidates),
        "candidate_count_positive": len(candidates) > 0,
        "duplicates_against_expanded_population": duplicates,
        "no_duplicates": not duplicates,
        "seed_overlap_counts": seed_overlaps,
        "seed_stages_disjoint": all(int(value) == 0 for value in seed_overlaps.values()),
        "stage_game_rows": counts_by_stage,
        "truncations": total_truncations,
        "zero_truncations": total_truncations == 0,
        "score_rows": len(score_rows),
        "game_rows": len(game_rows),
        "confirmed_response": confirmed_response,
        "strategic_policy_promoted": False,
        "evidence_catalog_core_validation": evidence_catalog["core_validation"],
    }
    audit = {
        "revision": REVISION,
        "schema": "muc5.rev0097_learned_response_oracle_audit.v1",
        "passed": (
            checks["support_is_admitted_response"]
            and checks["registry_schema"]
            and checks["registry_agent_count_matches_models"]
            and checks["feature_count_positive"]
            and checks["candidate_count_positive"]
            and checks["no_duplicates"]
            and checks["seed_stages_disjoint"]
            and checks["zero_truncations"]
            and evidence_catalog["core_validation"].get("passed") is True
        ),
        "checks": checks,
    }

    dump_json(data / "rev0097_learned_response_oracle_summary.json", summary)
    dump_json(data / "rev0097_learned_response_oracle_audit.json", audit)
    write_csv(data / "rev0097_learned_response_oracle_games.csv", rectangular_rows(game_rows))
    write_csv(data / "rev0097_learned_response_oracle_scores.csv", rectangular_rows(score_rows))
    write_csv(data / "rev0097_learned_response_oracle_catalog.csv", rectangular_rows(catalog_rows))
    write_csv(data / "rev0097_learned_response_agent_registry.csv", rectangular_rows(registry_rows))
    write_csv(data / "rev0097_learned_response_deck_sources.csv", rectangular_rows(deck_rows))

    print(json.dumps({"summary": summary, "audit": audit}, indent=2, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
