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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law import (
    compute_minimum_timeout_for_capture_fraction,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law import (
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
            'fraction denominator must be positive'
        )
    return Fraction(numerator, denominator)


def _deserialize_fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


@lru_cache(maxsize=None)
def compute_capture_adjusted_effective_hold_cost_for_target_margin(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_capture_numerator: int,
    target_capture_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = _normalize_fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
            'hold cost must be nonnegative'
        )
    if target_margin < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
            'target margin must be nonnegative'
        )

    timeout_policy = compute_minimum_timeout_for_capture_fraction(
        arrival_probability.numerator,
        arrival_probability.denominator,
        int(target_capture_numerator),
        int(target_capture_denominator),
    )
    if not timeout_policy['finite_timeout_exists']:
        return {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'target_margin_bits_per_script': _serialize_fraction(target_margin),
            'target_capture_fraction_of_asymptotic_positive_wait_value': timeout_policy['target_capture_fraction_of_asymptotic_positive_wait_value'],
            'effective_hold_cost_bits_per_script_per_tick': None,
            'effective_margin_tax_bits_per_script_per_tick': None,
            'capture_fraction_by_minimum_timeout': None,
            'minimum_timeout_ticks': None,
            'finite_timeout_exists': False,
            'margin_floor_finite_policy_exists': False,
            'reason': timeout_policy['reason'],
        }

    capture_fraction = _deserialize_fraction(timeout_policy['achieved_capture_fraction_by_minimum_timeout'])
    effective_margin_tax = Fraction(0, 1) if target_margin == 0 else arrival_probability * target_margin / capture_fraction
    effective_hold_cost = hold_cost + effective_margin_tax
    return {
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'target_capture_fraction_of_asymptotic_positive_wait_value': timeout_policy['target_capture_fraction_of_asymptotic_positive_wait_value'],
        'effective_hold_cost_bits_per_script_per_tick': _serialize_fraction(effective_hold_cost),
        'effective_margin_tax_bits_per_script_per_tick': _serialize_fraction(effective_margin_tax),
        'capture_fraction_by_minimum_timeout': timeout_policy['achieved_capture_fraction_by_minimum_timeout'],
        'minimum_timeout_ticks': timeout_policy['minimum_timeout_ticks'],
        'expected_wait_ticks_by_minimum_timeout': timeout_policy['expected_wait_ticks_by_minimum_timeout'],
        'finite_timeout_exists': True,
        'margin_floor_finite_policy_exists': True,
        'timeout_closed_form': timeout_policy['timeout_closed_form'],
        'reason': 'capture_target_turns_margin_floor_into_effective_hold_cost',
        'margin_floor_condition': 'p * state_prefix_bits / (n(n+1)) >= hold_cost + p * target_margin / capture_fraction',
    }


