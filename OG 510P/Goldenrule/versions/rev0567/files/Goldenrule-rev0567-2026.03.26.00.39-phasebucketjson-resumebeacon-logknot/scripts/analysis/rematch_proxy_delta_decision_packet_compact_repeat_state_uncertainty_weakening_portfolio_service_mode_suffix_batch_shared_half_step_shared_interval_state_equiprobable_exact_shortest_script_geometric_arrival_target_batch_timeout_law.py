#!/usr/bin/env python3
from __future__ import annotations

import json
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


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
            'fraction denominator must be positive'
        )
    return Fraction(numerator, denominator)


def _deserialize_fraction(payload: dict[str, int | float] | None) -> Fraction | None:
    if payload is None:
        return None
    return Fraction(int(payload['numerator']), int(payload['denominator']))


@lru_cache(maxsize=None)
def _state_prefix_bits(state: tuple[int, int] | list[int]) -> int:
    profile = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        _normalize_state(state),
        1,
        1,
        2,
        1,
        10,
        1,
    )
    return int(profile['state_prefix_bits'])


@lru_cache(maxsize=None)
def compute_minimum_timeout_for_state_batch_target_margin(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
            'current batch length must be positive'
        )

    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = _normalize_fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
            'hold cost must be nonnegative'
        )
    if target_margin < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
            'target margin must be nonnegative'
        )

    state_prefix_bits = _state_prefix_bits(state)
    per_tick_budget = arrival_probability * Fraction(state_prefix_bits, current_batch_length * (current_batch_length + 1))
    sign_invariant_term = per_tick_budget - hold_cost

    result: dict[str, Any] = {
        'state': serialize_feasible_interval_kernel_state(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(sign_invariant_term),
        'closed_form_required_capture_condition': 'required_capture <= 1 iff target_margin <= state_prefix_bits / (n(n+1)) - hold_cost / p',
        'margin_floor_condition': 'capture_fraction * (state_prefix_bits / (n(n+1)) - hold_cost / p) >= target_margin',
    }

    if arrival_probability == 0:
        result.update(
            {
                'required_capture_fraction_of_asymptotic_positive_wait_value': None,
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'zero_arrival_probability_cannot_support_positive_waiting_service_promises',
            }
        )
        return result

    asymptotic_margin = sign_invariant_term / arrival_probability
    result['asymptotic_margin_bits_per_script'] = _serialize_fraction(asymptotic_margin)

    if sign_invariant_term < 0:
        result.update(
            {
                'required_capture_fraction_of_asymptotic_positive_wait_value': None,
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'target_batch_is_already_negative_in_the_asymptotic_limit',
            }
        )
        return result

    if sign_invariant_term == 0:
        if target_margin == 0:
            achieved_margin = _deserialize_fraction(
                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                    state,
                    current_batch_length,
                    arrival_probability.numerator,
                    arrival_probability.denominator,
                    hold_cost.numerator,
                    hold_cost.denominator,
                    1,
                )['expected_net_wait_value_bits_per_script']
            )
            result.update(
                {
                    'required_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(Fraction(0, 1)),
                    'minimum_timeout_ticks': 1,
                    'finite_timeout_exists': True,
                    'asymptotically_feasible': True,
                    'achieved_margin_bits_per_script_by_minimum_timeout': _serialize_fraction(achieved_margin),
                    'reason': 'break_even_asymptote_meets_zero_margin_immediately',
                }
            )
            return result
        result.update(
            {
                'required_capture_fraction_of_asymptotic_positive_wait_value': None,
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'target_margin_exceeds_break_even_asymptotic_value',
            }
        )
        return result

    required_capture = Fraction(0, 1) if target_margin == 0 else arrival_probability * target_margin / sign_invariant_term
    result['required_capture_fraction_of_asymptotic_positive_wait_value'] = _serialize_fraction(required_capture)

    if required_capture > 1:
        result.update(
            {
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'target_margin_exceeds_asymptotic_positive_wait_value',
            }
        )
        return result

    if required_capture == 1:
        if arrival_probability == 1:
            achieved_margin = _deserialize_fraction(
                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                    state,
                    current_batch_length,
                    1,
                    1,
                    hold_cost.numerator,
                    hold_cost.denominator,
                    1,
                )['expected_net_wait_value_bits_per_script']
            )
            result.update(
                {
                    'minimum_timeout_ticks': 1,
                    'finite_timeout_exists': True,
                    'asymptotically_feasible': True,
                    'achieved_margin_bits_per_script_by_minimum_timeout': _serialize_fraction(achieved_margin),
                    'reason': 'certain_arrival_reaches_full_asymptotic_margin_immediately',
                }
            )
            return result
        result.update(
            {
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': True,
                'reason': 'target_margin_equals_asymptotic_positive_wait_value_but_requires_infinite_timeout_when_arrival_probability_is_below_one',
            }
        )
        return result

    if required_capture == 0:
        timeout_policy = {
            'minimum_timeout_ticks': 1,
            'finite_timeout_exists': True,
            'achieved_capture_fraction_by_minimum_timeout': _serialize_fraction(arrival_probability),
            'expected_wait_ticks_by_minimum_timeout': _serialize_fraction(Fraction(1, 1)),
            'timeout_closed_form': '1',
        }
    else:
        timeout_policy = compute_minimum_timeout_for_capture_fraction(
            arrival_probability.numerator,
            arrival_probability.denominator,
            required_capture.numerator,
            required_capture.denominator,
        )
    assert timeout_policy['minimum_timeout_ticks'] is not None
    minimum_timeout_ticks = int(timeout_policy['minimum_timeout_ticks'])
    achieved_margin = _deserialize_fraction(
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
            state,
            current_batch_length,
            arrival_probability.numerator,
            arrival_probability.denominator,
            hold_cost.numerator,
            hold_cost.denominator,
            minimum_timeout_ticks,
        )['expected_net_wait_value_bits_per_script']
    )

    result.update(
        {
            'minimum_timeout_ticks': minimum_timeout_ticks,
            'finite_timeout_exists': True,
            'asymptotically_feasible': True,
            'achieved_capture_fraction_by_minimum_timeout': timeout_policy['achieved_capture_fraction_by_minimum_timeout'],
            'expected_wait_ticks_by_minimum_timeout': timeout_policy['expected_wait_ticks_by_minimum_timeout'],
            'achieved_margin_bits_per_script_by_minimum_timeout': _serialize_fraction(achieved_margin),
            'timeout_closed_form': '1 if required_capture <= 0 or p = 1 else ceil(log(1 - required_capture) / log(1 - p))',
            'reason': 'minimum_timeout_reaching_target_margin_for_fixed_batch_length',
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_universal_minimum_timeout_for_batch_target_margin(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    current_batch_length = int(current_batch_length)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
            'current batch length must be positive'
        )

    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = _normalize_fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    per_tick_budget = arrival_probability * Fraction(7, current_batch_length * (current_batch_length + 1))
    sign_invariant_term = per_tick_budget - hold_cost

    result: dict[str, Any] = {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(sign_invariant_term),
        'closed_form_required_capture_condition': 'required_capture <= 1 iff target_margin <= 7 / (n(n+1)) - hold_cost / p',
        'margin_floor_condition': 'capture_fraction * (7 / (n(n+1)) - hold_cost / p) >= target_margin',
    }

    if arrival_probability == 0:
        result.update(
            {
                'required_capture_fraction_of_asymptotic_positive_wait_value': None,
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'zero_arrival_probability_cannot_support_positive_waiting_service_promises',
            }
        )
        return result

    asymptotic_margin = sign_invariant_term / arrival_probability
    result['asymptotic_margin_bits_per_script'] = _serialize_fraction(asymptotic_margin)

    if sign_invariant_term < 0:
        result.update(
            {
                'required_capture_fraction_of_asymptotic_positive_wait_value': None,
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'target_batch_is_already_negative_in_the_universal_asymptotic_limit',
            }
        )
        return result

    if sign_invariant_term == 0:
        if target_margin == 0:
            result.update(
                {
                    'required_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(Fraction(0, 1)),
                    'minimum_timeout_ticks': 1,
                    'finite_timeout_exists': True,
                    'asymptotically_feasible': True,
                    'reason': 'universal_break_even_asymptote_meets_zero_margin_immediately',
                }
            )
            return result
        result.update(
            {
                'required_capture_fraction_of_asymptotic_positive_wait_value': None,
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'target_margin_exceeds_universal_break_even_asymptotic_value',
            }
        )
        return result

    required_capture = Fraction(0, 1) if target_margin == 0 else arrival_probability * target_margin / sign_invariant_term
    result['required_capture_fraction_of_asymptotic_positive_wait_value'] = _serialize_fraction(required_capture)

    if required_capture > 1:
        result.update(
            {
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': False,
                'reason': 'target_margin_exceeds_universal_asymptotic_positive_wait_value',
            }
        )
        return result

    if required_capture == 1:
        if arrival_probability == 1:
            result.update(
                {
                    'minimum_timeout_ticks': 1,
                    'finite_timeout_exists': True,
                    'asymptotically_feasible': True,
                    'reason': 'certain_arrival_reaches_full_universal_asymptotic_margin_immediately',
                }
            )
            return result
        result.update(
            {
                'minimum_timeout_ticks': None,
                'finite_timeout_exists': False,
                'asymptotically_feasible': True,
                'reason': 'target_margin_equals_universal_asymptotic_positive_wait_value_but_requires_infinite_timeout_when_arrival_probability_is_below_one',
            }
        )
        return result

    if required_capture == 0:
        result.update(
            {
                'minimum_timeout_ticks': 1,
                'finite_timeout_exists': True,
                'asymptotically_feasible': True,
                'achieved_capture_fraction_by_minimum_timeout': _serialize_fraction(arrival_probability),
                'expected_wait_ticks_by_minimum_timeout': _serialize_fraction(Fraction(1, 1)),
                'timeout_closed_form': '1',
                'reason': 'one_tick_timeout_already_meets_zero_margin_floor',
            }
        )
        return result

    timeout_policy = compute_minimum_timeout_for_capture_fraction(
        arrival_probability.numerator,
        arrival_probability.denominator,
        required_capture.numerator,
        required_capture.denominator,
    )
    assert timeout_policy['minimum_timeout_ticks'] is not None
    result.update(
        {
            'minimum_timeout_ticks': int(timeout_policy['minimum_timeout_ticks']),
            'finite_timeout_exists': True,
            'asymptotically_feasible': True,
            'achieved_capture_fraction_by_minimum_timeout': timeout_policy['achieved_capture_fraction_by_minimum_timeout'],
            'expected_wait_ticks_by_minimum_timeout': timeout_policy['expected_wait_ticks_by_minimum_timeout'],
            'timeout_closed_form': '1 if required_capture <= 0 or p = 1 else ceil(log(1 - required_capture) / log(1 - p))',
            'reason': 'minimum_timeout_reaching_universal_target_margin_for_fixed_batch_length',
        }
    )
    return result


@lru_cache(maxsize=1)
def build_geometric_arrival_target_batch_timeout_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 9))
    arrival_probabilities = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    hold_costs = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    target_margins = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))

    validated_state_batch_parameter_panels = 0
    finite_state_timeouts = 0
    asymptotic_only_state_schedules = 0
    impossible_state_schedules = 0
    state_reason_histogram: dict[str, int] = {}
    finite_timeout_histogram: dict[int, int] = {}

    for state in states:
        for batch_length in audited_batch_lengths:
            for arrival_probability in arrival_probabilities:
                for hold_cost in hold_costs:
                    for target_margin in target_margins:
                        schedule = compute_minimum_timeout_for_state_batch_target_margin(
                            state,
                            batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        reason = str(schedule['reason'])
                        state_reason_histogram[reason] = state_reason_histogram.get(reason, 0) + 1
                        minimum_timeout_ticks = schedule['minimum_timeout_ticks']
                        finite_timeout_exists = bool(schedule['finite_timeout_exists'])
                        asymptotically_feasible = bool(schedule['asymptotically_feasible'])

                        if finite_timeout_exists:
                            finite_state_timeouts += 1
                            assert minimum_timeout_ticks is not None
                            finite_timeout_histogram[int(minimum_timeout_ticks)] = finite_timeout_histogram.get(int(minimum_timeout_ticks), 0) + 1
                            achieved_margin = _deserialize_fraction(
                                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                    state,
                                    batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    int(minimum_timeout_ticks),
                                )['expected_net_wait_value_bits_per_script']
                            )
                            if achieved_margin < target_margin:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                    f'state timeout misses target for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target_margin}'
                                )
                            if int(minimum_timeout_ticks) > 1:
                                previous_margin = _deserialize_fraction(
                                    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                        state,
                                        batch_length,
                                        arrival_probability.numerator,
                                        arrival_probability.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        int(minimum_timeout_ticks) - 1,
                                    )['expected_net_wait_value_bits_per_script']
                                )
                                if previous_margin >= target_margin:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                        f'state timeout is not minimal for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target_margin}'
                                    )
                        elif asymptotically_feasible:
                            asymptotic_only_state_schedules += 1
                            asymptotic_margin = _deserialize_fraction(schedule['asymptotic_margin_bits_per_script'])
                            if asymptotic_margin != target_margin:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                    f'asymptotic-only state case should sit exactly on the asymptotic boundary for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target_margin}'
                                )
                            long_margin = _deserialize_fraction(
                                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                    state,
                                    batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    64,
                                )['expected_net_wait_value_bits_per_script']
                            )
                            if long_margin >= target_margin:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                    f'asymptotic-only state case unexpectedly met target at finite timeout for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target_margin}'
                                )
                        else:
                            impossible_state_schedules += 1
                            asymptotic_margin_payload = schedule.get('asymptotic_margin_bits_per_script')
                            if asymptotic_margin_payload is not None:
                                asymptotic_margin = _deserialize_fraction(asymptotic_margin_payload)
                                if asymptotic_margin >= target_margin:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                        f'impossible state case still has enough asymptotic margin for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target_margin}'
                                    )
                        validated_state_batch_parameter_panels += 1

    validated_universal_parameter_schedules = 0
    finite_universal_timeouts = 0
    asymptotic_only_universal_schedules = 0
    impossible_universal_schedules = 0
    universal_reason_histogram: dict[str, int] = {}

    for batch_length in audited_batch_lengths:
        for arrival_probability in arrival_probabilities:
            for hold_cost in hold_costs:
                for target_margin in target_margins:
                    schedule = compute_universal_minimum_timeout_for_batch_target_margin(
                        batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    reason = str(schedule['reason'])
                    universal_reason_histogram[reason] = universal_reason_histogram.get(reason, 0) + 1
                    minimum_timeout_ticks = schedule['minimum_timeout_ticks']
                    finite_timeout_exists = bool(schedule['finite_timeout_exists'])
                    asymptotically_feasible = bool(schedule['asymptotically_feasible'])
                    target = target_margin

                    if finite_timeout_exists:
                        finite_universal_timeouts += 1
                        assert minimum_timeout_ticks is not None
                        guaranteed_margin = min(
                            _deserialize_fraction(
                                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                    state,
                                    batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    int(minimum_timeout_ticks),
                                )['expected_net_wait_value_bits_per_script']
                            )
                            for state in states
                        )
                        if guaranteed_margin < target:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                f'universal timeout misses target for n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target}'
                            )
                        if int(minimum_timeout_ticks) > 1:
                            previous_guaranteed_margin = min(
                                _deserialize_fraction(
                                    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                        state,
                                        batch_length,
                                        arrival_probability.numerator,
                                        arrival_probability.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        int(minimum_timeout_ticks) - 1,
                                    )['expected_net_wait_value_bits_per_script']
                                )
                                for state in states
                            )
                            if previous_guaranteed_margin >= target:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                    f'universal timeout is not minimal for n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target}'
                                )
                    elif asymptotically_feasible:
                        asymptotic_only_universal_schedules += 1
                        asymptotic_margin = _deserialize_fraction(schedule['asymptotic_margin_bits_per_script'])
                        if asymptotic_margin != target:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                f'universal asymptotic-only case should sit exactly on the asymptotic boundary for n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target}'
                            )
                    else:
                        impossible_universal_schedules += 1
                        asymptotic_margin_payload = schedule.get('asymptotic_margin_bits_per_script')
                        if asymptotic_margin_payload is not None:
                            asymptotic_margin = _deserialize_fraction(asymptotic_margin_payload)
                            if asymptotic_margin >= target:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTargetBatchTimeoutLawError(
                                    f'universal impossible case still has enough asymptotic margin for n={batch_length}, p={arrival_probability}, c={hold_cost}, margin={target}'
                                )
                    validated_universal_parameter_schedules += 1

    return {
        'audited_state_count': len(states),
        'validated_state_batch_parameter_panels': validated_state_batch_parameter_panels,
        'finite_state_timeouts': finite_state_timeouts,
        'asymptotic_only_state_schedules': asymptotic_only_state_schedules,
        'impossible_state_schedules': impossible_state_schedules,
        'state_reason_histogram': state_reason_histogram,
        'finite_timeout_histogram': finite_timeout_histogram,
        'validated_universal_parameter_schedules': validated_universal_parameter_schedules,
        'finite_universal_timeouts': finite_universal_timeouts,
        'asymptotic_only_universal_schedules': asymptotic_only_universal_schedules,
        'impossible_universal_schedules': impossible_universal_schedules,
        'universal_reason_histogram': universal_reason_histogram,
        'audited_batch_lengths': list(audited_batch_lengths),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in arrival_probabilities],
        'audited_hold_costs': [_serialize_fraction(value) for value in hold_costs],
        'audited_target_margins': [_serialize_fraction(value) for value in target_margins],
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_target_batch_timeout_validation_summary()

    universal_timeout_examples = [
        {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(1, 10)),
            'target_margin_schedule': [
                {
                    'current_batch_length': batch_length,
                    'target_margin_bits_per_script': _serialize_fraction(Fraction(1, 2)),
                    'minimum_timeout_ticks': compute_universal_minimum_timeout_for_batch_target_margin(
                        batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        1,
                        10,
                        1,
                        2,
                    )['minimum_timeout_ticks'],
                    'required_capture_fraction_of_asymptotic_positive_wait_value': compute_universal_minimum_timeout_for_batch_target_margin(
                        batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        1,
                        10,
                        1,
                        2,
                    )['required_capture_fraction_of_asymptotic_positive_wait_value'],
                    'asymptotically_feasible': compute_universal_minimum_timeout_for_batch_target_margin(
                        batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        1,
                        10,
                        1,
                        2,
                    )['asymptotically_feasible'],
                }
                for batch_length in (1, 2, 3, 4)
            ],
        }
        for arrival_probability in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    ]

    state_examples = [
        compute_minimum_timeout_for_state_batch_target_margin((0, 16), 2, 1, 2, 1, 10, 1, 2),
        compute_minimum_timeout_for_state_batch_target_margin((7, 12), 2, 1, 2, 1, 10, 1, 1),
        compute_minimum_timeout_for_state_batch_target_margin((8, 8), 2, 3, 4, 1, 10, 1, 1),
        compute_minimum_timeout_for_state_batch_target_margin((15, 15), 4, 1, 4, 1, 20, 1, 2),
    ]

    boundary_examples = [
        compute_universal_minimum_timeout_for_batch_target_margin(2, 1, 4, 1, 10, 1, 2),
        compute_universal_minimum_timeout_for_batch_target_margin(3, 1, 2, 1, 10, 1, 2),
        compute_universal_minimum_timeout_for_batch_target_margin(4, 1, 2, 1, 20, 1, 4),
        compute_universal_minimum_timeout_for_batch_target_margin(4, 1, 1, 1, 10, 1, 2),
    ]

    return {
        'focus': 'invert realized-margin batch promises into exact required capture fractions and minimum timeouts',
        'headline_findings': {
            'required_capture_rule': 'a fixed batch length n meets target realized margin m iff the timeout captures at least required_capture = p * m / (p * state_prefix_bits / (n(n+1)) - c) of asymptotic positive wait value whenever the denominator is positive',
            'minimum_timeout_rule': 'when 0 < required_capture < 1, the minimum timeout is exactly ceil(log(1 - required_capture) / log(1 - p)) for p < 1 and 1 for p = 1',
            'asymptotic_boundary_rule': 'required_capture = 1 marks the asymptotic frontier: finite timeout is impossible unless arrival is certain',
            'universal_timeout_rule': 'replace state_prefix_bits by 7 to get an all-realized-state minimum-timeout schedule for any fixed batch length',
        },
        'decision_rules': [
            'Choose the batch length n you want to keep open and the realized margin floor m you must hit.',
            'Compute the denominator p * state_prefix_bits / (n(n+1)) - c, or p * 7 / (n(n+1)) - c for an all-state guardrail.',
            'If that denominator is negative, the target batch is impossible even asymptotically; if it is zero, only zero realized margin is attainable.',
            'Otherwise compute required_capture = p * m / (p * state_prefix_bits / (n(n+1)) - c).',
            'If required_capture > 1, the target margin exceeds the asymptotic upside; if required_capture = 1, only certainty of arrival makes finite timeout possible.',
            'If required_capture < 1, use the arrival-only timeout law with required_capture as the target capture fraction.',
        ],
        'universal_timeout_examples': universal_timeout_examples,
        'state_examples': state_examples,
        'boundary_examples': boundary_examples,
        'validation_summary': validation_summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_snapshot(), indent=2, sort_keys=True))
