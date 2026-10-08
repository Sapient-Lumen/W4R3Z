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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law import (
    compute_minimum_timeout_for_state_batch_target_margin,
    compute_universal_minimum_timeout_for_batch_target_margin,
)


class GeometricArrivalLiveMinimumDeadlineLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 13))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
POSITIVE_TARGET_MARGIN_GRID = TARGET_MARGIN_GRID[1:]


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _schedule_class(schedule: dict[str, Any]) -> str:
    if bool(schedule['finite_timeout_exists']):
        return 'finite'
    if bool(schedule['asymptotically_feasible']):
        return 'asymptotic_only'
    return 'impossible'


@lru_cache(maxsize=None)
def compute_state_minimum_live_deadline(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    c = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    m = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    blind_schedule = compute_minimum_timeout_for_state_batch_target_margin(
        state,
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    schedule_class = _schedule_class(blind_schedule)
    state_prefix_bits = int(blind_schedule['state_prefix_bits'])

    result: dict[str, Any] = {
        'state': list(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(c),
        'target_margin_bits_per_script': _serialize_fraction(m),
        'blind_commit_schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': blind_schedule['minimum_timeout_ticks'],
        'minimum_nominal_live_deadline_ticks': None,
        'odd_deadline_entry': None,
        'positive_promise_odd_ladder_formula': 'for positive margin floors with finite blind minimum timeout K, the minimum same-deadline stateless live deadline is exactly 2K - 1',
        'zero_margin_formula': 'at zero margin floor, immediate close is already safe, so the minimum nominal live deadline is 1',
    }

    if m == 0:
        result.update(
            {
                'minimum_nominal_live_deadline_ticks': 1,
                'odd_deadline_entry': True,
                'reason': 'zero_margin_floor_makes_immediate_close_safe_so_the_live_deadline_floor_is_one_tick',
            }
        )
        return result

    if schedule_class != 'finite':
        result.update(
            {
                'reason': 'positive_promise_has_no_finite_same_deadline_live_deadline_without_a_finite_blind_minimum_timeout',
            }
        )
        return result

    minimum_timeout_ticks = int(blind_schedule['minimum_timeout_ticks'])
    minimum_live_deadline_ticks = 2 * minimum_timeout_ticks - 1
    result.update(
        {
            'minimum_nominal_live_deadline_ticks': minimum_live_deadline_ticks,
            'odd_deadline_entry': minimum_live_deadline_ticks % 2 == 1,
            'reason': 'positive_minimum_same_deadline_live_deadline_is_the_odd_image_of_the_blind_minimum_timeout',
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_universal_minimum_live_deadline(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    c = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    m = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    blind_schedule = compute_universal_minimum_timeout_for_batch_target_margin(
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    schedule_class = _schedule_class(blind_schedule)

    result: dict[str, Any] = {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(c),
        'target_margin_bits_per_script': _serialize_fraction(m),
        'blind_commit_schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': blind_schedule['minimum_timeout_ticks'],
        'minimum_nominal_live_deadline_ticks': None,
        'odd_deadline_entry': None,
        'positive_promise_odd_ladder_formula': 'for positive universal margin floors with finite blind minimum timeout K, the minimum same-deadline stateless live deadline is exactly 2K - 1',
        'zero_margin_formula': 'at zero universal margin floor, immediate close is already safe, so the minimum nominal live deadline is 1',
    }

    if m == 0:
        result.update(
            {
                'minimum_nominal_live_deadline_ticks': 1,
                'odd_deadline_entry': True,
                'reason': 'zero_universal_margin_floor_makes_immediate_close_safe_so_the_live_deadline_floor_is_one_tick',
            }
        )
        return result

    if schedule_class != 'finite':
        result.update(
            {
                'reason': 'positive_universal_promise_has_no_finite_same_deadline_live_deadline_without_a_finite_blind_minimum_timeout',
            }
        )
        return result

    minimum_timeout_ticks = int(blind_schedule['minimum_timeout_ticks'])
    minimum_live_deadline_ticks = 2 * minimum_timeout_ticks - 1
    result.update(
        {
            'minimum_nominal_live_deadline_ticks': minimum_live_deadline_ticks,
            'odd_deadline_entry': minimum_live_deadline_ticks % 2 == 1,
            'reason': 'positive_universal_minimum_same_deadline_live_deadline_is_the_odd_image_of_the_blind_minimum_timeout',
        }
    )
    return result


@lru_cache(maxsize=1)
def build_geometric_arrival_live_minimum_deadline_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    positive_finite_state_contexts = 0
    positive_asymptotic_state_contexts = 0
    positive_impossible_state_contexts = 0
    positive_finite_universal_contexts = 0
    positive_asymptotic_universal_contexts = 0
    positive_impossible_universal_contexts = 0
    zero_margin_state_contexts = 0
    zero_margin_universal_contexts = 0
    odd_minimum_state_deadlines = 0
    odd_minimum_universal_deadlines = 0
    state_even_deadline_predecessor_equivalences = 0
    universal_even_deadline_predecessor_equivalences = 0

    state_zero_example: dict[str, Any] | None = None
    state_finite_example: dict[str, Any] | None = None
    state_nonfinite_example: dict[str, Any] | None = None
    universal_zero_example: dict[str, Any] | None = None
    universal_finite_example: dict[str, Any] | None = None
    universal_nonfinite_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        for n in BATCH_GRID:
            for p in ARRIVAL_GRID:
                for c in HOLD_COST_GRID:
                    for m in TARGET_MARGIN_GRID:
                        profile = compute_state_minimum_live_deadline(
                            state,
                            n,
                            p.numerator,
                            p.denominator,
                            c.numerator,
                            c.denominator,
                            m.numerator,
                            m.denominator,
                        )
                        minimum_live_deadline_ticks = profile['minimum_nominal_live_deadline_ticks']
                        schedule_class = str(profile['blind_commit_schedule_class'])
                        validated_state_contexts += 1

                        if m == 0:
                            zero_margin_state_contexts += 1
                            if minimum_live_deadline_ticks != 1:
                                raise GeometricArrivalLiveMinimumDeadlineLawError('zero-margin state minimum live deadline must equal 1')
                            live_at_one = evaluate_state_effective_horizon_profile(
                                state,
                                n,
                                p.numerator,
                                p.denominator,
                                c.numerator,
                                c.denominator,
                                m.numerator,
                                m.denominator,
                                1,
                            )
                            if not bool(live_at_one['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveMinimumDeadlineLawError('zero-margin state live deadline 1 failed to preserve')
                            if state_zero_example is None:
                                state_zero_example = {
                                    'minimum_live_deadline_profile': profile,
                                    'live_profile_at_minimum_deadline': live_at_one,
                                }
                            continue

                        if schedule_class == 'finite':
                            positive_finite_state_contexts += 1
                            K = int(profile['minimum_timeout_ticks_for_blind_commit_margin'])
                            expected_H = 2 * K - 1
                            if minimum_live_deadline_ticks != expected_H:
                                raise GeometricArrivalLiveMinimumDeadlineLawError('finite state minimum live deadline mismatch')
                            if minimum_live_deadline_ticks % 2 != 1:
                                raise GeometricArrivalLiveMinimumDeadlineLawError('finite state minimum live deadline must be odd')
                            odd_minimum_state_deadlines += 1
                            at_minimum = evaluate_state_effective_horizon_profile(
                                state,
                                n,
                                p.numerator,
                                p.denominator,
                                c.numerator,
                                c.denominator,
                                m.numerator,
                                m.denominator,
                                minimum_live_deadline_ticks,
                            )
                            if not bool(at_minimum['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveMinimumDeadlineLawError('finite state minimum live deadline failed to preserve')
                            if minimum_live_deadline_ticks > 1:
                                before_minimum = evaluate_state_effective_horizon_profile(
                                    state,
                                    n,
                                    p.numerator,
                                    p.denominator,
                                    c.numerator,
                                    c.denominator,
                                    m.numerator,
                                    m.denominator,
                                    minimum_live_deadline_ticks - 1,
                                )
                                if bool(before_minimum['live_countdown_preserves_original_margin']):
                                    raise GeometricArrivalLiveMinimumDeadlineLawError('finite state predecessor deadline unexpectedly preserved')
                            even_partner = evaluate_state_effective_horizon_profile(
                                state,
                                n,
                                p.numerator,
                                p.denominator,
                                c.numerator,
                                c.denominator,
                                m.numerator,
                                m.denominator,
                                minimum_live_deadline_ticks + 1,
                            )
                            if bool(even_partner['live_countdown_preserves_original_margin']) != bool(at_minimum['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveMinimumDeadlineLawError('finite state odd/even deadline pair mismatch at frontier')
                            state_even_deadline_predecessor_equivalences += 1
                            if state_finite_example is None and minimum_live_deadline_ticks > 1:
                                state_finite_example = {
                                    'minimum_live_deadline_profile': profile,
                                    'live_profile_at_predecessor_even_deadline': before_minimum,
                                    'live_profile_at_minimum_deadline': at_minimum,
                                    'live_profile_at_equivalent_even_deadline': even_partner,
                                }
                        else:
                            if minimum_live_deadline_ticks is not None:
                                raise GeometricArrivalLiveMinimumDeadlineLawError('nonfinite state context should not have finite minimum live deadline')
                            if schedule_class == 'asymptotic_only':
                                positive_asymptotic_state_contexts += 1
                            elif schedule_class == 'impossible':
                                positive_impossible_state_contexts += 1
                            else:
                                raise GeometricArrivalLiveMinimumDeadlineLawError(f'unexpected state schedule class {schedule_class}')
                            if state_nonfinite_example is None:
                                state_nonfinite_example = {
                                    'minimum_live_deadline_profile': profile,
                                }

    for n in BATCH_GRID:
        for p in ARRIVAL_GRID:
            for c in HOLD_COST_GRID:
                for m in TARGET_MARGIN_GRID:
                    profile = compute_universal_minimum_live_deadline(
                        n,
                        p.numerator,
                        p.denominator,
                        c.numerator,
                        c.denominator,
                        m.numerator,
                        m.denominator,
                    )
                    minimum_live_deadline_ticks = profile['minimum_nominal_live_deadline_ticks']
                    schedule_class = str(profile['blind_commit_schedule_class'])
                    validated_universal_contexts += 1

                    if m == 0:
                        zero_margin_universal_contexts += 1
                        if minimum_live_deadline_ticks != 1:
                            raise GeometricArrivalLiveMinimumDeadlineLawError('zero-margin universal minimum live deadline must equal 1')
                        live_at_one = evaluate_universal_effective_horizon_profile(
                            n,
                            p.numerator,
                            p.denominator,
                            c.numerator,
                            c.denominator,
                            m.numerator,
                            m.denominator,
                            1,
                        )
                        if not bool(live_at_one['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveMinimumDeadlineLawError('zero-margin universal live deadline 1 failed to preserve')
                        if universal_zero_example is None:
                            universal_zero_example = {
                                'minimum_live_deadline_profile': profile,
                                'live_profile_at_minimum_deadline': live_at_one,
                            }
                        continue

                    if schedule_class == 'finite':
                        positive_finite_universal_contexts += 1
                        K = int(profile['minimum_timeout_ticks_for_blind_commit_margin'])
                        expected_H = 2 * K - 1
                        if minimum_live_deadline_ticks != expected_H:
                            raise GeometricArrivalLiveMinimumDeadlineLawError('finite universal minimum live deadline mismatch')
                        if minimum_live_deadline_ticks % 2 != 1:
                            raise GeometricArrivalLiveMinimumDeadlineLawError('finite universal minimum live deadline must be odd')
                        odd_minimum_universal_deadlines += 1
                        at_minimum = evaluate_universal_effective_horizon_profile(
                            n,
                            p.numerator,
                            p.denominator,
                            c.numerator,
                            c.denominator,
                            m.numerator,
                            m.denominator,
                            minimum_live_deadline_ticks,
                        )
                        if not bool(at_minimum['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveMinimumDeadlineLawError('finite universal minimum live deadline failed to preserve')
                        if minimum_live_deadline_ticks > 1:
                            before_minimum = evaluate_universal_effective_horizon_profile(
                                n,
                                p.numerator,
                                p.denominator,
                                c.numerator,
                                c.denominator,
                                m.numerator,
                                m.denominator,
                                minimum_live_deadline_ticks - 1,
                            )
                            if bool(before_minimum['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveMinimumDeadlineLawError('finite universal predecessor deadline unexpectedly preserved')
                        even_partner = evaluate_universal_effective_horizon_profile(
                            n,
                            p.numerator,
                            p.denominator,
                            c.numerator,
                            c.denominator,
                            m.numerator,
                            m.denominator,
                            minimum_live_deadline_ticks + 1,
                        )
                        if bool(even_partner['live_countdown_preserves_original_margin']) != bool(at_minimum['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveMinimumDeadlineLawError('finite universal odd/even deadline pair mismatch at frontier')
                        universal_even_deadline_predecessor_equivalences += 1
                        if universal_finite_example is None and minimum_live_deadline_ticks > 1:
                            universal_finite_example = {
                                'minimum_live_deadline_profile': profile,
                                'live_profile_at_predecessor_even_deadline': before_minimum,
                                'live_profile_at_minimum_deadline': at_minimum,
                                'live_profile_at_equivalent_even_deadline': even_partner,
                            }
                    else:
                        if minimum_live_deadline_ticks is not None:
                            raise GeometricArrivalLiveMinimumDeadlineLawError('nonfinite universal context should not have finite minimum live deadline')
                        if schedule_class == 'asymptotic_only':
                            positive_asymptotic_universal_contexts += 1
                        elif schedule_class == 'impossible':
                            positive_impossible_universal_contexts += 1
                        else:
                            raise GeometricArrivalLiveMinimumDeadlineLawError(f'unexpected universal schedule class {schedule_class}')
                        if universal_nonfinite_example is None:
                            universal_nonfinite_example = {
                                'minimum_live_deadline_profile': profile,
                            }

    if state_zero_example is None or state_finite_example is None or state_nonfinite_example is None:
        raise GeometricArrivalLiveMinimumDeadlineLawError('missing state witness example')
    if universal_zero_example is None or universal_finite_example is None or universal_nonfinite_example is None:
        raise GeometricArrivalLiveMinimumDeadlineLawError('missing universal witness example')

    return {
        'audited_state_count': len(STATE_GRID),
        'audited_batch_lengths': list(BATCH_GRID),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in ARRIVAL_GRID],
        'audited_hold_costs': [_serialize_fraction(value) for value in HOLD_COST_GRID],
        'audited_target_margins': [_serialize_fraction(value) for value in TARGET_MARGIN_GRID],
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'positive_finite_state_contexts': positive_finite_state_contexts,
        'positive_asymptotic_state_contexts': positive_asymptotic_state_contexts,
        'positive_impossible_state_contexts': positive_impossible_state_contexts,
        'positive_finite_universal_contexts': positive_finite_universal_contexts,
        'positive_asymptotic_universal_contexts': positive_asymptotic_universal_contexts,
        'positive_impossible_universal_contexts': positive_impossible_universal_contexts,
        'zero_margin_state_contexts': zero_margin_state_contexts,
        'zero_margin_universal_contexts': zero_margin_universal_contexts,
        'odd_minimum_state_deadlines': odd_minimum_state_deadlines,
        'odd_minimum_universal_deadlines': odd_minimum_universal_deadlines,
        'state_even_deadline_predecessor_equivalences': state_even_deadline_predecessor_equivalences,
        'universal_even_deadline_predecessor_equivalences': universal_even_deadline_predecessor_equivalences,
        'state_zero_margin_example': state_zero_example,
        'state_positive_finite_example': state_finite_example,
        'state_positive_nonfinite_example': state_nonfinite_example,
        'universal_zero_margin_example': universal_zero_example,
        'universal_positive_finite_example': universal_finite_example,
        'universal_positive_nonfinite_example': universal_nonfinite_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_minimum_deadline_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_minimum_deadline_validation_summary()
    return {
        'focus': 'turn same-deadline stateless live control into a direct minimum nominal deadline rule for positive promises and a one-tick zero-floor shortcut',
        'headline_findings': {
            'positive_minimum_live_deadline_rule': 'for positive margin floors with finite blind minimum timeout K, the minimum same-deadline live deadline is exactly 2K - 1',
            'odd_entry_rule': 'every finite positive same-deadline live promise enters on an odd deadline, never uniquely on an even one',
            'zero_margin_rule': 'for zero margin floors, the minimum same-deadline live deadline is 1 because immediate close is already safe',
            'positive_finite_state_contexts': summary['positive_finite_state_contexts'],
            'positive_finite_universal_contexts': summary['positive_finite_universal_contexts'],
            'positive_asymptotic_state_contexts': summary['positive_asymptotic_state_contexts'],
            'positive_impossible_state_contexts': summary['positive_impossible_state_contexts'],
        },
        'decision_rules': [
            'For positive margin floors, first solve the blind minimum timeout K for the batch promise; the minimum same-deadline stateless live deadline is then exactly 2K - 1.',
            'Equivalently, same-deadline live promise admission lives on the odd ladder 1, 3, 5, ...; even deadlines are never uniquely minimal because 2j and 2j - 1 preserve the same promise class.',
            'If the positive blind schedule is asymptotic-only or impossible, there is no finite same-deadline live deadline that preserves the original promise.',
            'At zero margin floor, the controller can close immediately, so the minimum same-deadline live deadline collapses to 1 for every batch and state context.',
            'The same odd-ladder minimum-deadline law holds under the seven-bit all-state lower envelope.',
        ],
        'state_zero_margin_example': summary['state_zero_margin_example'],
        'state_positive_finite_example': summary['state_positive_finite_example'],
        'state_positive_nonfinite_example': summary['state_positive_nonfinite_example'],
        'universal_zero_margin_example': summary['universal_zero_margin_example'],
        'universal_positive_finite_example': summary['universal_positive_finite_example'],
        'universal_positive_nonfinite_example': summary['universal_positive_nonfinite_example'],
        'validation_summary': {key: value for key, value in summary.items() if 'example' not in key},
        'source_reports': [
            'artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_minimum_deadline_law.py',
    }


def main() -> None:
    print(json.dumps(build_geometric_arrival_live_minimum_deadline_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
