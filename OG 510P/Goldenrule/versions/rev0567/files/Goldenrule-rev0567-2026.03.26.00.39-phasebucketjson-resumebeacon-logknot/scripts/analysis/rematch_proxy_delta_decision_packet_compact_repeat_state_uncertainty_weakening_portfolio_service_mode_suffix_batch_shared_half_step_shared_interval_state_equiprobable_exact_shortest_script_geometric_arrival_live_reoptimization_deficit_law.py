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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law import (
    compute_minimum_timeout_for_state_batch_target_margin,
    compute_universal_minimum_timeout_for_batch_target_margin,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law import (
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
REMAINING_HORIZON_GRID = (1, 2, 3, 4, 5, 6, 7, 8)


def _serialize_fraction(value: Fraction | None) -> dict[str, int | float] | None:
    if value is None:
        return None
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _deserialize_fraction(payload: dict[str, int | float] | None) -> Fraction | None:
    if payload is None:
        return None
    return Fraction(int(payload['numerator']), int(payload['denominator']))


@lru_cache(maxsize=None)
def _state_prefix_bits(state: tuple[int, int]) -> int:
    profile = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        state,
        1,
        1,
        2,
        1,
        10,
        1,
    )
    return int(profile['state_prefix_bits'])


@lru_cache(maxsize=None)
def _fixed_timeout_value_for_state(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability: Fraction,
    hold_cost: Fraction,
    timeout_ticks: int,
) -> Fraction:
    if timeout_ticks <= 0:
        return Fraction(0, 1)
    payload = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        state,
        current_batch_length,
        arrival_probability.numerator,
        arrival_probability.denominator,
        hold_cost.numerator,
        hold_cost.denominator,
        timeout_ticks,
    )
    value = _deserialize_fraction(payload['expected_net_wait_value_bits_per_script'])
    if value is None:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
            'state wait-value payload unexpectedly omitted expected net value'
        )
    return value


@lru_cache(maxsize=None)
def _fixed_timeout_value_for_universal(
    current_batch_length: int,
    arrival_probability: Fraction,
    hold_cost: Fraction,
    timeout_ticks: int,
) -> Fraction:
    if timeout_ticks <= 0:
        return Fraction(0, 1)
    if arrival_probability == 0:
        return -hold_cost * timeout_ticks
    success_probability = Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** timeout_ticks
    expected_wait_ticks = sum((Fraction(1, 1) - arrival_probability) ** step for step in range(timeout_ticks))
    gross_gain = success_probability * Fraction(7, current_batch_length * (current_batch_length + 1))
    return gross_gain - hold_cost * expected_wait_ticks


def _schedule_class(schedule: dict[str, Any]) -> str:
    if bool(schedule['finite_timeout_exists']):
        return 'finite'
    if bool(schedule['asymptotically_feasible']):
        return 'asymptotic_only'
    return 'impossible'


def _checked_fraction_div(numerator: Fraction, denominator: Fraction) -> Fraction | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _live_deficit_payload(
    gain_slope: Fraction,
    arrival_probability: Fraction,
    minimum_timeout_ticks: int,
    remaining_horizon_ticks: int,
    blind_commit_value: Fraction,
    live_value: Fraction,
) -> tuple[Fraction, Fraction, Fraction]:
    miss_probability = Fraction(1, 1) - arrival_probability
    formula_deficit = gain_slope * (miss_probability ** (remaining_horizon_ticks - minimum_timeout_ticks + 1)) * (Fraction(1, 1) - miss_probability ** (minimum_timeout_ticks - 1))
    observed_deficit = blind_commit_value - live_value
    if formula_deficit != observed_deficit:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
            f'closed-form live deficit mismatch: formula {formula_deficit} vs observed {observed_deficit}'
        )
    preservation_fraction = _checked_fraction_div(live_value, blind_commit_value)
    formula_preservation = _checked_fraction_div(
        Fraction(1, 1) - miss_probability ** (remaining_horizon_ticks - minimum_timeout_ticks + 1),
        Fraction(1, 1) - miss_probability ** remaining_horizon_ticks,
    )
    if blind_commit_value == 0:
        if live_value != 0 or observed_deficit != 0:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                'zero blind-commit value did not align with zero live value and zero deficit'
            )
        preservation_fraction = None
    else:
        if preservation_fraction is None or formula_preservation is None:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                'preservation fraction unexpectedly undefined for a nonzero finite schedule'
            )
        if preservation_fraction != formula_preservation:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                f'closed-form preservation fraction mismatch: formula {formula_preservation} vs observed {preservation_fraction}'
            )
    return observed_deficit, formula_deficit, preservation_fraction


