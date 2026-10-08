from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import math
from typing import Callable, Dict, Iterable, Mapping, Sequence

import numpy as np

from .agents import play_public_agent_game
from .mulligan_ranker import make_mulligan_agent
from .payoff import StrategyBundle
from .evaluation_design import balanced_pair_cells
from .population_frontier import zero_sum_maximin
from .public_agents import make_public_agent


AgentFactory = Callable[[str], object]
MulliganFactory = Callable[[object], object]


@dataclass(frozen=True)
class EmpiricalEvaluationConfig:
    life_totals: tuple[int, ...] = (20, 40)
    reps: int = 1
    max_decisions: int = 700
    base_seed: int = 9209200
    confidence_z: float = 1.96

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PairEstimate:
    focal_strategy: str
    opponent_strategy: str
    games: int
    mean_score: float
    standard_error: float
    ci_low: float
    ci_high: float
    truncations: int
    scores: tuple[float, ...]

    def as_dict(self, *, include_scores: bool = False) -> dict[str, object]:
        payload = {
            "focal_strategy": self.focal_strategy,
            "opponent_strategy": self.opponent_strategy,
            "games": self.games,
            "mean_score": self.mean_score,
            "standard_error": self.standard_error,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "truncations": self.truncations,
        }
        if include_scores:
            payload["scores"] = list(self.scores)
        return payload


@dataclass(frozen=True)
class FiniteOracleCandidate:
    strategy: StrategyBundle
    oracle_family: str
    source: str

    def as_dict(self) -> dict[str, object]:
        return {
            **self.strategy.as_dict(),
            "oracle_family": self.oracle_family,
            "source": self.source,
        }


@dataclass(frozen=True)
class MixtureSupport:
    """Effective positive-weight support of a normalized opponent mixture.

    ``omitted_weight`` is an audit bound, not a hidden correction.  Because
    payoffs are in [0, 1], evaluating only the included support and renormalizing
    can change any weighted mean by at most the omitted normalized mass.
    """

    indices: tuple[int, ...]
    strategy_ids: tuple[str, ...]
    weights: tuple[float, ...]
    omitted_zero_weight: int
    omitted_weight: float = 0.0
    included_weight: float = 1.0
    max_score_error_from_pruning: float = 0.0

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def positive_mixture_support(
    population: Sequence[StrategyBundle],
    mixture: Sequence[float],
    *,
    tolerance: float = 1e-12,
) -> MixtureSupport:
    """Normalize a mixture and return the mathematically relevant support.

    Response-oracle evaluation may skip exact-zero opponents, but that pruning
    must be centralized and auditable.  This helper rejects negative/nonfinite
    mixtures, normalizes harmless numerical residue, and renormalizes the
    positive support used by weighted response estimation.
    """

    raw_weights = np.asarray(tuple(float(weight) for weight in mixture), dtype=np.float64)
    if len(raw_weights) != len(population):
        raise ValueError("population and mixture must have the same length")
    if np.any(raw_weights < -float(tolerance)) or not np.isfinite(raw_weights).all() or float(raw_weights.sum()) <= 0.0:
        raise ValueError("mixture must be finite and nonnegative")
    raw_weights = np.maximum(raw_weights, 0.0)
    raw_weights /= float(raw_weights.sum())
    support_indices = tuple(index for index, weight in enumerate(raw_weights) if float(weight) > float(tolerance))
    if not support_indices:
        raise ValueError("mixture has no positive support after tolerance pruning")
    support_weights = tuple(float(raw_weights[index]) for index in support_indices)
    support_total = float(sum(support_weights))
    omitted_weight = float(1.0 - support_total)
    return MixtureSupport(
        indices=support_indices,
        strategy_ids=tuple(population[index].strategy_id for index in support_indices),
        weights=tuple(weight / support_total for weight in support_weights),
        omitted_zero_weight=len(population) - len(support_indices),
        omitted_weight=omitted_weight,
        included_weight=support_total,
        max_score_error_from_pruning=max(0.0, omitted_weight),
    )


