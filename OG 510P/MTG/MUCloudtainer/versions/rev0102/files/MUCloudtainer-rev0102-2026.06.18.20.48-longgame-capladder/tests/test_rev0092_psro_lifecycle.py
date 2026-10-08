from __future__ import annotations

from random import Random

import pytest

from src.muc5.action_schema import activate_jace
from src.muc5.agents import play_public_agent_game
from src.muc5.cards import CARD_FORCE, CARD_ISLAND
from src.muc5.decision import DecisionFrame, PublicHeuristicAgent
from src.muc5.deckspace import DeckVector
from src.muc5.payoff import StrategyBundle
from src.muc5.psro import EmpiricalEvaluationConfig, build_symmetric_empirical_game, stable_seed
from src.muc5.public_agents import PublicInformationStateAgent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.replay import record_public_decision_trace


DECK = DeckVector(40, 24, 6, 4, 3, 3)


class _StatefulProbe:
    name = "stateful_probe_rev0092"
    requires_episode_reset = True

    def __init__(self) -> None:
        self.base = PublicHeuristicAgent()
        self.reset_contexts = []
        self.end_results = []
        self.steps_this_episode = 999

    def reset_episode(self, context) -> None:
        self.reset_contexts.append(context)
        self.steps_this_episode = 0

    def choose_action_index(self, frame, rng) -> int:
        assert self.steps_this_episode < 999
        self.steps_this_episode += 1
        return self.base.choose_action_index(frame, rng)

    def end_episode(self, result) -> None:
        self.end_results.append(result)


def test_public_game_resets_reused_stateful_wrappers_and_finishes_each_seat():
    left = _StatefulProbe()
    right = _StatefulProbe()
    for episode in ("episode-a", "episode-b"):
        play_public_agent_game(
            DECK,
            DECK,
            left,
            right,
            seed=9201,
            max_decisions=12,
            record_log=False,
            episode_id=episode,
        )

    assert [context.episode_id for context in left.reset_contexts] == ["episode-a", "episode-b"]
    assert [context.player for context in left.reset_contexts] == [0, 0]
    assert [context.player for context in right.reset_contexts] == [1, 1]
    assert len(left.end_results) == len(right.end_results) == 2
    assert all(result.player == 0 for result in left.end_results)
    assert all(result.player == 1 for result in right.end_results)


def test_same_mutable_policy_object_cannot_occupy_both_seats():
    shared = _StatefulProbe()
    with pytest.raises(ValueError, match="distinct policy objects"):
        play_public_agent_game(DECK, DECK, shared, shared, seed=9202, max_decisions=2, record_log=False)


def test_replay_recording_uses_the_same_episode_lifecycle_contract():
    left = _StatefulProbe()
    right = _StatefulProbe()
    trace = record_public_decision_trace(DECK, DECK, left, right, seed=9203, max_decisions=8)
    assert trace["events"]
    assert len(left.reset_contexts) == len(right.reset_contexts) == 1
    assert len(left.end_results) == len(right.end_results) == 1
    assert left.reset_contexts[0].episode_id.startswith("trace-")


def test_information_state_changes_a_decision_with_identical_observation():
    observation = {
        "frame": "MAIN",
        "player": 0,
        "starting_life": 20,
        "public_self": {"life": 20, "islands_untapped": 4, "jace_loyalty": 3},
        "public_opponent": {"life": 20},
    }
    actions = (
        activate_jace("zero"),
        activate_jace("plus2", target_player="opponent"),
    )
    own_island = DecisionFrame(
        player=0,
        state_revision=1,
        observation=observation,
        legal_actions=actions,
        information_state={"known_top_cards": {"0": CARD_ISLAND}, "public_events": []},
    )
    opponent_force = DecisionFrame(
        player=0,
        state_revision=1,
        observation=observation,
        legal_actions=actions,
        information_state={"known_top_cards": {"1": CARD_FORCE}, "public_events": []},
    )
    agent = PublicInformationStateAgent("heuristic")
    assert agent.choose_action_index(own_island, Random(1)) == 0
    assert agent.choose_action_index(opponent_force, Random(1)) == 1


