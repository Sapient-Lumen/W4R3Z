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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law import (
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
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
def _capture_fraction_by_timeout(arrival_probability: Fraction, timeout_ticks: int) -> Fraction:
    timeout_ticks = int(timeout_ticks)
    if timeout_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'timeout ticks must be positive'
        )
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'arrival probability must lie in [0, 1]'
        )
    return Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** timeout_ticks


@lru_cache(maxsize=None)
def _maximum_batch_length_from_quadratic_budget(batch_budget: Fraction) -> int:
    if batch_budget < 2:
        return 0

    low = 0
    high = 1
    while Fraction(high * (high + 1), 1) <= batch_budget:
        low = high
        high *= 2

    while low + 1 < high:
        mid = (low + high) // 2
        if Fraction(mid * (mid + 1), 1) <= batch_budget:
            low = mid
        else:
            high = mid
    return low


@lru_cache(maxsize=None)
def compute_maximum_batch_length_for_state_timeout_target_margin(
    state: tuple[int, int] | list[int],
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    timeout_ticks: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = _normalize_fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    timeout_ticks = int(timeout_ticks)

    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'hold cost must be nonnegative'
        )
    if target_margin < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'target margin must be nonnegative'
        )
    if timeout_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'timeout ticks must be positive'
        )

    state_prefix_bits = _state_prefix_bits(state)
    capture_fraction = _capture_fraction_by_timeout(arrival_probability, timeout_ticks)

    result: dict[str, Any] = {
        'state': serialize_feasible_interval_kernel_state(state),
        'state_prefix_bits': state_prefix_bits,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'timeout_ticks': timeout_ticks,
        'capture_fraction_by_timeout': _serialize_fraction(capture_fraction),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'margin_floor_condition': 'capture_fraction * (state_prefix_bits / (n(n+1)) - hold_cost / p) >= target_margin',
        'batch_cap_condition': 'n(n+1) <= p * state_prefix_bits / (hold_cost + p * target_margin / capture_fraction)',
        'maximum_batch_length_closed_form': 'floor(max {n >= 0 : n(n+1) <= p * state_prefix_bits / (hold_cost + p * target_margin / capture_fraction)})',
    }

    if capture_fraction == 0:
        if hold_cost == 0 and target_margin == 0:
            result.update(
                {
                    'effective_hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(0, 1)),
                    'quadratic_budget_for_n_times_n_plus_1': None,
                    'maximum_admissible_batch_length': None,
                    'unbounded_batch_cap': True,
                    'finite_positive_batch_exists': True,
                    'reason': 'zero_capture_with_zero_cost_and_zero_margin_leaves_every_batch_at_break_even',
                }
            )
            return result
        result.update(
            {
                'effective_hold_cost_bits_per_script_per_tick': None,
                'quadratic_budget_for_n_times_n_plus_1': None,
                'maximum_admissible_batch_length': 0,
                'unbounded_batch_cap': False,
                'finite_positive_batch_exists': False,
                'reason': 'zero_capture_timeout_cannot_support_positive_batch_promises',
            }
        )
        return result

    effective_hold_cost = hold_cost + arrival_probability * target_margin / capture_fraction
    result['effective_hold_cost_bits_per_script_per_tick'] = _serialize_fraction(effective_hold_cost)

    if effective_hold_cost == 0:
        result.update(
            {
                'quadratic_budget_for_n_times_n_plus_1': None,
                'maximum_admissible_batch_length': None,
                'unbounded_batch_cap': True,
                'finite_positive_batch_exists': True,
                'reason': 'zero_effective_hold_cost_leaves_every_positive_batch_admissible',
            }
        )
        return result

    batch_budget = arrival_probability * state_prefix_bits / effective_hold_cost
    maximum_batch_length = _maximum_batch_length_from_quadratic_budget(batch_budget)
    result.update(
        {
            'quadratic_budget_for_n_times_n_plus_1': _serialize_fraction(batch_budget),
            'maximum_admissible_batch_length': maximum_batch_length,
            'unbounded_batch_cap': False,
            'finite_positive_batch_exists': maximum_batch_length >= 1,
            'reason': 'fixed_timeout_margin_floor_turns_into_a_direct_batch_cap',
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_universal_maximum_batch_length_for_timeout_target_margin(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    timeout_ticks: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = _normalize_fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    timeout_ticks = int(timeout_ticks)

    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'hold cost must be nonnegative'
        )
    if target_margin < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'target margin must be nonnegative'
        )
    if timeout_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
            'timeout ticks must be positive'
        )

    capture_fraction = _capture_fraction_by_timeout(arrival_probability, timeout_ticks)
    result: dict[str, Any] = {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'timeout_ticks': timeout_ticks,
        'capture_fraction_by_timeout': _serialize_fraction(capture_fraction),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'margin_floor_condition': 'capture_fraction * (7 / (n(n+1)) - hold_cost / p) >= target_margin',
        'batch_cap_condition': 'n(n+1) <= 7p / (hold_cost + p * target_margin / capture_fraction)',
        'maximum_batch_length_closed_form': 'floor(max {n >= 0 : n(n+1) <= 7p / (hold_cost + p * target_margin / capture_fraction)})',
    }

    if capture_fraction == 0:
        if hold_cost == 0 and target_margin == 0:
            result.update(
                {
                    'effective_hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(0, 1)),
                    'quadratic_budget_for_n_times_n_plus_1': None,
                    'maximum_admissible_batch_length': None,
                    'unbounded_batch_cap': True,
                    'finite_positive_batch_exists': True,
                    'reason': 'zero_capture_with_zero_cost_and_zero_margin_leaves_every_universal_batch_at_break_even',
                }
            )
            return result
        result.update(
            {
                'effective_hold_cost_bits_per_script_per_tick': None,
                'quadratic_budget_for_n_times_n_plus_1': None,
                'maximum_admissible_batch_length': 0,
                'unbounded_batch_cap': False,
                'finite_positive_batch_exists': False,
                'reason': 'zero_capture_timeout_cannot_support_positive_universal_batch_promises',
            }
        )
        return result

    effective_hold_cost = hold_cost + arrival_probability * target_margin / capture_fraction
    result['effective_hold_cost_bits_per_script_per_tick'] = _serialize_fraction(effective_hold_cost)

    if effective_hold_cost == 0:
        result.update(
            {
                'quadratic_budget_for_n_times_n_plus_1': None,
                'maximum_admissible_batch_length': None,
                'unbounded_batch_cap': True,
                'finite_positive_batch_exists': True,
                'reason': 'zero_effective_hold_cost_leaves_every_universal_batch_admissible',
            }
        )
        return result

    batch_budget = arrival_probability * 7 / effective_hold_cost
    maximum_batch_length = _maximum_batch_length_from_quadratic_budget(batch_budget)
    result.update(
        {
            'effective_hold_cost_bits_per_script_per_tick': _serialize_fraction(effective_hold_cost),
            'quadratic_budget_for_n_times_n_plus_1': _serialize_fraction(batch_budget),
            'maximum_admissible_batch_length': maximum_batch_length,
            'unbounded_batch_cap': False,
            'finite_positive_batch_exists': maximum_batch_length >= 1,
            'reason': 'fixed_timeout_margin_floor_turns_into_a_direct_universal_batch_cap',
        }
    )
    return result