class EmpiricalGameEvaluator:
    """Seat-isolated evaluator with reusable, episode-reset policy wrappers."""

    def __init__(
        self,
        *,
        agent_factory: AgentFactory = make_public_agent,
        mulligan_factory: MulliganFactory = make_mulligan_agent,
    ) -> None:
        self.agent_factory = agent_factory
        self.mulligan_factory = mulligan_factory
        self._agents: Dict[tuple[tuple[object, ...], int], object] = {}
        self._mulligans: Dict[tuple[tuple[object, ...], int], object] = {}

    def agent(self, strategy: StrategyBundle, seat: int) -> object:
        # A human-readable ID is provenance, not an object-identity guarantee.
        # Key by the complete strategy signature so a changed pilot cannot reuse
        # a stale recurrent wrapper merely because its label was recycled.
        key = (strategy_signature(strategy), int(seat))
        if key not in self._agents:
            self._agents[key] = self.agent_factory(strategy.agent_name)
        return self._agents[key]

    def mulligan(self, strategy: StrategyBundle, seat: int) -> object:
        key = (strategy_signature(strategy), int(seat))
        if key not in self._mulligans:
            self._mulligans[key] = self.mulligan_factory(strategy.mulligan_policy)
        return self._mulligans[key]

    def evaluate_focal_pair(
        self,
        focal: StrategyBundle,
        opponent: StrategyBundle,
        config: EmpiricalEvaluationConfig,
        *,
        stage: str,
    ) -> tuple[PairEstimate, list[dict[str, object]]]:
        """Estimate a strategy's score in both seats and both play/draw roles."""

        scores: list[float] = []
        rows: list[dict[str, object]] = []
        truncations = 0
        for cell in balanced_pair_cells(config.life_totals, config.reps):
            life = int(cell.starting_life)
            rep = int(cell.rep)
            orientation = int(cell.orientation)
            starting_player = int(cell.starting_player)
            seat0, seat1 = (focal, opponent) if orientation == 0 else (opponent, focal)
            focal_player = int(cell.focal_player)
            seed = stable_seed(
                config.base_seed,
                stage,
                focal.strategy_id,
                opponent.strategy_id,
                life,
                rep,
                orientation,
                starting_player,
            )
            state, result = play_public_agent_game(
                seat0.deck,
                seat1.deck,
                self.agent(seat0, 0),  # type: ignore[arg-type]
                self.agent(seat1, 1),  # type: ignore[arg-type]
                seed=seed,
                transition_seed=seed,
                agent_seed=seed + 1000003,
                starting_player=starting_player,
                starting_life=life,
                max_decisions=int(config.max_decisions),
                mulligan_agents=(self.mulligan(seat0, 0), self.mulligan(seat1, 1)),  # type: ignore[arg-type]
                record_log=False,
                episode_id=f"{stage}:{focal.strategy_id}:{opponent.strategy_id}:{life}:{rep}:{orientation}:{starting_player}",
            )
            score = 0.5 if result.winner is None else (1.0 if result.winner == focal_player else 0.0)
            scores.append(score)
            truncation = result.loss_reason == "max_decisions_reached"
            truncations += int(truncation)
            rows.append(
                {
                    "stage": stage,
                    "focal_strategy": focal.strategy_id,
                    "opponent_strategy": opponent.strategy_id,
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
                    "truncation": truncation,
                    "decisions": result.decisions,
                    "turn_number": state.turn_number,
                    "interface": "public_decision_frame+information_state",
                }
            )
        estimate = estimate_scores(
            focal.strategy_id,
            opponent.strategy_id,
            scores,
            truncations=truncations,
            confidence_z=config.confidence_z,
        )
        return estimate, rows


def stable_seed(base_seed: int, *parts: object) -> int:
    payload = "|".join([str(int(base_seed)), *(str(part) for part in parts)])
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return 1 + int.from_bytes(digest[:8], "big") % 2_000_000_000


def strategy_signature(strategy: StrategyBundle) -> tuple[object, ...]:
    return (
        *strategy.deck.as_tuple(),
        strategy.agent_name.strip().lower().replace("-", "_"),
        str(strategy.mulligan_policy),
    )


