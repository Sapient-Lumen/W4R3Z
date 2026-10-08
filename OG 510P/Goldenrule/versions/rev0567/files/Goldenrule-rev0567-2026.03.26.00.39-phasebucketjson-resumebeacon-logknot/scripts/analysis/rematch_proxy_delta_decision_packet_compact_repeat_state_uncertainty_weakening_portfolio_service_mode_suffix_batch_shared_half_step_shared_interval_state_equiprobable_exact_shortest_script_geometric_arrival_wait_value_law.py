#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law import (
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _normalize_fraction(numerator: int, denominator: int = 1) -> Fraction:
    numerator = int(numerator)
    denominator = int(denominator)
    if denominator <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'fraction denominator must be positive'
        )
    return Fraction(numerator, denominator)


@lru_cache(maxsize=None)
def build_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_profile(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'current batch length must be positive'
        )
    marginal = evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain(state, current_batch_length)
    marginal_gain = Fraction(
        int(marginal['equiprobable_marginal_mean_cost_gain_bits_per_script']['numerator']),
        int(marginal['equiprobable_marginal_mean_cost_gain_bits_per_script']['denominator']),
    )
    state_prefix_bits = int(marginal['marginal_gain_state_prefix_bits'])
    return {
        'state': serialize_feasible_interval_kernel_state(state),
        'current_batch_length': current_batch_length,
        'state_prefix_bits': state_prefix_bits,
        'marginal_gain_bits_per_script_if_one_more_same_state_script_arrives': _serialize_fraction(marginal_gain),
        'marginal_gain_formula': f'{state_prefix_bits}/(n(n+1))',
    }


@lru_cache(maxsize=None)
def evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    timeout_ticks: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    timeout_ticks = int(timeout_ticks)
    if timeout_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'timeout ticks must be positive'
        )
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'hold cost must be nonnegative'
        )

    profile = build_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_profile(state, current_batch_length)
    marginal_gain = Fraction(
        int(profile['marginal_gain_bits_per_script_if_one_more_same_state_script_arrives']['numerator']),
        int(profile['marginal_gain_bits_per_script_if_one_more_same_state_script_arrives']['denominator']),
    )

    if arrival_probability == 0:
        success_probability = Fraction(0, 1)
        expected_wait_ticks = Fraction(timeout_ticks, 1)
        expected_gross_gain = Fraction(0, 1)
        expected_net_value = -hold_cost * expected_wait_ticks
        sign_invariant_term = -hold_cost
        sign_classification = 'negative' if expected_net_value < 0 else 'zero'
        return {
            **profile,
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'timeout_ticks': timeout_ticks,
            'success_probability_by_timeout': _serialize_fraction(success_probability),
            'expected_wait_ticks_until_success_or_timeout': _serialize_fraction(expected_wait_ticks),
            'expected_gross_gain_bits_per_script': _serialize_fraction(expected_gross_gain),
            'expected_net_wait_value_bits_per_script': _serialize_fraction(expected_net_value),
            'sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(sign_invariant_term),
            'sign_classification': sign_classification,
            'sign_is_timeout_invariant': True,
            'net_formula': '-hold_cost * timeout_ticks (arrival probability zero)',
        }

    failure_probability = Fraction(1, 1) - arrival_probability
    success_probability = Fraction(1, 1) - failure_probability ** timeout_ticks
    expected_wait_ticks = sum(failure_probability ** step for step in range(timeout_ticks))
    expected_gross_gain = success_probability * marginal_gain
    expected_net_value = expected_gross_gain - hold_cost * expected_wait_ticks
    sign_invariant_term = arrival_probability * marginal_gain - hold_cost
    if sign_invariant_term > 0:
        sign_classification = 'positive'
    elif sign_invariant_term < 0:
        sign_classification = 'negative'
    else:
        sign_classification = 'zero'

    return {
        **profile,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'timeout_ticks': timeout_ticks,
        'success_probability_by_timeout': _serialize_fraction(success_probability),
        'expected_wait_ticks_until_success_or_timeout': _serialize_fraction(expected_wait_ticks),
        'expected_gross_gain_bits_per_script': _serialize_fraction(expected_gross_gain),
        'expected_net_wait_value_bits_per_script': _serialize_fraction(expected_net_value),
        'sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(sign_invariant_term),
        'sign_classification': sign_classification,
        'sign_is_timeout_invariant': True,
        'net_formula': '(1 - (1 - p)^T) * (gain - hold_cost / p)',
    }


