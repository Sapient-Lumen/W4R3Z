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


class GeometricArrivalEffectiveHorizonLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
NOMINAL_HORIZON_GRID = tuple(range(1, 7))


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


def _effective_horizon(nominal_horizon_ticks: int) -> int:
    return (nominal_horizon_ticks + 1) // 2


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
        raise GeometricArrivalEffectiveHorizonLawError('state wait-value payload unexpectedly omitted exact value')
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
def evaluate_state_effective_horizon_profile(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    arrival_probability = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)

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
    schedule_class = (
        'finite'
        if bool(schedule['finite_timeout_exists'])
        else 'asymptotic_only'
        if bool(schedule['asymptotically_feasible'])
        else 'impossible'
    )
    minimum_timeout_ticks = schedule['minimum_timeout_ticks']
    blind_effective_value = _fixed_timeout_value_for_state(
        state,
        current_batch_length,
        arrival_probability,
        hold_cost,
        effective_horizon_ticks,
    )
    countdown_profile = evaluate_state_countdown_reserve_profile(
        state,
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
        nominal_horizon_ticks,
    )
    live_value = _deserialize_fraction(countdown_profile['live_countdown_policy_value_bits_per_script'])
    if live_value is None:
        raise GeometricArrivalEffectiveHorizonLawError('state countdown payload unexpectedly omitted exact live value')

    live_preserves_margin = bool(countdown_profile['live_countdown_policy_meets_original_margin_floor'])
    close_or_blind_effective_value = max(Fraction(0, 1), blind_effective_value)
    blind_effective_preserves_margin = blind_effective_value >= target_margin
    close_or_blind_effective_preserves_margin = close_or_blind_effective_value >= target_margin
    if live_preserves_margin != close_or_blind_effective_preserves_margin:
        raise GeometricArrivalEffectiveHorizonLawError(
            f'effective-horizon mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
        )

    if schedule_class == 'finite':
        expected_live_preserves_margin = nominal_horizon_ticks >= 2 * int(minimum_timeout_ticks) - 1
        if live_preserves_margin != expected_live_preserves_margin:
            raise GeometricArrivalEffectiveHorizonLawError(
                f'state live preservation boundary mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
            )
    else:
        expected_live_preserves_margin = live_preserves_margin

    return {
        'state': list(state),
        'state_prefix_bits': int(sum(state)),
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_commit_horizon_ticks': int(effective_horizon_ticks),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': minimum_timeout_ticks,
        'live_countdown_preserves_original_margin': live_preserves_margin,
        'blind_commit_at_effective_horizon_preserves_original_margin': blind_effective_preserves_margin,
        'close_or_blind_effective_horizon_preserves_original_margin': close_or_blind_effective_preserves_margin,
        'live_countdown_value_bits_per_script': _serialize_fraction(live_value),
        'blind_commit_value_at_effective_horizon_bits_per_script': _serialize_fraction(blind_effective_value),
        'close_or_blind_value_at_effective_horizon_bits_per_script': _serialize_fraction(close_or_blind_effective_value),
        'effective_horizon_formula': 'for nonnegative margin floors, same-deadline stateless live reoptimization is exactly as promise-safe as choosing the better of immediate close and blind commit with horizon floor((H + 1) / 2); for positive promises this reduces to blind commit with that effective horizon',
        'pair_collapse_rule': 'nominal live deadlines 2j-1 and 2j have the same promise-safe effective blind horizon j',
        'reason': (
            'same_deadline_live_reoptimization_is_exactly_as_promise_safe_as_blind_commit_with_half_up_rounded_down_horizon'
            if live_preserves_margin
            else 'nominal_live_deadline_lacks_enough_effective_blind_horizon_to_preserve_the_original_promise'
        ),
    }


