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

from src.muc5.deckspace import DeckVector
from src.muc5.payoff import StrategyBundle, write_csv
from src.muc5.population_frontier import zero_sum_maximin
from src.muc5.psro import (
    EmpiricalEvaluationConfig,
    EmpiricalGameEvaluator,
    FiniteOracleCandidate,
    build_symmetric_empirical_game,
    evaluate_candidates_against_mixture,
    run_finite_psro_round,
)
from src.muc5.public_agents import make_public_agent
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.response_matrix import rev0067_response_matrix_arms
from src.muc5.terminal_decomposition import CF34_MULLIGAN, THREAT_MULLIGAN

REVISION = "rev0092"
MINIMUM_GAIN = 0.02


def current_population() -> list[StrategyBundle]:
    """Freeze the eight distinct strategies already present in the response ecology."""

    by_id: dict[str, StrategyBundle] = {}
    for arm in rev0067_response_matrix_arms(ROOT / "data" / "seed_decks.json"):
        by_id.setdefault(arm.target.strategy_id, arm.target)
        by_id.setdefault(arm.opponent.strategy_id, arm.opponent)
    order = [
        "guard_counter_wall40",
        "guard_counter_wall60",
        "pub_threat40_closure",
        "pub_threat40_pressure",
        "pub_threat40_surge",
        "pub_threat60_closure",
        "pub_threat60_pressure",
        "pub_threat60_surge",
    ]
    return [by_id[strategy_id] for strategy_id in order]


def information_upgrade_candidates(population: Sequence[StrategyBundle]) -> list[FiniteOracleCandidate]:
    """Hold deck and mulligan fixed while making rev0091 information usable."""

    out: list[FiniteOracleCandidate] = []
    for strategy in population:
        profile = strategy.agent_name.strip().lower().replace("-", "_")
        out.append(
            FiniteOracleCandidate(
                strategy=StrategyBundle(
                    strategy_id=f"oracle_info_{strategy.strategy_id}",
                    deck_name=strategy.deck_name,
                    deck=strategy.deck,
                    agent_name=f"infostate_{profile}",
                    mulligan_policy=strategy.mulligan_policy,
                ),
                oracle_family="information_state_policy_upgrade",
                source=f"same deck/mulligan as {strategy.strategy_id}; policy consumes durable information state",
            )
        )
    return out


def map_elites_candidates(limit: int = 8) -> list[FiniteOracleCandidate]:
    """Reuse the old descriptor archive as a finite proposal oracle.

    rev0014 fitness was static, so no archived quality number is treated as game
    evidence.  We select interpretable niches and let current gameplay determine
    whether any proposal is a response to the restricted-game mixture.
    """

    rows = list(csv.DictReader((ROOT / "data" / "rev0014_map_elites_archive.csv").open()))
    preferred_keys = [
        ("40", "mixed_threats", "counter_mid"),
        ("40", "overlord_heavy", "counter_mid"),
        ("40", "jace_heavy", "counter_mid"),
        ("40", "mixed_threats", "counter_wall"),
        ("60", "mixed_threats", "counter_mid"),
        ("60", "overlord_heavy", "counter_mid"),
        ("60", "jace_heavy", "counter_mid"),
        ("60", "mixed_threats", "counter_wall"),
    ]
    selected: list[dict[str, str]] = []
    for key in preferred_keys:
        row = next(
            (
                item
                for item in rows
                if (item["deck_size"], item["desc_threat_bin"], item["desc_counter_bin"]) == key
            ),
            None,
        )
        if row is not None:
            selected.append(row)

    out: list[FiniteOracleCandidate] = []
    for index, row in enumerate(selected[:limit], 1):
        deck = DeckVector(
            int(row["deck_size"]),
            int(row["island"]),
            int(row["counterspell"]),
            int(row["force"]),
            int(row["jace"]),
            int(row["overlord"]),
        )
        deck.validate()
        threat_bin = row["desc_threat_bin"]
        counter_bin = row["desc_counter_bin"]
        if counter_bin == "counter_wall":
            profile = "counter_guard"
            mulligan = CF34_MULLIGAN
        elif threat_bin == "overlord_heavy":
            profile = "threat_surge"
            mulligan = THREAT_MULLIGAN
        elif threat_bin == "jace_heavy":
            profile = "threat_pressure"
            mulligan = THREAT_MULLIGAN
        else:
            profile = "threat_closure"
            mulligan = THREAT_MULLIGAN
        strategy_id = f"oracle_map_{index:02d}_{deck.size}_{threat_bin}_{counter_bin}"
        out.append(
            FiniteOracleCandidate(
                strategy=StrategyBundle(
                    strategy_id=strategy_id,
                    deck_name=f"rev0014_cell_{row['cell_id']}",
                    deck=deck,
                    agent_name=f"infostate_{profile}",
                    mulligan_policy=mulligan,
                ),
                oracle_family="static_map_elites_candidate",
                source=(
                    f"rev0014 cell {row['cell_id']} quality={float(row['quality']):.6f}; "
                    "descriptor archive used only for proposal"
                ),
            )
        )
    return out


