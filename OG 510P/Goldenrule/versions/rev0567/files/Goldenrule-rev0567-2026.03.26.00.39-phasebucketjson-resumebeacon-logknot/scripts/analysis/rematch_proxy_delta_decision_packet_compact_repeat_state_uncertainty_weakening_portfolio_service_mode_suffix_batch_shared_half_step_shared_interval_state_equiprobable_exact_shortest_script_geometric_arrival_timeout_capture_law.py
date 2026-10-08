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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law import (
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
            'fraction denominator must be positive'
        )
    return Fraction(numerator, denominator)


def _deserialize_fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


@lru_cache(maxsize=None)
def build_positive_wait_timeout_capture_profile(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    timeout_ticks: int,
) -> dict[str, Any]:
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    timeout_ticks = int(timeout_ticks)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
            'arrival probability must lie in [0, 1]'
        )
    if timeout_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
            'timeout ticks must be positive'
        )

    if arrival_probability == 0:
        capture_fraction = Fraction(0, 1)
        expected_wait_ticks = Fraction(timeout_ticks, 1)
    else:
        capture_fraction = Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** timeout_ticks
        expected_wait_ticks = capture_fraction / arrival_probability

    return {
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'timeout_ticks': timeout_ticks,
        'capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(capture_fraction),
        'expected_wait_ticks_until_success_or_timeout': _serialize_fraction(expected_wait_ticks),
        'capture_formula': '1 - (1 - p)^T',
        'expected_wait_formula': '(1 - (1 - p)^T) / p',
    }


@lru_cache(maxsize=None)
def compute_minimum_timeout_for_capture_fraction(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    target_capture_numerator: int,
    target_capture_denominator: int,
) -> dict[str, Any]:
    arrival_probability = _normalize_fraction(arrival_probability_numerator, arrival_probability_denominator)
    target_capture = _normalize_fraction(target_capture_numerator, target_capture_denominator)
    if arrival_probability < 0 or arrival_probability > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
            'arrival probability must lie in [0, 1]'
        )
    if target_capture <= 0 or target_capture > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
            'target capture fraction must lie in (0, 1]'
        )

    if arrival_probability == 0:
        return {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'target_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(target_capture),
            'minimum_timeout_ticks': None,
            'finite_timeout_exists': False,
            'reason': 'zero_arrival_probability_cannot_capture_positive_asymptotic_value',
        }

    if target_capture == 1:
        if arrival_probability == 1:
            profile = build_positive_wait_timeout_capture_profile(1, 1, 1)
            return {
                'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
                'target_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(target_capture),
                'minimum_timeout_ticks': 1,
                'finite_timeout_exists': True,
                'reason': 'certain_arrival_captures_full_value_immediately',
                'achieved_capture_fraction_by_minimum_timeout': profile['capture_fraction_of_asymptotic_positive_wait_value'],
                'expected_wait_ticks_by_minimum_timeout': profile['expected_wait_ticks_until_success_or_timeout'],
                'timeout_closed_form': '1',
            }
        return {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'target_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(target_capture),
            'minimum_timeout_ticks': None,
            'finite_timeout_exists': False,
            'reason': 'finite_timeout_cannot_capture_full_asymptotic_value_when_arrival_probability_is_below_one',
        }

    timeout_ticks = 1
    while True:
        profile = build_positive_wait_timeout_capture_profile(
            arrival_probability.numerator,
            arrival_probability.denominator,
            timeout_ticks,
        )
        capture_fraction = _deserialize_fraction(profile['capture_fraction_of_asymptotic_positive_wait_value'])
        if capture_fraction >= target_capture:
            break
        timeout_ticks += 1

    previous_capture_fraction = None
    if timeout_ticks > 1:
        previous_profile = build_positive_wait_timeout_capture_profile(
            arrival_probability.numerator,
            arrival_probability.denominator,
            timeout_ticks - 1,
        )
        previous_capture_fraction = previous_profile['capture_fraction_of_asymptotic_positive_wait_value']

    timeout_closed_form = '1' if arrival_probability == 1 else 'ceil(log(1 - alpha) / log(1 - p))'
    return {
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'target_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(target_capture),
        'minimum_timeout_ticks': timeout_ticks,
        'finite_timeout_exists': True,
        'reason': 'minimum_timeout_reaching_capture_target',
        'achieved_capture_fraction_by_minimum_timeout': profile['capture_fraction_of_asymptotic_positive_wait_value'],
        'expected_wait_ticks_by_minimum_timeout': profile['expected_wait_ticks_until_success_or_timeout'],
        'previous_timeout_capture_fraction': previous_capture_fraction,
        'timeout_closed_form': timeout_closed_form,
    }


