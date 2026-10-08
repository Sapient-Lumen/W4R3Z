from __future__ import annotations

import pytest

from src.muc5.deckspace import DeckVector
from src.muc5.payoff import StrategyBundle
from src.muc5.psro import EmpiricalEvaluationConfig, FiniteOracleCandidate, PairEstimate, evaluate_candidates_against_mixture, positive_mixture_support
from src.muc5.psro_catalog import (
    REV0092_ADMITTED_STRATEGY_ID,
    candidate_by_id,
    current_oracle_catalog,
    current_response_population,
    duplicate_signatures,
    incumbent_population_candidates,
)

DECK = DeckVector(40, 24, 6, 4, 3, 3)


def test_effective_mixture_support_reports_tiny_pruning_error_bound():
    population = [
        StrategyBundle("main", "d", DECK, "heuristic", "land_band"),
        StrategyBundle("dust-a", "d", DECK, "patient", "land_band"),
        StrategyBundle("dust-b", "d", DECK, "counter_guard", "land_band"),
    ]
    support = positive_mixture_support(population, (0.99992, 0.00004, 0.00004), tolerance=0.001)
    assert support.indices == (0,)
    assert support.strategy_ids == ("main",)
    assert support.weights == pytest.approx((1.0,))
    assert support.included_weight == pytest.approx(0.99992)
    assert support.omitted_weight == pytest.approx(0.00008)
    assert support.max_score_error_from_pruning == pytest.approx(0.00008)


def test_candidate_evaluation_can_use_effective_support_tolerance_with_audited_bound():
    population = [
        StrategyBundle("main", "d", DECK, "heuristic", "land_band"),
        StrategyBundle("dust-a", "d", DECK, "patient", "land_band"),
        StrategyBundle("dust-b", "d", DECK, "counter_guard", "land_band"),
    ]
    candidate = FiniteOracleCandidate(
        StrategyBundle("candidate", "d", DECK, "heuristic", "land_band"),
        "unit",
        "unit",
    )

    class _StubEvaluator:
        def __init__(self):
            self.calls = []

        def evaluate_focal_pair(self, focal, opponent, config, *, stage):
            self.calls.append(opponent.strategy_id)
            return (
                PairEstimate(
                    focal.strategy_id,
                    opponent.strategy_id,
                    4,
                    0.75,
                    0.1,
                    0.554,
                    0.946,
                    0,
                    (1.0, 1.0, 0.5, 0.5),
                ),
                [],
            )

    evaluator = _StubEvaluator()
    results, estimates, _ = evaluate_candidates_against_mixture(
        [candidate],
        population,
        (0.99992, 0.00004, 0.00004),
        EmpiricalEvaluationConfig(life_totals=(20,), reps=1),
        evaluator=evaluator,
        stage="unit_effective_support",
        support_tolerance=0.001,
    )
    assert evaluator.calls == ["main"]
    assert len(estimates) == 1
    assert results[0]["support_pruning_error_bound"] == pytest.approx(0.00008)
    assert results[0]["evaluated_support_strategies"] == ["main"]


def test_rev0094_catalog_refactor_reconstructs_population_and_admitted_response():
    population = current_response_population("data/seed_decks.json")
    catalog = current_oracle_catalog(".", population)
    admitted = candidate_by_id(catalog, REV0092_ADMITTED_STRATEGY_ID)
    expanded = [*population, admitted.strategy]
    controls = incumbent_population_candidates(population)
    duplicates = duplicate_signatures(expanded, controls)

    assert len(population) == 8
    assert len(catalog) == 16
    assert admitted.strategy.deck.size == 60
    assert admitted.strategy.agent_name == "infostate_counter_guard"
    assert set(duplicates) == {strategy.strategy_id for strategy in population}
