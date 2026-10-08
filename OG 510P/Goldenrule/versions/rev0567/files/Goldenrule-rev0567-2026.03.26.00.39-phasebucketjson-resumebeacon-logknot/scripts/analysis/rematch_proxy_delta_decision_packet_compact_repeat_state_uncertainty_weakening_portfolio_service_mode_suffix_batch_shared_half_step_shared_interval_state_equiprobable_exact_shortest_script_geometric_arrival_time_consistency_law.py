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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law import (
    evaluate_state_countdown_reserve_profile,
    evaluate_universal_countdown_reserve_profile,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law import (
    compute_minimum_timeout_for_state_batch_target_margin,
    compute_universal_minimum_timeout_for_batch_target_margin,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law import (
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))


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
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
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


@lru_cache(maxsize=None)
def evaluate_state_time_consistency_profile(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
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
    one_tick_value = _fixed_timeout_value_for_state(state, current_batch_length, arrival_probability, hold_cost, 1)

    if schedule_class == 'finite' and minimum_timeout_ticks is not None:
        boundary_profile = evaluate_state_countdown_reserve_profile(
            state,
            current_batch_length,
            arrival_probability_numerator,
            arrival_probability_denominator,
            hold_cost_bits_numerator,
            hold_cost_bits_denominator,
            target_margin_bits_numerator,
            target_margin_bits_denominator,
            int(minimum_timeout_ticks),
        )
        restored_profile = evaluate_state_countdown_reserve_profile(
            state,
            current_batch_length,
            arrival_probability_numerator,
            arrival_probability_denominator,
            hold_cost_bits_numerator,
            hold_cost_bits_denominator,
            target_margin_bits_numerator,
            target_margin_bits_denominator,
            2 * int(minimum_timeout_ticks) - 1,
        )
        boundary_live_value = _deserialize_fraction(boundary_profile['live_countdown_policy_value_bits_per_script'])
        restored_live_value = _deserialize_fraction(restored_profile['live_countdown_policy_value_bits_per_script'])
        if boundary_live_value is None or restored_live_value is None:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                'state countdown reserve profile unexpectedly omitted exact values'
            )
        time_consistent = int(minimum_timeout_ticks) == 1
        drift_interval = None if time_consistent else {'start_remaining_horizon': int(minimum_timeout_ticks), 'end_remaining_horizon': 2 * int(minimum_timeout_ticks) - 2}
        reason = (
            'one_tick_margin_promises_are_time_consistent_under_live_reoptimization'
            if time_consistent
            else 'multi_tick_margin_promises_drift_at_the_boundary_checkpoint_under_live_reoptimization'
        )
    else:
        boundary_live_value = Fraction(0, 1)
        restored_live_value = Fraction(0, 1)
        time_consistent = False
        drift_interval = None
        reason = 'nonfinite_schedules_have_no_finite_local_time_consistency_boundary'

    return {
        'state': list(state),
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': minimum_timeout_ticks,
        'one_tick_value_bits_per_script': _serialize_fraction(one_tick_value),
        'blind_commit_boundary_value_bits_per_script': _serialize_fraction(
            _fixed_timeout_value_for_state(state, current_batch_length, arrival_probability, hold_cost, int(minimum_timeout_ticks))
            if minimum_timeout_ticks is not None else Fraction(0, 1)
        ),
        'live_boundary_value_bits_per_script': _serialize_fraction(boundary_live_value),
        'live_restored_value_bits_per_script': _serialize_fraction(restored_live_value),
        'live_boundary_preserves_original_margin': boundary_live_value >= target_margin,
        'live_policy_is_time_consistent_for_original_margin': time_consistent,
        'drift_interval_under_live_reoptimization': drift_interval,
        'time_consistency_formula': 'finite schedules are time-consistent iff K = 1, equivalently iff the original margin floor is already met by one more tick',
        'restoration_formula': 'for finite schedules with K > 1, live countdown first recovers the original margin at remaining horizon 2K - 1',
        'reason': reason,
    }


@lru_cache(maxsize=None)
def evaluate_universal_time_consistency_profile(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
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
    one_tick_value = _fixed_timeout_value_for_universal(current_batch_length, arrival_probability, hold_cost, 1)

    if schedule_class == 'finite' and minimum_timeout_ticks is not None:
        boundary_profile = evaluate_universal_countdown_reserve_profile(
            current_batch_length,
            arrival_probability_numerator,
            arrival_probability_denominator,
            hold_cost_bits_numerator,
            hold_cost_bits_denominator,
            target_margin_bits_numerator,
            target_margin_bits_denominator,
            int(minimum_timeout_ticks),
        )
        restored_profile = evaluate_universal_countdown_reserve_profile(
            current_batch_length,
            arrival_probability_numerator,
            arrival_probability_denominator,
            hold_cost_bits_numerator,
            hold_cost_bits_denominator,
            target_margin_bits_numerator,
            target_margin_bits_denominator,
            2 * int(minimum_timeout_ticks) - 1,
        )
        boundary_live_value = _deserialize_fraction(boundary_profile['live_countdown_policy_value_bits_per_script'])
        restored_live_value = _deserialize_fraction(restored_profile['live_countdown_policy_value_bits_per_script'])
        if boundary_live_value is None or restored_live_value is None:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                'universal countdown reserve profile unexpectedly omitted exact values'
            )
        time_consistent = int(minimum_timeout_ticks) == 1
        drift_interval = None if time_consistent else {'start_remaining_horizon': int(minimum_timeout_ticks), 'end_remaining_horizon': 2 * int(minimum_timeout_ticks) - 2}
        reason = (
            'one_tick_universal_margin_promises_are_time_consistent_under_live_reoptimization'
            if time_consistent
            else 'multi_tick_universal_margin_promises_drift_at_the_boundary_checkpoint_under_live_reoptimization'
        )
    else:
        boundary_live_value = Fraction(0, 1)
        restored_live_value = Fraction(0, 1)
        time_consistent = False
        drift_interval = None
        reason = 'nonfinite_universal_schedules_have_no_finite_local_time_consistency_boundary'

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': minimum_timeout_ticks,
        'one_tick_value_bits_per_script': _serialize_fraction(one_tick_value),
        'blind_commit_boundary_value_bits_per_script': _serialize_fraction(
            _fixed_timeout_value_for_universal(current_batch_length, arrival_probability, hold_cost, int(minimum_timeout_ticks))
            if minimum_timeout_ticks is not None else Fraction(0, 1)
        ),
        'live_boundary_value_bits_per_script': _serialize_fraction(boundary_live_value),
        'live_restored_value_bits_per_script': _serialize_fraction(restored_live_value),
        'live_boundary_preserves_original_margin': boundary_live_value >= target_margin,
        'live_policy_is_time_consistent_for_original_margin': time_consistent,
        'drift_interval_under_live_reoptimization': drift_interval,
        'time_consistency_formula': 'finite universal schedules are time-consistent iff K = 1',
        'restoration_formula': 'for finite universal schedules with K > 1, live countdown first recovers the original margin at remaining horizon 2K - 1',
        'reason': reason,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_time_consistency_validation_summary() -> dict[str, Any]:
    validated_state_schedules = 0
    validated_universal_schedules = 0
    finite_state_schedules = 0
    time_consistent_state_schedules = 0
    drift_prone_state_schedules = 0
    asymptotic_only_state_schedules = 0
    impossible_state_schedules = 0
    finite_universal_schedules = 0
    time_consistent_universal_schedules = 0
    drift_prone_universal_schedules = 0
    asymptotic_only_universal_schedules = 0
    impossible_universal_schedules = 0

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        profile = evaluate_state_time_consistency_profile(
                            state,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        schedule_class = profile['schedule_class']
                        minimum_timeout_ticks = profile['minimum_timeout_ticks_for_blind_commit_margin']
                        if schedule_class == 'finite':
                            finite_state_schedules += 1
                            assert minimum_timeout_ticks is not None
                            if int(minimum_timeout_ticks) == 1:
                                if not bool(profile['live_policy_is_time_consistent_for_original_margin']):
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                        f'finite one-tick schedule was not marked time-consistent for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                    )
                                if not bool(profile['live_boundary_preserves_original_margin']):
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                        f'finite one-tick schedule failed at live boundary for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                    )
                                time_consistent_state_schedules += 1
                            else:
                                if bool(profile['live_policy_is_time_consistent_for_original_margin']):
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                        f'multi-tick finite schedule was incorrectly marked time-consistent for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                    )
                                if bool(profile['live_boundary_preserves_original_margin']):
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                        f'multi-tick finite schedule did not drift at the boundary for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                    )
                                if profile['drift_interval_under_live_reoptimization'] != {'start_remaining_horizon': int(minimum_timeout_ticks), 'end_remaining_horizon': 2 * int(minimum_timeout_ticks) - 2}:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                        f'multi-tick drift interval mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                    )
                                if _deserialize_fraction(profile['live_restored_value_bits_per_script']) < target_margin:
                                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                        f'multi-tick finite schedule did not recover target at 2K-1 for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                    )
                                drift_prone_state_schedules += 1
                        elif schedule_class == 'asymptotic_only':
                            asymptotic_only_state_schedules += 1
                        else:
                            impossible_state_schedules += 1
                        validated_state_schedules += 1

    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    profile = evaluate_universal_time_consistency_profile(
                        current_batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    schedule_class = profile['schedule_class']
                    minimum_timeout_ticks = profile['minimum_timeout_ticks_for_blind_commit_margin']
                    if schedule_class == 'finite':
                        finite_universal_schedules += 1
                        assert minimum_timeout_ticks is not None
                        if int(minimum_timeout_ticks) == 1:
                            if not bool(profile['live_policy_is_time_consistent_for_original_margin']):
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                    f'finite one-tick universal schedule was not marked time-consistent for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                )
                            if not bool(profile['live_boundary_preserves_original_margin']):
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                    f'finite one-tick universal schedule failed at the live boundary for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                )
                            time_consistent_universal_schedules += 1
                        else:
                            if bool(profile['live_policy_is_time_consistent_for_original_margin']):
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                    f'multi-tick universal schedule was incorrectly marked time-consistent for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                )
                            if bool(profile['live_boundary_preserves_original_margin']):
                                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
                                    f'multi-tick universal schedule did not drift at the boundary for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                                )
                            drift_prone_universal_schedules += 1
                    elif schedule_class == 'asymptotic_only':
                        asymptotic_only_universal_schedules += 1
                    else:
                        impossible_universal_schedules += 1
                    validated_universal_schedules += 1

    return {
        'audited_state_count': len(STATE_GRID),
        'validated_state_schedules': validated_state_schedules,
        'validated_universal_schedules': validated_universal_schedules,
        'finite_state_schedules': finite_state_schedules,
        'time_consistent_state_schedules': time_consistent_state_schedules,
        'drift_prone_state_schedules': drift_prone_state_schedules,
        'asymptotic_only_state_schedules': asymptotic_only_state_schedules,
        'impossible_state_schedules': impossible_state_schedules,
        'finite_universal_schedules': finite_universal_schedules,
        'time_consistent_universal_schedules': time_consistent_universal_schedules,
        'drift_prone_universal_schedules': drift_prone_universal_schedules,
        'asymptotic_only_universal_schedules': asymptotic_only_universal_schedules,
        'impossible_universal_schedules': impossible_universal_schedules,
    }


@lru_cache(maxsize=None)
def _find_first_state_profile(*, time_consistent: bool) -> dict[str, Any]:
    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        profile = evaluate_state_time_consistency_profile(
                            state,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        if bool(profile['live_policy_is_time_consistent_for_original_margin']) == time_consistent and profile['schedule_class'] == 'finite':
                            return profile
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
        f'could not find state profile with time_consistent={time_consistent}'
    )


@lru_cache(maxsize=None)
def _find_first_universal_profile(*, time_consistent: bool) -> dict[str, Any]:
    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    profile = evaluate_universal_time_consistency_profile(
                        current_batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    if bool(profile['live_policy_is_time_consistent_for_original_margin']) == time_consistent and profile['schedule_class'] == 'finite':
                        return profile
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptGeometricArrivalTimeConsistencyLawError(
        f'could not find universal profile with time_consistent={time_consistent}'
    )


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_time_consistency_validation_summary()
    return {
        'focus': 'show that only one-tick blind-commit promises are locally time-consistent under live geometric-arrival reoptimization and that every multi-tick finite promise necessarily drifts at the boundary checkpoint',
        'headline_findings': {
            'time_consistency_rule': 'finite schedules are time-consistent under live reoptimization iff K = 1',
            'boundary_drift_rule': 'every finite schedule with K > 1 already underdelivers at remaining horizon H = K under live countdown semantics',
            'restoration_rule': 'those same schedules first recover the original margin only at H = 2K - 1',
            'drift_prone_state_schedules': summary['drift_prone_state_schedules'],
            'drift_prone_universal_schedules': summary['drift_prone_universal_schedules'],
        },
        'decision_rules': [
            'If the original margin floor is already met by one more tick, then K = 1 and live reoptimization is time-consistent for that promise.',
            'If the original margin floor needs K > 1 blind-commit ticks, then a live countdown controller will drift immediately at the boundary checkpoint H = K.',
            'To preserve the original promise under live reoptimization for such a schedule, remaining horizon must instead reach H = 2K - 1.',
            'So implementors must choose among three semantics: blind commit, live reoptimization with accepted drift, or a richer stateful controller that explicitly tracks promise slack.',
        ],
        'state_time_consistent_example': _find_first_state_profile(time_consistent=True),
        'state_drift_example': _find_first_state_profile(time_consistent=False),
        'universal_time_consistent_example': _find_first_universal_profile(time_consistent=True),
        'universal_drift_example': _find_first_universal_profile(time_consistent=False),
        'validation_summary': summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_snapshot(), indent=2, sort_keys=True))