def test_public_payoff_cache_is_seat_scoped_even_for_self_play():
    strategy = StrategyBundle("self", "self", DECK, "heuristic", "land_band")
    rows = build_public_payoff_rows(
        [strategy],
        simulator_revision="rev0092",
        life_totals=(20,),
        reps=1,
        base_seed=9204,
        max_decisions=6,
    )
    assert len(rows) == 2
    assert all(row["strategy0"] == row["strategy1"] == "self" for row in rows)


def test_empirical_game_is_constant_sum_and_stage_seeds_are_namespaced():
    population = [
        StrategyBundle("balanced", "balanced", DECK, "heuristic", "land_band"),
        StrategyBundle("patient", "patient", DECK, "patient", "land_band"),
    ]
    matrix, estimates, rows = build_symmetric_empirical_game(
        population,
        EmpiricalEvaluationConfig(life_totals=(20,), reps=1, max_decisions=8, base_seed=9205),
        stage="unit_restricted",
    )
    assert matrix.shape == (2, 2)
    assert matrix[0, 0] == matrix[1, 1] == 0.5
    assert matrix[0, 1] + matrix[1, 0] == pytest.approx(1.0)
    assert len(estimates) == 1
    assert len(rows) == 4
    assert stable_seed(9205, "selection", "x") != stable_seed(9205, "holdout", "x")


def test_response_evaluation_skips_exact_zero_weight_opponents():
    from src.muc5.psro import (
        FiniteOracleCandidate,
        PairEstimate,
        evaluate_candidates_against_mixture,
    )

    population = [
        StrategyBundle("opp-live", "d", DECK, "heuristic", "land_band"),
        StrategyBundle("opp-zero-a", "d", DECK, "patient", "land_band"),
        StrategyBundle("opp-zero-b", "d", DECK, "counter_guard", "land_band"),
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
            estimate = PairEstimate(
                focal.strategy_id,
                opponent.strategy_id,
                4,
                0.75,
                0.1,
                0.554,
                0.946,
                0,
                (1.0, 1.0, 0.5, 0.5),
            )
            return estimate, []

    evaluator = _StubEvaluator()
    results, estimates, rows = evaluate_candidates_against_mixture(
        [candidate],
        population,
        (1.0, 0.0, 0.0),
        EmpiricalEvaluationConfig(life_totals=(20,), reps=1),
        evaluator=evaluator,
        stage="unit_support",
    )
    assert evaluator.calls == ["opp-live"]
    assert len(estimates) == 1
    assert rows == []
    assert results[0]["omitted_zero_weight_opponents"] == 2
    assert results[0]["evaluated_support_strategies"] == ["opp-live"]


def test_empirical_evaluator_cache_keys_complete_strategy_not_recycled_id():
    from src.muc5.psro import EmpiricalGameEvaluator

    created = []

    def factory(name):
        marker = object()
        created.append((name, marker))
        return marker

    evaluator = EmpiricalGameEvaluator(agent_factory=factory)
    first = StrategyBundle("recycled", "d", DECK, "heuristic", "land_band")
    changed = StrategyBundle("recycled", "d", DECK, "patient", "land_band")
    first_object = evaluator.agent(first, 0)
    changed_object = evaluator.agent(changed, 0)
    assert first_object is not changed_object
    assert [name for name, _ in created] == ["heuristic", "patient"]


def test_positive_mixture_support_normalizes_and_reports_omitted_rows():
    from src.muc5.psro import positive_mixture_support

    population = [
        StrategyBundle("a", "d", DECK, "heuristic", "land_band"),
        StrategyBundle("b", "d", DECK, "patient", "land_band"),
        StrategyBundle("c", "d", DECK, "counter_guard", "land_band"),
    ]
    support = positive_mixture_support(population, (2.0, 0.0, 6.0))
    assert support.indices == (0, 2)
    assert support.strategy_ids == ("a", "c")
    assert support.weights == pytest.approx((0.25, 0.75))
    assert support.omitted_zero_weight == 1

    with pytest.raises(ValueError, match="finite and nonnegative"):
        positive_mixture_support(population, (1.0, -0.1, 0.0))
