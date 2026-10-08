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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law import (
    evaluate_checkpoint_extension_value_for_state,
    evaluate_universal_checkpoint_extension_value,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law import (
    compute_minimum_timeout_for_state_batch_target_margin,
    compute_universal_minimum_timeout_for_batch_target_margin,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law import (
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
ELAPSED_GRID = (0, 1, 5)
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


def _classify_schedule(schedule: dict[str, Any]) -> str:
    if bool(schedule['finite_timeout_exists']):
        return 'finite'
    if bool(schedule['asymptotically_feasible']):
        return 'asymptotic_only'
    return 'impossible'


@lru_cache(maxsize=None)
def evaluate_checkpoint_remaining_horizon_decision_for_state(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    elapsed_no_arrival_ticks: int,
    remaining_horizon_ticks: int,
) -> dict[str, Any]:
    if remaining_horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
            'remaining horizon ticks must be positive'
        )

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
    checkpoint_value = evaluate_checkpoint_extension_value_for_state(
        state,
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        elapsed_no_arrival_ticks,
        remaining_horizon_ticks,
    )
    expected_net = _deserialize_fraction(
        checkpoint_value['conditional_expected_net_extension_value_bits_per_script']
    )
    if expected_net is None:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
            'checkpoint extension result unexpectedly omitted net value'
        )

    minimum_remaining_horizon_ticks = schedule['minimum_timeout_ticks']
    schedule_class = _classify_schedule(schedule)
    if schedule_class == 'finite':
        assert minimum_remaining_horizon_ticks is not None
        threshold_decision = int(remaining_horizon_ticks) >= int(minimum_remaining_horizon_ticks)
        decision_reason = (
            'remaining_horizon_meets_precomputed_minimum_timeout_threshold'
            if threshold_decision
            else 'remaining_horizon_falls_short_of_precomputed_minimum_timeout_threshold'
        )
    elif schedule_class == 'asymptotic_only':
        threshold_decision = False
        decision_reason = 'target_margin_sits_on_the_asymptotic_boundary_and_no_finite_remaining_horizon_suffices'
    else:
        threshold_decision = False
        decision_reason = 'target_margin_exceeds_checkpoint_feasible_value_under_current_state_batch_economics'

    exact_decision = expected_net >= target_margin

    return {
        'state': list(state),
        'state_prefix_bits': _state_prefix_bits(state),
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': schedule['arrival_probability_per_tick'],
        'hold_cost_bits_per_script_per_tick': schedule['hold_cost_bits_per_script_per_tick'],
        'target_margin_bits_per_script': schedule['target_margin_bits_per_script'],
        'elapsed_no_arrival_ticks': int(elapsed_no_arrival_ticks),
        'remaining_horizon_ticks': int(remaining_horizon_ticks),
        'minimum_remaining_horizon_ticks_for_target_margin': minimum_remaining_horizon_ticks,
        'schedule_class': schedule_class,
        'checkpoint_expected_net_value_bits_per_script': _serialize_fraction(expected_net),
        'checkpoint_meets_target_margin_exactly': exact_decision,
        'should_continue_from_remaining_horizon_threshold': threshold_decision,
        'countdown_formula': 'continue iff (1 - (1 - p)^H) * (state_prefix_bits / (n(n+1)) - hold_cost / p) >= target_margin when p > 0',
        'minimum_horizon_formula': 'same as the minimum timeout law because elapsed miss streak does not change checkpoint value',
        'elapsed_no_arrival_streak_changes_threshold': False,
        'reason': decision_reason,
    }


@lru_cache(maxsize=None)
def evaluate_universal_checkpoint_remaining_horizon_decision(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    elapsed_no_arrival_ticks: int,
    remaining_horizon_ticks: int,
) -> dict[str, Any]:
    if remaining_horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
            'remaining horizon ticks must be positive'
        )

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
    checkpoint_value = evaluate_universal_checkpoint_extension_value(
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        elapsed_no_arrival_ticks,
        remaining_horizon_ticks,
    )
    expected_net = _deserialize_fraction(
        checkpoint_value['conditional_expected_net_extension_value_bits_per_script']
    )
    if expected_net is None:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
            'universal checkpoint extension result unexpectedly omitted net value'
        )

    minimum_remaining_horizon_ticks = schedule['minimum_timeout_ticks']
    schedule_class = _classify_schedule(schedule)
    if schedule_class == 'finite':
        assert minimum_remaining_horizon_ticks is not None
        threshold_decision = int(remaining_horizon_ticks) >= int(minimum_remaining_horizon_ticks)
        decision_reason = (
            'remaining_horizon_meets_universal_minimum_timeout_threshold'
            if threshold_decision
            else 'remaining_horizon_falls_short_of_universal_minimum_timeout_threshold'
        )
    elif schedule_class == 'asymptotic_only':
        threshold_decision = False
        decision_reason = 'universal_target_margin_sits_on_the_asymptotic_boundary_and_no_finite_remaining_horizon_suffices'
    else:
        threshold_decision = False
        decision_reason = 'universal_target_margin_exceeds_checkpoint_feasible_value_under_current_batch_economics'

    exact_decision = expected_net >= target_margin

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': schedule['arrival_probability_per_tick'],
        'hold_cost_bits_per_script_per_tick': schedule['hold_cost_bits_per_script_per_tick'],
        'target_margin_bits_per_script': schedule['target_margin_bits_per_script'],
        'elapsed_no_arrival_ticks': int(elapsed_no_arrival_ticks),
        'remaining_horizon_ticks': int(remaining_horizon_ticks),
        'minimum_remaining_horizon_ticks_for_target_margin': minimum_remaining_horizon_ticks,
        'schedule_class': schedule_class,
        'checkpoint_expected_net_value_bits_per_script': _serialize_fraction(expected_net),
        'checkpoint_meets_target_margin_exactly': exact_decision,
        'should_continue_from_remaining_horizon_threshold': threshold_decision,
        'countdown_formula': 'continue iff (1 - (1 - p)^H) * (7 / (n(n+1)) - hold_cost / p) >= target_margin when p > 0',
        'minimum_horizon_formula': 'same as the universal minimum timeout law because elapsed miss streak does not change checkpoint value',
        'elapsed_no_arrival_streak_changes_threshold': False,
        'reason': decision_reason,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_deadline_countdown_validation_summary() -> dict[str, Any]:
    validated_state_checkpoint_margin_panels = 0
    validated_universal_checkpoint_margin_panels = 0
    continue_state_panels = 0
    close_state_panels = 0
    continue_universal_panels = 0
    close_universal_panels = 0
    finite_state_schedules = 0
    asymptotic_only_state_schedules = 0
    impossible_state_schedules = 0
    finite_universal_schedules = 0
    asymptotic_only_universal_schedules = 0
    impossible_universal_schedules = 0
    visible_state_frontiers = 0
    visible_universal_frontiers = 0
    strict_state_horizon_growth_ladders = 0
    strict_universal_horizon_growth_ladders = 0

    universal_schedule_cache: dict[tuple[int, Fraction, Fraction, Fraction], dict[str, Any]] = {}
    universal_net_cache: dict[tuple[int, Fraction, Fraction, int, int], Fraction] = {}

    for batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for elapsed in ELAPSED_GRID:
                    for remaining_horizon in REMAINING_HORIZON_GRID:
                        universal_profile = evaluate_universal_checkpoint_extension_value(
                            batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            elapsed,
                            remaining_horizon,
                        )
                        universal_net_cache[(batch_length, arrival_probability, hold_cost, elapsed, remaining_horizon)] = _deserialize_fraction(
                            universal_profile['conditional_expected_net_extension_value_bits_per_script']
                        )

    for state in STATE_GRID:
        for batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    baseline_state_nets: dict[int, Fraction] = {}
                    for remaining_horizon in REMAINING_HORIZON_GRID:
                        profile = evaluate_checkpoint_extension_value_for_state(
                            state,
                            batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            ELAPSED_GRID[0],
                            remaining_horizon,
                        )
                        baseline_state_nets[remaining_horizon] = _deserialize_fraction(
                            profile['conditional_expected_net_extension_value_bits_per_script']
                        )

                    for elapsed in ELAPSED_GRID[1:]:
                        for remaining_horizon in REMAINING_HORIZON_GRID:
                            profile = evaluate_checkpoint_extension_value_for_state(
                                state,
                                batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                elapsed,
                                remaining_horizon,
                            )
                            elapsed_net = _deserialize_fraction(profile['conditional_expected_net_extension_value_bits_per_script'])
                            if elapsed_net != baseline_state_nets[remaining_horizon]:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
                                    f'state checkpoint net changed across elapsed streaks for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, H={remaining_horizon}'
                                )

                    state_continue_by_horizon: dict[Fraction, list[bool]] = {}
                    universal_continue_by_horizon: dict[Fraction, list[bool]] = {}

                    for target_margin in TARGET_MARGIN_GRID:
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
                        schedule_class = _classify_schedule(schedule)
                        if schedule_class == 'finite':
                            finite_state_schedules += 1
                            minimum_horizon = int(schedule['minimum_timeout_ticks'])
                            if minimum_horizon in REMAINING_HORIZON_GRID:
                                visible_state_frontiers += 1
                        elif schedule_class == 'asymptotic_only':
                            asymptotic_only_state_schedules += 1
                            minimum_horizon = None
                        else:
                            impossible_state_schedules += 1
                            minimum_horizon = None

                        state_continue_ladder: list[bool] = []
                        universal_continue_ladder: list[bool] = []

                        ukey = (batch_length, arrival_probability, hold_cost, target_margin)
                        if ukey not in universal_schedule_cache:
                            universal_schedule_cache[ukey] = compute_universal_minimum_timeout_for_batch_target_margin(
                                batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                            )
                        universal_schedule = universal_schedule_cache[ukey]
                        universal_schedule_class = _classify_schedule(universal_schedule)
                        if state == STATE_GRID[0]:
                            if universal_schedule_class == 'finite':
                                finite_universal_schedules += 1
                                universal_minimum_horizon = int(universal_schedule['minimum_timeout_ticks'])
                                if universal_minimum_horizon in REMAINING_HORIZON_GRID:
                                    visible_universal_frontiers += 1
                            elif universal_schedule_class == 'asymptotic_only':
                                asymptotic_only_universal_schedules += 1
                            else:
                                impossible_universal_schedules += 1

                        universal_minimum_horizon = (
                            int(universal_schedule['minimum_timeout_ticks']) if universal_schedule['minimum_timeout_ticks'] is not None else None
                        )
                        for elapsed in ELAPSED_GRID:
                            for remaining_horizon in REMAINING_HORIZON_GRID:
                                state_net = baseline_state_nets[remaining_horizon]
                                state_exact_decision = state_net >= target_margin
                                expected_from_threshold = (
                                    schedule_class == 'finite' and minimum_horizon is not None and remaining_horizon >= minimum_horizon
                                )
                                if state_exact_decision != expected_from_threshold:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
                                        f'state exact net and threshold law disagree for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, elapsed={elapsed}, H={remaining_horizon}'
                                    )
                                if state_exact_decision:
                                    continue_state_panels += 1
                                else:
                                    close_state_panels += 1
                                validated_state_checkpoint_margin_panels += 1
                                if elapsed == ELAPSED_GRID[0]:
                                    state_continue_ladder.append(state_exact_decision)

                                universal_net = universal_net_cache[(batch_length, arrival_probability, hold_cost, elapsed, remaining_horizon)]
                                universal_exact_decision = universal_net >= target_margin
                                universal_expected_from_threshold = (
                                    universal_schedule_class == 'finite'
                                    and universal_minimum_horizon is not None
                                    and remaining_horizon >= universal_minimum_horizon
                                )
                                if universal_exact_decision != universal_expected_from_threshold:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
                                        f'universal exact net and threshold law disagree for n={batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, elapsed={elapsed}, H={remaining_horizon}'
                                    )
                                if universal_exact_decision and not state_exact_decision:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
                                        f'universal countdown continued while exact state closed for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, elapsed={elapsed}, H={remaining_horizon}'
                                    )
                                if state == STATE_GRID[0]:
                                    if universal_exact_decision:
                                        continue_universal_panels += 1
                                    else:
                                        close_universal_panels += 1
                                    validated_universal_checkpoint_margin_panels += 1
                                    if elapsed == ELAPSED_GRID[0]:
                                        universal_continue_ladder.append(universal_exact_decision)

                        state_continue_by_horizon[target_margin] = state_continue_ladder
                        if state == STATE_GRID[0]:
                            universal_continue_by_horizon[target_margin] = universal_continue_ladder

                    if any(any(current and not nxt for current, nxt in zip(ladder[:-1], ladder[1:])) for ladder in state_continue_by_horizon.values()):
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
                            f'state continuation ladder moved downward with more remaining horizon for state {state}, n={batch_length}, p={arrival_probability}, c={hold_cost}'
                        )
                    if any(any((not current) and nxt for current, nxt in zip(ladder[:-1], ladder[1:])) for ladder in state_continue_by_horizon.values()):
                        strict_state_horizon_growth_ladders += 1

                    if state == STATE_GRID[0]:
                        if any(any(current and not nxt for current, nxt in zip(ladder[:-1], ladder[1:])) for ladder in universal_continue_by_horizon.values()):
                            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
                                f'universal continuation ladder moved downward with more remaining horizon for n={batch_length}, p={arrival_probability}, c={hold_cost}'
                            )
                        if any(any((not current) and nxt for current, nxt in zip(ladder[:-1], ladder[1:])) for ladder in universal_continue_by_horizon.values()):
                            strict_universal_horizon_growth_ladders += 1

    return {
        'audited_state_count': len(STATE_GRID),
        'audited_elapsed_no_arrival_ticks': list(ELAPSED_GRID),
        'audited_remaining_horizon_ticks': list(REMAINING_HORIZON_GRID),
        'validated_state_checkpoint_margin_panels': validated_state_checkpoint_margin_panels,
        'validated_universal_checkpoint_margin_panels': validated_universal_checkpoint_margin_panels,
        'continue_state_panels': continue_state_panels,
        'close_state_panels': close_state_panels,
        'continue_universal_panels': continue_universal_panels,
        'close_universal_panels': close_universal_panels,
        'finite_state_schedules': finite_state_schedules,
        'asymptotic_only_state_schedules': asymptotic_only_state_schedules,
        'impossible_state_schedules': impossible_state_schedules,
        'finite_universal_schedules': finite_universal_schedules,
        'asymptotic_only_universal_schedules': asymptotic_only_universal_schedules,
        'impossible_universal_schedules': impossible_universal_schedules,
        'visible_state_frontiers_within_audited_horizon_grid': visible_state_frontiers,
        'visible_universal_frontiers_within_audited_horizon_grid': visible_universal_frontiers,
        'strict_state_horizon_growth_ladders': strict_state_horizon_growth_ladders,
        'strict_universal_horizon_growth_ladders': strict_universal_horizon_growth_ladders,
    }