@lru_cache(maxsize=1)
def build_geometric_arrival_timeout_batch_cap_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 13))
    arrival_probabilities = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    hold_costs = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    timeouts = (1, 2, 3, 4, 5, 6)
    target_margins = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))

    validated_state_batch_parameter_panels = 0
    validated_state_schedule_inversions = 0
    feasible_state_schedules = 0
    impossible_state_schedules = 0
    state_reason_histogram: dict[str, int] = {}
    state_max_batch_histogram: dict[int, int] = {}

    for state in states:
        for arrival_probability in arrival_probabilities:
            for hold_cost in hold_costs:
                for timeout_ticks in timeouts:
                    for target_margin in target_margins:
                        schedule = compute_maximum_batch_length_for_state_timeout_target_margin(
                            state,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            timeout_ticks,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        reason = str(schedule['reason'])
                        state_reason_histogram[reason] = state_reason_histogram.get(reason, 0) + 1
                        max_batch = schedule['maximum_admissible_batch_length']
                        unbounded = bool(schedule['unbounded_batch_cap'])

                        if unbounded:
                            feasible_state_schedules += 1
                        elif int(max_batch) >= 1:
                            feasible_state_schedules += 1
                            state_max_batch_histogram[int(max_batch)] = state_max_batch_histogram.get(int(max_batch), 0) + 1
                        else:
                            impossible_state_schedules += 1

                        for batch_length in audited_batch_lengths:
                            realized_margin = _deserialize_fraction(
                                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                    state,
                                    batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    timeout_ticks,
                                )['expected_net_wait_value_bits_per_script']
                            )
                            meets_target = realized_margin >= target_margin
                            closed_form_meets_target = True if unbounded else batch_length <= int(max_batch)
                            if meets_target != closed_form_meets_target:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                                    f'state batch-cap mismatch for state {state}, p={arrival_probability}, c={hold_cost}, T={timeout_ticks}, m={target_margin}, n={batch_length}'
                                )
                            validated_state_batch_parameter_panels += 1

                        if not unbounded:
                            frontier_batch = int(max_batch)
                            if frontier_batch >= 1:
                                frontier_margin = _deserialize_fraction(
                                    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                        state,
                                        frontier_batch,
                                        arrival_probability.numerator,
                                        arrival_probability.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        timeout_ticks,
                                    )['expected_net_wait_value_bits_per_script']
                                )
                                if frontier_margin < target_margin:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                                        f'closed-form frontier undershoots target for state {state}, p={arrival_probability}, c={hold_cost}, T={timeout_ticks}, m={target_margin}'
                                    )
                            next_margin = _deserialize_fraction(
                                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                    state,
                                    frontier_batch + 1,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    timeout_ticks,
                                )['expected_net_wait_value_bits_per_script']
                            )
                            if next_margin >= target_margin:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                                    f'next batch unexpectedly still meets target for state {state}, p={arrival_probability}, c={hold_cost}, T={timeout_ticks}, m={target_margin}'
                                )
                        validated_state_schedule_inversions += 1

    validated_state_timeout_ladders = 0
    state_timeout_ladders_with_growth = 0
    for state in states:
        for arrival_probability in arrival_probabilities:
            for hold_cost in hold_costs:
                for target_margin in target_margins:
                    ladder = [
                        compute_maximum_batch_length_for_state_timeout_target_margin(
                            state,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            timeout_ticks,
                            target_margin.numerator,
                            target_margin.denominator,
                        )['maximum_admissible_batch_length']
                        for timeout_ticks in timeouts
                    ]
                    if any(value is None for value in ladder):
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                            'unbounded ladders are outside the audited positive-cost grid'
                        )
                    ladder_ints = [int(value) for value in ladder]
                    if ladder_ints != sorted(ladder_ints):
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                            f'timeout ladder is not monotone for state {state}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                        )
                    if len(set(ladder_ints)) > 1:
                        state_timeout_ladders_with_growth += 1
                    validated_state_timeout_ladders += 1

    validated_universal_parameter_schedules = 0
    validated_universal_schedule_inversions = 0
    feasible_universal_schedules = 0
    impossible_universal_schedules = 0
    universal_reason_histogram: dict[str, int] = {}
    universal_max_batch_histogram: dict[int, int] = {}

    for arrival_probability in arrival_probabilities:
        for hold_cost in hold_costs:
            for timeout_ticks in timeouts:
                for target_margin in target_margins:
                    schedule = compute_universal_maximum_batch_length_for_timeout_target_margin(
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        timeout_ticks,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    reason = str(schedule['reason'])
                    universal_reason_histogram[reason] = universal_reason_histogram.get(reason, 0) + 1
                    max_batch = schedule['maximum_admissible_batch_length']
                    unbounded = bool(schedule['unbounded_batch_cap'])
                    if unbounded:
                        feasible_universal_schedules += 1
                    elif int(max_batch) >= 1:
                        feasible_universal_schedules += 1
                        universal_max_batch_histogram[int(max_batch)] = universal_max_batch_histogram.get(int(max_batch), 0) + 1
                    else:
                        impossible_universal_schedules += 1

                    for batch_length in audited_batch_lengths:
                        realized_margin = _deserialize_fraction(
                            evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                (0, 16),
                                batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                timeout_ticks,
                            )['expected_net_wait_value_bits_per_script']
                        )
                        # Replace state-specific prefix with exact seven-bit lower envelope for the universal guardrail.
                        universal_realized_margin = _capture_fraction_by_timeout(arrival_probability, timeout_ticks) * (
                            Fraction(7, batch_length * (batch_length + 1)) - hold_cost / arrival_probability
                        ) if arrival_probability > 0 else realized_margin
                        meets_target = universal_realized_margin >= target_margin
                        closed_form_meets_target = True if unbounded else batch_length <= int(max_batch)
                        if meets_target != closed_form_meets_target:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                                f'universal batch-cap mismatch for p={arrival_probability}, c={hold_cost}, T={timeout_ticks}, m={target_margin}, n={batch_length}'
                            )
                        validated_universal_parameter_schedules += 1

                    if not unbounded:
                        frontier_batch = int(max_batch)
                        if frontier_batch >= 1:
                            frontier_margin = _capture_fraction_by_timeout(arrival_probability, timeout_ticks) * (
                                Fraction(7, frontier_batch * (frontier_batch + 1)) - hold_cost / arrival_probability
                            ) if arrival_probability > 0 else Fraction(0, 1)
                            if frontier_margin < target_margin:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                                    f'universal closed-form frontier undershoots target for p={arrival_probability}, c={hold_cost}, T={timeout_ticks}, m={target_margin}'
                                )
                        next_margin = _capture_fraction_by_timeout(arrival_probability, timeout_ticks) * (
                            Fraction(7, (frontier_batch + 1) * (frontier_batch + 2)) - hold_cost / arrival_probability
                        ) if arrival_probability > 0 else Fraction(0, 1)
                        if next_margin >= target_margin:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                                f'universal next batch unexpectedly still meets target for p={arrival_probability}, c={hold_cost}, T={timeout_ticks}, m={target_margin}'
                            )
                    validated_universal_schedule_inversions += 1

    validated_universal_timeout_ladders = 0
    universal_timeout_ladders_with_growth = 0
    for arrival_probability in arrival_probabilities:
        for hold_cost in hold_costs:
            for target_margin in target_margins:
                ladder = [
                    compute_universal_maximum_batch_length_for_timeout_target_margin(
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        timeout_ticks,
                        target_margin.numerator,
                        target_margin.denominator,
                    )['maximum_admissible_batch_length']
                    for timeout_ticks in timeouts
                ]
                if any(value is None for value in ladder):
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                        'unbounded universal ladders are outside the audited positive-cost grid'
                    )
                ladder_ints = [int(value) for value in ladder]
                if ladder_ints != sorted(ladder_ints):
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutBatchCapLawError(
                        f'universal timeout ladder is not monotone for p={arrival_probability}, c={hold_cost}, m={target_margin}'
                    )
                if len(set(ladder_ints)) > 1:
                    universal_timeout_ladders_with_growth += 1
                validated_universal_timeout_ladders += 1

    return {
        'audited_state_count': len(states),
        'audited_batch_lengths': list(audited_batch_lengths),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in arrival_probabilities],
        'audited_hold_costs': [_serialize_fraction(value) for value in hold_costs],
        'audited_timeouts': list(timeouts),
        'audited_target_margins': [_serialize_fraction(value) for value in target_margins],
        'validated_state_batch_parameter_panels': validated_state_batch_parameter_panels,
        'validated_state_schedule_inversions': validated_state_schedule_inversions,
        'feasible_state_schedules': feasible_state_schedules,
        'impossible_state_schedules': impossible_state_schedules,
        'state_reason_histogram': dict(sorted(state_reason_histogram.items())),
        'state_max_batch_histogram': dict(sorted(state_max_batch_histogram.items())),
        'validated_state_timeout_ladders': validated_state_timeout_ladders,
        'state_timeout_ladders_with_growth': state_timeout_ladders_with_growth,
        'validated_universal_parameter_schedules': validated_universal_parameter_schedules,
        'validated_universal_schedule_inversions': validated_universal_schedule_inversions,
        'feasible_universal_schedules': feasible_universal_schedules,
        'impossible_universal_schedules': impossible_universal_schedules,
        'universal_reason_histogram': dict(sorted(universal_reason_histogram.items())),
        'universal_max_batch_histogram': dict(sorted(universal_max_batch_histogram.items())),
        'validated_universal_timeout_ladders': validated_universal_timeout_ladders,
        'universal_timeout_ladders_with_growth': universal_timeout_ladders_with_growth,
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_timeout_batch_cap_validation_summary()

    universal_examples = [
        compute_universal_maximum_batch_length_for_timeout_target_margin(1, 4, 1, 10, 1, 1, 4),
        compute_universal_maximum_batch_length_for_timeout_target_margin(1, 2, 1, 10, 2, 1, 2),
        compute_universal_maximum_batch_length_for_timeout_target_margin(3, 4, 1, 10, 4, 1, 1),
        compute_universal_maximum_batch_length_for_timeout_target_margin(1, 1, 1, 4, 1, 1, 2),
    ]

    state_examples = [
        compute_maximum_batch_length_for_state_timeout_target_margin((0, 16), 1, 2, 1, 10, 2, 1, 2),
        compute_maximum_batch_length_for_state_timeout_target_margin((7, 12), 1, 2, 1, 10, 4, 1, 1),
        compute_maximum_batch_length_for_state_timeout_target_margin((8, 8), 3, 4, 1, 20, 3, 1, 2),
        compute_maximum_batch_length_for_state_timeout_target_margin((15, 15), 1, 1, 1, 20, 6, 1, 2),
    ]

    timeout_ladder_examples = [
        {
            'state': serialize_feasible_interval_kernel_state((0, 16)),
            'arrival_probability_per_tick': _serialize_fraction(Fraction(1, 2)),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(1, 10)),
            'target_margin_bits_per_script': _serialize_fraction(Fraction(1, 2)),
            'timeout_to_maximum_batch_length': [
                {
                    'timeout_ticks': timeout_ticks,
                    'maximum_admissible_batch_length': compute_maximum_batch_length_for_state_timeout_target_margin(
                        (0, 16),
                        1,
                        2,
                        1,
                        10,
                        timeout_ticks,
                        1,
                        2,
                    )['maximum_admissible_batch_length'],
                }
                for timeout_ticks in (1, 2, 3, 4, 5, 6)
            ],
        },
        {
            'guarantee_scope': 'all_realized_states',
            'arrival_probability_per_tick': _serialize_fraction(Fraction(1, 2)),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(1, 10)),
            'target_margin_bits_per_script': _serialize_fraction(Fraction(1, 2)),
            'timeout_to_maximum_batch_length': [
                {
                    'timeout_ticks': timeout_ticks,
                    'maximum_admissible_batch_length': compute_universal_maximum_batch_length_for_timeout_target_margin(
                        1,
                        2,
                        1,
                        10,
                        timeout_ticks,
                        1,
                        2,
                    )['maximum_admissible_batch_length'],
                }
                for timeout_ticks in (1, 2, 3, 4, 5, 6)
            ],
        },
    ]

    boundary_examples = [
        compute_universal_maximum_batch_length_for_timeout_target_margin(1, 4, 1, 10, 1, 1, 2),
        compute_universal_maximum_batch_length_for_timeout_target_margin(1, 4, 1, 10, 6, 1, 2),
        compute_maximum_batch_length_for_state_timeout_target_margin((0, 16), 1, 4, 1, 2, 1, 1, 2),
        compute_maximum_batch_length_for_state_timeout_target_margin((0, 16), 1, 1, 1, 20, 6, 2, 1),
    ]

    return {
        'focus': 'turn a fixed geometric-arrival timeout and realized margin floor into a direct admissible batch-length cap',
        'headline_findings': {
            'catalog_state_count': validation_summary['audited_state_count'],
            'validated_state_batch_parameter_panels': validation_summary['validated_state_batch_parameter_panels'],
            'validated_state_schedule_inversions': validation_summary['validated_state_schedule_inversions'],
            'feasible_state_schedules': validation_summary['feasible_state_schedules'],
            'impossible_state_schedules': validation_summary['impossible_state_schedules'],
            'validated_universal_parameter_schedules': validation_summary['validated_universal_parameter_schedules'],
            'one_tick_simplification': 'for timeout T = 1, capture_fraction = p, so the realized-margin tax becomes exactly target_margin and the batch cap denominator collapses to hold_cost + target_margin',
            'fixed_timeout_cap_rule': 'maximum admissible batch length is the largest n with n(n+1) <= p * state_prefix_bits / (hold_cost + p * target_margin / (1 - (1 - p)^T))',
        },
        'decision_rules': [
            'With a fixed finite timeout T, realized expected net wait value is exactly (1 - (1 - p)^T) * (state_prefix_bits / (n(n+1)) - hold_cost / p) whenever p > 0.',
            'Therefore a realized margin floor m is feasible exactly when n(n+1) <= p * state_prefix_bits / (hold_cost + p * m / (1 - (1 - p)^T)).',
            'So online scheduling can skip capture-target indirection: plug in the timeout you will actually run and recover the largest admissible current batch length directly.',
            'The all-state guardrail is the same inequality with state_prefix_bits replaced by the exact seven-bit lower envelope on the current path.',
            'Longer timeouts can only weakly increase the admissible batch cap because capture_fraction = 1 - (1 - p)^T is monotone in T and the effective realized-margin tax shrinks accordingly.',
            'At T = 1 the realized-margin tax is exactly m itself, independent of arrival hazard, because one tick captures exactly p of the asymptotic positive wait value.',
        ],
        'universal_examples': universal_examples,
        'state_examples': state_examples,
        'timeout_ladder_examples': timeout_ladder_examples,
        'boundary_examples': boundary_examples,
        'validation_summary': validation_summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot_20260316.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law_snapshot_20260316.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law_snapshot_20260316.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law.py',
    }


def main() -> None:
    json.dump(
        build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_snapshot(),
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
