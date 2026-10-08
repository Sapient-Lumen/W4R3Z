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
    build_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_profile,
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'fraction denominator must be positive'
        )
    return Fraction(numerator, denominator)


def _deserialize_fraction(payload: dict[str, int | float] | None) -> Fraction | None:
    if payload is None:
        return None
    return Fraction(int(payload['numerator']), int(payload['denominator']))


@lru_cache(maxsize=None)
def _marginal_gain_for_state_batch(state: tuple[int, int] | list[int], current_batch_length: int) -> tuple[int, Fraction]:
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_profile(
        _normalize_state(state),
        int(current_batch_length),
    )
    return (
        int(profile['state_prefix_bits']),
        _deserialize_fraction(profile['marginal_gain_bits_per_script_if_one_more_same_state_script_arrives']),
    )


@lru_cache(maxsize=None)
def _capture_fraction(arrival_probability: Fraction, horizon_ticks: int) -> Fraction:
    horizon_ticks = int(horizon_ticks)
    if horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'horizon ticks must be positive'
        )
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'arrival probability must lie in [0, 1]'
        )
    return Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** horizon_ticks


@lru_cache(maxsize=None)
def _expected_wait_ticks(arrival_probability: Fraction, horizon_ticks: int) -> Fraction:
    horizon_ticks = int(horizon_ticks)
    if horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'horizon ticks must be positive'
        )
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'arrival probability must lie in [0, 1]'
        )
    if arrival_probability == 0:
        return Fraction(horizon_ticks, 1)
    failure_probability = Fraction(1, 1) - arrival_probability
    return sum(failure_probability ** step for step in range(horizon_ticks))


@lru_cache(maxsize=None)
def evaluate_checkpoint_extension_value_for_state(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    elapsed_no_arrival_ticks: int,
    extension_ticks: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    elapsed_no_arrival_ticks = int(elapsed_no_arrival_ticks)
    extension_ticks = int(extension_ticks)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'current batch length must be positive'
        )
    if elapsed_no_arrival_ticks < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'elapsed no-arrival ticks must be nonnegative'
        )
    if extension_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'extension ticks must be positive'
        )

    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'hold cost must be nonnegative'
        )

    state_prefix_bits, marginal_gain = _marginal_gain_for_state_batch(state, current_batch_length)
    capture_fraction = _capture_fraction(arrival_probability, extension_ticks)
    expected_wait_ticks = _expected_wait_ticks(arrival_probability, extension_ticks)
    expected_gross_gain = capture_fraction * marginal_gain
    expected_net_value = expected_gross_gain - hold_cost * expected_wait_ticks
    one_more_tick_value = arrival_probability * marginal_gain - hold_cost

    if one_more_tick_value > 0:
        one_more_tick_sign = 'positive'
    elif one_more_tick_value < 0:
        one_more_tick_sign = 'negative'
    else:
        one_more_tick_sign = 'zero'

    return {
        'state': serialize_feasible_interval_kernel_state(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'elapsed_no_arrival_ticks': elapsed_no_arrival_ticks,
        'extension_ticks': extension_ticks,
        'conditional_success_probability_over_extension': _serialize_fraction(capture_fraction),
        'conditional_expected_additional_wait_ticks': _serialize_fraction(expected_wait_ticks),
        'conditional_expected_gross_gain_bits_per_script': _serialize_fraction(expected_gross_gain),
        'conditional_expected_net_extension_value_bits_per_script': _serialize_fraction(expected_net_value),
        'conditional_one_more_tick_extension_value_bits_per_script': _serialize_fraction(one_more_tick_value),
        'conditional_one_more_tick_sign': one_more_tick_sign,
        'conditional_extension_formula': '(1 - (1 - p)^H) * (gain - hold_cost / p) when p > 0',
        'conditional_one_more_tick_formula': 'p * state_prefix_bits / (n(n+1)) - hold_cost',
        'elapsed_no_arrival_streak_changes_value': False,
        'reason': 'geometric_arrival_memorylessness_makes_checkpoint_extension_depend_only_on_remaining_horizon',
    }


@lru_cache(maxsize=None)
def evaluate_universal_checkpoint_extension_value(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    elapsed_no_arrival_ticks: int,
    extension_ticks: int,
) -> dict[str, Any]:
    current_batch_length = int(current_batch_length)
    elapsed_no_arrival_ticks = int(elapsed_no_arrival_ticks)
    extension_ticks = int(extension_ticks)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'current batch length must be positive'
        )
    if elapsed_no_arrival_ticks < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'elapsed no-arrival ticks must be nonnegative'
        )
    if extension_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'extension ticks must be positive'
        )

    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'hold cost must be nonnegative'
        )

    marginal_gain = Fraction(7, current_batch_length * (current_batch_length + 1))
    capture_fraction = _capture_fraction(arrival_probability, extension_ticks)
    expected_wait_ticks = _expected_wait_ticks(arrival_probability, extension_ticks)
    expected_gross_gain = capture_fraction * marginal_gain
    expected_net_value = expected_gross_gain - hold_cost * expected_wait_ticks
    one_more_tick_value = arrival_probability * marginal_gain - hold_cost

    if one_more_tick_value > 0:
        one_more_tick_sign = 'positive'
    elif one_more_tick_value < 0:
        one_more_tick_sign = 'negative'
    else:
        one_more_tick_sign = 'zero'

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'elapsed_no_arrival_ticks': elapsed_no_arrival_ticks,
        'extension_ticks': extension_ticks,
        'conditional_success_probability_over_extension': _serialize_fraction(capture_fraction),
        'conditional_expected_additional_wait_ticks': _serialize_fraction(expected_wait_ticks),
        'conditional_expected_gross_gain_bits_per_script': _serialize_fraction(expected_gross_gain),
        'conditional_expected_net_extension_value_bits_per_script': _serialize_fraction(expected_net_value),
        'conditional_one_more_tick_extension_value_bits_per_script': _serialize_fraction(one_more_tick_value),
        'conditional_one_more_tick_sign': one_more_tick_sign,
        'conditional_extension_formula': '(1 - (1 - p)^H) * (7/(n(n+1)) - hold_cost / p) when p > 0',
        'conditional_one_more_tick_formula': '7p / (n(n+1)) - hold_cost',
        'elapsed_no_arrival_streak_changes_value': False,
        'reason': 'seven_bit_lower_envelope_gives_the_universal_checkpoint_extension_guardrail',
    }