@lru_cache(maxsize=None)
def evaluate_positive_wait_timeout_capture_policy_for_state_batch(
    state: tuple[int, int] | list[int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_capture_numerator: int,
    target_capture_denominator: int,
) -> dict[str, Any]:
    state = _normalize_state(state)
    current_batch_length = int(current_batch_length)
    if current_batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
            'current batch length must be positive'
        )
    wait_value = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        state,
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        1,
    )
    arrival_probability = _deserialize_fraction(wait_value['arrival_probability_per_tick'])
    target_capture = _normalize_fraction(target_capture_numerator, target_capture_denominator)
    sign_invariant_term = _deserialize_fraction(wait_value['sign_invariant_term_bits_per_script_per_tick'])

    result: dict[str, Any] = {
        'state': serialize_feasible_interval_kernel_state(state),
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': wait_value['arrival_probability_per_tick'],
        'hold_cost_bits_per_script_per_tick': wait_value['hold_cost_bits_per_script_per_tick'],
        'target_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(target_capture),
        'state_prefix_bits': wait_value['state_prefix_bits'],
        'sign_classification': wait_value['sign_classification'],
        'sign_invariant_term_bits_per_script_per_tick': wait_value['sign_invariant_term_bits_per_script_per_tick'],
    }

    if arrival_probability == 0 or sign_invariant_term <= 0:
        result.update(
            {
                'positive_wait_exists': False,
                'minimum_timeout_ticks': None,
                'reason': 'nonpositive_wait_value_or_zero_arrival',
            }
        )
        return result

    asymptotic_positive_wait_value = sign_invariant_term / arrival_probability
    timeout_policy = compute_minimum_timeout_for_capture_fraction(
        arrival_probability.numerator,
        arrival_probability.denominator,
        target_capture.numerator,
        target_capture.denominator,
    )
    assert timeout_policy['minimum_timeout_ticks'] is not None
    timeout_ticks = int(timeout_policy['minimum_timeout_ticks'])
    final_wait_value = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        state,
        current_batch_length,
        arrival_probability.numerator,
        arrival_probability.denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        timeout_ticks,
    )
    achieved_net = _deserialize_fraction(final_wait_value['expected_net_wait_value_bits_per_script'])
    achieved_capture = achieved_net / asymptotic_positive_wait_value

    result.update(
        {
            'positive_wait_exists': True,
            'asymptotic_positive_wait_value_bits_per_script': _serialize_fraction(asymptotic_positive_wait_value),
            'minimum_timeout_ticks': timeout_ticks,
            'achieved_capture_fraction_by_minimum_timeout': _serialize_fraction(achieved_capture),
            'expected_net_wait_value_by_minimum_timeout_bits_per_script': final_wait_value['expected_net_wait_value_bits_per_script'],
            'expected_wait_ticks_by_minimum_timeout': timeout_policy['expected_wait_ticks_by_minimum_timeout'],
            'reason': timeout_policy['reason'],
        }
    )
    previous_timeout_capture_fraction = timeout_policy.get('previous_timeout_capture_fraction')
    if previous_timeout_capture_fraction is not None:
        result['previous_timeout_capture_fraction'] = previous_timeout_capture_fraction
    return result