@lru_cache(maxsize=None)
def evaluate_timeout_margin_floor_policy_for_state_batch(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_capture_numerator: int,
    target_capture_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
            'current batch length must be positive'
        )

    effective_hold_cost_profile = compute_capture_adjusted_effective_hold_cost_for_target_margin(
        int(arrival_probability_numerator),
        int(arrival_probability_denominator),
        int(hold_cost_bits_numerator),
        int(hold_cost_bits_denominator),
        int(target_capture_numerator),
        int(target_capture_denominator),
        int(target_margin_bits_numerator),
        int(target_margin_bits_denominator),
    )
    target_margin = _normalize_fraction(target_margin_bits_numerator, target_margin_bits_denominator)

    result: dict[str, Any] = {
        'state': serialize_feasible_interval_kernel_state(state),
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': effective_hold_cost_profile['arrival_probability_per_tick'],
        'hold_cost_bits_per_script_per_tick': effective_hold_cost_profile['hold_cost_bits_per_script_per_tick'],
        'target_capture_fraction_of_asymptotic_positive_wait_value': effective_hold_cost_profile['target_capture_fraction_of_asymptotic_positive_wait_value'],
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'effective_hold_cost_bits_per_script_per_tick': effective_hold_cost_profile['effective_hold_cost_bits_per_script_per_tick'],
        'effective_margin_tax_bits_per_script_per_tick': effective_hold_cost_profile['effective_margin_tax_bits_per_script_per_tick'],
        'capture_fraction_by_minimum_timeout': effective_hold_cost_profile['capture_fraction_by_minimum_timeout'],
        'minimum_timeout_ticks': effective_hold_cost_profile['minimum_timeout_ticks'],
        'reason': effective_hold_cost_profile['reason'],
    }

    if not effective_hold_cost_profile['margin_floor_finite_policy_exists']:
        result['meets_target_margin'] = False
        return result

    timeout_ticks = int(effective_hold_cost_profile['minimum_timeout_ticks'])
    wait_value = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        state,
        current_batch_length,
        int(arrival_probability_numerator),
        int(arrival_probability_denominator),
        int(hold_cost_bits_numerator),
        int(hold_cost_bits_denominator),
        timeout_ticks,
    )
    achieved_margin = _deserialize_fraction(wait_value['expected_net_wait_value_bits_per_script'])
    effective_hold_cost = _deserialize_fraction(effective_hold_cost_profile['effective_hold_cost_bits_per_script_per_tick'])
    arrival_probability = _deserialize_fraction(wait_value['arrival_probability_per_tick'])
    state_prefix_bits = int(wait_value['state_prefix_bits'])
    threshold_term = arrival_probability * Fraction(state_prefix_bits, current_batch_length * (current_batch_length + 1))
    meets_target = achieved_margin >= target_margin
    closed_form_meets_target = threshold_term >= effective_hold_cost
    if meets_target != closed_form_meets_target:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
            f'margin-floor closed form mismatch for state {state}, n={current_batch_length}'
        )

    result.update(
        {
            'state_prefix_bits': state_prefix_bits,
            'achieved_margin_bits_per_script_by_minimum_timeout': wait_value['expected_net_wait_value_bits_per_script'],
            'meets_target_margin': meets_target,
            'closed_form_margin_floor_term_bits_per_script_per_tick': _serialize_fraction(threshold_term),
            'margin_floor_condition': 'p * state_prefix_bits / (n(n+1)) >= hold_cost + p * target_margin / capture_fraction',
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_max_current_batch_length_for_state_capture_target_margin(
    state: tuple[int, int] | list[int],
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_capture_numerator: int,
    target_capture_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    profile_at_one = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        state,
        1,
        1,
        2,
        1,
        10,
        1,
    )
    state_prefix_bits = int(profile_at_one['state_prefix_bits'])
    effective_hold_cost_profile = compute_capture_adjusted_effective_hold_cost_for_target_margin(
        int(arrival_probability_numerator),
        int(arrival_probability_denominator),
        int(hold_cost_bits_numerator),
        int(hold_cost_bits_denominator),
        int(target_capture_numerator),
        int(target_capture_denominator),
        int(target_margin_bits_numerator),
        int(target_margin_bits_denominator),
    )

    result: dict[str, Any] = {
        'state': serialize_feasible_interval_kernel_state(state),
        'state_prefix_bits': state_prefix_bits,
        'arrival_probability_per_tick': effective_hold_cost_profile['arrival_probability_per_tick'],
        'hold_cost_bits_per_script_per_tick': effective_hold_cost_profile['hold_cost_bits_per_script_per_tick'],
        'target_capture_fraction_of_asymptotic_positive_wait_value': effective_hold_cost_profile['target_capture_fraction_of_asymptotic_positive_wait_value'],
        'target_margin_bits_per_script': effective_hold_cost_profile['target_margin_bits_per_script'],
        'effective_hold_cost_bits_per_script_per_tick': effective_hold_cost_profile['effective_hold_cost_bits_per_script_per_tick'],
        'effective_margin_tax_bits_per_script_per_tick': effective_hold_cost_profile['effective_margin_tax_bits_per_script_per_tick'],
        'capture_fraction_by_minimum_timeout': effective_hold_cost_profile['capture_fraction_by_minimum_timeout'],
        'minimum_timeout_ticks': effective_hold_cost_profile['minimum_timeout_ticks'],
        'maximum_current_batch_length_meeting_target_margin': None,
        'margin_floor_feasible': False,
        'reason': effective_hold_cost_profile['reason'],
        'margin_floor_condition': 'p * state_prefix_bits / (n(n+1)) >= hold_cost + p * target_margin / capture_fraction',
    }

    if not effective_hold_cost_profile['margin_floor_finite_policy_exists']:
        return result

    arrival_probability = _deserialize_fraction(effective_hold_cost_profile['arrival_probability_per_tick'])
    effective_hold_cost = _deserialize_fraction(effective_hold_cost_profile['effective_hold_cost_bits_per_script_per_tick'])

    if effective_hold_cost == 0:
        result.update(
            {
                'maximum_current_batch_length_meeting_target_margin': None,
                'margin_floor_feasible': True,
                'reason': 'zero_effective_hold_cost_unbounded',
            }
        )
        return result

    ratio_budget = arrival_probability * state_prefix_bits / effective_hold_cost
    quota = math.floor(ratio_budget)
    if quota < 2:
        result.update(
            {
                'margin_floor_feasible': False,
                'strict_ratio_budget_ps_over_effective_cost': _serialize_fraction(ratio_budget),
                'reason': 'target_margin_unattainable_even_at_batch_length_one',
            }
        )
        return result

    maximum_current_batch_length = (math.isqrt(1 + 4 * quota) - 1) // 2
    timeout_ticks = int(effective_hold_cost_profile['minimum_timeout_ticks'])
    achieved_margin = _deserialize_fraction(
        evaluate_timeout_margin_floor_policy_for_state_batch(
            state,
            maximum_current_batch_length,
            int(arrival_probability_numerator),
            int(arrival_probability_denominator),
            int(hold_cost_bits_numerator),
            int(hold_cost_bits_denominator),
            int(target_capture_numerator),
            int(target_capture_denominator),
            int(target_margin_bits_numerator),
            int(target_margin_bits_denominator),
        )['achieved_margin_bits_per_script_by_minimum_timeout']
    )
    next_margin = _deserialize_fraction(
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
            state,
            maximum_current_batch_length + 1,
            int(arrival_probability_numerator),
            int(arrival_probability_denominator),
            int(hold_cost_bits_numerator),
            int(hold_cost_bits_denominator),
            timeout_ticks,
        )['expected_net_wait_value_bits_per_script']
    )

    result.update(
        {
            'maximum_current_batch_length_meeting_target_margin': maximum_current_batch_length,
            'margin_floor_feasible': True,
            'strict_ratio_budget_ps_over_effective_cost': _serialize_fraction(ratio_budget),
            'achieved_margin_bits_per_script_at_maximum_batch_length': _serialize_fraction(achieved_margin),
            'next_margin_bits_per_script_after_maximum_batch_length': _serialize_fraction(next_margin),
            'reason': 'closed_form_margin_floor_inversion',
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_universal_max_current_batch_length_for_capture_target_margin(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_capture_numerator: int,
    target_capture_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    effective_hold_cost_profile = compute_capture_adjusted_effective_hold_cost_for_target_margin(
        int(arrival_probability_numerator),
        int(arrival_probability_denominator),
        int(hold_cost_bits_numerator),
        int(hold_cost_bits_denominator),
        int(target_capture_numerator),
        int(target_capture_denominator),
        int(target_margin_bits_numerator),
        int(target_margin_bits_denominator),
    )

    result: dict[str, Any] = {
        'arrival_probability_per_tick': effective_hold_cost_profile['arrival_probability_per_tick'],
        'hold_cost_bits_per_script_per_tick': effective_hold_cost_profile['hold_cost_bits_per_script_per_tick'],
        'target_capture_fraction_of_asymptotic_positive_wait_value': effective_hold_cost_profile['target_capture_fraction_of_asymptotic_positive_wait_value'],
        'target_margin_bits_per_script': effective_hold_cost_profile['target_margin_bits_per_script'],
        'effective_hold_cost_bits_per_script_per_tick': effective_hold_cost_profile['effective_hold_cost_bits_per_script_per_tick'],
        'effective_margin_tax_bits_per_script_per_tick': effective_hold_cost_profile['effective_margin_tax_bits_per_script_per_tick'],
        'capture_fraction_by_minimum_timeout': effective_hold_cost_profile['capture_fraction_by_minimum_timeout'],
        'minimum_timeout_ticks': effective_hold_cost_profile['minimum_timeout_ticks'],
        'maximum_current_batch_length_meeting_target_margin': None,
        'margin_floor_feasible': False,
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'reason': effective_hold_cost_profile['reason'],
        'margin_floor_condition': 'p * 7 / (n(n+1)) >= hold_cost + p * target_margin / capture_fraction',
    }

    if not effective_hold_cost_profile['margin_floor_finite_policy_exists']:
        return result

    arrival_probability = _deserialize_fraction(effective_hold_cost_profile['arrival_probability_per_tick'])
    effective_hold_cost = _deserialize_fraction(effective_hold_cost_profile['effective_hold_cost_bits_per_script_per_tick'])

    if effective_hold_cost == 0:
        result.update(
            {
                'maximum_current_batch_length_meeting_target_margin': None,
                'margin_floor_feasible': True,
                'reason': 'zero_effective_hold_cost_unbounded',
            }
        )
        return result

    ratio_budget = arrival_probability * 7 / effective_hold_cost
    quota = math.floor(ratio_budget)
    if quota < 2:
        result.update(
            {
                'margin_floor_feasible': False,
                'strict_ratio_budget_ps_over_effective_cost': _serialize_fraction(ratio_budget),
                'reason': 'target_margin_unattainable_for_some_realized_state_even_at_batch_length_one',
            }
        )
        return result

    maximum_current_batch_length = (math.isqrt(1 + 4 * quota) - 1) // 2
    result.update(
        {
            'maximum_current_batch_length_meeting_target_margin': maximum_current_batch_length,
            'margin_floor_feasible': True,
            'strict_ratio_budget_ps_over_effective_cost': _serialize_fraction(ratio_budget),
            'reason': 'closed_form_margin_floor_inversion',
        }
    )
    return result


@lru_cache(maxsize=1)
def build_geometric_arrival_timeout_margin_floor_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 9))
    arrival_probabilities = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    hold_costs = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    capture_targets = (Fraction(1, 2), Fraction(3, 4), Fraction(7, 8), Fraction(15, 16))
    target_margins = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))

    validated_state_batch_parameter_panels = 0
    validated_state_parameter_schedules = 0
    feasible_state_parameter_schedules = 0
    impossible_state_parameter_schedules = 0
    max_batch_histogram: dict[int, int] = {}

    for state in states:
        for arrival_probability in arrival_probabilities:
            for hold_cost in hold_costs:
                for capture_target in capture_targets:
                    for target_margin in target_margins:
                        schedule = compute_max_current_batch_length_for_state_capture_target_margin(
                            state,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            capture_target.numerator,
                            capture_target.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        max_n = schedule['maximum_current_batch_length_meeting_target_margin']
                        feasible = bool(schedule['margin_floor_feasible'])
                        if feasible:
                            feasible_state_parameter_schedules += 1
                            if max_n is not None:
                                max_batch_histogram[int(max_n)] = max_batch_histogram.get(int(max_n), 0) + 1
                        else:
                            impossible_state_parameter_schedules += 1

                        for batch_length in audited_batch_lengths:
                            panel = evaluate_timeout_margin_floor_policy_for_state_batch(
                                state,
                                batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                capture_target.numerator,
                                capture_target.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                            )
                            expected = feasible and (max_n is None or batch_length <= int(max_n))
                            if panel['meets_target_margin'] != expected:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
                                    f'state panel mismatch for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, alpha={capture_target}, margin={target_margin}'
                                )
                            validated_state_batch_parameter_panels += 1

                        if feasible and max_n is not None:
                            at_maximum = evaluate_timeout_margin_floor_policy_for_state_batch(
                                state,
                                int(max_n),
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                capture_target.numerator,
                                capture_target.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                            )
                            after_maximum = evaluate_timeout_margin_floor_policy_for_state_batch(
                                state,
                                int(max_n) + 1,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                capture_target.numerator,
                                capture_target.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                            )
                            if not at_maximum['meets_target_margin']:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
                                    f'state schedule fails at claimed maximum for state {state}'
                                )
                            if after_maximum['meets_target_margin']:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
                                    f'state schedule fails to stop before target floor breaks for state {state}'
                                )
                        validated_state_parameter_schedules += 1

    validated_universal_parameter_schedules = 0
    feasible_universal_parameter_schedules = 0
    impossible_universal_parameter_schedules = 0
    universal_max_batch_histogram: dict[int, int] = {}
    for arrival_probability in arrival_probabilities:
        for hold_cost in hold_costs:
            for capture_target in capture_targets:
                for target_margin in target_margins:
                    schedule = compute_universal_max_current_batch_length_for_capture_target_margin(
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        capture_target.numerator,
                        capture_target.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    max_n = schedule['maximum_current_batch_length_meeting_target_margin']
                    feasible = bool(schedule['margin_floor_feasible'])
                    timeout_ticks = schedule['minimum_timeout_ticks']
                    assert timeout_ticks is not None
                    if feasible:
                        feasible_universal_parameter_schedules += 1
                        if max_n is not None:
                            universal_max_batch_histogram[int(max_n)] = universal_max_batch_histogram.get(int(max_n), 0) + 1
                            guaranteed_margin = min(
                                _deserialize_fraction(
                                    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                        state,
                                        int(max_n),
                                        arrival_probability.numerator,
                                        arrival_probability.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        int(timeout_ticks),
                                    )['expected_net_wait_value_bits_per_script']
                                )
                                for state in states
                            )
                            next_margin = min(
                                _deserialize_fraction(
                                    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                        state,
                                        int(max_n) + 1,
                                        arrival_probability.numerator,
                                        arrival_probability.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        int(timeout_ticks),
                                    )['expected_net_wait_value_bits_per_script']
                                )
                                for state in states
                            )
                            if guaranteed_margin < target_margin:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
                                    f'universal schedule misses target at p={arrival_probability}, c={hold_cost}, alpha={capture_target}, margin={target_margin}'
                                )
                            if next_margin >= target_margin:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
                                    f'universal schedule is not minimal at p={arrival_probability}, c={hold_cost}, alpha={capture_target}, margin={target_margin}'
                                )
                    else:
                        impossible_universal_parameter_schedules += 1
                        first_batch_best_case = min(
                            _deserialize_fraction(
                                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                    state,
                                    1,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    int(timeout_ticks),
                                )['expected_net_wait_value_bits_per_script']
                            )
                            for state in states
                        )
                        if first_batch_best_case >= target_margin:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutMarginFloorLawError(
                                f'universal impossibility claim failed at p={arrival_probability}, c={hold_cost}, alpha={capture_target}, margin={target_margin}'
                            )
                    validated_universal_parameter_schedules += 1

    return {
        'audited_state_count': len(states),
        'validated_state_batch_parameter_panels': validated_state_batch_parameter_panels,
        'validated_state_parameter_schedules': validated_state_parameter_schedules,
        'feasible_state_parameter_schedules': feasible_state_parameter_schedules,
        'impossible_state_parameter_schedules': impossible_state_parameter_schedules,
        'validated_universal_parameter_schedules': validated_universal_parameter_schedules,
        'feasible_universal_parameter_schedules': feasible_universal_parameter_schedules,
        'impossible_universal_parameter_schedules': impossible_universal_parameter_schedules,
        'state_max_batch_histogram': max_batch_histogram,
        'universal_max_batch_histogram': universal_max_batch_histogram,
        'audited_batch_lengths': list(audited_batch_lengths),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in arrival_probabilities],
        'audited_hold_costs': [_serialize_fraction(value) for value in hold_costs],
        'audited_capture_targets': [_serialize_fraction(value) for value in capture_targets],
        'audited_target_margins': [_serialize_fraction(value) for value in target_margins],
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_timeout_margin_floor_validation_summary()
    universal_schedule_examples = [
        {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(1, 10)),
            'target_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(Fraction(15, 16)),
            'target_margin_schedule': [
                {
                    'target_margin_bits_per_script': _serialize_fraction(target_margin),
                    'maximum_current_batch_length_meeting_target_margin': compute_universal_max_current_batch_length_for_capture_target_margin(
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        1,
                        10,
                        15,
                        16,
                        target_margin.numerator,
                        target_margin.denominator,
                    )['maximum_current_batch_length_meeting_target_margin'],
                    'minimum_timeout_ticks': compute_universal_max_current_batch_length_for_capture_target_margin(
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        1,
                        10,
                        15,
                        16,
                        target_margin.numerator,
                        target_margin.denominator,
                    )['minimum_timeout_ticks'],
                }
                for target_margin in (Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
            ],
        }
        for arrival_probability in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    ]

    state_examples = [
        compute_max_current_batch_length_for_state_capture_target_margin((0, 16), 1, 2, 1, 10, 15, 16, 1, 2),
        compute_max_current_batch_length_for_state_capture_target_margin((7, 12), 1, 2, 1, 10, 15, 16, 1, 1),
        compute_max_current_batch_length_for_state_capture_target_margin((8, 8), 3, 4, 1, 10, 7, 8, 1, 1),
        compute_max_current_batch_length_for_state_capture_target_margin((15, 15), 1, 4, 1, 20, 15, 16, 1, 2),
    ]

    policy_boundary_examples = [
        compute_universal_max_current_batch_length_for_capture_target_margin(1, 4, 1, 2, 1, 2, 2, 1),
        compute_universal_max_current_batch_length_for_capture_target_margin(1, 4, 1, 10, 1, 2, 4, 1),
        compute_universal_max_current_batch_length_for_capture_target_margin(1, 2, 1, 10, 15, 16, 1, 1),
        compute_universal_max_current_batch_length_for_capture_target_margin(1, 1, 1, 10, 15, 16, 1, 1),
    ]

    return {
        'focus': 'turn positive geometric-arrival waiting with capture targets into exact realized-margin floor batch caps',
        'headline_findings': {
            'exact_margin_floor_rule': 'a minimum-timeout capture-target policy meets target realized margin m iff p * state_prefix_bits / (n(n+1)) >= c + p * m / beta(alpha, p), where beta(alpha, p) is the actual capture fraction reached by the minimum timeout for target alpha',
            'effective_hold_cost_rule': 'capture-targeted realized margin behaves exactly like an added hold-cost tax p * m / beta(alpha, p)',
            'universal_floor_rule': 'replace state_prefix_bits by 7 to get an all-realized-state guarantee on the current path',
            'timeout_decoupling_result': 'timeout selection stays arrival-only while batch admissibility absorbs capture target and realized-margin target through one scalar effective cost',
        },
        'decision_rules': [
            'Choose target capture alpha and compute the minimum timeout T_min(alpha, p) from the earlier arrival-only timeout law.',
            'Let beta(alpha, p) be the actual capture fraction achieved at that minimum timeout.',
            'For target realized margin m, treat p * m / beta(alpha, p) as an extra per-tick effective hold-cost tax.',
            'Keep a state-specific batch open only while p * state_prefix_bits / (n(n+1)) >= c + p * m / beta(alpha, p).',
            'Use p * 7 / (n(n+1)) >= c + p * m / beta(alpha, p) when one all-state guardrail is enough.',
        ],
        'universal_schedule_examples': universal_schedule_examples,
        'state_examples': state_examples,
        'policy_boundary_examples': policy_boundary_examples,
        'validation_summary': validation_summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_snapshot(), indent=2, sort_keys=True))