@lru_cache(maxsize=None)
def evaluate_ex_ante_extra_tick_value_for_state(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    already_scheduled_timeout_ticks: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    already_scheduled_timeout_ticks = int(already_scheduled_timeout_ticks)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'current batch length must be positive'
        )
    if already_scheduled_timeout_ticks < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'already scheduled timeout ticks must be nonnegative'
        )

    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = _normalize_fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'arrival probability must lie in [0, 1]'
        )
    if hold_cost < 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
            'hold cost must be nonnegative'
        )

    state_prefix_bits, marginal_gain = _marginal_gain_for_state_batch(state, current_batch_length)
    sign_term = arrival_probability * marginal_gain - hold_cost
    failure_probability = Fraction(1, 1) - arrival_probability
    ex_ante_increment = failure_probability ** already_scheduled_timeout_ticks * sign_term

    if sign_term > 0:
        sign_classification = 'positive'
    elif sign_term < 0:
        sign_classification = 'negative'
    else:
        sign_classification = 'zero'

    return {
        'state': serialize_feasible_interval_kernel_state(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'already_scheduled_timeout_ticks': already_scheduled_timeout_ticks,
        'start_of_wait_value_of_one_more_planned_tick_bits_per_script': _serialize_fraction(ex_ante_increment),
        'checkpoint_value_if_that_tick_is_reached_bits_per_script': _serialize_fraction(sign_term),
        'ex_ante_increment_formula': '(1 - p)^T * (p * state_prefix_bits / (n(n+1)) - hold_cost)',
        'checkpoint_formula_if_tick_is_reached': 'p * state_prefix_bits / (n(n+1)) - hold_cost',
        'sign_classification': sign_classification,
        'reason': 'extra_planned_ticks_have_geometric_ex_ante_decay_but_constant_checkpoint_value',
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_checkpoint_extension_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 9))
    arrival_probabilities = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    hold_costs = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    elapsed_miss_streaks = tuple(range(0, 6))
    extension_horizons = tuple(range(1, 7))
    scheduled_timeout_prefixes = tuple(range(0, 6))

    validated_state_checkpoint_panels = 0
    validated_universal_lower_bound_panels = 0
    validated_state_one_more_tick_panels = 0
    validated_state_ex_ante_increment_panels = 0
    validated_ex_ante_ratio_panels = 0
    positive_one_more_tick_panels = 0
    negative_one_more_tick_panels = 0
    zero_one_more_tick_panels = 0
    positive_universal_one_more_tick_panels = 0
    negative_universal_one_more_tick_panels = 0
    zero_universal_one_more_tick_panels = 0

    for state in states:
        for current_batch_length in audited_batch_lengths:
            for arrival_probability in arrival_probabilities:
                for hold_cost in hold_costs:
                    base_one_more = None
                    for elapsed_no_arrival_ticks in elapsed_miss_streaks:
                        one_more_checkpoint = evaluate_checkpoint_extension_value_for_state(
                            state,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            elapsed_no_arrival_ticks,
                            1,
                        )
                        one_more_value = _deserialize_fraction(
                            one_more_checkpoint['conditional_one_more_tick_extension_value_bits_per_script']
                        )
                        if base_one_more is None:
                            base_one_more = one_more_value
                            if one_more_value > 0:
                                positive_one_more_tick_panels += 1
                            elif one_more_value < 0:
                                negative_one_more_tick_panels += 1
                            else:
                                zero_one_more_tick_panels += 1
                        elif one_more_value != base_one_more:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
                                f'checkpoint one-more value changed across elapsed streaks for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}'
                            )
                        validated_state_one_more_tick_panels += 1

                        for extension_ticks in extension_horizons:
                            checkpoint_value = evaluate_checkpoint_extension_value_for_state(
                                state,
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                elapsed_no_arrival_ticks,
                                extension_ticks,
                            )
                            base_value = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                state,
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                extension_ticks,
                            )
                            checkpoint_net = _deserialize_fraction(
                                checkpoint_value['conditional_expected_net_extension_value_bits_per_script']
                            )
                            base_net = _deserialize_fraction(base_value['expected_net_wait_value_bits_per_script'])
                            if checkpoint_net != base_net:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
                                    f'checkpoint extension value mismatched base timeout value for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, elapsed={elapsed_no_arrival_ticks}, H={extension_ticks}'
                                )
                            if bool(checkpoint_value['elapsed_no_arrival_streak_changes_value']):
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
                                    'checkpoint result incorrectly claimed elapsed streak changes value'
                                )
                            universal_value = evaluate_universal_checkpoint_extension_value(
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                elapsed_no_arrival_ticks,
                                extension_ticks,
                            )
                            universal_net = _deserialize_fraction(
                                universal_value['conditional_expected_net_extension_value_bits_per_script']
                            )
                            if checkpoint_net < universal_net:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
                                    f'universal checkpoint lower bound exceeded exact state value for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, elapsed={elapsed_no_arrival_ticks}, H={extension_ticks}'
                                )
                            validated_state_checkpoint_panels += 1
                            validated_universal_lower_bound_panels += 1

                    universal_one_more = evaluate_universal_checkpoint_extension_value(
                        current_batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        0,
                        1,
                    )
                    universal_one_more_value = _deserialize_fraction(
                        universal_one_more['conditional_one_more_tick_extension_value_bits_per_script']
                    )
                    if universal_one_more_value > 0:
                        positive_universal_one_more_tick_panels += 1
                    elif universal_one_more_value < 0:
                        negative_universal_one_more_tick_panels += 1
                    else:
                        zero_universal_one_more_tick_panels += 1

                    for already_scheduled_timeout_ticks in scheduled_timeout_prefixes:
                        increment = evaluate_ex_ante_extra_tick_value_for_state(
                            state,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            already_scheduled_timeout_ticks,
                        )
                        current_total_value = _deserialize_fraction(
                            evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                state,
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                already_scheduled_timeout_ticks + 1,
                            )['expected_net_wait_value_bits_per_script']
                        )
                        prior_total_value = Fraction(0, 1)
                        if already_scheduled_timeout_ticks > 0:
                            prior_total_value = _deserialize_fraction(
                                evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                                    state,
                                    current_batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    already_scheduled_timeout_ticks,
                                )['expected_net_wait_value_bits_per_script']
                            )
                        increment_value = _deserialize_fraction(
                            increment['start_of_wait_value_of_one_more_planned_tick_bits_per_script']
                        )
                        if current_total_value - prior_total_value != increment_value:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
                                f'ex ante extra-tick increment mismatched timeout difference for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, T={already_scheduled_timeout_ticks}'
                            )
                        validated_state_ex_ante_increment_panels += 1

                        if already_scheduled_timeout_ticks + 1 in scheduled_timeout_prefixes:
                            next_increment = _deserialize_fraction(
                                evaluate_ex_ante_extra_tick_value_for_state(
                                    state,
                                    current_batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    already_scheduled_timeout_ticks + 1,
                                )['start_of_wait_value_of_one_more_planned_tick_bits_per_script']
                            )
                            failure_probability = Fraction(1, 1) - arrival_probability
                            if next_increment != increment_value * failure_probability:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCheckpointExtensionLawError(
                                    f'ex ante increment did not decay by failure probability for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, T={already_scheduled_timeout_ticks}'
                                )
                            validated_ex_ante_ratio_panels += 1

    return {
        'audited_state_count': len(states),
        'audited_batch_lengths': list(audited_batch_lengths),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in arrival_probabilities],
        'audited_hold_costs': [_serialize_fraction(value) for value in hold_costs],
        'audited_elapsed_miss_streaks': list(elapsed_miss_streaks),
        'audited_extension_horizons': list(extension_horizons),
        'audited_scheduled_timeout_prefixes': list(scheduled_timeout_prefixes),
        'validated_state_checkpoint_panels': validated_state_checkpoint_panels,
        'validated_universal_lower_bound_panels': validated_universal_lower_bound_panels,
        'validated_state_one_more_tick_panels': validated_state_one_more_tick_panels,
        'validated_state_ex_ante_increment_panels': validated_state_ex_ante_increment_panels,
        'validated_ex_ante_ratio_panels': validated_ex_ante_ratio_panels,
        'positive_one_more_tick_panels': positive_one_more_tick_panels,
        'negative_one_more_tick_panels': negative_one_more_tick_panels,
        'zero_one_more_tick_panels': zero_one_more_tick_panels,
        'positive_universal_one_more_tick_panels': positive_universal_one_more_tick_panels,
        'negative_universal_one_more_tick_panels': negative_universal_one_more_tick_panels,
        'zero_universal_one_more_tick_panels': zero_universal_one_more_tick_panels,
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_checkpoint_extension_validation_summary()

    state_examples = [
        evaluate_checkpoint_extension_value_for_state((0, 16), 5, 1, 2, 1, 10, 0, 3),
        evaluate_checkpoint_extension_value_for_state((0, 16), 5, 1, 2, 1, 10, 4, 3),
        evaluate_checkpoint_extension_value_for_state((7, 12), 3, 1, 4, 1, 10, 5, 2),
        evaluate_checkpoint_extension_value_for_state((0, 16), 4, 1, 4, 1, 10, 3, 1),
    ]

    universal_examples = [
        evaluate_universal_checkpoint_extension_value(3, 1, 2, 1, 10, 0, 2),
        evaluate_universal_checkpoint_extension_value(3, 1, 2, 1, 10, 5, 2),
        evaluate_universal_checkpoint_extension_value(5, 3, 4, 1, 10, 2, 4),
        evaluate_universal_checkpoint_extension_value(1, 1, 4, 1, 2, 4, 1),
    ]

    ex_ante_ladder_examples = [
        {
            'state': serialize_feasible_interval_kernel_state((0, 16)),
            'current_batch_length': 5,
            'arrival_probability_per_tick': _serialize_fraction(Fraction(1, 2)),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(1, 10)),
            'extra_tick_index_to_start_of_wait_value': [
                {
                    'already_scheduled_timeout_ticks': timeout_prefix,
                    'start_of_wait_value_of_one_more_planned_tick_bits_per_script': evaluate_ex_ante_extra_tick_value_for_state(
                        (0, 16),
                        5,
                        1,
                        2,
                        1,
                        10,
                        timeout_prefix,
                    )['start_of_wait_value_of_one_more_planned_tick_bits_per_script'],
                }
                for timeout_prefix in range(0, 6)
            ],
        },
        {
            'state': serialize_feasible_interval_kernel_state((8, 8)),
            'current_batch_length': 3,
            'arrival_probability_per_tick': _serialize_fraction(Fraction(3, 4)),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(Fraction(1, 20)),
            'extra_tick_index_to_start_of_wait_value': [
                {
                    'already_scheduled_timeout_ticks': timeout_prefix,
                    'start_of_wait_value_of_one_more_planned_tick_bits_per_script': evaluate_ex_ante_extra_tick_value_for_state(
                        (8, 8),
                        3,
                        3,
                        4,
                        1,
                        20,
                        timeout_prefix,
                    )['start_of_wait_value_of_one_more_planned_tick_bits_per_script'],
                }
                for timeout_prefix in range(0, 6)
            ],
        },
    ]

    one_more_tick_examples = [
        evaluate_checkpoint_extension_value_for_state((0, 16), 5, 1, 2, 1, 10, 0, 1),
        evaluate_checkpoint_extension_value_for_state((0, 16), 5, 1, 2, 1, 10, 5, 1),
        evaluate_checkpoint_extension_value_for_state((0, 16), 6, 1, 4, 1, 10, 5, 1),
        evaluate_universal_checkpoint_extension_value(5, 1, 2, 1, 10, 4, 1),
    ]

    return {
        'focus': 'turn geometric no-arrival streak checkpoints into horizon-only continuation values so implementors stop panic-closing positive batches for the wrong reason',
        'headline_findings': {
            'catalog_state_count': validation_summary['audited_state_count'],
            'validated_state_checkpoint_panels': validation_summary['validated_state_checkpoint_panels'],
            'validated_universal_lower_bound_panels': validation_summary['validated_universal_lower_bound_panels'],
            'validated_state_ex_ante_increment_panels': validation_summary['validated_state_ex_ante_increment_panels'],
            'positive_one_more_tick_panels': validation_summary['positive_one_more_tick_panels'],
            'negative_one_more_tick_panels': validation_summary['negative_one_more_tick_panels'],
            'zero_one_more_tick_panels': validation_summary['zero_one_more_tick_panels'],
            'main_rule': 'conditioned on a miss streak, the value of granting H more ticks depends only on H, not on how many empty ticks have already elapsed',
        },
        'decision_rules': [
            'Under the current geometric-arrival model, conditioning on any number of prior no-arrival ticks leaves the future arrival process unchanged, so the expected net value of granting H additional ticks is exactly the same closed form as starting fresh with timeout H.',
            'Therefore the conditional value of granting one more tick right now is always p * state_prefix_bits / (n(n+1)) - hold_cost for the current state and batch length.',
            'So a positive-wait batch should not be panic-closed merely because it has already survived several empty ticks; miss streak age alone is not new economic evidence under stationary hazard, hold cost, and state.',
            'The all-state guardrail is the same checkpoint rule with state_prefix_bits replaced by the exact seven-bit lower envelope on the current path.',
            'From the beginning of the wait, however, the value of planning one extra future tick does decay geometrically as (1 - p)^T times that same one-more-tick checkpoint value, because fewer runs survive long enough to reach late ticks.',
            'So timeout should be chosen up front from explicit latency or service constraints, but mid-wait retuning should key off changed hazard, changed cost, changed shared state, or exhausted remaining horizon rather than mere elapsed miss streaks.',
        ],
        'state_examples': state_examples,
        'universal_examples': universal_examples,
        'ex_ante_ladder_examples': ex_ante_ladder_examples,
        'one_more_tick_examples': one_more_tick_examples,
        'validation_summary': validation_summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot_20260316.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law_snapshot_20260316.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law_snapshot_20260316.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law.py',
    }


def main() -> None:
    json.dump(
        build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_snapshot(),
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
