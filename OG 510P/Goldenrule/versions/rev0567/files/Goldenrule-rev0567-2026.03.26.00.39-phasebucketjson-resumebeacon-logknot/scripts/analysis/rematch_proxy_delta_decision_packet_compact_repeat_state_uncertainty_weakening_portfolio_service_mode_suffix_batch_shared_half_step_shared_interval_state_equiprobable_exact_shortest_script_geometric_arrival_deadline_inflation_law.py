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


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
BLIND_HORIZON_GRID = (1, 2, 3, 4, 5, 6, 7, 8)


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
    payload = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(state, 1, 1, 2, 1, 10, 1)
    return int(payload['state_prefix_bits'])


@lru_cache(maxsize=None)
def _fixed_timeout_state_value(state: tuple[int, int], n: int, p: Fraction, c: Fraction, timeout_ticks: int) -> Fraction:
    if timeout_ticks <= 0:
        return Fraction(0, 1)
    payload = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value(
        state,
        n,
        p.numerator,
        p.denominator,
        c.numerator,
        c.denominator,
        timeout_ticks,
    )
    value = _deserialize_fraction(payload['expected_net_wait_value_bits_per_script'])
    if value is None:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError('missing state fixed-timeout value')
    return value


@lru_cache(maxsize=None)
def _fixed_timeout_universal_value(n: int, p: Fraction, c: Fraction, timeout_ticks: int) -> Fraction:
    if timeout_ticks <= 0:
        return Fraction(0, 1)
    if p == 0:
        return -c * timeout_ticks
    q = Fraction(1, 1) - p
    success = Fraction(1, 1) - q ** timeout_ticks
    expected_wait = sum(q ** step for step in range(timeout_ticks))
    gross = success * Fraction(7, n * (n + 1))
    return gross - c * expected_wait


def _schedule_class(schedule: dict[str, Any]) -> str:
    if bool(schedule['finite_timeout_exists']):
        return 'finite'
    if bool(schedule['asymptotically_feasible']):
        return 'asymptotic_only'
    return 'impossible'


@lru_cache(maxsize=None)
def evaluate_state_deadline_inflation_profile(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    blind_commit_horizon_ticks: int,
) -> dict[str, Any]:
    if blind_commit_horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError('blind horizon must be positive')
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    c = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    m = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
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
    K = schedule['minimum_timeout_ticks']
    blind_value = _fixed_timeout_state_value(state, current_batch_length, p, c, blind_commit_horizon_ticks)
    if schedule_class == 'finite' and K is not None:
        compensation_ticks = int(K) - 1
        required_live_horizon = blind_commit_horizon_ticks + compensation_ticks
        live_value = _fixed_timeout_state_value(state, current_batch_length, p, c, blind_commit_horizon_ticks)
        uncompensated_live_value = _fixed_timeout_state_value(state, current_batch_length, p, c, max(blind_commit_horizon_ticks - compensation_ticks, 0))
        reason = 'inflating_the_live_deadline_by_K_minus_1_exactly_restores_the_same_blind_commit_value'
    else:
        compensation_ticks = None
        required_live_horizon = None
        live_value = None
        uncompensated_live_value = None
        reason = 'no_finite_deadline_inflation_is_defined_without_a_finite_schedule'
    return {
        'state': list(state),
        'state_prefix_bits': _state_prefix_bits(state),
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(c),
        'target_margin_bits_per_script': _serialize_fraction(m),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': K,
        'blind_commit_horizon_ticks': int(blind_commit_horizon_ticks),
        'required_live_horizon_ticks_for_value_equivalence': required_live_horizon,
        'deadline_inflation_ticks': compensation_ticks,
        'blind_commit_value_bits_per_script': _serialize_fraction(blind_value),
        'value_equivalent_live_reoptimization_value_bits_per_script': _serialize_fraction(live_value),
        'uncompensated_live_value_at_same_horizon_minus_inflation_bits_per_script': _serialize_fraction(uncompensated_live_value),
        'inflation_formula': 'for finite schedules, stateless live reoptimization needs exactly K - 1 extra ticks to reproduce blind-commit horizon H',
        'equivalence_formula': 'live(H + K - 1) = blind_commit(H)',
        'reason': reason,
    }


