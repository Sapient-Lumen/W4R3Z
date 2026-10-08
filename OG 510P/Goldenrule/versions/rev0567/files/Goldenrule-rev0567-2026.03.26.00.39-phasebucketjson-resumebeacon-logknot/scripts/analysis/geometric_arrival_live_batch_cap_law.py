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
    compute_maximum_batch_length_for_state_timeout_target_margin,
    compute_universal_maximum_batch_length_for_timeout_target_margin,
)


class GeometricArrivalLiveBatchCapLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 13))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
POSITIVE_TARGET_MARGIN_GRID = TARGET_MARGIN_GRID[1:]
NOMINAL_HORIZON_GRID = tuple(range(1, 9))


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _effective_horizon(nominal_horizon_ticks: int) -> int:
    return (nominal_horizon_ticks + 1) // 2


@lru_cache(maxsize=None)
def compute_state_live_maximum_batch_length(
    state: tuple[int, int],
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    nominal_horizon_ticks: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    arrival_probability = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)

    if target_margin == 0:
        return {
            'state': list(state),
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
            'effective_blind_horizon_ticks': int(effective_horizon_ticks),
            'target_margin_bits_per_script': _serialize_fraction(target_margin),
            'maximum_admissible_batch_length': None,
            'unbounded_batch_cap': True,
            'controller_equivalence': 'same-deadline live control is as promise-safe as choosing the better of immediate close and blind commit with effective horizon floor((H + 1) / 2)',
            'reason': 'zero_margin_floor_makes_every_batch_safe_because_immediate_close_meets_the_floor',
        }

    blind_schedule = compute_maximum_batch_length_for_state_timeout_target_margin(
        state,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        effective_horizon_ticks,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    return {
        'state': list(state),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'maximum_admissible_batch_length': blind_schedule['maximum_admissible_batch_length'],
        'unbounded_batch_cap': bool(blind_schedule['unbounded_batch_cap']),
        'effective_timeout_batch_cap_condition': blind_schedule['batch_cap_condition'],
        'reason': 'positive_live_batch_cap_equals_blind_batch_cap_at_effective_horizon',
    }


@lru_cache(maxsize=None)
def compute_universal_live_maximum_batch_length(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    nominal_horizon_ticks: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    arrival_probability = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)

    if target_margin == 0:
        return {
            'guarantee_scope': 'all_realized_states',
            'guarantee_state_prefix_bits': 7,
            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
            'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
            'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
            'effective_blind_horizon_ticks': int(effective_horizon_ticks),
            'target_margin_bits_per_script': _serialize_fraction(target_margin),
            'maximum_admissible_batch_length': None,
            'unbounded_batch_cap': True,
            'controller_equivalence': 'same-deadline live control is as universal-promise-safe as choosing the better of immediate close and blind commit with effective horizon floor((H + 1) / 2)',
            'reason': 'zero_margin_floor_makes_every_batch_universally_safe_because_immediate_close_meets_the_floor',
        }

    blind_schedule = compute_universal_maximum_batch_length_for_timeout_target_margin(
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        effective_horizon_ticks,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'maximum_admissible_batch_length': blind_schedule['maximum_admissible_batch_length'],
        'unbounded_batch_cap': bool(blind_schedule['unbounded_batch_cap']),
        'effective_timeout_batch_cap_condition': blind_schedule['batch_cap_condition'],
        'reason': 'positive_universal_live_batch_cap_equals_blind_batch_cap_at_effective_horizon',
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_batch_cap_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    validated_state_frontier_checks = 0
    validated_universal_frontier_checks = 0
    positive_state_feasible_contexts = 0
    positive_state_impossible_contexts = 0
    positive_universal_feasible_contexts = 0
    positive_universal_impossible_contexts = 0
    zero_margin_state_contexts = 0
    zero_margin_universal_contexts = 0
    state_deadline_ladders = 0
    state_deadline_ladders_with_growth = 0
    universal_deadline_ladders = 0
    universal_deadline_ladders_with_growth = 0
    state_odd_even_pair_plateaus = 0
    universal_odd_even_pair_plateaus = 0

    for state in STATE_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    prior_cap: int | None = None
                    prior_unbounded: bool | None = None
                    ladder_values: list[int] = []
                    for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                        cap_profile = compute_state_live_maximum_batch_length(
                            state,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            nominal_horizon_ticks,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        unbounded = bool(cap_profile['unbounded_batch_cap'])
                        max_batch = cap_profile['maximum_admissible_batch_length']
                        if target_margin == 0:
                            if not unbounded:
                                raise GeometricArrivalLiveBatchCapLawError(
                                    f'zero-margin live cap unexpectedly bounded for state {state}, p={arrival_probability}, c={hold_cost}, H={nominal_horizon_ticks}'
                                )
                            zero_margin_state_contexts += 1
                            sample_batch = BATCH_GRID[-1]
                            actual = bool(
                                evaluate_state_effective_horizon_profile(
                                    state,
                                    sample_batch,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )['live_countdown_preserves_original_margin']
                            )
                            if not actual:
                                raise GeometricArrivalLiveBatchCapLawError(
                                    f'zero-margin live controller unexpectedly rejected state {state}, p={arrival_probability}, c={hold_cost}, H={nominal_horizon_ticks}, n={sample_batch}'
                                )
                            validated_state_frontier_checks += 1
                        else:
                            if unbounded:
                                raise GeometricArrivalLiveBatchCapLawError(
                                    f'positive-margin live cap unexpectedly unbounded for state {state}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )
                            assert max_batch is not None
                            max_batch_int = int(max_batch)
                            ladder_values.append(max_batch_int)
                            if max_batch_int >= 1:
                                positive_state_feasible_contexts += 1
                                frontier_actual = bool(
                                    evaluate_state_effective_horizon_profile(
                                        state,
                                        max_batch_int,
                                        arrival_probability.numerator,
                                        arrival_probability.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        target_margin.numerator,
                                        target_margin.denominator,
                                        nominal_horizon_ticks,
                                    )['live_countdown_preserves_original_margin']
                                )
                                if not frontier_actual:
                                    raise GeometricArrivalLiveBatchCapLawError(
                                        f'state live cap frontier unexpectedly failed at state {state}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}, n={max_batch_int}'
                                    )
                                validated_state_frontier_checks += 1
                            else:
                                positive_state_impossible_contexts += 1
                            next_actual = bool(
                                evaluate_state_effective_horizon_profile(
                                    state,
                                    max_batch_int + 1,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )['live_countdown_preserves_original_margin']
                            )
                            if next_actual:
                                raise GeometricArrivalLiveBatchCapLawError(
                                    f'state live cap next batch unexpectedly preserved margin for state {state}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}, n={max_batch_int + 1}'
                                )
                            validated_state_frontier_checks += 1

                        if nominal_horizon_ticks % 2 == 0:
                            if prior_unbounded != unbounded or prior_cap != max_batch:
                                raise GeometricArrivalLiveBatchCapLawError(
                                    f'state odd-even live cap plateau failed for state {state}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                                )
                            state_odd_even_pair_plateaus += 1
                        prior_cap = None if max_batch is None else int(max_batch)
                        prior_unbounded = unbounded
                        validated_state_contexts += 1

                    if target_margin > 0:
                        if ladder_values != sorted(ladder_values):
                            raise GeometricArrivalLiveBatchCapLawError(
                                f'state live cap ladder is not monotone for state {state}, p={arrival_probability}, c={hold_cost}, m={target_margin}'
                            )
                        if len(set(ladder_values)) > 1:
                            state_deadline_ladders_with_growth += 1
                        state_deadline_ladders += 1

    for arrival_probability in ARRIVAL_GRID:
        for hold_cost in HOLD_COST_GRID:
            for target_margin in TARGET_MARGIN_GRID:
                prior_cap = None
                prior_unbounded = None
                ladder_values = []
                for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                    cap_profile = compute_universal_live_maximum_batch_length(
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        nominal_horizon_ticks,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    unbounded = bool(cap_profile['unbounded_batch_cap'])
                    max_batch = cap_profile['maximum_admissible_batch_length']
                    if target_margin == 0:
                        if not unbounded:
                            raise GeometricArrivalLiveBatchCapLawError(
                                f'zero-margin universal live cap unexpectedly bounded for p={arrival_probability}, c={hold_cost}, H={nominal_horizon_ticks}'
                            )
                        zero_margin_universal_contexts += 1
                        sample_batch = BATCH_GRID[-1]
                        actual = bool(
                            evaluate_universal_effective_horizon_profile(
                                sample_batch,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                nominal_horizon_ticks,
                            )['live_countdown_preserves_original_margin']
                        )
                        if not actual:
                            raise GeometricArrivalLiveBatchCapLawError(
                                f'zero-margin universal live controller unexpectedly rejected p={arrival_probability}, c={hold_cost}, H={nominal_horizon_ticks}, n={sample_batch}'
                            )
                        validated_universal_frontier_checks += 1
                    else:
                        if unbounded:
                            raise GeometricArrivalLiveBatchCapLawError(
                                f'positive-margin universal live cap unexpectedly unbounded for p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                            )
                        assert max_batch is not None
                        max_batch_int = int(max_batch)
                        ladder_values.append(max_batch_int)
                        if max_batch_int >= 1:
                            positive_universal_feasible_contexts += 1
                            frontier_actual = bool(
                                evaluate_universal_effective_horizon_profile(
                                    max_batch_int,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )['live_countdown_preserves_original_margin']
                            )
                            if not frontier_actual:
                                raise GeometricArrivalLiveBatchCapLawError(
                                    f'universal live cap frontier unexpectedly failed for p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}, n={max_batch_int}'
                                )
                            validated_universal_frontier_checks += 1
                        else:
                            positive_universal_impossible_contexts += 1
                        next_actual = bool(
                            evaluate_universal_effective_horizon_profile(
                                max_batch_int + 1,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                nominal_horizon_ticks,
                            )['live_countdown_preserves_original_margin']
                        )
                        if next_actual:
                            raise GeometricArrivalLiveBatchCapLawError(
                                f'universal live cap next batch unexpectedly preserved margin for p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}, n={max_batch_int + 1}'
                            )
                        validated_universal_frontier_checks += 1

                    if nominal_horizon_ticks % 2 == 0:
                        if prior_unbounded != unbounded or prior_cap != max_batch:
                            raise GeometricArrivalLiveBatchCapLawError(
                                f'universal odd-even live cap plateau failed for p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                            )
                        universal_odd_even_pair_plateaus += 1
                    prior_cap = None if max_batch is None else int(max_batch)
                    prior_unbounded = unbounded
                    validated_universal_contexts += 1

                if target_margin > 0:
                    if ladder_values != sorted(ladder_values):
                        raise GeometricArrivalLiveBatchCapLawError(
                            f'universal live cap ladder is not monotone for p={arrival_probability}, c={hold_cost}, m={target_margin}'
                        )
                    if len(set(ladder_values)) > 1:
                        universal_deadline_ladders_with_growth += 1
                    universal_deadline_ladders += 1

    return {
        'audited_state_count': len(STATE_GRID),
        'audited_batch_lengths': list(BATCH_GRID),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in ARRIVAL_GRID],
        'audited_hold_costs': [_serialize_fraction(value) for value in HOLD_COST_GRID],
        'audited_target_margins': [_serialize_fraction(value) for value in TARGET_MARGIN_GRID],
        'audited_nominal_live_deadlines': list(NOMINAL_HORIZON_GRID),
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'validated_state_frontier_checks': validated_state_frontier_checks,
        'validated_universal_frontier_checks': validated_universal_frontier_checks,
        'positive_state_feasible_contexts': positive_state_feasible_contexts,
        'positive_state_impossible_contexts': positive_state_impossible_contexts,
        'positive_universal_feasible_contexts': positive_universal_feasible_contexts,
        'positive_universal_impossible_contexts': positive_universal_impossible_contexts,
        'zero_margin_state_contexts': zero_margin_state_contexts,
        'zero_margin_universal_contexts': zero_margin_universal_contexts,
        'validated_state_deadline_ladders': state_deadline_ladders,
        'state_deadline_ladders_with_growth': state_deadline_ladders_with_growth,
        'validated_universal_deadline_ladders': universal_deadline_ladders,
        'universal_deadline_ladders_with_growth': universal_deadline_ladders_with_growth,
        'state_odd_even_pair_plateaus': state_odd_even_pair_plateaus,
        'universal_odd_even_pair_plateaus': universal_odd_even_pair_plateaus,
    }


@lru_cache(maxsize=None)
def _find_state_profile(*, positive_margin: bool, preserved: bool, nominal_horizon_ticks: int) -> dict[str, Any]:
    target_grid = POSITIVE_TARGET_MARGIN_GRID if positive_margin else (Fraction(0, 1),)
    for state in STATE_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in target_grid:
                    cap_profile = compute_state_live_maximum_batch_length(
                        state,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        nominal_horizon_ticks,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    if positive_margin:
                        max_batch = int(cap_profile['maximum_admissible_batch_length'])
                        batch = max(1, max_batch) if preserved else max_batch + 1
                    else:
                        batch = 12
                    actual = evaluate_state_effective_horizon_profile(
                        state,
                        batch,
                        arrival_probability.numerator,
                        arrival_probability.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                        nominal_horizon_ticks,
                    )
                    if bool(actual['live_countdown_preserves_original_margin']) == preserved:
                        return {
                            'cap_profile': cap_profile,
                            'batch_length_checked': batch,
                            'live_profile': actual,
                        }
    raise GeometricArrivalLiveBatchCapLawError(
        f'could not find state example with positive_margin={positive_margin}, preserved={preserved}, H={nominal_horizon_ticks}'
    )


@lru_cache(maxsize=None)
def _find_universal_profile(*, positive_margin: bool, preserved: bool, nominal_horizon_ticks: int) -> dict[str, Any]:
    target_grid = POSITIVE_TARGET_MARGIN_GRID if positive_margin else (Fraction(0, 1),)
    for arrival_probability in ARRIVAL_GRID:
        for hold_cost in HOLD_COST_GRID:
            for target_margin in target_grid:
                cap_profile = compute_universal_live_maximum_batch_length(
                    arrival_probability.numerator,
                    arrival_probability.denominator,
                    hold_cost.numerator,
                    hold_cost.denominator,
                    nominal_horizon_ticks,
                    target_margin.numerator,
                    target_margin.denominator,
                )
                if positive_margin:
                    max_batch = int(cap_profile['maximum_admissible_batch_length'])
                    batch = max(1, max_batch) if preserved else max_batch + 1
                else:
                    batch = 12
                actual = evaluate_universal_effective_horizon_profile(
                    batch,
                    arrival_probability.numerator,
                    arrival_probability.denominator,
                    hold_cost.numerator,
                    hold_cost.denominator,
                    target_margin.numerator,
                    target_margin.denominator,
                    nominal_horizon_ticks,
                )
                if bool(actual['live_countdown_preserves_original_margin']) == preserved:
                    return {
                        'cap_profile': cap_profile,
                        'batch_length_checked': batch,
                        'live_profile': actual,
                    }
    raise GeometricArrivalLiveBatchCapLawError(
        f'could not find universal example with positive_margin={positive_margin}, preserved={preserved}, H={nominal_horizon_ticks}'
    )


@lru_cache(maxsize=1)
def build_geometric_arrival_live_batch_cap_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_batch_cap_validation_summary()
    return {
        'focus': 'turn same-deadline stateless live control into a direct admissible batch-length cap without first solving timeout promises batch by batch',
        'headline_findings': {
            'positive_live_batch_cap_rule': 'for positive margin floors, nominal live deadline H has exactly the blind-commit batch cap at effective horizon floor((H + 1) / 2)',
            'zero_margin_degeneracy': 'for zero margin floors, every batch is safe because immediate close already meets the floor',
            'odd_even_pair_rule': 'deadlines 2j-1 and 2j have identical live batch caps',
            'state_positive_feasible_contexts': summary['positive_state_feasible_contexts'],
            'state_positive_impossible_contexts': summary['positive_state_impossible_contexts'],
            'universal_positive_feasible_contexts': summary['positive_universal_feasible_contexts'],
            'universal_positive_impossible_contexts': summary['positive_universal_impossible_contexts'],
        },
        'decision_rules': [
            'For positive margin floors m > 0, the same-deadline live admissible batch cap is the largest n with n(n+1) <= p * state_prefix_bits / (hold_cost + p * m / (1 - (1 - p)^floor((H + 1) / 2))).',
            'So an implementor can reuse the earlier fixed-timeout batch-cap law exactly by substituting effective timeout floor((H + 1) / 2) for the nominal live deadline H.',
            'Deadlines 1 and 2 therefore admit the same positive live batch cap, deadlines 3 and 4 admit the same next cap, and so on.',
            'At zero margin floor, immediate close makes every batch admissible under the live controller, so the promise-safe live cap is unbounded in n.',
            'The all-state guardrail is the same formula with state_prefix_bits replaced by the exact seven-bit lower envelope on the current path.',
        ],
        'state_positive_preserved_example': _find_state_profile(positive_margin=True, preserved=True, nominal_horizon_ticks=3),
        'state_positive_rejected_example': _find_state_profile(positive_margin=True, preserved=False, nominal_horizon_ticks=2),
        'state_zero_margin_example': _find_state_profile(positive_margin=False, preserved=True, nominal_horizon_ticks=1),
        'universal_positive_preserved_example': _find_universal_profile(positive_margin=True, preserved=True, nominal_horizon_ticks=3),
        'universal_positive_rejected_example': _find_universal_profile(positive_margin=True, preserved=False, nominal_horizon_ticks=2),
        'universal_zero_margin_example': _find_universal_profile(positive_margin=False, preserved=True, nominal_horizon_ticks=1),
        'validation_summary': summary,
        'source_reports': [
            'artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_batch_cap_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_geometric_arrival_live_batch_cap_snapshot(), indent=2, sort_keys=True))