@lru_cache(maxsize=None)
def evaluate_universal_effective_horizon_profile(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    arrival_probability = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)

    schedule = compute_universal_minimum_timeout_for_batch_target_margin(
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    schedule_class = (
        'finite'
        if bool(schedule['finite_timeout_exists'])
        else 'asymptotic_only'
        if bool(schedule['asymptotically_feasible'])
        else 'impossible'
    )
    minimum_timeout_ticks = schedule['minimum_timeout_ticks']
    blind_effective_value = _fixed_timeout_value_for_universal(
        current_batch_length,
        arrival_probability,
        hold_cost,
        effective_horizon_ticks,
    )
    countdown_profile = evaluate_universal_countdown_reserve_profile(
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
        nominal_horizon_ticks,
    )
    live_value = _deserialize_fraction(countdown_profile['live_countdown_policy_value_bits_per_script'])
    if live_value is None:
        raise GeometricArrivalEffectiveHorizonLawError('universal countdown payload unexpectedly omitted exact live value')

    live_preserves_margin = bool(countdown_profile['live_countdown_policy_meets_original_margin_floor'])
    close_or_blind_effective_value = max(Fraction(0, 1), blind_effective_value)
    blind_effective_preserves_margin = blind_effective_value >= target_margin
    close_or_blind_effective_preserves_margin = close_or_blind_effective_value >= target_margin
    if live_preserves_margin != close_or_blind_effective_preserves_margin:
        raise GeometricArrivalEffectiveHorizonLawError(
            f'universal effective-horizon mismatch for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
        )

    if schedule_class == 'finite':
        expected_live_preserves_margin = nominal_horizon_ticks >= 2 * int(minimum_timeout_ticks) - 1
        if live_preserves_margin != expected_live_preserves_margin:
            raise GeometricArrivalEffectiveHorizonLawError(
                f'universal live preservation boundary mismatch for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
            )
    else:
        expected_live_preserves_margin = live_preserves_margin

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_commit_horizon_ticks': int(effective_horizon_ticks),
        'schedule_class': schedule_class,
        'minimum_timeout_ticks_for_blind_commit_margin': minimum_timeout_ticks,
        'live_countdown_preserves_original_margin': live_preserves_margin,
        'blind_commit_at_effective_horizon_preserves_original_margin': blind_effective_preserves_margin,
        'close_or_blind_effective_horizon_preserves_original_margin': close_or_blind_effective_preserves_margin,
        'live_countdown_value_bits_per_script': _serialize_fraction(live_value),
        'blind_commit_value_at_effective_horizon_bits_per_script': _serialize_fraction(blind_effective_value),
        'close_or_blind_value_at_effective_horizon_bits_per_script': _serialize_fraction(close_or_blind_effective_value),
        'effective_horizon_formula': 'for nonnegative margin floors, same-deadline stateless live reoptimization is exactly as universal-promise-safe as choosing the better of immediate close and blind commit with horizon floor((H + 1) / 2); for positive promises this reduces to blind commit with that effective horizon',
        'pair_collapse_rule': 'nominal live deadlines 2j-1 and 2j have the same universal promise-safe effective blind horizon j',
        'reason': (
            'same_deadline_live_reoptimization_is_exactly_as_universal_promise_safe_as_blind_commit_with_half_up_rounded_down_horizon'
            if live_preserves_margin
            else 'nominal_live_deadline_lacks_enough_universal_effective_blind_horizon_to_preserve_the_original_promise'
        ),
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_effective_horizon_validation_summary() -> dict[str, Any]:
    validated_state_panels = 0
    validated_universal_panels = 0
    state_preserved_panels = 0
    state_not_preserved_panels = 0
    universal_preserved_panels = 0
    universal_not_preserved_panels = 0
    state_pair_equivalent_panels = 0
    universal_pair_equivalent_panels = 0

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        prior_live_decision: bool | None = None
                        for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                            profile = evaluate_state_effective_horizon_profile(
                                state,
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                nominal_horizon_ticks,
                            )
                            if bool(profile['live_countdown_preserves_original_margin']):
                                state_preserved_panels += 1
                            else:
                                state_not_preserved_panels += 1
                            if nominal_horizon_ticks % 2 == 0:
                                assert prior_live_decision is not None
                                if prior_live_decision != bool(profile['live_countdown_preserves_original_margin']):
                                    raise GeometricArrivalEffectiveHorizonLawError(
                                        f'state odd-even deadline pair unexpectedly changed promise-safe decision for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                                    )
                                state_pair_equivalent_panels += 1
                            prior_live_decision = bool(profile['live_countdown_preserves_original_margin'])
                            validated_state_panels += 1

    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    prior_live_decision = None
                    for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                        profile = evaluate_universal_effective_horizon_profile(
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        if bool(profile['live_countdown_preserves_original_margin']):
                            universal_preserved_panels += 1
                        else:
                            universal_not_preserved_panels += 1
                        if nominal_horizon_ticks % 2 == 0:
                            assert prior_live_decision is not None
                            if prior_live_decision != bool(profile['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalEffectiveHorizonLawError(
                                    f'universal odd-even deadline pair unexpectedly changed promise-safe decision for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                                )
                            universal_pair_equivalent_panels += 1
                        prior_live_decision = bool(profile['live_countdown_preserves_original_margin'])
                        validated_universal_panels += 1

    return {
        'audited_state_count': len(STATE_GRID),
        'validated_state_panels': validated_state_panels,
        'validated_universal_panels': validated_universal_panels,
        'state_preserved_panels': state_preserved_panels,
        'state_not_preserved_panels': state_not_preserved_panels,
        'universal_preserved_panels': universal_preserved_panels,
        'universal_not_preserved_panels': universal_not_preserved_panels,
        'state_odd_even_pair_equivalent_panels': state_pair_equivalent_panels,
        'universal_odd_even_pair_equivalent_panels': universal_pair_equivalent_panels,
    }


@lru_cache(maxsize=None)
def _find_first_state_profile(*, preserved: bool, nominal_horizon_ticks: int) -> dict[str, Any]:
    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        profile = evaluate_state_effective_horizon_profile(
                            state,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        if bool(profile['live_countdown_preserves_original_margin']) == preserved:
                            return profile
    raise GeometricArrivalEffectiveHorizonLawError(
        f'could not find state example with preserved={preserved} at H={nominal_horizon_ticks}'
    )


@lru_cache(maxsize=None)
def _find_first_universal_profile(*, preserved: bool, nominal_horizon_ticks: int) -> dict[str, Any]:
    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    profile = evaluate_universal_effective_horizon_profile(
                        current_batch_length,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                        nominal_horizon_ticks,
                    )
                    if bool(profile['live_countdown_preserves_original_margin']) == preserved:
                        return profile
    raise GeometricArrivalEffectiveHorizonLawError(
        f'could not find universal example with preserved={preserved} at H={nominal_horizon_ticks}'
    )


@lru_cache(maxsize=1)
def build_geometric_arrival_effective_horizon_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_effective_horizon_validation_summary()
    return {
        'focus': 'show that same-deadline stateless live reoptimization is exactly as promise-safe as blind commit with effective horizon floor((H + 1) / 2), so only about half of a nominal deadline is truly promise-usable',
        'headline_findings': {
            'effective_horizon_rule': 'for positive promises, live deadline H preserves exactly the blind-commit promises with minimum timeout K <= floor((H + 1) / 2)',
            'controller_equivalence_rule': 'for nonnegative floors, a stateless live controller with nominal deadline H is equivalent to choosing the better of immediate close and blind commit with horizon floor((H + 1) / 2)',
            'odd_even_pair_rule': 'deadlines 2j-1 and 2j are promise-equivalent because both expose effective blind horizon j',
            'state_preserved_panels': summary['state_preserved_panels'],
            'universal_preserved_panels': summary['universal_preserved_panels'],
        },
        'decision_rules': [
            'When planning positive same-deadline stateless live promises, budget usable blind horizon as floor((H + 1) / 2) rather than as the full nominal deadline H.',
            'If a blind-commit promise needs minimum timeout K, then the same promise is safe under stateless live reoptimization only when nominal deadline H >= 2K - 1.',
            'So deadlines 1 and 2 support the same promise-safe class, deadlines 3 and 4 support the next class, and so on.',
            'Every second nominal deadline tick is therefore dead reserve when the implementation goal is exact positive-promise preservation rather than accepted drift.',
        ],
        'state_preserved_example': _find_first_state_profile(preserved=True, nominal_horizon_ticks=3),
        'state_not_preserved_example': _find_first_state_profile(preserved=False, nominal_horizon_ticks=2),
        'universal_preserved_example': _find_first_universal_profile(preserved=True, nominal_horizon_ticks=3),
        'universal_not_preserved_example': _find_first_universal_profile(preserved=False, nominal_horizon_ticks=2),
        'validation_summary': summary,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law_snapshot_20260316.md',
            'artifacts/reports/geometric_arrival_deadline_inflation_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_effective_horizon_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_geometric_arrival_effective_horizon_snapshot(), indent=2, sort_keys=True))
