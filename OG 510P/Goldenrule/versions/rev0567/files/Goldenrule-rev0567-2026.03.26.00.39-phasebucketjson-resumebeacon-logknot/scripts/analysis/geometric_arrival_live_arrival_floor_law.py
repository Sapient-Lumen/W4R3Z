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

from scripts.analysis.geometric_arrival_live_margin_ceiling_law import (
    compute_state_live_margin_ceiling,
    compute_universal_live_margin_ceiling,
)
from scripts.analysis.geometric_arrival_effective_horizon_law import (
    evaluate_state_effective_horizon_profile,
    evaluate_universal_effective_horizon_profile,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law import (
    _state_prefix_bits,
)


class GeometricArrivalLiveArrivalFloorLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (
    Fraction(1, 8),
    Fraction(1, 4),
    Fraction(3, 8),
    Fraction(1, 2),
    Fraction(5, 8),
    Fraction(3, 4),
    Fraction(7, 8),
    Fraction(1, 1),
)
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
NOMINAL_HORIZON_GRID = tuple(range(1, 9))
TARGET_MARGIN_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
BOUNDARY_EPSILON = Fraction(1, 1_000_000)


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _effective_horizon(nominal_horizon_ticks: int) -> int:
    return (nominal_horizon_ticks + 1) // 2


@lru_cache(maxsize=None)
def _raw_live_margin_value(
    prefix_bits: int,
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> Fraction:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    prefix_budget = Fraction(prefix_bits, current_batch_length * (current_batch_length + 1))
    capture_fraction = Fraction(1, 1) - (Fraction(1, 1) - p) ** effective_horizon_ticks
    return capture_fraction * (prefix_budget - hold_cost / p)


@lru_cache(maxsize=None)
def _raw_live_margin_derivative_decomposition(
    prefix_bits: int,
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    if p <= 0 or p > 1:
        raise GeometricArrivalLiveArrivalFloorLawError('arrival probability must lie in (0, 1] for derivative decomposition')
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    q = Fraction(1, 1) - p
    prefix_budget = Fraction(prefix_bits, current_batch_length * (current_batch_length + 1))

    prefix_term = effective_horizon_ticks * p * p * (q ** (effective_horizon_ticks - 1)) * prefix_budget
    hold_terms = [p * ((q ** i) - (q ** (effective_horizon_ticks - 1))) for i in range(effective_horizon_ticks - 1)]
    hold_term_total = hold_cost * sum(hold_terms, Fraction(0, 1))
    derivative_numerator = prefix_term + hold_term_total
    derivative = derivative_numerator / (p * p)

    return {
        'prefix_budget_bits_per_script': _serialize_fraction(prefix_budget),
        'effective_blind_horizon_ticks': effective_horizon_ticks,
        'derivative_numerator_over_p_squared': _serialize_fraction(derivative_numerator),
        'derivative_bits_per_script_per_tick_probability': _serialize_fraction(derivative),
        'prefix_term_over_p_squared': _serialize_fraction(prefix_term),
        'hold_term_components_over_p_squared': [_serialize_fraction(term) for term in hold_terms],
        'hold_term_total_over_p_squared': _serialize_fraction(hold_term_total),
        'derivative_nonnegative_certificate': (
            'p^2 * d/dp raw_live_margin = k * p^2 * (1-p)^(k-1) * prefix_budget '
            '+ hold_cost * p * sum_{i=0}^{k-2}((1-p)^i - (1-p)^(k-1)) >= 0'
        ),
    }


@lru_cache(maxsize=None)
def compute_state_live_arrival_floor_profile(
    state: tuple[int, int],
    current_batch_length: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    prefix_bits = _state_prefix_bits(state)
    prefix_budget = Fraction(prefix_bits, current_batch_length * (current_batch_length + 1))
    certain_arrival_full_capture_margin = prefix_budget - hold_cost
    one_tick_closed_form_floor: Fraction | None = None
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    if effective_horizon_ticks == 1 and prefix_budget > 0:
        one_tick_closed_form_floor = (hold_cost + target_margin) / prefix_budget

    ladder: list[dict[str, Any]] = []
    first_feasible_arrival: Fraction | None = None
    for p in ARRIVAL_GRID:
        ceiling_profile = compute_state_live_margin_ceiling(
            state,
            current_batch_length,
            p.numerator,
            p.denominator,
            hold_cost.numerator,
            hold_cost.denominator,
            nominal_horizon_ticks,
        )
        ceiling_payload = ceiling_profile['maximum_preservable_nonnegative_margin_bits_per_script']
        ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
        preserves = ceiling >= target_margin
        if preserves and first_feasible_arrival is None:
            first_feasible_arrival = p
        ladder.append(
            {
                'arrival_probability_per_tick': _serialize_fraction(p),
                'maximum_preservable_nonnegative_margin_bits_per_script': ceiling_payload,
                'preserves_target_margin': preserves,
            }
        )

    return {
        'state': list(state),
        'state_prefix_bits': prefix_bits,
        'current_batch_length': int(current_batch_length),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': effective_horizon_ticks,
        'state_prefix_budget_bits_per_script': _serialize_fraction(prefix_budget),
        'certain_arrival_full_capture_margin_bits_per_script': _serialize_fraction(certain_arrival_full_capture_margin),
        'positive_continuous_arrival_floor_exists': target_margin <= certain_arrival_full_capture_margin,
        'one_tick_closed_form_minimum_arrival_probability_per_tick': (
            _serialize_fraction(one_tick_closed_form_floor) if one_tick_closed_form_floor is not None else None
        ),
        'minimum_audited_feasible_arrival_probability_per_tick': (
            _serialize_fraction(first_feasible_arrival) if first_feasible_arrival is not None else None
        ),
        'arrival_threshold_rule': (
            'for fixed batch, cost, promise, and nominal live deadline, the raw positive branch '
            '(1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p) '
            'is nondecreasing in p, so positive same-deadline live promise admission is upward-closed in arrival hazard'
        ),
        'ladder': ladder,
    }


@lru_cache(maxsize=None)
def compute_universal_live_arrival_floor_profile(
    current_batch_length: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    prefix_budget = Fraction(7, current_batch_length * (current_batch_length + 1))
    certain_arrival_full_capture_margin = prefix_budget - hold_cost
    one_tick_closed_form_floor: Fraction | None = None
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    if effective_horizon_ticks == 1 and prefix_budget > 0:
        one_tick_closed_form_floor = (hold_cost + target_margin) / prefix_budget

    ladder: list[dict[str, Any]] = []
    first_feasible_arrival: Fraction | None = None
    for p in ARRIVAL_GRID:
        ceiling_profile = compute_universal_live_margin_ceiling(
            current_batch_length,
            p.numerator,
            p.denominator,
            hold_cost.numerator,
            hold_cost.denominator,
            nominal_horizon_ticks,
        )
        ceiling_payload = ceiling_profile['maximum_preservable_nonnegative_margin_bits_per_script']
        ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
        preserves = ceiling >= target_margin
        if preserves and first_feasible_arrival is None:
            first_feasible_arrival = p
        ladder.append(
            {
                'arrival_probability_per_tick': _serialize_fraction(p),
                'maximum_preservable_nonnegative_margin_bits_per_script': ceiling_payload,
                'preserves_target_margin': preserves,
            }
        )

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': effective_horizon_ticks,
        'guarantee_prefix_budget_bits_per_script': _serialize_fraction(prefix_budget),
        'certain_arrival_full_capture_margin_bits_per_script': _serialize_fraction(certain_arrival_full_capture_margin),
        'positive_continuous_arrival_floor_exists': target_margin <= certain_arrival_full_capture_margin,
        'one_tick_closed_form_minimum_arrival_probability_per_tick': (
            _serialize_fraction(one_tick_closed_form_floor) if one_tick_closed_form_floor is not None else None
        ),
        'minimum_audited_feasible_arrival_probability_per_tick': (
            _serialize_fraction(first_feasible_arrival) if first_feasible_arrival is not None else None
        ),
        'arrival_threshold_rule': (
            'for fixed universal batch, cost, promise, and nominal live deadline, the raw positive branch '
            '(1 - (1 - p)^floor((H + 1) / 2)) * (7 / (n(n + 1)) - hold_cost / p) '
            'is nondecreasing in p, so positive universal same-deadline live promise admission is upward-closed in arrival hazard'
        ),
        'ladder': ladder,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_arrival_floor_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    state_arrival_ladders = 0
    universal_arrival_ladders = 0
    state_single_crossing_ladders = 0
    universal_single_crossing_ladders = 0
    state_ladders_with_positive_growth = 0
    universal_ladders_with_positive_growth = 0
    state_continuous_floor_exists_contexts = 0
    state_impossible_contexts = 0
    universal_continuous_floor_exists_contexts = 0
    universal_impossible_contexts = 0
    state_one_tick_closed_form_checks = 0
    universal_one_tick_closed_form_checks = 0
    state_derivative_certificates = 0
    universal_derivative_certificates = 0

    state_positive_example: dict[str, Any] | None = None
    state_impossible_example: dict[str, Any] | None = None
    universal_positive_example: dict[str, Any] | None = None
    universal_impossible_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        prefix_bits = _state_prefix_bits(state)
        for current_batch_length in BATCH_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                        profile = compute_state_live_arrival_floor_profile(
                            state,
                            current_batch_length,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        validated_state_contexts += 1
                        state_arrival_ladders += 1
                        if bool(profile['positive_continuous_arrival_floor_exists']):
                            state_continuous_floor_exists_contexts += 1
                            if state_positive_example is None:
                                state_positive_example = profile
                        else:
                            state_impossible_contexts += 1
                            if state_impossible_example is None:
                                state_impossible_example = profile

                        prior_ceiling: Fraction | None = None
                        saw_preserving = False
                        saw_failure_after_preserving = False
                        saw_strict_growth = False
                        for rung in profile['ladder']:
                            p_payload = rung['arrival_probability_per_tick']
                            p = Fraction(int(p_payload['numerator']), int(p_payload['denominator']))
                            ceiling_payload = rung['maximum_preservable_nonnegative_margin_bits_per_script']
                            ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
                            preserves = bool(rung['preserves_target_margin'])

                            if prior_ceiling is not None:
                                if ceiling < prior_ceiling:
                                    raise GeometricArrivalLiveArrivalFloorLawError(
                                        f'state arrival ladder decreased for state {state}, n={current_batch_length}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                    )
                                if ceiling > prior_ceiling:
                                    saw_strict_growth = True
                            prior_ceiling = ceiling

                            if preserves:
                                saw_preserving = True
                            elif saw_preserving:
                                saw_failure_after_preserving = True

                            certificate = _raw_live_margin_derivative_decomposition(
                                prefix_bits,
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                nominal_horizon_ticks,
                            )
                            derivative_payload = certificate['derivative_bits_per_script_per_tick_probability']
                            derivative = Fraction(int(derivative_payload['numerator']), int(derivative_payload['denominator']))
                            if derivative < 0:
                                raise GeometricArrivalLiveArrivalFloorLawError(
                                    f'state derivative certificate went negative for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks}'
                                )
                            state_derivative_certificates += 1

                        if saw_failure_after_preserving:
                            raise GeometricArrivalLiveArrivalFloorLawError(
                                f'state positive promise admission was not upward-closed in arrival hazard for state {state}, n={current_batch_length}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                            )
                        state_single_crossing_ladders += 1
                        if saw_strict_growth:
                            state_ladders_with_positive_growth += 1

                        effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
                        if effective_horizon_ticks == 1:
                            prefix_budget = Fraction(prefix_bits, current_batch_length * (current_batch_length + 1))
                            if prefix_budget > 0:
                                closed_form_floor = (hold_cost + target_margin) / prefix_budget
                                one_tick_profile = profile['one_tick_closed_form_minimum_arrival_probability_per_tick']
                                if one_tick_profile is None:
                                    raise GeometricArrivalLiveArrivalFloorLawError(
                                        f'state one-tick closed-form floor missing for state {state}, n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                    )
                                recovered_floor = Fraction(
                                    int(one_tick_profile['numerator']),
                                    int(one_tick_profile['denominator']),
                                )
                                if recovered_floor != closed_form_floor:
                                    raise GeometricArrivalLiveArrivalFloorLawError(
                                        f'state one-tick closed-form floor mismatch for state {state}, n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                    )
                                if closed_form_floor <= 1:
                                    at_floor = evaluate_state_effective_horizon_profile(
                                        state,
                                        current_batch_length,
                                        closed_form_floor.numerator,
                                        closed_form_floor.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        target_margin.numerator,
                                        target_margin.denominator,
                                        nominal_horizon_ticks,
                                    )
                                    if not bool(at_floor['live_countdown_preserves_original_margin']):
                                        raise GeometricArrivalLiveArrivalFloorLawError(
                                            f'state one-tick closed-form floor failed at boundary for state {state}, n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                        )
                                    if closed_form_floor > 0:
                                        below_floor = closed_form_floor - BOUNDARY_EPSILON
                                        if below_floor > 0:
                                            below = evaluate_state_effective_horizon_profile(
                                                state,
                                                current_batch_length,
                                                below_floor.numerator,
                                                below_floor.denominator,
                                                hold_cost.numerator,
                                                hold_cost.denominator,
                                                target_margin.numerator,
                                                target_margin.denominator,
                                                nominal_horizon_ticks,
                                            )
                                            if bool(below['live_countdown_preserves_original_margin']):
                                                raise GeometricArrivalLiveArrivalFloorLawError(
                                                    f'state one-tick closed-form floor preserved below threshold for state {state}, n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                                )
                                state_one_tick_closed_form_checks += 1

    for current_batch_length in BATCH_GRID:
        for hold_cost in HOLD_COST_GRID:
            for target_margin in TARGET_MARGIN_GRID:
                for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                    profile = compute_universal_live_arrival_floor_profile(
                        current_batch_length,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                        nominal_horizon_ticks,
                    )
                    validated_universal_contexts += 1
                    universal_arrival_ladders += 1
                    if bool(profile['positive_continuous_arrival_floor_exists']):
                        universal_continuous_floor_exists_contexts += 1
                        if universal_positive_example is None:
                            universal_positive_example = profile
                    else:
                        universal_impossible_contexts += 1
                        if universal_impossible_example is None:
                            universal_impossible_example = profile

                    prior_ceiling: Fraction | None = None
                    saw_preserving = False
                    saw_failure_after_preserving = False
                    saw_strict_growth = False
                    for rung in profile['ladder']:
                        p_payload = rung['arrival_probability_per_tick']
                        p = Fraction(int(p_payload['numerator']), int(p_payload['denominator']))
                        ceiling_payload = rung['maximum_preservable_nonnegative_margin_bits_per_script']
                        ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
                        preserves = bool(rung['preserves_target_margin'])

                        if prior_ceiling is not None:
                            if ceiling < prior_ceiling:
                                raise GeometricArrivalLiveArrivalFloorLawError(
                                    f'universal arrival ladder decreased for n={current_batch_length}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )
                            if ceiling > prior_ceiling:
                                saw_strict_growth = True
                        prior_ceiling = ceiling

                        if preserves:
                            saw_preserving = True
                        elif saw_preserving:
                            saw_failure_after_preserving = True

                        certificate = _raw_live_margin_derivative_decomposition(
                            7,
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            nominal_horizon_ticks,
                        )
                        derivative_payload = certificate['derivative_bits_per_script_per_tick_probability']
                        derivative = Fraction(int(derivative_payload['numerator']), int(derivative_payload['denominator']))
                        if derivative < 0:
                            raise GeometricArrivalLiveArrivalFloorLawError(
                                f'universal derivative certificate went negative for n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks}'
                            )
                        universal_derivative_certificates += 1

                    if saw_failure_after_preserving:
                        raise GeometricArrivalLiveArrivalFloorLawError(
                            f'universal positive promise admission was not upward-closed in arrival hazard for n={current_batch_length}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                        )
                    universal_single_crossing_ladders += 1
                    if saw_strict_growth:
                        universal_ladders_with_positive_growth += 1

                    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
                    if effective_horizon_ticks == 1:
                        prefix_budget = Fraction(7, current_batch_length * (current_batch_length + 1))
                        if prefix_budget > 0:
                            closed_form_floor = (hold_cost + target_margin) / prefix_budget
                            one_tick_profile = profile['one_tick_closed_form_minimum_arrival_probability_per_tick']
                            if one_tick_profile is None:
                                raise GeometricArrivalLiveArrivalFloorLawError(
                                    f'universal one-tick closed-form floor missing for n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                )
                            recovered_floor = Fraction(
                                int(one_tick_profile['numerator']),
                                int(one_tick_profile['denominator']),
                            )
                            if recovered_floor != closed_form_floor:
                                raise GeometricArrivalLiveArrivalFloorLawError(
                                    f'universal one-tick closed-form floor mismatch for n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                )
                            if closed_form_floor <= 1:
                                at_floor = evaluate_universal_effective_horizon_profile(
                                    current_batch_length,
                                    closed_form_floor.numerator,
                                    closed_form_floor.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )
                                if not bool(at_floor['live_countdown_preserves_original_margin']):
                                    raise GeometricArrivalLiveArrivalFloorLawError(
                                        f'universal one-tick closed-form floor failed at boundary for n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                    )
                                if closed_form_floor > 0:
                                    below_floor = closed_form_floor - BOUNDARY_EPSILON
                                    if below_floor > 0:
                                        below = evaluate_universal_effective_horizon_profile(
                                            current_batch_length,
                                            below_floor.numerator,
                                            below_floor.denominator,
                                            hold_cost.numerator,
                                            hold_cost.denominator,
                                            target_margin.numerator,
                                            target_margin.denominator,
                                            nominal_horizon_ticks,
                                        )
                                        if bool(below['live_countdown_preserves_original_margin']):
                                            raise GeometricArrivalLiveArrivalFloorLawError(
                                                f'universal one-tick closed-form floor preserved below threshold for n={current_batch_length}, c={hold_cost}, m={target_margin}'
                                            )
                            universal_one_tick_closed_form_checks += 1

    if state_positive_example is None or state_impossible_example is None:
        raise GeometricArrivalLiveArrivalFloorLawError('failed to find both positive and impossible state examples')
    if universal_positive_example is None or universal_impossible_example is None:
        raise GeometricArrivalLiveArrivalFloorLawError('failed to find both positive and impossible universal examples')

    return {
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'state_arrival_ladders': state_arrival_ladders,
        'universal_arrival_ladders': universal_arrival_ladders,
        'state_single_crossing_ladders': state_single_crossing_ladders,
        'universal_single_crossing_ladders': universal_single_crossing_ladders,
        'state_ladders_with_positive_growth': state_ladders_with_positive_growth,
        'universal_ladders_with_positive_growth': universal_ladders_with_positive_growth,
        'state_continuous_floor_exists_contexts': state_continuous_floor_exists_contexts,
        'state_impossible_contexts': state_impossible_contexts,
        'universal_continuous_floor_exists_contexts': universal_continuous_floor_exists_contexts,
        'universal_impossible_contexts': universal_impossible_contexts,
        'state_one_tick_closed_form_checks': state_one_tick_closed_form_checks,
        'universal_one_tick_closed_form_checks': universal_one_tick_closed_form_checks,
        'state_derivative_certificates': state_derivative_certificates,
        'universal_derivative_certificates': universal_derivative_certificates,
        'state_positive_example': state_positive_example,
        'state_impossible_example': state_impossible_example,
        'universal_positive_example': universal_positive_example,
        'universal_impossible_example': universal_impossible_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_arrival_floor_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_live_arrival_floor_validation_summary()
    state_positive_example = validation_summary['state_positive_example']
    state_impossible_example = validation_summary['state_impossible_example']
    universal_positive_example = validation_summary['universal_positive_example']
    universal_impossible_example = validation_summary['universal_impossible_example']

    compact_validation_summary = {
        key: value
        for key, value in validation_summary.items()
        if key
        not in {
            'state_positive_example',
            'state_impossible_example',
            'universal_positive_example',
            'universal_impossible_example',
        }
    }

    return {
        'focus': 'same-deadline stateless live positive-promise admission is monotone in arrival hazard, so each fixed context has at most one positive arrival floor',
        'headline_findings': {
            'state_arrival_floor_rule': 'the raw positive live value branch is nondecreasing in p, so positive state promise admission is upward-closed in arrival hazard',
            'universal_arrival_floor_rule': 'the same monotonicity and upward-closed admission hold under the seven-bit universal guardrail',
            'one_tick_closed_form_rule': 'at effective horizon 1, the exact positive arrival floor is (hold_cost + margin_floor) / prefix_budget',
            'existence_rule': 'a positive continuous arrival floor exists iff certain-arrival full-capture value prefix_budget - hold_cost still covers the promised margin',
        },
        'decision_rules': [
            'Fix batch length, hold cost, promised margin, and nominal same-deadline live horizon H; then reduce to effective blind horizon floor((H + 1) / 2).',
            'Treat arrival hazard as a one-dimensional threshold variable: once the promise is safe at some p, it stays safe for all larger p.',
            'A positive continuous arrival floor exists exactly when full-capture certain-arrival value prefix_budget - hold_cost is at least the promised margin.',
            'At one effective tick, the exact positive arrival floor is (hold_cost + margin_floor) / prefix_budget; larger hazards remain safe and smaller hazards fail.',
        ],
        'state_positive_example': state_positive_example,
        'state_impossible_example': state_impossible_example,
        'universal_positive_example': universal_positive_example,
        'universal_impossible_example': universal_impossible_example,
        'validation_summary': compact_validation_summary,
        'source_reports': [
            'geometric_arrival_live_margin_ceiling_law_snapshot_20260316.json',
            'geometric_arrival_effective_horizon_law_snapshot_20260316.json',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_arrival_floor_law.py',
    }


def main() -> None:
    print(json.dumps(build_geometric_arrival_live_arrival_floor_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