@lru_cache(maxsize=None)
def compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair(
    state: tuple[int, int] | list[int],
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'hold cost must be nonnegative'
        )

    profile = build_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_profile(state, 1)
    state_prefix_bits = int(profile['state_prefix_bits'])

    if hold_cost == 0:
        return {
            'state': serialize_feasible_interval_kernel_state(state),
            'state_prefix_bits': state_prefix_bits,
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'maximum_strictly_positive_current_batch_length': None,
            'strictly_positive_wait_exists': arrival_probability > 0,
            'reason': 'zero_hold_cost_unbounded' if arrival_probability > 0 else 'zero_arrival_zero_hold_cost',
            'sign_boundary_condition': 'arrival_probability * state_prefix_bits / (n(n+1)) > hold_cost',
        }

    if arrival_probability == 0:
        return {
            'state': serialize_feasible_interval_kernel_state(state),
            'state_prefix_bits': state_prefix_bits,
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'maximum_strictly_positive_current_batch_length': None,
            'strictly_positive_wait_exists': False,
            'reason': 'zero_arrival_probability',
            'sign_boundary_condition': 'arrival_probability * state_prefix_bits / (n(n+1)) > hold_cost',
        }

    ratio = arrival_probability * state_prefix_bits / hold_cost
    quota = int(math.floor((ratio.numerator - 1) / ratio.denominator)) if ratio > 0 else -1
    if quota < 2:
        return {
            'state': serialize_feasible_interval_kernel_state(state),
            'state_prefix_bits': state_prefix_bits,
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'maximum_strictly_positive_current_batch_length': None,
            'strictly_positive_wait_exists': False,
            'reason': 'hold_cost_dominates_even_at_batch_length_one',
            'strict_positive_ratio_budget_ps_over_c': _serialize_fraction(ratio),
            'sign_boundary_condition': 'arrival_probability * state_prefix_bits / (n(n+1)) > hold_cost',
        }

    maximum_current_batch_length = (math.isqrt(1 + 4 * quota) - 1) // 2
    achieved_term = arrival_probability * Fraction(state_prefix_bits, maximum_current_batch_length * (maximum_current_batch_length + 1)) - hold_cost
    next_term = arrival_probability * Fraction(state_prefix_bits, (maximum_current_batch_length + 1) * (maximum_current_batch_length + 2)) - hold_cost
    return {
        'state': serialize_feasible_interval_kernel_state(state),
        'state_prefix_bits': state_prefix_bits,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'maximum_strictly_positive_current_batch_length': maximum_current_batch_length,
        'strictly_positive_wait_exists': True,
        'reason': 'closed_form_positive_wait_inversion',
        'strict_positive_ratio_budget_ps_over_c': _serialize_fraction(ratio),
        'achieved_sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(achieved_term),
        'next_nonpositive_sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(next_term),
        'sign_boundary_condition': 'arrival_probability * state_prefix_bits / (n(n+1)) > hold_cost',
    }


