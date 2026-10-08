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


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
REMAINING_HORIZON_GRID = (1, 2, 3, 4, 5, 6)


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
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


@lru_cache(maxsize=None)
def _countdown_reoptimized_value_by_recursion(
    state_prefix_bits: int,
    current_batch_length: int,
    arrival_probability: Fraction,
    hold_cost: Fraction,
    minimum_timeout_ticks: int,
    remaining_horizon_ticks: int,
) -> Fraction:
    if remaining_horizon_ticks < minimum_timeout_ticks:
        return Fraction(0, 1)
    next_value = _countdown_reoptimized_value_by_recursion(
        state_prefix_bits,
        current_batch_length,
        arrival_probability,
        hold_cost,
        minimum_timeout_ticks,
        remaining_horizon_ticks - 1,
    )
    return -hold_cost + arrival_probability * Fraction(state_prefix_bits, current_batch_length * (current_batch_length + 1)) + (Fraction(1, 1) - arrival_probability) * next_value


@lru_cache(maxsize=None)
def evaluate_state_countdown_reserve_profile(
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
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
    blind_commit_value = _fixed_timeout_value_for_state(
        state,
        current_batch_length,
        arrival_probability,
        hold_cost,
        remaining_horizon_ticks,
    )

    minimum_timeout_ticks = schedule['minimum_timeout_ticks']
    finite_timeout_exists = bool(schedule['finite_timeout_exists'])
    asymptotically_feasible = bool(schedule['asymptotically_feasible'])
    if finite_timeout_exists:
        schedule_class = 'finite'
    elif asymptotically_feasible:
        schedule_class = 'asymptotic_only'
    else:
        schedule_class = 'impossible'

    state_prefix_bits = _state_prefix_bits(state)
    if schedule_class == 'finite' and minimum_timeout_ticks is not None and remaining_horizon_ticks >= int(minimum_timeout_ticks):
        dead_reserve_ticks = int(minimum_timeout_ticks) - 1
        usable_wait_window_ticks = remaining_horizon_ticks - dead_reserve_ticks
        reoptimized_value = _fixed_timeout_value_for_state(
            state,
            current_batch_length,
            arrival_probability,
            hold_cost,
            usable_wait_window_ticks,
        )
        minimum_horizon_to_preserve_original_margin = 2 * int(minimum_timeout_ticks) - 1
        continues_under_live_countdown_policy = True
        reason = 'countdown_policy_runs_only_the_usable_wait_window_and_holds_the_last_ticks_as_dead_reserve'
    else:
        dead_reserve_ticks = int(minimum_timeout_ticks) - 1 if minimum_timeout_ticks is not None else None
        usable_wait_window_ticks = 0
        reoptimized_value = Fraction(0, 1)
        minimum_horizon_to_preserve_original_margin = 2 * int(minimum_timeout_ticks) - 1 if minimum_timeout_ticks is not None else None
        continues_under_live_countdown_policy = False
        reason = 'countdown_policy_closes_immediately_because_remaining_horizon_does_not_reach_a_finite_viable_threshold'

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
        'dead_reserve_ticks_under_live_countdown_policy': dead_reserve_ticks,
        'usable_wait_window_ticks_under_live_countdown_policy': usable_wait_window_ticks,
        'blind_commit_value_bits_per_script': _serialize_fraction(blind_commit_value),
        'live_countdown_policy_value_bits_per_script': _serialize_fraction(reoptimized_value),
        'live_countdown_policy_continues': continues_under_live_countdown_policy,
        'blind_commit_meets_original_margin_floor': blind_commit_value >= target_margin,
        'live_countdown_policy_meets_original_margin_floor': reoptimized_value >= target_margin,
        'minimum_remaining_horizon_ticks_to_preserve_original_margin_under_live_countdown': minimum_horizon_to_preserve_original_margin,
        'blind_commit_threshold_formula': 'blind commit meets margin iff H >= K',
        'live_countdown_value_formula': 'live countdown value equals fixed-timeout value with usable window max(H - K + 1, 0)',
        'margin_preservation_formula': 'live countdown preserves original margin iff H >= 2K - 1 for finite schedules',
        'reason': reason,
    }