@lru_cache(maxsize=None)
def _find_first_state_schedule_case(schedule_class: str) -> dict[str, Any]:
    for state in STATE_GRID:
        for batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
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
                        if _classify_schedule(schedule) == schedule_class:
                            return {
                                'state': state,
                                'batch_length': batch_length,
                                'arrival_probability': arrival_probability,
                                'hold_cost': hold_cost,
                                'target_margin': target_margin,
                                'schedule': schedule,
                            }
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
        f'could not find state schedule case for class {schedule_class}'
    )


@lru_cache(maxsize=None)
def _find_first_universal_schedule_case(schedule_class: str) -> dict[str, Any]:
    for batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    schedule = compute_universal_minimum_timeout_for_batch_target_margin(
                        batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    if _classify_schedule(schedule) == schedule_class:
                        return {
                            'batch_length': batch_length,
                            'arrival_probability': arrival_probability,
                            'hold_cost': hold_cost,
                            'target_margin': target_margin,
                            'schedule': schedule,
                        }
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
        f'could not find universal schedule case for class {schedule_class}'
    )




@lru_cache(maxsize=None)
def _find_first_state_finite_case_with_visible_threshold(minimum_threshold: int = 2) -> dict[str, Any]:
    minimum_threshold = int(minimum_threshold)
    for state in STATE_GRID:
        for batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
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
                        if _classify_schedule(schedule) != 'finite':
                            continue
                        minimum_horizon = schedule['minimum_timeout_ticks']
                        if minimum_horizon is None:
                            continue
                        minimum_horizon = int(minimum_horizon)
                        if minimum_threshold <= minimum_horizon <= max(REMAINING_HORIZON_GRID):
                            return {
                                'state': state,
                                'batch_length': batch_length,
                                'arrival_probability': arrival_probability,
                                'hold_cost': hold_cost,
                                'target_margin': target_margin,
                                'schedule': schedule,
                            }
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
        'could not find finite state case with a visible threshold above one tick'
    )