@lru_cache(maxsize=1)
def build_geometric_arrival_timeout_capture_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = tuple(range(1, 9))
    arrival_probabilities = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    hold_costs = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
    capture_targets = (
        Fraction(1, 2),
        Fraction(3, 4),
        Fraction(7, 8),
        Fraction(15, 16),
        Fraction(31, 32),
    )

    positive_wait_panels = 0
    negative_wait_panels = 0
    zero_wait_panels = 0
    validated_positive_wait_capture_panels = 0
    seen_timeout: dict[tuple[Fraction, Fraction], int] = {}

    for state in states:
        for batch_length in audited_batch_lengths:
            for arrival_probability in arrival_probabilities:
                for hold_cost in hold_costs:
                    base = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
                        state,
                        batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        1,
                    )
                    sign_classification = base['sign_classification']
                    if sign_classification == 'negative':
                        negative_wait_panels += 1
                        continue
                    if sign_classification == 'zero':
                        zero_wait_panels += 1
                        continue

                    positive_wait_panels += 1
                    asymptotic_positive_wait_value = _deserialize_fraction(base['sign_invariant_term_bits_per_script_per_tick']) / arrival_probability
                    for capture_target in capture_targets:
                        policy = evaluate_positive_wait_timeout_capture_policy_for_state_batch(
                            state,
                            batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            capture_target.numerator,
                            capture_target.denominator,
                        )
                        timeout_ticks = int(policy['minimum_timeout_ticks'])
                        achieved_capture_fraction = _deserialize_fraction(policy['achieved_capture_fraction_by_minimum_timeout'])
                        achieved_net_value = _deserialize_fraction(policy['expected_net_wait_value_by_minimum_timeout_bits_per_script'])
                        if achieved_net_value != achieved_capture_fraction * asymptotic_positive_wait_value:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
                                f'capture ratio mismatch for state {state}, batch {batch_length}, p={arrival_probability}, c={hold_cost}, alpha={capture_target}'
                            )
                        if achieved_capture_fraction < capture_target:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
                                f'capture target missed for state {state}, batch {batch_length}, p={arrival_probability}, c={hold_cost}, alpha={capture_target}'
                            )
                        if timeout_ticks > 1 and arrival_probability < 1:
                            previous_capture_fraction = _deserialize_fraction(policy['previous_timeout_capture_fraction'])
                            if previous_capture_fraction >= capture_target:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
                                    f'timeout was not minimal for state {state}, batch {batch_length}, p={arrival_probability}, c={hold_cost}, alpha={capture_target}'
                                )
                        key = (arrival_probability, capture_target)
                        if key in seen_timeout and seen_timeout[key] != timeout_ticks:
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeoutCaptureLawError(
                                f'timeout state-independence failed for p={arrival_probability}, alpha={capture_target}'
                            )
                        seen_timeout[key] = timeout_ticks
                        validated_positive_wait_capture_panels += 1

    validated_arrival_target_schedules = 0
    for arrival_probability in arrival_probabilities:
        for capture_target in capture_targets:
            schedule = compute_minimum_timeout_for_capture_fraction(
                arrival_probability.numerator,
                arrival_probability.denominator,
                capture_target.numerator,
                capture_target.denominator,
            )
            assert schedule['finite_timeout_exists'] is True
            assert schedule['minimum_timeout_ticks'] is not None
            validated_arrival_target_schedules += 1

    return {
        'audited_state_count': len(states),
        'audited_batch_lengths': list(audited_batch_lengths),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in arrival_probabilities],
        'audited_hold_costs': [_serialize_fraction(value) for value in hold_costs],
        'audited_capture_targets': [_serialize_fraction(value) for value in capture_targets],
        'positive_wait_panels': positive_wait_panels,
        'negative_wait_panels': negative_wait_panels,
        'zero_wait_panels': zero_wait_panels,
        'validated_positive_wait_capture_panels': validated_positive_wait_capture_panels,
        'validated_arrival_target_schedules': validated_arrival_target_schedules,
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_timeout_capture_validation_summary()
    capture_targets = [Fraction(1, 2), Fraction(3, 4), Fraction(7, 8), Fraction(15, 16), Fraction(31, 32)]

    arrival_schedule_examples = []
    for arrival_probability in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1)):
        row: dict[str, Any] = {
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'capture_schedule': [],
        }
        for capture_target in capture_targets:
            schedule = compute_minimum_timeout_for_capture_fraction(
                arrival_probability.numerator,
                arrival_probability.denominator,
                capture_target.numerator,
                capture_target.denominator,
            )
            row['capture_schedule'].append(
                {
                    'target_capture_fraction_of_asymptotic_positive_wait_value': _serialize_fraction(capture_target),
                    'minimum_timeout_ticks': schedule['minimum_timeout_ticks'],
                    'achieved_capture_fraction_by_minimum_timeout': schedule['achieved_capture_fraction_by_minimum_timeout'],
                    'expected_wait_ticks_by_minimum_timeout': schedule['expected_wait_ticks_by_minimum_timeout'],
                }
            )
        arrival_schedule_examples.append(row)

    state_examples = [
        evaluate_positive_wait_timeout_capture_policy_for_state_batch((0, 16), 5, 1, 2, 1, 10, 15, 16),
        evaluate_positive_wait_timeout_capture_policy_for_state_batch((7, 12), 3, 1, 2, 1, 10, 15, 16),
        evaluate_positive_wait_timeout_capture_policy_for_state_batch((8, 8), 3, 1, 4, 1, 10, 7, 8),
        evaluate_positive_wait_timeout_capture_policy_for_state_batch((15, 15), 1, 1, 4, 1, 2, 31, 32),
    ]

    policy_boundary_examples = [
        compute_minimum_timeout_for_capture_fraction(1, 4, 15, 16),
        compute_minimum_timeout_for_capture_fraction(1, 2, 15, 16),
        compute_minimum_timeout_for_capture_fraction(3, 4, 31, 32),
        compute_minimum_timeout_for_capture_fraction(1, 1, 31, 32),
    ]

    return {
        'focus': 'turn positive geometric-arrival waiting into a compact timeout-selection rule by targeting a desired fraction of asymptotic positive wait value',
        'headline_findings': {
            'catalog_state_count': validation_summary['audited_state_count'],
            'positive_wait_panels': validation_summary['positive_wait_panels'],
            'validated_positive_wait_capture_panels': validation_summary['validated_positive_wait_capture_panels'],
            'validated_arrival_target_schedules': validation_summary['validated_arrival_target_schedules'],
            'universal_positive_wait_timeout_rule': 'once wait is positive, choose the smallest T with 1 - (1 - p)^T >= target_capture_fraction',
            'finite_full_capture_result': 'finite timeout reaches 100% of asymptotic positive wait value only when arrival probability equals one',
        },
        'decision_rules': [
            'If the earlier wait-value sign test is nonpositive, do not wait at all; timeout tuning is irrelevant there.',
            'If wait is positive, the asymptotic net value as timeout grows is exactly gain - hold_cost / p = (p * gain - hold_cost) / p.',
            'A finite timeout T captures exactly the fraction 1 - (1 - p)^T of that asymptotic positive wait value.',
            'Therefore the minimum timeout for capture target alpha in (0, 1) is ceil(log(1 - alpha) / log(1 - p)) for 0 < p < 1, with T = 1 when p = 1.',
            'No finite timeout can capture 100% of the asymptotic positive value unless p = 1; for p < 1 treat full capture as an asymptote, not an operational target.',
            'Expected wait ticks at the selected timeout are exactly capture_fraction / p, so service latency budgets can be priced directly from the same arrival-only schedule.',
        ],
        'arrival_schedule_examples': arrival_schedule_examples,
        'state_examples': state_examples,
        'policy_boundary_examples': policy_boundary_examples,
        'validation_summary': validation_summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot_20260316.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law.py',
    }


def main() -> None:
    json.dump(
        build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_snapshot(),
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