def estimate_scores(
    focal_strategy: str,
    opponent_strategy: str,
    scores: Sequence[float],
    *,
    truncations: int = 0,
    confidence_z: float = 1.96,
) -> PairEstimate:
    values = np.asarray(tuple(float(score) for score in scores), dtype=np.float64)
    if values.size == 0:
        raise ValueError("at least one score is required")
    if np.any(values < 0.0) or np.any(values > 1.0) or not np.isfinite(values).all():
        raise ValueError("scores must be finite values in [0, 1]")
    mean = float(values.mean())
    if values.size <= 1:
        standard_error = 0.5
    else:
        standard_error = float(values.std(ddof=1) / math.sqrt(values.size))
    radius = float(confidence_z) * standard_error
    return PairEstimate(
        focal_strategy=focal_strategy,
        opponent_strategy=opponent_strategy,
        games=int(values.size),
        mean_score=mean,
        standard_error=standard_error,
        ci_low=max(0.0, mean - radius),
        ci_high=min(1.0, mean + radius),
        truncations=int(truncations),
        scores=tuple(float(value) for value in values),
    )


def build_symmetric_empirical_game(
    population: Sequence[StrategyBundle],
    config: EmpiricalEvaluationConfig,
    *,
    evaluator: EmpiricalGameEvaluator | None = None,
    stage: str = "restricted_game",
) -> tuple[np.ndarray, list[PairEstimate], list[dict[str, object]]]:
    """Build an exactly constant-sum score matrix from paired seat evaluations."""

    if not population:
        raise ValueError("population cannot be empty")
    ids = [strategy.strategy_id for strategy in population]
    if len(ids) != len(set(ids)):
        raise ValueError("population strategy_id values must be unique")
    runner = evaluator or EmpiricalGameEvaluator()
    n = len(population)
    matrix = np.full((n, n), 0.5, dtype=np.float64)
    estimates: list[PairEstimate] = []
    rows: list[dict[str, object]] = []
    for i in range(n):
        for j in range(i + 1, n):
            estimate, pair_rows = runner.evaluate_focal_pair(population[i], population[j], config, stage=stage)
            matrix[i, j] = estimate.mean_score
            matrix[j, i] = 1.0 - estimate.mean_score
            estimates.append(estimate)
            rows.extend(pair_rows)
    return matrix, estimates, rows


def weighted_response_estimate(
    candidate_id: str,
    estimates: Sequence[PairEstimate],
    opponent_ids: Sequence[str],
    mixture: Sequence[float],
    *,
    confidence_z: float = 1.96,
) -> dict[str, object]:
    by_opponent = {estimate.opponent_strategy: estimate for estimate in estimates}
    if len(opponent_ids) != len(mixture):
        raise ValueError("opponent_ids and mixture must have the same length")
    weights = np.asarray(tuple(float(weight) for weight in mixture), dtype=np.float64)
    if np.any(weights < -1e-12) or not np.isfinite(weights).all() or float(weights.sum()) <= 0.0:
        raise ValueError("mixture must be finite and nonnegative")
    weights = np.maximum(weights, 0.0)
    weights /= float(weights.sum())
    means: list[float] = []
    variances: list[float] = []
    games = 0
    truncations = 0
    for opponent_id in opponent_ids:
        estimate = by_opponent.get(opponent_id)
        if estimate is None:
            raise ValueError(f"missing candidate estimate against {opponent_id}")
        means.append(estimate.mean_score)
        variances.append(estimate.standard_error**2)
        games += estimate.games
        truncations += estimate.truncations
    mean = float(weights @ np.asarray(means, dtype=np.float64))
    standard_error = math.sqrt(float(np.sum((weights**2) * np.asarray(variances, dtype=np.float64))))
    radius = float(confidence_z) * standard_error
    return {
        "candidate_strategy": candidate_id,
        "mixture_mean_score": mean,
        "mixture_standard_error": standard_error,
        "mixture_ci_low": max(0.0, mean - radius),
        "mixture_ci_high": min(1.0, mean + radius),
        "games": games,
        "truncations": truncations,
        "opponent_scores": {opponent_id: by_opponent[opponent_id].mean_score for opponent_id in opponent_ids},
    }