@lru_cache(maxsize=None)
def evaluate_universal_countdown_reserve_profile(
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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
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
    blind_commit_value = _fixed_timeout_value_for_universal(
        current_batch_length,
        arrival_probability,
        hold_cost,
        remaining_horizon_ticks,
    )

    minimum_timeout_ticks = schedule['minimum_timeout_ticks']
    finite_timeout_exists = bool(schedule['finite_timeout_exists'])
    asymptotically_feasible = bool(schedule['asymptotically_feasible'])
    if finite_timeout_exists:
        schedule_class = 'finite'
    elif asymptotically_feasible:
        schedule_class = 'asymptotic_only'
    else:
        schedule_class = 'impossible'

    if schedule_class == 'finite' and minimum_timeout_ticks is not None and remaining_horizon_ticks >= int(minimum_timeout_ticks):
        dead_reserve_ticks = int(minimum_timeout_ticks) - 1
        usable_wait_window_ticks = remaining_horizon_ticks - dead_reserve_ticks
        reoptimized_value = _fixed_timeout_value_for_universal(
            current_batch_length,
            arrival_probability,
            hold_cost,
            usable_wait_window_ticks,
        )
        minimum_horizon_to_preserve_original_margin = 2 * int(minimum_timeout_ticks) - 1
        continues_under_live_countdown_policy = True
        reason = 'universal_countdown_policy_runs_only_the_usable_wait_window_and_holds_the_last_ticks_as_dead_reserve'
    else:
        dead_reserve_ticks = int(minimum_timeout_ticks) - 1 if minimum_timeout_ticks is not None else None
        usable_wait_window_ticks = 0
        reoptimized_value = Fraction(0, 1)
        minimum_horizon_to_preserve_original_margin = 2 * int(minimum_timeout_ticks) - 1 if minimum_timeout_ticks is not None else None
        continues_under_live_countdown_policy = False
        reason = 'universal_countdown_policy_closes_immediately_because_remaining_horizon_does_not_reach_a_finite_viable_threshold'

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
        'dead_reserve_ticks_under_live_countdown_policy': dead_reserve_ticks,
        'usable_wait_window_ticks_under_live_countdown_policy': usable_wait_window_ticks,
        'blind_commit_value_bits_per_script': _serialize_fraction(blind_commit_value),
        'live_countdown_policy_value_bits_per_script': _serialize_fraction(reoptimized_value),
        'live_countdown_policy_continues': continues_under_live_countdown_policy,
        'blind_commit_meets_original_margin_floor': blind_commit_value >= target_margin,
        'live_countdown_policy_meets_original_margin_floor': reoptimized_value >= target_margin,
        'minimum_remaining_horizon_ticks_to_preserve_original_margin_under_live_countdown': minimum_horizon_to_preserve_original_margin,
        'blind_commit_threshold_formula': 'blind commit meets margin iff H >= K',
        'live_countdown_value_formula': 'live countdown value equals fixed-timeout value with usable window max(H - K + 1, 0)',
        'margin_preservation_formula': 'live countdown preserves original margin iff H >= 2K - 1 for finite schedules',
        'reason': reason,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_countdown_reserve_validation_summary() -> dict[str, Any]:
    validated_state_panels = 0
    validated_universal_panels = 0
    state_live_continue_panels = 0
    state_live_close_panels = 0
    universal_live_continue_panels = 0
    universal_live_close_panels = 0
    state_live_margin_preserved_panels = 0
    state_live_margin_drift_panels = 0
    universal_live_margin_preserved_panels = 0
    universal_live_margin_drift_panels = 0
    finite_state_schedules = 0
    asymptotic_only_state_schedules = 0
    impossible_state_schedules = 0
    finite_universal_schedules = 0
    asymptotic_only_universal_schedules = 0
    impossible_universal_schedules = 0

    universal_schedule_counted: set[tuple[int, Fraction, Fraction, Fraction]] = set()

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    gain = Fraction(_state_prefix_bits(state), current_batch_length * (current_batch_length + 1))
                    for target_margin in TARGET_MARGIN_GRID:
                        schedule = compute_minimum_timeout_for_state_batch_target_margin(
                            state,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        minimum_timeout_ticks = schedule['minimum_timeout_ticks']
                        if bool(schedule['finite_timeout_exists']):
                            finite_state_schedules += 1
                        elif bool(schedule['asymptotically_feasible']):
                            asymptotic_only_state_schedules += 1
                        else:
                            impossible_state_schedules += 1

                        ukey = (current_batch_length, arrival_probability, hold_cost, target_margin)
                        if ukey not in universal_schedule_counted:
                            universal_schedule_counted.add(ukey)
                            uschedule = compute_universal_minimum_timeout_for_batch_target_margin(
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                            )
                            if bool(uschedule['finite_timeout_exists']):
                                finite_universal_schedules += 1
                            elif bool(uschedule['asymptotically_feasible']):
                                asymptotic_only_universal_schedules += 1
                            else:
                                impossible_universal_schedules += 1

                        for remaining_horizon_ticks in REMAINING_HORIZON_GRID:
                            profile = evaluate_state_countdown_reserve_profile(
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
                            blind_commit_value = _deserialize_fraction(profile['blind_commit_value_bits_per_script'])
                            live_value = _deserialize_fraction(profile['live_countdown_policy_value_bits_per_script'])
                            if blind_commit_value is None or live_value is None:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                    'state countdown reserve profile omitted exact values'
                                )
                            continues = bool(profile['live_countdown_policy_continues'])
                            if continues:
                                state_live_continue_panels += 1
                            else:
                                state_live_close_panels += 1

                            expected_blind = _fixed_timeout_value_for_state(
                                state,
                                current_batch_length,
                                arrival_probability,
                                hold_cost,
                                remaining_horizon_ticks,
                            )
                            if blind_commit_value != expected_blind:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                    f'state blind-commit mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                )

                            if minimum_timeout_ticks is not None and remaining_horizon_ticks >= int(minimum_timeout_ticks):
                                usable_wait_window_ticks = remaining_horizon_ticks - int(minimum_timeout_ticks) + 1
                                expected_live = _fixed_timeout_value_for_state(
                                    state,
                                    current_batch_length,
                                    arrival_probability,
                                    hold_cost,
                                    usable_wait_window_ticks,
                                )
                                recursive_live = _countdown_reoptimized_value_by_recursion(
                                    _state_prefix_bits(state),
                                    current_batch_length,
                                    arrival_probability,
                                    hold_cost,
                                    int(minimum_timeout_ticks),
                                    remaining_horizon_ticks,
                                )
                                if live_value != expected_live or live_value != recursive_live:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                        f'state live countdown mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )
                                if profile['usable_wait_window_ticks_under_live_countdown_policy'] != usable_wait_window_ticks:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                        f'state usable-window mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )
                                expected_preservation = remaining_horizon_ticks >= 2 * int(minimum_timeout_ticks) - 1
                                if bool(profile['live_countdown_policy_meets_original_margin_floor']) != expected_preservation:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                        f'state margin-preservation threshold mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )
                            else:
                                if live_value != 0:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                        f'state live countdown should be zero for non-continuation case state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )

                            if bool(profile['live_countdown_policy_meets_original_margin_floor']):
                                state_live_margin_preserved_panels += 1
                            elif continues:
                                state_live_margin_drift_panels += 1

                            validated_state_panels += 1

                            if state == STATE_GRID[0]:
                                uprofile = evaluate_universal_countdown_reserve_profile(
                                    current_batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    remaining_horizon_ticks,
                                )
                                ublind = _deserialize_fraction(uprofile['blind_commit_value_bits_per_script'])
                                ulive = _deserialize_fraction(uprofile['live_countdown_policy_value_bits_per_script'])
                                if ublind is None or ulive is None:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                        'universal countdown reserve profile omitted exact values'
                                    )
                                ucontinues = bool(uprofile['live_countdown_policy_continues'])
                                if ucontinues:
                                    universal_live_continue_panels += 1
                                else:
                                    universal_live_close_panels += 1
                                expected_ublind = _fixed_timeout_value_for_universal(
                                    current_batch_length,
                                    arrival_probability,
                                    hold_cost,
                                    remaining_horizon_ticks,
                                )
                                if ublind != expected_ublind:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                        f'universal blind-commit mismatch for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                    )
                                umin = uprofile['minimum_timeout_ticks_for_blind_commit_margin']
                                if umin is not None and remaining_horizon_ticks >= int(umin):
                                    uusable = remaining_horizon_ticks - int(umin) + 1
                                    expected_ulive = _fixed_timeout_value_for_universal(
                                        current_batch_length,
                                        arrival_probability,
                                        hold_cost,
                                        uusable,
                                    )
                                    recursive_ulive = _countdown_reoptimized_value_by_recursion(
                                        7,
                                        current_batch_length,
                                        arrival_probability,
                                        hold_cost,
                                        int(umin),
                                        remaining_horizon_ticks,
                                    )
                                    if ulive != expected_ulive or ulive != recursive_ulive:
                                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                            f'universal live countdown mismatch for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                        )
                                    uexpected_preservation = remaining_horizon_ticks >= 2 * int(umin) - 1
                                    if bool(uprofile['live_countdown_policy_meets_original_margin_floor']) != uexpected_preservation:
                                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                            f'universal margin-preservation threshold mismatch for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                        )
                                else:
                                    if ulive != 0:
                                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
                                            f'universal live countdown should be zero for non-continuation case n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={remaining_horizon_ticks}'
                                        )

                                if bool(uprofile['live_countdown_policy_meets_original_margin_floor']):
                                    universal_live_margin_preserved_panels += 1
                                elif ucontinues:
                                    universal_live_margin_drift_panels += 1
                                validated_universal_panels += 1

    return {
        'audited_state_count': len(STATE_GRID),
        'audited_remaining_horizon_ticks': list(REMAINING_HORIZON_GRID),
        'validated_state_panels': validated_state_panels,
        'validated_universal_panels': validated_universal_panels,
        'state_live_continue_panels': state_live_continue_panels,
        'state_live_close_panels': state_live_close_panels,
        'universal_live_continue_panels': universal_live_continue_panels,
        'universal_live_close_panels': universal_live_close_panels,
        'state_live_margin_preserved_panels': state_live_margin_preserved_panels,
        'state_live_margin_drift_panels': state_live_margin_drift_panels,
        'universal_live_margin_preserved_panels': universal_live_margin_preserved_panels,
        'universal_live_margin_drift_panels': universal_live_margin_drift_panels,
        'finite_state_schedules': finite_state_schedules,
        'asymptotic_only_state_schedules': asymptotic_only_state_schedules,
        'impossible_state_schedules': impossible_state_schedules,
        'finite_universal_schedules': finite_universal_schedules,
        'asymptotic_only_universal_schedules': asymptotic_only_universal_schedules,
        'impossible_universal_schedules': impossible_universal_schedules,
    }