def matrix_rows(strategy_ids: Sequence[str], matrix: Sequence[Sequence[float]], *, stage: str) -> list[dict[str, object]]:
    return [
        {
            "stage": stage,
            "row_strategy": row_id,
            "column_strategy": column_id,
            "row_score": float(matrix[i][j]),
        }
        for i, row_id in enumerate(strategy_ids)
        for j, column_id in enumerate(strategy_ids)
    ]


def rectangular_rows(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    material = [dict(row) for row in rows]
    fields = sorted({key for row in material for key in row})
    return [{key: row.get(key, "") for key in fields} for row in material]


def candidate_by_id(candidates: Sequence[FiniteOracleCandidate], strategy_id: str) -> FiniteOracleCandidate:
    return next(candidate for candidate in candidates if candidate.strategy.strategy_id == strategy_id)


def paired_information_ablation(
    candidate: FiniteOracleCandidate,
    population: Sequence[StrategyBundle],
    mixture: Sequence[float],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Attribute the response to deck search versus the new information wrapper.

    Both variants use exactly the same game seeds.  They differ only in whether
    the pilot adds rev0092 information-state adjustments to the incumbent profile.
    """

    info_strategy = candidate.strategy
    if not info_strategy.agent_name.startswith("infostate_"):
        raise ValueError("paired information ablation requires an infostate candidate")
    legacy_strategy = StrategyBundle(
        strategy_id=info_strategy.strategy_id,  # identical ID keeps stable seeds paired
        deck_name=info_strategy.deck_name,
        deck=info_strategy.deck,
        agent_name=info_strategy.agent_name.removeprefix("infostate_"),
        mulligan_policy=info_strategy.mulligan_policy,
    )
    config = EmpiricalEvaluationConfig(reps=6, max_decisions=900, base_seed=9249200)
    info_summary, _, info_rows = evaluate_candidates_against_mixture(
        [candidate],
        population,
        mixture,
        config,
        evaluator=EmpiricalGameEvaluator(),
        stage="information_ablation",
    )
    legacy_candidate = FiniteOracleCandidate(
        strategy=legacy_strategy,
        oracle_family="paired_legacy_policy_control",
        source="same deck, mulligan, opponent mixture, and seeds; information-state adjustment removed",
    )
    legacy_summary, _, legacy_rows = evaluate_candidates_against_mixture(
        [legacy_candidate],
        population,
        mixture,
        config,
        evaluator=EmpiricalGameEvaluator(),
        stage="information_ablation",
    )
    for row in info_rows:
        row["ablation_variant"] = "information_state"
    for row in legacy_rows:
        row["ablation_variant"] = "legacy_observation_only"

    key_fields = (
        "opponent_strategy",
        "starting_life",
        "rep",
        "orientation",
        "starting_player",
        "seed",
    )
    info_by_key = {tuple(row[field] for field in key_fields): float(row["score"]) for row in info_rows}
    legacy_by_key = {tuple(row[field] for field in key_fields): float(row["score"]) for row in legacy_rows}
    if info_by_key.keys() != legacy_by_key.keys():
        raise AssertionError("information ablation did not preserve a complete paired seed panel")
    deltas = [info_by_key[key] - legacy_by_key[key] for key in sorted(info_by_key, key=str)]
    mean_delta = sum(deltas) / len(deltas)
    if len(deltas) > 1:
        sample_variance = sum((delta - mean_delta) ** 2 for delta in deltas) / (len(deltas) - 1)
        standard_error = math.sqrt(sample_variance / len(deltas))
    else:
        standard_error = 0.5
    payload = {
        "schema": "muc5.paired_information_ablation.v1",
        "candidate_strategy": info_strategy.strategy_id,
        "information_agent": info_strategy.agent_name,
        "legacy_agent": legacy_strategy.agent_name,
        "config": config.as_dict(),
        "information_summary": info_summary[0],
        "legacy_summary": legacy_summary[0],
        "paired_games": len(deltas),
        "paired_mean_score_delta": mean_delta,
        "paired_standard_error": standard_error,
        "paired_ci_low": mean_delta - 1.96 * standard_error,
        "paired_ci_high": mean_delta + 1.96 * standard_error,
        "nonzero_score_deltas": sum(abs(delta) > 1e-12 for delta in deltas),
        "all_seeds_paired": True,
        "interpretation": (
            "This panel isolates the hand-coded information-state adjustment on the confirmed deck. "
            "A zero result does not show information is generally useless; it means this response's "
            "observed gain should not be attributed to that wrapper."
        ),
    }
    return payload, info_rows + legacy_rows


def expanded_restricted_game(
    population: Sequence[StrategyBundle],
    admitted: FiniteOracleCandidate,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Actually add the confirmed response and re-solve the empirical game."""

    expanded = [*population, admitted.strategy]
    config = EmpiricalEvaluationConfig(reps=2, max_decisions=900, base_seed=9259200)
    matrix, pair_estimates, rows = build_symmetric_empirical_game(
        expanded,
        config,
        evaluator=EmpiricalGameEvaluator(),
        stage="expanded_restricted_game",
    )
    solution = zero_sum_maximin(matrix, iterations=100000)
    index = len(expanded) - 1
    payload = {
        "schema": "muc5.expanded_restricted_game.v1",
        "config": config.as_dict(),
        "strategy_ids": [strategy.strategy_id for strategy in expanded],
        "score_matrix": [[float(value) for value in row] for row in matrix],
        "pair_estimates": [estimate.as_dict() for estimate in pair_estimates],
        "solver": {
            "method": solution.solution_method,
            "iterations": solution.iterations,
            "row_mixture": list(solution.row_strategy),
            "column_mixture": list(solution.column_strategy),
            "guaranteed_value": solution.guaranteed_value,
            "restricted_best_response_value": solution.exploitability_upper_value,
            "solver_gap": solution.exploitability_upper_value - solution.guaranteed_value,
        },
        "admitted_strategy": admitted.strategy.as_dict(),
        "admitted_row_mixture_mass": float(solution.row_strategy[index]),
        "admitted_column_mixture_mass": float(solution.column_strategy[index]),
        "admitted_empirical_floor": float(min(matrix[index, :])),
        "scope": "exploratory population expansion; no strategic promotion claim",
    }
    return payload, rows


def replay_guard(
    admitted: FiniteOracleCandidate,
    population: Sequence[StrategyBundle],
    old_mixture: Sequence[float],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    support_index = max(range(len(old_mixture)), key=lambda index: float(old_mixture[index]))
    opponent = population[support_index]
    traces: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    for index, (life, starting_player) in enumerate(((20, 0), (20, 1), (40, 0), (40, 1))):
        trace = record_public_decision_trace(
            admitted.strategy.deck,
            opponent.deck,
            make_public_agent(admitted.strategy.agent_name),
            make_public_agent(opponent.agent_name),
            seed=9292000 + index,
            transition_seed=9292000 + index,
            agent_seed=10292003 + index,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=900,
            mulligan_policies=(admitted.strategy.mulligan_policy, opponent.mulligan_policy),
        )
        trace["rev0092_context"] = {
            "candidate_strategy": admitted.strategy.strategy_id,
            "opponent_strategy": opponent.strategy_id,
            "stage": "psro_replay_guard",
        }
        traces.append(trace)
        result = replay_public_decision_trace(trace).as_dict()
        result.update(
            {
                "candidate_strategy": admitted.strategy.strategy_id,
                "opponent_strategy": opponent.strategy_id,
                "starting_life": life,
                "starting_player": starting_player,
            }
        )
        results.append(result)
    return traces, results


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


def main() -> None:
    population = current_population()
    candidates = information_upgrade_candidates(population) + map_elites_candidates()
    payload = run_finite_psro_round(
        population,
        candidates,
        restricted_config=EmpiricalEvaluationConfig(reps=2, max_decisions=900, base_seed=9209200),
        selection_config=EmpiricalEvaluationConfig(reps=1, max_decisions=900, base_seed=9219200),
        holdout_config=EmpiricalEvaluationConfig(reps=3, max_decisions=900, base_seed=9229200),
        confirmation_config=EmpiricalEvaluationConfig(reps=10, max_decisions=900, base_seed=9239200),
        holdout_top_k=4,
        minimum_gain=MINIMUM_GAIN,
    )
    payload["revision"] = REVISION
    payload["interpretation"] = (
        "First executable finite-oracle PSRO expansion. Screening, holdout, and single-candidate confirmation "
        "use disjoint seeds. Admission is only to the exploratory empirical-game population."
    )
    game_rows = list(payload.pop("game_rows"))

    recommended = payload.get("recommended_expansion")
    if not isinstance(recommended, dict):
        raise AssertionError("rev0092 preregistered bootstrap expected one confirmed exploratory response")
    admitted_id = str(recommended["strategy_id"])
    admitted = candidate_by_id(candidates, admitted_id)
    old_mixture = list(payload["restricted_game"]["solver"]["column_mixture"])  # type: ignore[index]

    ablation, ablation_rows = paired_information_ablation(admitted, population, old_mixture)
    game_rows.extend(ablation_rows)
    expanded, expanded_rows = expanded_restricted_game(population, admitted)
    game_rows.extend(expanded_rows)
    payload["information_state_ablation"] = ablation
    payload["expanded_restricted_game"] = expanded
    payload["status"] = "exploratory_population_expanded"

    traces, replay_results = replay_guard(admitted, population, old_mixture)
    payload["replay_guard"] = {
        "traces": len(traces),
        "passed": bool(replay_results) and all(bool(row.get("passed")) for row in replay_results),
        "results_file": "data/rev0092_psro_replay_results.json",
        "traces_file": "data/rev0092_psro_replay_traces.jsonl",
    }

    data = ROOT / "data"
    write_csv(data / "rev0092_psro_games.csv", rectangular_rows(game_rows))
    write_csv(data / "rev0092_psro_candidate_catalog.csv", rectangular_rows(candidate.as_dict() for candidate in candidates))
    restricted = payload["restricted_game"]
    write_csv(
        data / "rev0092_psro_matrix.csv",
        matrix_rows(list(restricted["strategy_ids"]), list(restricted["score_matrix"]), stage="restricted_game"),
    )
    write_csv(
        data / "rev0092_psro_expanded_matrix.csv",
        matrix_rows(expanded["strategy_ids"], expanded["score_matrix"], stage="expanded_restricted_game"),
    )

    score_rows: list[dict[str, object]] = []
    for stage in ("oracle_selection", "oracle_holdout", "oracle_confirmation"):
        for row in payload[stage]:
            flattened = {key: value for key, value in row.items() if key not in {"opponent_scores", "deck"}}
            flattened["stage"] = stage
            flattened["opponent_scores_json"] = json.dumps(row.get("opponent_scores", {}), sort_keys=True)
            flattened["deck_json"] = json.dumps(row.get("deck", {}), sort_keys=True)
            score_rows.append(flattened)
    for variant_key, stage in (("information_summary", "information_ablation"), ("legacy_summary", "legacy_ablation_control")):
        row = dict(ablation[variant_key])
        row["stage"] = stage
        row["opponent_scores_json"] = json.dumps(row.pop("opponent_scores", {}), sort_keys=True)
        row["deck_json"] = json.dumps(row.pop("deck", {}), sort_keys=True)
        score_rows.append(row)
    write_csv(data / "rev0092_psro_candidate_scores.csv", rectangular_rows(score_rows))
    write_trace_jsonl(traces, data / "rev0092_psro_replay_traces.jsonl")
    (data / "rev0092_psro_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True) + "\n")
    (data / "rev0092_information_ablation.json").write_text(json.dumps(ablation, indent=2, sort_keys=True) + "\n")
    (data / "rev0092_psro_expanded_game.json").write_text(json.dumps(expanded, indent=2, sort_keys=True) + "\n")
    (data / "rev0092_psro_round.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    overlaps = stage_seed_overlaps(game_rows)
    stage_counts = Counter(str(row["stage"]) for row in game_rows)
    support_size = sum(float(weight) > 1e-12 for weight in old_mixture)
    pruned_stages = ("oracle_selection", "oracle_holdout", "oracle_confirmation", "information_ablation")
    support_rows = sum(stage_counts[stage] for stage in pruned_stages)
    full_population_equivalent_rows = int(round(support_rows * len(population) / support_size))
    zero_weight_rows_avoided = full_population_equivalent_rows - support_rows
    payload["evaluation_efficiency"] = {
        "restricted_mixture_support_size": support_size,
        "population_size": len(population),
        "support_only_game_rows": support_rows,
        "full_population_equivalent_game_rows": full_population_equivalent_rows,
        "zero_weight_game_rows_avoided": zero_weight_rows_avoided,
        "support_stage_reduction_fraction": zero_weight_rows_avoided / full_population_equivalent_rows,
        "whole_round_counterfactual_rows": len(game_rows) + zero_weight_rows_avoided,
        "whole_round_reduction_fraction": zero_weight_rows_avoided / (len(game_rows) + zero_weight_rows_avoided),
        "reason": "exact-zero mixture opponents cannot affect a weighted best-response estimate",
    }
    # Rewrite after adding the efficiency accounting to the canonical payload.
    (data / "rev0092_psro_round.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    restricted_matrix = list(restricted["score_matrix"])
    restricted_anti_error = max(
        abs(float(restricted_matrix[i][j]) + float(restricted_matrix[j][i]) - 1.0)
        for i in range(len(restricted_matrix))
        for j in range(len(restricted_matrix))
    )
    expanded_matrix = list(expanded["score_matrix"])
    expanded_anti_error = max(
        abs(float(expanded_matrix[i][j]) + float(expanded_matrix[j][i]) - 1.0)
        for i in range(len(expanded_matrix))
        for j in range(len(expanded_matrix))
    )
    confirmation = payload["oracle_confirmation"][0]
    audit = {
        "revision": REVISION,
        "schema": "muc5.psro_bootstrap_audit.v2",
        "passed": (
            bool(payload["replay_guard"]["passed"])
            and restricted_anti_error <= 1e-12
            and expanded_anti_error <= 1e-12
            and all(value == 0 for value in overlaps.values())
            and len(population) == 8
            and len(candidates) == 16
            and len(payload["oracle_holdout"]) == 4
            and bool(confirmation["confirmation_pass"])
            and len(expanded["strategy_ids"]) == 9
            and bool(ablation["all_seeds_paired"])
            and int(ablation["paired_games"]) > 0
            and sum(bool(row["truncation"]) for row in game_rows) == 0
        ),
        "checks": {
            "population_strategies_before": len(population),
            "population_strategies_after": len(expanded["strategy_ids"]),
            "oracle_candidates": len(candidates),
            "information_state_candidates": sum(c.oracle_family == "information_state_policy_upgrade" for c in candidates),
            "map_elites_candidates": sum(c.oracle_family == "static_map_elites_candidate" for c in candidates),
            "game_rows": len(game_rows),
            "evaluation_efficiency": payload["evaluation_efficiency"],
            "stage_game_rows": dict(sorted(stage_counts.items())),
            "restricted_matrix_constant_sum_max_error": restricted_anti_error,
            "expanded_matrix_constant_sum_max_error": expanded_anti_error,
            "seed_overlap_counts": overlaps,
            "restricted_solver": restricted["solver"],
            "expanded_solver": expanded["solver"],
            "status": payload["status"],
            "confirmed_expansion": recommended,
            "confirmation": confirmation,
            "information_state_ablation": {
                "paired_games": ablation["paired_games"],
                "paired_mean_score_delta": ablation["paired_mean_score_delta"],
                "nonzero_score_deltas": ablation["nonzero_score_deltas"],
            },
            "replay_guard": payload["replay_guard"],
            "truncations": sum(bool(row["truncation"]) for row in game_rows),
        },
    }
    (data / "rev0092_psro_bootstrap_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"round": payload, "audit": audit}, indent=2, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