def evaluate_candidates_against_mixture(
    candidates: Sequence[FiniteOracleCandidate],
    population: Sequence[StrategyBundle],
    mixture: Sequence[float],
    config: EmpiricalEvaluationConfig,
    *,
    evaluator: EmpiricalGameEvaluator | None = None,
    stage: str,
    support_tolerance: float = 1e-12,
) -> tuple[list[dict[str, object]], list[PairEstimate], list[dict[str, object]]]:
    runner = evaluator or EmpiricalGameEvaluator()
    population_signatures = {strategy_signature(strategy) for strategy in population}
    support = positive_mixture_support(population, mixture, tolerance=support_tolerance)
    support_population = [population[index] for index in support.indices]
    support_weights = list(support.weights)
    opponent_ids = list(support.strategy_ids)
    results: list[dict[str, object]] = []
    all_estimates: list[PairEstimate] = []
    all_rows: list[dict[str, object]] = []
    for candidate in candidates:
        candidate_estimates: list[PairEstimate] = []
        for opponent in support_population:
            estimate, rows = runner.evaluate_focal_pair(candidate.strategy, opponent, config, stage=stage)
            candidate_estimates.append(estimate)
            all_estimates.append(estimate)
            all_rows.extend(rows)
        weighted = weighted_response_estimate(
            candidate.strategy.strategy_id,
            candidate_estimates,
            opponent_ids,
            support_weights,
            confidence_z=config.confidence_z,
        )
        weighted.update(
            {
                "oracle_family": candidate.oracle_family,
                "source": candidate.source,
                "duplicate_of_population": strategy_signature(candidate.strategy) in population_signatures,
                "agent_name": candidate.strategy.agent_name,
                "mulligan_policy": str(candidate.strategy.mulligan_policy),
                "deck": candidate.strategy.deck.counts(),
                "deck_size": candidate.strategy.deck.size,
                "evaluated_support_strategies": opponent_ids,
                "evaluated_support_weights": support_weights,
                "omitted_zero_weight_opponents": support.omitted_zero_weight,
                "mixture_support": support.as_dict(),
                "support_tolerance": float(support_tolerance),
                "support_pruning_error_bound": support.max_score_error_from_pruning,
            }
        )
        results.append(weighted)
    results.sort(
        key=lambda row: (
            bool(not row["duplicate_of_population"]),
            float(row["mixture_mean_score"]),
            float(row["mixture_ci_low"]),
        ),
        reverse=True,
    )
    return results, all_estimates, all_rows