@lru_cache(maxsize=None)
def evaluate_universal_deadline_inflation_profile(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    blind_commit_horizon_ticks: int,
) -> dict[str, Any]:
    if blind_commit_horizon_ticks <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError('blind horizon must be positive')
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    c = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    m = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
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
    K = schedule['minimum_timeout_ticks']
    blind_value = _fixed_timeout_universal_value(current_batch_length, p, c, blind_commit_horizon_ticks)
    if schedule_class == 'finite' and K is not None:
        compensation_ticks = int(K) - 1
        required_live_horizon = blind_commit_horizon_ticks + compensation_ticks
        live_value = _fixed_timeout_universal_value(current_batch_length, p, c, blind_commit_horizon_ticks)
        uncompensated_live_value = _fixed_timeout_universal_value(current_batch_length, p, c, max(blind_commit_horizon_ticks - compensation_ticks, 0))
        reason = 'inflating_the_universal_live_deadline_by_K_minus_1_exactly_restores_the_same_blind_commit_value'
    else:
        compensation_ticks = None
        required_live_horizon = None
        live_value = None
        uncompensated_live_value = None
        reason = 'no_finite_universal_deadline_inflation_is_defined_without_a_finite_schedule'
    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(c),
        'target_margin_bits_per_script': _serialize_fraction(m),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': K,
        'blind_commit_horizon_ticks': int(blind_commit_horizon_ticks),
        'required_live_horizon_ticks_for_value_equivalence': required_live_horizon,
        'deadline_inflation_ticks': compensation_ticks,
        'blind_commit_value_bits_per_script': _serialize_fraction(blind_value),
        'value_equivalent_live_reoptimization_value_bits_per_script': _serialize_fraction(live_value),
        'uncompensated_live_value_at_same_horizon_minus_inflation_bits_per_script': _serialize_fraction(uncompensated_live_value),
        'inflation_formula': 'for finite universal schedules, stateless live reoptimization needs exactly K - 1 extra ticks to reproduce blind-commit horizon H',
        'equivalence_formula': 'live(H + K - 1) = blind_commit(H)',
        'reason': reason,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_deadline_inflation_validation_summary() -> dict[str, Any]:
    validated_state_panels = 0
    validated_universal_panels = 0
    finite_state_panels = 0
    finite_universal_panels = 0
    positive_inflation_state_panels = 0
    zero_inflation_state_panels = 0
    positive_inflation_universal_panels = 0
    zero_inflation_universal_panels = 0
    for state in STATE_GRID:
        for n in BATCH_GRID:
            for p in ARRIVAL_GRID:
                for c in HOLD_COST_GRID:
                    for m in TARGET_MARGIN_GRID:
                        schedule = compute_minimum_timeout_for_state_batch_target_margin(state, n, p.numerator, p.denominator, c.numerator, c.denominator, m.numerator, m.denominator)
                        if _schedule_class(schedule) == 'finite':
                            K = int(schedule['minimum_timeout_ticks'])
                            for H in BLIND_HORIZON_GRID:
                                profile = evaluate_state_deadline_inflation_profile(state, n, p.numerator, p.denominator, c.numerator, c.denominator, m.numerator, m.denominator, H)
                                finite_state_panels += 1
                                if profile['deadline_inflation_ticks'] != K - 1:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError('state inflation tick mismatch')
                                blind = _deserialize_fraction(profile['blind_commit_value_bits_per_script'])
                                live = _deserialize_fraction(profile['value_equivalent_live_reoptimization_value_bits_per_script'])
                                if blind != live:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError('state inflated live value mismatch')
                                if K == 1:
                                    zero_inflation_state_panels += 1
                                else:
                                    positive_inflation_state_panels += 1
                                validated_state_panels += 1
                        else:
                            validated_state_panels += len(BLIND_HORIZON_GRID)
    for n in BATCH_GRID:
        for p in ARRIVAL_GRID:
            for c in HOLD_COST_GRID:
                for m in TARGET_MARGIN_GRID:
                    schedule = compute_universal_minimum_timeout_for_batch_target_margin(n, p.numerator, p.denominator, c.numerator, c.denominator, m.numerator, m.denominator)
                    if _schedule_class(schedule) == 'finite':
                        K = int(schedule['minimum_timeout_ticks'])
                        for H in BLIND_HORIZON_GRID:
                            profile = evaluate_universal_deadline_inflation_profile(n, p.numerator, p.denominator, c.numerator, c.denominator, m.numerator, m.denominator, H)
                            finite_universal_panels += 1
                            if profile['deadline_inflation_ticks'] != K - 1:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError('universal inflation tick mismatch')
                            blind = _deserialize_fraction(profile['blind_commit_value_bits_per_script'])
                            live = _deserialize_fraction(profile['value_equivalent_live_reoptimization_value_bits_per_script'])
                            if blind != live:
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalDeadlineInflationLawError('universal inflated live value mismatch')
                            if K == 1:
                                zero_inflation_universal_panels += 1
                            else:
                                positive_inflation_universal_panels += 1
                            validated_universal_panels += 1
                    else:
                        validated_universal_panels += len(BLIND_HORIZON_GRID)
    return {
        'audited_state_count': len(STATE_GRID),
        'blind_horizon_grid': list(BLIND_HORIZON_GRID),
        'validated_state_panels': validated_state_panels,
        'validated_universal_panels': validated_universal_panels,
        'finite_state_panels': finite_state_panels,
        'finite_universal_panels': finite_universal_panels,
        'positive_inflation_state_panels': positive_inflation_state_panels,
        'zero_inflation_state_panels': zero_inflation_state_panels,
        'positive_inflation_universal_panels': positive_inflation_universal_panels,
        'zero_inflation_universal_panels': zero_inflation_universal_panels,
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_inflation_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_deadline_inflation_validation_summary()
    state_example = evaluate_state_deadline_inflation_profile((0, 0), 1, 1, 4, 1, 20, 1, 1, 2)
    universal_example = evaluate_universal_deadline_inflation_profile(1, 1, 4, 1, 20, 1, 1, 2)
    return {
        'focus': 'show that the exact deadline compensation for using stateless live reoptimization instead of blind commit is simply reserve-length inflation by K - 1 ticks',
        'headline_findings': {
            'compensation_rule': 'for finite schedules, live(H + K - 1) = blind_commit(H)',
            'inflation_rule': 'the exact deadline inflation needed to neutralize the live-reoptimization haircut is K - 1 ticks',
            'zero_inflation_rule': 'only one-tick schedules require no deadline inflation',
            'positive_inflation_state_panels': summary['positive_inflation_state_panels'],
            'positive_inflation_universal_panels': summary['positive_inflation_universal_panels'],
        },
        'decision_rules': [
            'If the implementor insists on stateless live reoptimization, compensate it by K - 1 extra ticks whenever it needs blind-commit value equivalence rather than merely accepted drift.',
            'This compensation is exact and parameter-free once K is known: it does not require solving another nonlinear problem online.',
            'One-tick schedules remain the special zero-inflation case.',
            'So reserve tax, deficit tax, and deadline inflation are the same phenomenon seen in three coordinate systems.',
        ],
        'state_example': state_example,
        'universal_example': universal_example,
        'validation_summary': summary,
        'source_reports': [
            'artifacts/reports/geometric_arrival_live_reoptimization_deficit_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_inflation_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_inflation_snapshot(), indent=2, sort_keys=True))