@lru_cache(maxsize=None)
def compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
) -> dict[str, Any]:
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'hold cost must be nonnegative'
        )
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
            'arrival probability must lie in [0, 1]'
        )

    if hold_cost == 0:
        return {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'maximum_strictly_positive_current_batch_length': None,
            'strictly_positive_wait_exists': arrival_probability > 0,
            'guarantee_scope': 'all_realized_states',
            'guarantee_state_prefix_bits': 7,
            'reason': 'zero_hold_cost_unbounded' if arrival_probability > 0 else 'zero_arrival_zero_hold_cost',
            'sign_boundary_condition': 'arrival_probability * 7 / (n(n+1)) > hold_cost',
        }

    if arrival_probability == 0:
        return {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'maximum_strictly_positive_current_batch_length': None,
            'strictly_positive_wait_exists': False,
            'guarantee_scope': 'all_realized_states',
            'guarantee_state_prefix_bits': 7,
            'reason': 'zero_arrival_probability',
            'sign_boundary_condition': 'arrival_probability * 7 / (n(n+1)) > hold_cost',
        }

    ratio = arrival_probability * 7 / hold_cost
    quota = int(math.floor((ratio.numerator - 1) / ratio.denominator)) if ratio > 0 else -1
    if quota < 2:
        return {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'maximum_strictly_positive_current_batch_length': None,
            'strictly_positive_wait_exists': False,
            'guarantee_scope': 'all_realized_states',
            'guarantee_state_prefix_bits': 7,
            'reason': 'hold_cost_dominates_even_at_batch_length_one',
            'strict_positive_ratio_budget_ps_over_c': _serialize_fraction(ratio),
            'sign_boundary_condition': 'arrival_probability * 7 / (n(n+1)) > hold_cost',
        }

    maximum_current_batch_length = (math.isqrt(1 + 4 * quota) - 1) // 2
    achieved_term = arrival_probability * Fraction(7, maximum_current_batch_length * (maximum_current_batch_length + 1)) - hold_cost
    next_term = arrival_probability * Fraction(7, (maximum_current_batch_length + 1) * (maximum_current_batch_length + 2)) - hold_cost
    return {
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'maximum_strictly_positive_current_batch_length': maximum_current_batch_length,
        'strictly_positive_wait_exists': True,
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'reason': 'closed_form_positive_wait_inversion',
        'strict_positive_ratio_budget_ps_over_c': _serialize_fraction(ratio),
        'achieved_sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(achieved_term),
        'next_nonpositive_sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(next_term),
        'sign_boundary_condition': 'arrival_probability * 7 / (n(n+1)) > hold_cost',
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_wait_value_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 9))
    arrival_probabilities = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    hold_costs = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    timeouts = tuple(range(1, 7))

    matched_cases = 0
    timeout_sign_invariance_checks = 0
    for state in states:
        for batch_length in audited_batch_lengths:
            marginal_gain = Fraction(
                int(
                    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                        state,
                        batch_length,
                        1,
                        2,
                        1,
                        10,
                        1,
                    )['marginal_gain_bits_per_script_if_one_more_same_state_script_arrives']['numerator']
                ),
                int(
                    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                        state,
                        batch_length,
                        1,
                        2,
                        1,
                        10,
                        1,
                    )['marginal_gain_bits_per_script_if_one_more_same_state_script_arrives']['denominator']
                ),
            )
            for arrival_probability in arrival_probabilities:
                for hold_cost in hold_costs:
                    expected_sign = arrival_probability * marginal_gain - hold_cost
                    sign_labels = []
                    for timeout_ticks in timeouts:
                        result = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                            state,
                            batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            timeout_ticks,
                        )
                        direct_success_probability = Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** timeout_ticks
                        direct_expected_wait_ticks = sum((Fraction(1, 1) - arrival_probability) ** step for step in range(timeout_ticks))
                        direct_expected_gross_gain = direct_success_probability * marginal_gain
                        direct_expected_net = direct_expected_gross_gain - hold_cost * direct_expected_wait_ticks
                        reported_net = Fraction(
                            int(result['expected_net_wait_value_bits_per_script']['numerator']),
                            int(result['expected_net_wait_value_bits_per_script']['denominator']),
                        )
                        if direct_expected_net != reported_net:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
                                f'net-value mismatch for state {state}, batch {batch_length}, p={arrival_probability}, c={hold_cost}, T={timeout_ticks}: {direct_expected_net} != {reported_net}'
                            )
                        reported_term = Fraction(
                            int(result['sign_invariant_term_bits_per_script_per_tick']['numerator']),
                            int(result['sign_invariant_term_bits_per_script_per_tick']['denominator']),
                        )
                        if reported_term != expected_sign:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
                                f'sign-invariant-term mismatch for state {state}, batch {batch_length}, p={arrival_probability}, c={hold_cost}'
                            )
                        sign_labels.append(result['sign_classification'])
                        matched_cases += 1
                    if len(set(sign_labels)) != 1:
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
                            f'timeout sign invariance failed for state {state}, batch {batch_length}, p={arrival_probability}, c={hold_cost}'
                        )
                    timeout_sign_invariance_checks += 1

    state_schedule_pairs = [
        ((0, 16), Fraction(1, 2), Fraction(1, 10)),
        ((7, 12), Fraction(1, 4), Fraction(1, 10)),
        ((8, 8), Fraction(3, 4), Fraction(1, 4)),
        ((15, 15), Fraction(1, 4), Fraction(1, 2)),
    ]
    validated_state_schedules = 0
    for state, arrival_probability, hold_cost in state_schedule_pairs:
        schedule = compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair(
            state,
            arrival_probability.numerator,
            arrival_probability.denominator,
            hold_cost.numerator,
            hold_cost.denominator,
        )
        max_n = schedule['maximum_strictly_positive_current_batch_length']
        if schedule['strictly_positive_wait_exists']:
            assert max_n is not None
            good = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                state,
                max_n,
                arrival_probability.numerator,
                arrival_probability.denominator,
                hold_cost.numerator,
                hold_cost.denominator,
                5,
            )
            next_bad = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                state,
                max_n + 1,
                arrival_probability.numerator,
                arrival_probability.denominator,
                hold_cost.numerator,
                hold_cost.denominator,
                5,
            )
            if Fraction(int(good['expected_net_wait_value_bits_per_script']['numerator']), int(good['expected_net_wait_value_bits_per_script']['denominator'])) <= 0:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
                    f'state schedule failed to certify positive wait value for state {state}'
                )
            if Fraction(int(next_bad['expected_net_wait_value_bits_per_script']['numerator']), int(next_bad['expected_net_wait_value_bits_per_script']['denominator'])) > 0:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
                    f'state schedule failed to stop before nonpositive region for state {state}'
                )
        validated_state_schedules += 1

    universal_pairs = [
        (Fraction(1, 4), Fraction(1, 10)),
        (Fraction(1, 2), Fraction(1, 10)),
        (Fraction(3, 4), Fraction(1, 10)),
        (Fraction(1, 2), Fraction(1, 4)),
        (Fraction(1, 4), Fraction(1, 2)),
    ]
    validated_universal_schedules = 0
    for arrival_probability, hold_cost in universal_pairs:
        schedule = compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(
            arrival_probability.numerator,
            arrival_probability.denominator,
            hold_cost.numerator,
            hold_cost.denominator,
        )
        max_n = schedule['maximum_strictly_positive_current_batch_length']
        if schedule['strictly_positive_wait_exists']:
            assert max_n is not None
            worst_good = min(
                Fraction(
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(state, max_n, arrival_probability.numerator, arrival_probability.denominator, hold_cost.numerator, hold_cost.denominator, 5)['expected_net_wait_value_bits_per_script']['numerator']),
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(state, max_n, arrival_probability.numerator, arrival_probability.denominator, hold_cost.numerator, hold_cost.denominator, 5)['expected_net_wait_value_bits_per_script']['denominator']),
                )
                for state in states
            )
            worst_next = min(
                Fraction(
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(state, max_n + 1, arrival_probability.numerator, arrival_probability.denominator, hold_cost.numerator, hold_cost.denominator, 5)['expected_net_wait_value_bits_per_script']['numerator']),
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(state, max_n + 1, arrival_probability.numerator, arrival_probability.denominator, hold_cost.numerator, hold_cost.denominator, 5)['expected_net_wait_value_bits_per_script']['denominator']),
                )
                for state in states
            )
            if worst_good <= 0:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
                    f'universal schedule failed for p={arrival_probability}, c={hold_cost}'
                )
            if worst_next > 0:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalWaitValueLawError(
                    f'universal schedule failed to stop before nonpositive region for p={arrival_probability}, c={hold_cost}'
                )
        validated_universal_schedules += 1

    return {
        'audited_state_count': len(states),
        'validated_state_batch_probability_cost_timeout_cases': matched_cases,
        'validated_timeout_sign_invariance_panels': timeout_sign_invariance_checks,
        'validated_state_schedule_pairs': validated_state_schedules,
        'validated_universal_schedule_pairs': validated_universal_schedules,
        'audited_batch_lengths': list(audited_batch_lengths),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in arrival_probabilities],
        'audited_hold_costs': [_serialize_fraction(value) for value in hold_costs],
        'audited_timeouts': list(timeouts),
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_wait_value_validation_summary()
    universal_schedule = [
        compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 4, 1, 10),
        compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 2, 1, 10),
        compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(3, 4, 1, 10),
        compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 2, 1, 4),
        compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 4, 1, 2),
    ]
    state_examples = [
        compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((0, 16), 1, 2, 1, 10),
        compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((7, 12), 1, 4, 1, 10),
        compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((8, 8), 3, 4, 1, 4),
        compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((15, 15), 1, 4, 1, 2),
    ]
    timeout_examples = [
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value((7, 12), 3, 1, 2, 1, 10, 1),
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value((7, 12), 3, 1, 2, 1, 10, 3),
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value((7, 12), 3, 1, 2, 1, 10, 6),
    ]
    return {
        'focus': 'shared-state equiprobable exact-shortest-script waiting gated by geometric same-state arrival hazard and per-tick hold cost',
        'headline_findings': {
            'catalog_state_count': validation_summary['audited_state_count'],
            'validated_state_batch_probability_cost_timeout_cases': validation_summary['validated_state_batch_probability_cost_timeout_cases'],
            'validated_timeout_sign_invariance_panels': validation_summary['validated_timeout_sign_invariance_panels'],
            'universal_all_state_rule': 'wait iff arrival_probability * 7 / (n(n+1)) > hold_cost',
            'timeout_sign_result': 'for any positive arrival probability, timeout only scales magnitude; it never changes the sign of expected net wait value',
        },
        'decision_rules': [
            'When a live writer may wait up to T ticks for one more same-state exact script, with independent same-state arrival probability p per tick and hold cost c bits per script per tick, expected net wait value equals (1 - (1 - p)^T) * (gain - c/p).',
            'Here gain is the one-more-script marginal mean-cost reduction, i.e. state_prefix_bits / (n(n+1)) on the current path.',
            'For any positive arrival probability, timeout T cannot change the sign of the waiting decision; it only rescales the magnitude by the success-capture factor 1 - (1 - p)^T.',
            'Therefore the exact sign test is p * state_prefix_bits / (n(n+1)) > c for a known state family, and p * 7 / (n(n+1)) > c for all-state guarantees on the current path.',
            'Equivalently, with positive hold cost use maximum_current_batch_length = floor((sqrt(1 + 4 * floor((p * state_prefix_bits / c) - epsilon)) - 1) / 2) under the strict inequality; if hold cost is zero and p > 0, waiting remains strictly positive for every current batch length.',
        ],
        'validation_summary': validation_summary,
        'universal_schedule_examples': universal_schedule,
        'state_examples': state_examples,
        'timeout_examples': timeout_examples,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_snapshot(), indent=2, sort_keys=True))