def run_finite_psro_round(
    population: Sequence[StrategyBundle],
    candidates: Sequence[FiniteOracleCandidate],
    *,
    restricted_config: EmpiricalEvaluationConfig,
    selection_config: EmpiricalEvaluationConfig,
    holdout_config: EmpiricalEvaluationConfig,
    confirmation_config: EmpiricalEvaluationConfig | None = None,
    holdout_top_k: int = 3,
    minimum_gain: float = 0.01,
    support_tolerance: float = 1e-12,
) -> dict[str, object]:
    """Run one finite restricted-game -> response-oracle -> confirmation round.

    Selection and holdout narrow the finite oracle catalog.  A candidate is not
    returned for population expansion unless one *additional*, seed-disjoint
    confirmation stage clears the preregistered lower-confidence threshold.
    This keeps ordinary screening from silently becoming strategic promotion.
    """

    if not candidates:
        raise ValueError("candidate set cannot be empty")
    evaluator = EmpiricalGameEvaluator()
    matrix, pair_estimates, restricted_rows = build_symmetric_empirical_game(
        population,
        restricted_config,
        evaluator=evaluator,
        stage="restricted_game",
    )
    solution = zero_sum_maximin(matrix)
    opponent_mixture = tuple(float(value) for value in solution.column_strategy)
    selection, selection_pairs, selection_rows = evaluate_candidates_against_mixture(
        candidates,
        population,
        opponent_mixture,
        selection_config,
        evaluator=evaluator,
        stage="oracle_selection",
        support_tolerance=support_tolerance,
    )
    eligible = [row for row in selection if not bool(row["duplicate_of_population"])]
    selected_ids = [str(row["candidate_strategy"]) for row in eligible[: max(1, int(holdout_top_k))]]
    by_id = {candidate.strategy.strategy_id: candidate for candidate in candidates}
    holdout_candidates = [by_id[candidate_id] for candidate_id in selected_ids]
    holdout, holdout_pairs, holdout_rows = evaluate_candidates_against_mixture(
        holdout_candidates,
        population,
        opponent_mixture,
        holdout_config,
        evaluator=evaluator,
        stage="oracle_holdout",
        support_tolerance=support_tolerance,
    )
    restricted_best_response_value = float(solution.exploitability_upper_value)
    threshold = restricted_best_response_value + float(minimum_gain)
    for row in selection:
        row["selection_excess_over_restricted_best"] = float(row["mixture_mean_score"]) - restricted_best_response_value
    for row in holdout:
        row["holdout_excess_over_restricted_best"] = float(row["mixture_mean_score"]) - restricted_best_response_value
        row["screen_threshold"] = threshold
        row["holdout_screen_pass"] = (
            not bool(row["duplicate_of_population"])
            and int(row["truncations"]) == 0
            and float(row["mixture_ci_low"]) > threshold
        )
    holdout.sort(
        key=lambda row: (bool(row["holdout_screen_pass"]), float(row["mixture_mean_score"])),
        reverse=True,
    )
    screened = [row for row in holdout if bool(row["holdout_screen_pass"])]
    nominated = screened[0] if screened else None

    confirmation: list[dict[str, object]] = []
    confirmation_pairs: list[PairEstimate] = []
    confirmation_rows: list[dict[str, object]] = []
    recommended_expansion: dict[str, object] | None = None
    if nominated is not None and confirmation_config is not None:
        nominated_id = str(nominated["candidate_strategy"])
        confirmation, confirmation_pairs, confirmation_rows = evaluate_candidates_against_mixture(
            [by_id[nominated_id]],
            population,
            opponent_mixture,
            confirmation_config,
            evaluator=evaluator,
            stage="oracle_confirmation",
            support_tolerance=support_tolerance,
        )
        confirmed = confirmation[0]
        confirmed["confirmation_threshold"] = threshold
        confirmed["confirmation_excess_over_restricted_best"] = (
            float(confirmed["mixture_mean_score"]) - restricted_best_response_value
        )
        confirmed["confirmation_pass"] = (
            not bool(confirmed["duplicate_of_population"])
            and int(confirmed["truncations"]) == 0
            and float(confirmed["mixture_ci_low"]) > threshold
        )
        if bool(confirmed["confirmation_pass"]):
            recommended_expansion = by_id[nominated_id].as_dict()
            status = "candidate_confirmed_for_exploratory_expansion"
        else:
            status = "candidate_failed_seed_disjoint_confirmation"
    elif nominated is not None:
        status = "holdout_complete_candidate_nominated"
    else:
        status = "round_complete_no_candidate"

    return {
        "schema": "muc5.psro_round.v2",
        "status": status,
        "population": [strategy.as_dict() for strategy in population],
        "candidates": [candidate.as_dict() for candidate in candidates],
        "restricted_game": {
            "strategy_ids": [strategy.strategy_id for strategy in population],
            "score_matrix": [[float(value) for value in row] for row in matrix],
            "pair_estimates": [estimate.as_dict() for estimate in pair_estimates],
            "solver": {
                "method": solution.solution_method,
                "row_mixture": list(solution.row_strategy),
                "column_mixture": list(solution.column_strategy),
                "guaranteed_value": solution.guaranteed_value,
                "restricted_best_response_value": solution.exploitability_upper_value,
                "solver_gap": solution.exploitability_upper_value - solution.guaranteed_value,
            },
        },
        "oracle_selection": selection,
        "oracle_holdout": holdout,
        "oracle_confirmation": confirmation,
        "nominated_candidate": nominated,
        "recommended_expansion": recommended_expansion,
        "admission_rule": {
            "stage_seed_disjointness_required": True,
            "minimum_gain": float(minimum_gain),
            "threshold": threshold,
            "screen_criterion": "holdout_ci_low > restricted_best_response_value + minimum_gain",
            "confirmation_criterion": "confirmation_ci_low > restricted_best_response_value + minimum_gain and zero truncations",
            "final_confirmation_required": True,
            "automatic_population_mutation": False,
            "scope": "exploratory empirical-game population only; not a strategic promotion",
            "support_tolerance": float(support_tolerance),
            "support_pruning_error_bound": positive_mixture_support(population, opponent_mixture, tolerance=support_tolerance).max_score_error_from_pruning,
        },
        "configs": {
            "restricted": restricted_config.as_dict(),
            "selection": selection_config.as_dict(),
            "holdout": holdout_config.as_dict(),
            "confirmation": None if confirmation_config is None else confirmation_config.as_dict(),
        },
        "game_rows": restricted_rows + selection_rows + holdout_rows + confirmation_rows,
        "pair_estimates": {
            "selection": [estimate.as_dict() for estimate in selection_pairs],
            "holdout": [estimate.as_dict() for estimate in holdout_pairs],
            "confirmation": [estimate.as_dict() for estimate in confirmation_pairs],
        },
    }