@lru_cache(maxsize=None)
def _find_first_state_case(*, requires_finite: bool, requires_drift: bool) -> dict[str, Any]:
    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        schedule = compute_minimum_timeout_for_state_batch_target_margin(
                            state,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        finite = bool(schedule['finite_timeout_exists'])
                        if requires_finite and not finite:
                            continue
                        for remaining_horizon_ticks in REMAINING_HORIZON_GRID:
                            profile = evaluate_state_countdown_reserve_profile(
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
                            drift = bool(profile['live_countdown_policy_continues']) and not bool(profile['live_countdown_policy_meets_original_margin_floor'])
                            if drift != requires_drift:
                                continue
                            return {
                                'state': state,
                                'batch_length': current_batch_length,
                                'arrival_probability': arrival_probability,
                                'hold_cost': hold_cost,
                                'target_margin': target_margin,
                                'remaining_horizon_ticks': remaining_horizon_ticks,
                                'profile': profile,
                            }
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
        f'could not find state case with requires_finite={requires_finite}, requires_drift={requires_drift}'
    )


@lru_cache(maxsize=None)
def _find_first_universal_case(*, requires_finite: bool, requires_drift: bool) -> dict[str, Any]:
    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    schedule = compute_universal_minimum_timeout_for_batch_target_margin(
                        current_batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    finite = bool(schedule['finite_timeout_exists'])
                    if requires_finite and not finite:
                        continue
                    for remaining_horizon_ticks in REMAINING_HORIZON_GRID:
                        profile = evaluate_universal_countdown_reserve_profile(
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            remaining_horizon_ticks,
                        )
                        drift = bool(profile['live_countdown_policy_continues']) and not bool(profile['live_countdown_policy_meets_original_margin_floor'])
                        if drift != requires_drift:
                            continue
                        return {
                            'batch_length': current_batch_length,
                            'arrival_probability': arrival_probability,
                            'hold_cost': hold_cost,
                            'target_margin': target_margin,
                            'remaining_horizon_ticks': remaining_horizon_ticks,
                            'profile': profile,
                        }
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalCountdownReserveLawError(
        f'could not find universal case with requires_finite={requires_finite}, requires_drift={requires_drift}'
    )


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_countdown_reserve_validation_summary()
    state_preserved = _find_first_state_case(requires_finite=True, requires_drift=False)
    state_drift = _find_first_state_case(requires_finite=True, requires_drift=True)
    universal_preserved = _find_first_universal_case(requires_finite=True, requires_drift=False)
    universal_drift = _find_first_universal_case(requires_finite=True, requires_drift=True)

    return {
        'focus': 'live geometric-arrival countdown control preserves a dead reserve and exposes only a shorter usable wait window under repeated checkpoint reoptimization',
        'headline_findings': {
            'state_live_countdown_value_equals_fixed_timeout_with_usable_window': 'max(H - K + 1, 0)',
            'state_margin_preservation_threshold_under_live_countdown': 'H >= 2K - 1',
            'universal_live_countdown_value_equals_fixed_timeout_with_usable_window': 'max(H - K + 1, 0)',
            'universal_margin_preservation_threshold_under_live_countdown': 'H >= 2K - 1',
            'state_live_margin_drift_panels': summary['state_live_margin_drift_panels'],
            'universal_live_margin_drift_panels': summary['universal_live_margin_drift_panels'],
        },
        'decision_rules': [
            'A blind commit of all remaining H ticks meets the original margin floor exactly when H reaches the previously computed minimum timeout K.',
            'A live countdown policy that rechecks after every miss has actual value equal to the fixed-timeout value of only the usable window max(H - K + 1, 0).',
            'Therefore the last K - 1 ticks act as a dead reserve under live reoptimization, not as economically usable service time.',
            'To preserve the original margin promise even under live reoptimization, require H >= 2K - 1 rather than only H >= K.',
        ],
        'state_preserved_example': state_preserved['profile'],
        'state_drift_example': state_drift['profile'],
        'universal_preserved_example': universal_preserved['profile'],
        'universal_drift_example': universal_drift['profile'],
        'validation_summary': summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
