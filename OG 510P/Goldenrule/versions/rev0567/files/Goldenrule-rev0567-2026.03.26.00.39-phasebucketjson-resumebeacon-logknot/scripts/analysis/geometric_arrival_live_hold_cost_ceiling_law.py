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


class GeometricArrivalLiveHoldCostCeilingLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
POSITIVE_TARGET_MARGIN_GRID = TARGET_MARGIN_GRID[1:]
NOMINAL_HORIZON_GRID = tuple(range(1, 9))
BOUNDARY_EPSILON = Fraction(1, 1_000_000)
ZERO_MARGIN_SAMPLE_HOLD_COST = Fraction(1, 2)


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _effective_horizon(nominal_horizon_ticks: int) -> int:
    return (nominal_horizon_ticks + 1) // 2


def _capture_fraction(arrival_probability: Fraction, effective_horizon_ticks: int) -> Fraction:
    return Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** effective_horizon_ticks


@lru_cache(maxsize=None)
def compute_state_live_hold_cost_ceiling(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    m = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    state_prefix_bits = _state_prefix_bits(state)

    result: dict[str, Any] = {
        'state': list(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'target_margin_bits_per_script': _serialize_fraction(m),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'maximum_admissible_hold_cost_bits_per_script_per_tick': None,
        'unbounded_hold_cost_ceiling': False,
        'positive_margin_feasible': False,
        'effective_capture_fraction': None,
        'positive_live_hold_cost_ceiling_formula': (
            'for positive margin floors m > 0, same-deadline stateless live control is promise-safe iff '
            'hold_cost <= p * (state_prefix_bits / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2)))'
        ),
        'zero_margin_formula': 'at zero margin floor, immediate close is already safe, so the live hold-cost ceiling is unbounded',
    }

    if m == 0:
        result.update(
            {
                'unbounded_hold_cost_ceiling': True,
                'reason': 'zero_margin_floor_makes_immediate_close_safe_so_no_positive_hold_cost_ceiling_is_needed',
            }
        )
        return result

    capture_fraction = _capture_fraction(p, effective_horizon_ticks)
    ceiling = p * (Fraction(state_prefix_bits, current_batch_length * (current_batch_length + 1)) - m / capture_fraction)
    result.update(
        {
            'effective_capture_fraction': _serialize_fraction(capture_fraction),
            'maximum_admissible_hold_cost_bits_per_script_per_tick': _serialize_fraction(ceiling),
            'positive_margin_feasible': ceiling >= 0,
            'reason': (
                'positive_live_promise_is_feasible_up_to_the_exact_closed_form_hold_cost_ceiling'
                if ceiling >= 0
                else 'even_zero_hold_cost_cannot_preserve_the_positive_live_promise_at_this_nominal_deadline'
            ),
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_universal_live_hold_cost_ceiling(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    m = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)

    result: dict[str, Any] = {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'target_margin_bits_per_script': _serialize_fraction(m),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'maximum_admissible_hold_cost_bits_per_script_per_tick': None,
        'unbounded_hold_cost_ceiling': False,
        'positive_margin_feasible': False,
        'effective_capture_fraction': None,
        'positive_live_hold_cost_ceiling_formula': (
            'for positive universal margin floors m > 0, same-deadline stateless live control is promise-safe iff '
            'hold_cost <= p * (7 / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2)))'
        ),
        'zero_margin_formula': 'at zero universal margin floor, immediate close is already safe, so the live hold-cost ceiling is unbounded',
    }

    if m == 0:
        result.update(
            {
                'unbounded_hold_cost_ceiling': True,
                'reason': 'zero_universal_margin_floor_makes_immediate_close_safe_so_no_positive_hold_cost_ceiling_is_needed',
            }
        )
        return result

    capture_fraction = _capture_fraction(p, effective_horizon_ticks)
    ceiling = p * (Fraction(7, current_batch_length * (current_batch_length + 1)) - m / capture_fraction)
    result.update(
        {
            'effective_capture_fraction': _serialize_fraction(capture_fraction),
            'maximum_admissible_hold_cost_bits_per_script_per_tick': _serialize_fraction(ceiling),
            'positive_margin_feasible': ceiling >= 0,
            'reason': (
                'positive_universal_live_promise_is_feasible_up_to_the_exact_closed_form_hold_cost_ceiling'
                if ceiling >= 0
                else 'even_zero_hold_cost_cannot_preserve_the_positive_universal_live_promise_at_this_nominal_deadline'
            ),
        }
    )
    return result


@lru_cache(maxsize=1)
def build_geometric_arrival_live_hold_cost_ceiling_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    positive_state_feasible_contexts = 0
    positive_state_impossible_contexts = 0
    positive_universal_feasible_contexts = 0
    positive_universal_impossible_contexts = 0
    zero_margin_state_contexts = 0
    zero_margin_universal_contexts = 0
    validated_state_boundary_checks = 0
    validated_universal_boundary_checks = 0
    state_deadline_ladders = 0
    state_deadline_ladders_with_strict_odd_growth = 0
    universal_deadline_ladders = 0
    universal_deadline_ladders_with_strict_odd_growth = 0
    state_odd_even_pair_plateaus = 0
    universal_odd_even_pair_plateaus = 0

    state_zero_example: dict[str, Any] | None = None
    state_feasible_example: dict[str, Any] | None = None
    state_impossible_example: dict[str, Any] | None = None
    universal_zero_example: dict[str, Any] | None = None
    universal_feasible_example: dict[str, Any] | None = None
    universal_impossible_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for p in ARRIVAL_GRID:
                for m in TARGET_MARGIN_GRID:
                    ladder: list[Fraction | None] = []
                    saw_strict_odd_growth = False
                    prior_ceiling: Fraction | None = None
                    for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                        profile = compute_state_live_hold_cost_ceiling(
                            state,
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            m.numerator,
                            m.denominator,
                            nominal_horizon_ticks,
                        )
                        validated_state_contexts += 1

                        if m == 0:
                            zero_margin_state_contexts += 1
                            if not bool(profile['unbounded_hold_cost_ceiling']):
                                raise GeometricArrivalLiveHoldCostCeilingLawError('zero-margin state live hold-cost ceiling unexpectedly bounded')
                            actual = bool(
                                evaluate_state_effective_horizon_profile(
                                    state,
                                    current_batch_length,
                                    p.numerator,
                                    p.denominator,
                                    ZERO_MARGIN_SAMPLE_HOLD_COST.numerator,
                                    ZERO_MARGIN_SAMPLE_HOLD_COST.denominator,
                                    m.numerator,
                                    m.denominator,
                                    nominal_horizon_ticks,
                                )['live_countdown_preserves_original_margin']
                            )
                            if not actual:
                                raise GeometricArrivalLiveHoldCostCeilingLawError('zero-margin state live controller unexpectedly failed at sample hold cost')
                            if state_zero_example is None:
                                state_zero_example = {
                                    'hold_cost_ceiling_profile': profile,
                                    'sample_hold_cost_bits_per_script_per_tick': _serialize_fraction(ZERO_MARGIN_SAMPLE_HOLD_COST),
                                    'sample_live_profile': evaluate_state_effective_horizon_profile(
                                        state,
                                        current_batch_length,
                                        p.numerator,
                                        p.denominator,
                                        ZERO_MARGIN_SAMPLE_HOLD_COST.numerator,
                                        ZERO_MARGIN_SAMPLE_HOLD_COST.denominator,
                                        m.numerator,
                                        m.denominator,
                                        nominal_horizon_ticks,
                                    ),
                                }
                            continue

                        ceiling_payload = profile['maximum_admissible_hold_cost_bits_per_script_per_tick']
                        if ceiling_payload is None:
                            raise GeometricArrivalLiveHoldCostCeilingLawError('positive state hold-cost ceiling payload unexpectedly missing')
                        ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
                        ladder.append(ceiling)

                        if prior_ceiling is not None and ceiling < prior_ceiling:
                            raise GeometricArrivalLiveHoldCostCeilingLawError(
                                f'state hold-cost ceiling ladder decreased for state {state}, n={current_batch_length}, p={p}, m={m}'
                            )
                        if nominal_horizon_ticks % 2 == 0:
                            if prior_ceiling is None or ceiling != prior_ceiling:
                                raise GeometricArrivalLiveHoldCostCeilingLawError(
                                    f'state odd/even live hold-cost ceiling plateau failed for state {state}, n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                                )
                            state_odd_even_pair_plateaus += 1
                        elif nominal_horizon_ticks > 1 and p < 1:
                            if prior_ceiling is None or ceiling <= prior_ceiling:
                                raise GeometricArrivalLiveHoldCostCeilingLawError(
                                    f'state live hold-cost ceiling failed strict odd-step growth for state {state}, n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks-1}->{nominal_horizon_ticks}'
                                )
                            saw_strict_odd_growth = True

                        if ceiling >= 0:
                            positive_state_feasible_contexts += 1
                            at_boundary = evaluate_state_effective_horizon_profile(
                                state,
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                ceiling.numerator,
                                ceiling.denominator,
                                m.numerator,
                                m.denominator,
                                nominal_horizon_ticks,
                            )
                            if not bool(at_boundary['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveHoldCostCeilingLawError(
                                    f'state boundary hold cost unexpectedly failed for state {state}, n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks}'
                                )
                            above_boundary_cost = ceiling + BOUNDARY_EPSILON
                            above_boundary = evaluate_state_effective_horizon_profile(
                                state,
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                above_boundary_cost.numerator,
                                above_boundary_cost.denominator,
                                m.numerator,
                                m.denominator,
                                nominal_horizon_ticks,
                            )
                            if bool(above_boundary['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveHoldCostCeilingLawError(
                                    f'state above-boundary hold cost unexpectedly preserved for state {state}, n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks}'
                                )
                            validated_state_boundary_checks += 2
                            if state_feasible_example is None and ceiling > 0:
                                state_feasible_example = {
                                    'hold_cost_ceiling_profile': profile,
                                    'boundary_live_profile': at_boundary,
                                    'above_boundary_hold_cost_bits_per_script_per_tick': _serialize_fraction(above_boundary_cost),
                                    'above_boundary_live_profile': above_boundary,
                                }
                        else:
                            positive_state_impossible_contexts += 1
                            at_zero = evaluate_state_effective_horizon_profile(
                                state,
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                0,
                                1,
                                m.numerator,
                                m.denominator,
                                nominal_horizon_ticks,
                            )
                            if bool(at_zero['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveHoldCostCeilingLawError(
                                    f'impossible state context unexpectedly preserved at zero hold cost for state {state}, n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks}'
                                )
                            validated_state_boundary_checks += 1
                            if state_impossible_example is None:
                                state_impossible_example = {
                                    'hold_cost_ceiling_profile': profile,
                                    'zero_hold_cost_live_profile': at_zero,
                                }

                        prior_ceiling = ceiling

                    if m > 0:
                        state_deadline_ladders += 1
                        if p < 1 and saw_strict_odd_growth:
                            state_deadline_ladders_with_strict_odd_growth += 1

    for current_batch_length in BATCH_GRID:
        for p in ARRIVAL_GRID:
            for m in TARGET_MARGIN_GRID:
                prior_ceiling: Fraction | None = None
                saw_strict_odd_growth = False
                for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                    profile = compute_universal_live_hold_cost_ceiling(
                        current_batch_length,
                        p.numerator,
                        p.denominator,
                        m.numerator,
                        m.denominator,
                        nominal_horizon_ticks,
                    )
                    validated_universal_contexts += 1

                    if m == 0:
                        zero_margin_universal_contexts += 1
                        if not bool(profile['unbounded_hold_cost_ceiling']):
                            raise GeometricArrivalLiveHoldCostCeilingLawError('zero-margin universal live hold-cost ceiling unexpectedly bounded')
                        actual = bool(
                            evaluate_universal_effective_horizon_profile(
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                ZERO_MARGIN_SAMPLE_HOLD_COST.numerator,
                                ZERO_MARGIN_SAMPLE_HOLD_COST.denominator,
                                m.numerator,
                                m.denominator,
                                nominal_horizon_ticks,
                            )['live_countdown_preserves_original_margin']
                        )
                        if not actual:
                            raise GeometricArrivalLiveHoldCostCeilingLawError('zero-margin universal live controller unexpectedly failed at sample hold cost')
                        if universal_zero_example is None:
                            universal_zero_example = {
                                'hold_cost_ceiling_profile': profile,
                                'sample_hold_cost_bits_per_script_per_tick': _serialize_fraction(ZERO_MARGIN_SAMPLE_HOLD_COST),
                                'sample_live_profile': evaluate_universal_effective_horizon_profile(
                                    current_batch_length,
                                    p.numerator,
                                    p.denominator,
                                    ZERO_MARGIN_SAMPLE_HOLD_COST.numerator,
                                    ZERO_MARGIN_SAMPLE_HOLD_COST.denominator,
                                    m.numerator,
                                    m.denominator,
                                    nominal_horizon_ticks,
                                ),
                            }
                        continue

                    ceiling_payload = profile['maximum_admissible_hold_cost_bits_per_script_per_tick']
                    if ceiling_payload is None:
                        raise GeometricArrivalLiveHoldCostCeilingLawError('positive universal hold-cost ceiling payload unexpectedly missing')
                    ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))

                    if prior_ceiling is not None and ceiling < prior_ceiling:
                        raise GeometricArrivalLiveHoldCostCeilingLawError(
                            f'universal hold-cost ceiling ladder decreased for n={current_batch_length}, p={p}, m={m}'
                        )
                    if nominal_horizon_ticks % 2 == 0:
                        if prior_ceiling is None or ceiling != prior_ceiling:
                            raise GeometricArrivalLiveHoldCostCeilingLawError(
                                f'universal odd/even live hold-cost ceiling plateau failed for n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                            )
                        universal_odd_even_pair_plateaus += 1
                    elif nominal_horizon_ticks > 1 and p < 1:
                        if prior_ceiling is None or ceiling <= prior_ceiling:
                            raise GeometricArrivalLiveHoldCostCeilingLawError(
                                f'universal live hold-cost ceiling failed strict odd-step growth for n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks-1}->{nominal_horizon_ticks}'
                            )
                        saw_strict_odd_growth = True

                    if ceiling >= 0:
                        positive_universal_feasible_contexts += 1
                        at_boundary = evaluate_universal_effective_horizon_profile(
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            ceiling.numerator,
                            ceiling.denominator,
                            m.numerator,
                            m.denominator,
                            nominal_horizon_ticks,
                        )
                        if not bool(at_boundary['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveHoldCostCeilingLawError(
                                f'universal boundary hold cost unexpectedly failed for n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks}'
                            )
                        above_boundary_cost = ceiling + BOUNDARY_EPSILON
                        above_boundary = evaluate_universal_effective_horizon_profile(
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            above_boundary_cost.numerator,
                            above_boundary_cost.denominator,
                            m.numerator,
                            m.denominator,
                            nominal_horizon_ticks,
                        )
                        if bool(above_boundary['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveHoldCostCeilingLawError(
                                f'universal above-boundary hold cost unexpectedly preserved for n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks}'
                            )
                        validated_universal_boundary_checks += 2
                        if universal_feasible_example is None and ceiling > 0:
                            universal_feasible_example = {
                                'hold_cost_ceiling_profile': profile,
                                'boundary_live_profile': at_boundary,
                                'above_boundary_hold_cost_bits_per_script_per_tick': _serialize_fraction(above_boundary_cost),
                                'above_boundary_live_profile': above_boundary,
                            }
                    else:
                        positive_universal_impossible_contexts += 1
                        at_zero = evaluate_universal_effective_horizon_profile(
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            0,
                            1,
                            m.numerator,
                            m.denominator,
                            nominal_horizon_ticks,
                        )
                        if bool(at_zero['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveHoldCostCeilingLawError(
                                f'impossible universal context unexpectedly preserved at zero hold cost for n={current_batch_length}, p={p}, m={m}, H={nominal_horizon_ticks}'
                            )
                        validated_universal_boundary_checks += 1
                        if universal_impossible_example is None:
                            universal_impossible_example = {
                                'hold_cost_ceiling_profile': profile,
                                'zero_hold_cost_live_profile': at_zero,
                            }

                    prior_ceiling = ceiling

                if m > 0:
                    universal_deadline_ladders += 1
                    if p < 1 and saw_strict_odd_growth:
                        universal_deadline_ladders_with_strict_odd_growth += 1

    if state_zero_example is None or state_feasible_example is None or state_impossible_example is None:
        raise GeometricArrivalLiveHoldCostCeilingLawError('missing state witness example')
    if universal_zero_example is None or universal_feasible_example is None or universal_impossible_example is None:
        raise GeometricArrivalLiveHoldCostCeilingLawError('missing universal witness example')

    return {
        'audited_state_count': len(STATE_GRID),
        'audited_batch_lengths': list(BATCH_GRID),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in ARRIVAL_GRID],
        'audited_target_margins': [_serialize_fraction(value) for value in TARGET_MARGIN_GRID],
        'audited_nominal_live_deadlines': list(NOMINAL_HORIZON_GRID),
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'positive_state_feasible_contexts': positive_state_feasible_contexts,
        'positive_state_impossible_contexts': positive_state_impossible_contexts,
        'positive_universal_feasible_contexts': positive_universal_feasible_contexts,
        'positive_universal_impossible_contexts': positive_universal_impossible_contexts,
        'zero_margin_state_contexts': zero_margin_state_contexts,
        'zero_margin_universal_contexts': zero_margin_universal_contexts,
        'validated_state_boundary_checks': validated_state_boundary_checks,
        'validated_universal_boundary_checks': validated_universal_boundary_checks,
        'state_deadline_ladders': state_deadline_ladders,
        'state_deadline_ladders_with_strict_odd_growth': state_deadline_ladders_with_strict_odd_growth,
        'universal_deadline_ladders': universal_deadline_ladders,
        'universal_deadline_ladders_with_strict_odd_growth': universal_deadline_ladders_with_strict_odd_growth,
        'state_odd_even_pair_plateaus': state_odd_even_pair_plateaus,
        'universal_odd_even_pair_plateaus': universal_odd_even_pair_plateaus,
        'state_zero_margin_example': state_zero_example,
        'state_positive_feasible_example': state_feasible_example,
        'state_positive_impossible_example': state_impossible_example,
        'universal_zero_margin_example': universal_zero_example,
        'universal_positive_feasible_example': universal_feasible_example,
        'universal_positive_impossible_example': universal_impossible_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_hold_cost_ceiling_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_hold_cost_ceiling_validation_summary()
    return {
        'focus': 'turn same-deadline stateless live control into a direct hold-cost affordability ceiling so an implementor can decide whether continued waiting is still promise-safe from one threshold comparison',
        'headline_findings': {
            'positive_live_hold_cost_ceiling_rule': 'for positive margin floors, same-deadline live waiting is promise-safe iff hold_cost <= p * (state_prefix_bits / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2)))',
            'effective_horizon_rule': 'the live hold-cost ceiling is exactly the blind-commit hold-cost ceiling at effective horizon floor((H + 1) / 2)',
            'odd_even_plateau_rule': 'deadlines 2j - 1 and 2j have identical positive live hold-cost ceilings',
            'zero_margin_rule': 'at zero margin floor, immediate close is safe, so the live hold-cost ceiling is unbounded',
            'positive_state_feasible_contexts': summary['positive_state_feasible_contexts'],
            'positive_state_impossible_contexts': summary['positive_state_impossible_contexts'],
            'positive_universal_feasible_contexts': summary['positive_universal_feasible_contexts'],
            'positive_universal_impossible_contexts': summary['positive_universal_impossible_contexts'],
        },
        'decision_rules': [
            'For a positive margin floor, compute the nominal live deadline H and reduce it to effective blind horizon floor((H + 1) / 2); the exact live hold-cost ceiling is then p * (state_prefix_bits / (n(n + 1)) - m / (1 - (1 - p)^floor((H + 1) / 2))).',
            'If the resulting ceiling is nonnegative, waiting is promise-safe exactly up to that per-tick hold cost; at any larger hold cost the original positive promise fails under same-deadline live reoptimization.',
            'If the resulting ceiling is negative, the positive promise is impossible even at zero hold cost for that batch, state, and nominal live deadline.',
            'Deadlines 2j - 1 and 2j have the same positive hold-cost ceiling, and the ceiling only grows when the nominal live deadline climbs to the next odd rung.',
            'At zero margin floor, immediate close is already safe, so the same-deadline live hold-cost ceiling is unbounded rather than finite.',
            'The same law holds under the seven-bit all-state lower envelope after replacing state_prefix_bits by 7.',
        ],
        'state_zero_margin_example': summary['state_zero_margin_example'],
        'state_positive_feasible_example': summary['state_positive_feasible_example'],
        'state_positive_impossible_example': summary['state_positive_impossible_example'],
        'universal_zero_margin_example': summary['universal_zero_margin_example'],
        'universal_positive_feasible_example': summary['universal_positive_feasible_example'],
        'universal_positive_impossible_example': summary['universal_positive_impossible_example'],
        'validation_summary': {key: value for key, value in summary.items() if 'example' not in key},
        'source_reports': [
            'artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.md',
            'artifacts/reports/geometric_arrival_live_batch_cap_law_snapshot_20260316.md',
            'artifacts/reports/geometric_arrival_live_minimum_deadline_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_hold_cost_ceiling_law.py',
    }


def main() -> None:
    print(json.dumps(build_geometric_arrival_live_hold_cost_ceiling_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