@lru_cache(maxsize=None)
def evaluate_state_live_reoptimization_deficit_profile(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    remaining_horizon_ticks: int,
) -> dict[str, Any]:
    if remaining_horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
            'remaining horizon ticks must be positive'
        )

    arrival_probability = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    schedule = compute_minimum_timeout_for_state_batch_target_margin(
        state,
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    schedule_class = _schedule_class(schedule)
    minimum_timeout_ticks = schedule['minimum_timeout_ticks']
    state_prefix_bits = _state_prefix_bits(state)
    gain_slope = Fraction(state_prefix_bits, current_batch_length * (current_batch_length + 1)) - hold_cost / arrival_probability

    blind_commit_value = _fixed_timeout_value_for_state(
        state,
        current_batch_length,
        arrival_probability,
        hold_cost,
        remaining_horizon_ticks,
    )

    if schedule_class == 'finite' and minimum_timeout_ticks is not None and remaining_horizon_ticks >= int(minimum_timeout_ticks):
        live_value = _fixed_timeout_value_for_state(
            state,
            current_batch_length,
            arrival_probability,
            hold_cost,
            remaining_horizon_ticks - int(minimum_timeout_ticks) + 1,
        )
        observed_deficit, formula_deficit, preservation_fraction = _live_deficit_payload(
            gain_slope,
            arrival_probability,
            int(minimum_timeout_ticks),
            remaining_horizon_ticks,
            blind_commit_value,
            live_value,
        )
        reason = 'stateless_live_reoptimization_prices_as_a_geometric_same_horizon_blind_commit_deficit'
    else:
        live_value = Fraction(0, 1)
        observed_deficit = None
        formula_deficit = None
        preservation_fraction = None
        reason = 'no_same_horizon_live_deficit_is_defined_without_a_finite_schedule_that_actually_continues'

    return {
        'state': list(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'remaining_horizon_ticks': int(remaining_horizon_ticks),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': minimum_timeout_ticks,
        'positive_wait_gain_slope_bits_per_script': _serialize_fraction(gain_slope),
        'blind_commit_same_horizon_value_bits_per_script': _serialize_fraction(blind_commit_value),
        'stateless_live_reoptimization_value_bits_per_script': _serialize_fraction(live_value),
        'same_horizon_live_deficit_bits_per_script': _serialize_fraction(observed_deficit),
        'same_horizon_live_deficit_formula_bits_per_script': _serialize_fraction(formula_deficit),
        'same_horizon_preservation_fraction_under_live_reoptimization': _serialize_fraction(preservation_fraction),
        'boundary_preservation_fraction_formula': 'for finite schedules at H = K, preserved share is p / (1 - (1 - p)^K)',
        'deficit_formula': 'for finite schedules with H >= K, blind_commit(H) - live(H) = (state_prefix_bits/(n(n+1)) - c/p) * (1-p)^(H-K+1) * (1 - (1-p)^(K-1))',
        'reason': reason,
    }


@lru_cache(maxsize=None)
def evaluate_universal_live_reoptimization_deficit_profile(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    remaining_horizon_ticks: int,
) -> dict[str, Any]:
    if remaining_horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
            'remaining horizon ticks must be positive'
        )

    arrival_probability = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    schedule = compute_universal_minimum_timeout_for_batch_target_margin(
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    schedule_class = _schedule_class(schedule)
    minimum_timeout_ticks = schedule['minimum_timeout_ticks']
    gain_slope = Fraction(7, current_batch_length * (current_batch_length + 1)) - hold_cost / arrival_probability

    blind_commit_value = _fixed_timeout_value_for_universal(
        current_batch_length,
        arrival_probability,
        hold_cost,
        remaining_horizon_ticks,
    )

    if schedule_class == 'finite' and minimum_timeout_ticks is not None and remaining_horizon_ticks >= int(minimum_timeout_ticks):
        live_value = _fixed_timeout_value_for_universal(
            current_batch_length,
            arrival_probability,
            hold_cost,
            remaining_horizon_ticks - int(minimum_timeout_ticks) + 1,
        )
        observed_deficit, formula_deficit, preservation_fraction = _live_deficit_payload(
            gain_slope,
            arrival_probability,
            int(minimum_timeout_ticks),
            remaining_horizon_ticks,
            blind_commit_value,
            live_value,
        )
        reason = 'stateless_universal_live_reoptimization_prices_as_a_geometric_same_horizon_blind_commit_deficit'
    else:
        live_value = Fraction(0, 1)
        observed_deficit = None
        formula_deficit = None
        preservation_fraction = None
        reason = 'no_same_horizon_universal_live_deficit_is_defined_without_a_finite_schedule_that_actually_continues'

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'remaining_horizon_ticks': int(remaining_horizon_ticks),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': minimum_timeout_ticks,
        'positive_wait_gain_slope_bits_per_script': _serialize_fraction(gain_slope),
        'blind_commit_same_horizon_value_bits_per_script': _serialize_fraction(blind_commit_value),
        'stateless_live_reoptimization_value_bits_per_script': _serialize_fraction(live_value),
        'same_horizon_live_deficit_bits_per_script': _serialize_fraction(observed_deficit),
        'same_horizon_live_deficit_formula_bits_per_script': _serialize_fraction(formula_deficit),
        'same_horizon_preservation_fraction_under_live_reoptimization': _serialize_fraction(preservation_fraction),
        'boundary_preservation_fraction_formula': 'for finite universal schedules at H = K, preserved share is p / (1 - (1 - p)^K)',
        'deficit_formula': 'for finite universal schedules with H >= K, blind_commit(H) - live(H) = (7/(n(n+1)) - c/p) * (1-p)^(H-K+1) * (1 - (1-p)^(K-1))',
        'reason': reason,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_reoptimization_deficit_validation_summary() -> dict[str, Any]:
    validated_state_panels = 0
    validated_universal_panels = 0
    finite_state_continuations = 0
    finite_universal_continuations = 0
    positive_state_deficits = 0
    zero_state_deficits = 0
    positive_universal_deficits = 0
    zero_universal_deficits = 0
    strictly_improving_state_ladders = 0
    strictly_improving_universal_ladders = 0

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        previous_deficit: Fraction | None = None
                        saw_strict_drop = False
                        for remaining_horizon_ticks in REMAINING_HORIZON_GRID:
                            profile = evaluate_state_live_reoptimization_deficit_profile(
                                state,
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                remaining_horizon_ticks,
                            )
                            minimum_timeout_ticks = profile['minimum_timeout_ticks_for_blind_commit_margin']
                            deficit = _deserialize_fraction(profile['same_horizon_live_deficit_bits_per_script'])
                            if profile['schedule_class'] == 'finite' and minimum_timeout_ticks is not None and remaining_horizon_ticks >= int(minimum_timeout_ticks):
                                finite_state_continuations += 1
                                assert deficit is not None
                                if int(minimum_timeout_ticks) == 1:
                                    if deficit != 0:
                                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                                            f'one-tick state schedule had nonzero live deficit for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                        )
                                    zero_state_deficits += 1
                                else:
                                    if deficit <= 0:
                                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                                            f'multi-tick state schedule had nonpositive live deficit for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                        )
                                    positive_state_deficits += 1
                                if previous_deficit is not None:
                                    if deficit > previous_deficit:
                                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                                            f'state live deficit grew with more horizon for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                        )
                                    if deficit < previous_deficit:
                                        saw_strict_drop = True
                                previous_deficit = deficit
                            validated_state_panels += 1
                        if saw_strict_drop:
                            strictly_improving_state_ladders += 1

    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    previous_deficit = None
                    saw_strict_drop = False
                    for remaining_horizon_ticks in REMAINING_HORIZON_GRID:
                        profile = evaluate_universal_live_reoptimization_deficit_profile(
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            remaining_horizon_ticks,
                        )
                        minimum_timeout_ticks = profile['minimum_timeout_ticks_for_blind_commit_margin']
                        deficit = _deserialize_fraction(profile['same_horizon_live_deficit_bits_per_script'])
                        if profile['schedule_class'] == 'finite' and minimum_timeout_ticks is not None and remaining_horizon_ticks >= int(minimum_timeout_ticks):
                            finite_universal_continuations += 1
                            assert deficit is not None
                            if int(minimum_timeout_ticks) == 1:
                                if deficit != 0:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                                        f'one-tick universal schedule had nonzero live deficit for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )
                                zero_universal_deficits += 1
                            else:
                                if deficit <= 0:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                                        f'multi-tick universal schedule had nonpositive live deficit for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )
                                positive_universal_deficits += 1
                            if previous_deficit is not None:
                                if deficit > previous_deficit:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalLiveReoptimizationDeficitLawError(
                                        f'universal live deficit grew with more horizon for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )
                                if deficit < previous_deficit:
                                    saw_strict_drop = True
                            previous_deficit = deficit
                        validated_universal_panels += 1
                    if saw_strict_drop:
                        strictly_improving_universal_ladders += 1

    return {
        'audited_state_count': len(STATE_GRID),
        'validated_state_panels': validated_state_panels,
        'validated_universal_panels': validated_universal_panels,
        'finite_state_continuation_panels': finite_state_continuations,
        'finite_universal_continuation_panels': finite_universal_continuations,
        'positive_state_deficit_panels': positive_state_deficits,
        'zero_state_deficit_panels': zero_state_deficits,
        'positive_universal_deficit_panels': positive_universal_deficits,
        'zero_universal_deficit_panels': zero_universal_deficits,
        'strictly_improving_state_ladders': strictly_improving_state_ladders,
        'strictly_improving_universal_ladders': strictly_improving_universal_ladders,
        'remaining_horizon_grid': list(REMAINING_HORIZON_GRID),
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_live_reoptimization_deficit_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_reoptimization_deficit_validation_summary()

    state_boundary_example = evaluate_state_live_reoptimization_deficit_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        2,
    )
    state_decay_example = evaluate_state_live_reoptimization_deficit_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        5,
    )
    universal_boundary_example = evaluate_universal_live_reoptimization_deficit_profile(
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        2,
    )

    return {
        'focus': 'price the exact same-horizon value haircut paid when a blind-commit batch promise is executed by stateless miss-by-miss live reoptimization instead',
        'headline_findings': {
            'deficit_rule': 'for finite schedules with H >= K, same-horizon blind-commit minus live-reoptimized value is a geometric deficit with gain slope factor and reserve-length factor',
            'boundary_rule': 'the boundary preserved share at H = K is exactly p / (1 - (1 - p)^K)',
            'zero_deficit_rule': 'same-horizon deficit is identically zero iff K = 1',
            'positive_state_deficit_panels': summary['positive_state_deficit_panels'],
            'positive_universal_deficit_panels': summary['positive_universal_deficit_panels'],
        },
        'decision_rules': [
            'If the implementation can only run stateless live reoptimization, price it as an explicit same-horizon blind-commit haircut instead of pretending it preserves the original schedule value.',
            'One-tick promises are the only finite schedules with zero same-horizon haircut.',
            'For any multi-tick finite promise, the haircut is largest at the boundary checkpoint and then decays geometrically as extra horizon accumulates.',
            'So a simpler live controller can still be used, but its economic value should be recorded as blind-commit value minus the exact deficit tax rather than as the blind-commit promise itself.',
        ],
        'state_boundary_example': state_boundary_example,
        'state_decay_example': state_decay_example,
        'universal_boundary_example': universal_boundary_example,
        'validation_summary': summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_live_reoptimization_deficit_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_live_reoptimization_deficit_snapshot(), indent=2, sort_keys=True))