@lru_cache(maxsize=None)
def _find_first_universal_finite_case_with_visible_threshold(minimum_threshold: int = 2) -> dict[str, Any]:
    minimum_threshold = int(minimum_threshold)
    for batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    schedule = compute_universal_minimum_timeout_for_batch_target_margin(
                        batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    if _classify_schedule(schedule) != 'finite':
                        continue
                    minimum_horizon = schedule['minimum_timeout_ticks']
                    if minimum_horizon is None:
                        continue
                    minimum_horizon = int(minimum_horizon)
                    if minimum_threshold <= minimum_horizon <= max(REMAINING_HORIZON_GRID):
                        return {
                            'batch_length': batch_length,
                            'arrival_probability': arrival_probability,
                            'hold_cost': hold_cost,
                            'target_margin': target_margin,
                            'schedule': schedule,
                        }
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineCountdownLawError(
        'could not find finite universal case with a visible threshold above one tick'
    )


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_deadline_countdown_validation_summary()

    finite_state_case = _find_first_state_finite_case_with_visible_threshold(2)
    impossible_state_case = _find_first_state_schedule_case('impossible')
    asymptotic_state_case = _find_first_state_schedule_case('asymptotic_only')
    finite_universal_case = _find_first_universal_finite_case_with_visible_threshold(2)

    finite_state_rows = [
        evaluate_checkpoint_remaining_horizon_decision_for_state(
            finite_state_case['state'],
            finite_state_case['batch_length'],
            finite_state_case['arrival_probability'].numerator,
            finite_state_case['arrival_probability'].denominator,
            finite_state_case['hold_cost'].numerator,
            finite_state_case['hold_cost'].denominator,
            finite_state_case['target_margin'].numerator,
            finite_state_case['target_margin'].denominator,
            0,
            remaining_horizon,
        )
        for remaining_horizon in REMAINING_HORIZON_GRID
    ]
    finite_state_delayed_rows = [
        evaluate_checkpoint_remaining_horizon_decision_for_state(
            finite_state_case['state'],
            finite_state_case['batch_length'],
            finite_state_case['arrival_probability'].numerator,
            finite_state_case['arrival_probability'].denominator,
            finite_state_case['hold_cost'].numerator,
            finite_state_case['hold_cost'].denominator,
            finite_state_case['target_margin'].numerator,
            finite_state_case['target_margin'].denominator,
            5,
            remaining_horizon,
        )
        for remaining_horizon in REMAINING_HORIZON_GRID
    ]

    state_examples = []
    for label, case in (
        ('finite', finite_state_case),
        ('asymptotic_only', asymptotic_state_case),
        ('impossible', impossible_state_case),
    ):
        row = evaluate_checkpoint_remaining_horizon_decision_for_state(
            case['state'],
            case['batch_length'],
            case['arrival_probability'].numerator,
            case['arrival_probability'].denominator,
            case['hold_cost'].numerator,
            case['hold_cost'].denominator,
            case['target_margin'].numerator,
            case['target_margin'].denominator,
            0,
            3,
        )
        row['example_class'] = label
        state_examples.append(row)

    universal_examples = []
    for label, schedule_class in (('finite', 'finite'), ('impossible', 'impossible')):
        case = _find_first_universal_schedule_case(schedule_class)
        row = evaluate_universal_checkpoint_remaining_horizon_decision(
            case['batch_length'],
            case['arrival_probability'].numerator,
            case['arrival_probability'].denominator,
            case['hold_cost'].numerator,
            case['hold_cost'].denominator,
            case['target_margin'].numerator,
            case['target_margin'].denominator,
            0,
            3,
        )
        row['example_class'] = label
        universal_examples.append(row)

    finite_universal_ladder = [
        evaluate_universal_checkpoint_remaining_horizon_decision(
            finite_universal_case['batch_length'],
            finite_universal_case['arrival_probability'].numerator,
            finite_universal_case['arrival_probability'].denominator,
            finite_universal_case['hold_cost'].numerator,
            finite_universal_case['hold_cost'].denominator,
            finite_universal_case['target_margin'].numerator,
            finite_universal_case['target_margin'].denominator,
            5,
            remaining_horizon,
        )
        for remaining_horizon in REMAINING_HORIZON_GRID
    ]

    return {
        'focus': 'turn a live checkpointed geometric-arrival batch promise into one precomputed remaining-horizon countdown threshold instead of repeated miss-age re-evaluation',
        'headline_findings': {
            'state_countdown_rule': 'At any checkpoint, continue exactly while remaining_horizon_ticks stays at or above the precomputed minimum timeout required for the current batch promise.',
            'elapsed_streak_irrelevance': 'Elapsed no-arrival streak length never changes the threshold under the current geometric-arrival model.',
            'universal_guardrail': 'The all-state countdown uses the same rule with state_prefix_bits fixed to the seven-bit lower envelope.',
            'implementation_payoff': 'A writer can precompute one countdown threshold per batch promise and then only decrement remaining time; no per-miss economics loop is needed unless hazard, cost, or state changes.',
        },
        'decision_rules': [
            'For a fixed state, batch length n, arrival hazard p, hold cost c, and target realized margin m, continue from a checkpoint with H ticks remaining iff (1 - (1 - p)^H) * (state_prefix_bits / (n(n+1)) - c / p) >= m whenever p > 0.',
            'Equivalently, compute the same minimum timeout K from the earlier target-batch-timeout law and continue iff H >= K.',
            'If the schedule class is asymptotic-only, finite remaining horizon never suffices unless arrival is certain and the boundary has already collapsed to the finite class.',
            'If the schedule class is impossible, the batch promise should be rejected or downsized immediately rather than nursed through checkpoints.',
            'The universal all-state guardrail is the same countdown rule with state_prefix_bits = 7.',
        ],
        'state_examples': state_examples,
        'finite_state_countdown_ladder_elapsed_0': finite_state_rows,
        'finite_state_countdown_ladder_elapsed_5': finite_state_delayed_rows,
        'universal_examples': universal_examples,
        'finite_universal_countdown_ladder_elapsed_5': finite_universal_ladder,
        'validation_summary': validation_summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law_snapshot_20260316.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law_snapshot_20260316.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law.py',
    }


def main() -> int:
    snapshot = build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_snapshot()
    json.dump(snapshot, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
