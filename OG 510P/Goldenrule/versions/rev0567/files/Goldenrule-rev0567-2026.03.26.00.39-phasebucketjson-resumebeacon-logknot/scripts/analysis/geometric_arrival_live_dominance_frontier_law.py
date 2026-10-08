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


class GeometricArrivalLiveDominanceFrontierLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
PREFIX_BITS_GRID = tuple(range(0, 17))
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
POSITIVE_MARGIN_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
NOMINAL_HORIZON_GRID = tuple(range(1, 9))


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


@lru_cache(maxsize=None)
def _effective_horizon(nominal_horizon_ticks: int) -> int:
    return (nominal_horizon_ticks + 1) // 2


@lru_cache(maxsize=None)
def _capture_fraction(arrival_probability: Fraction, nominal_horizon_ticks: int) -> Fraction:
    return Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** _effective_horizon(nominal_horizon_ticks)


@lru_cache(maxsize=None)
def _margin_ceiling_from_prefix_bits(
    prefix_bits: int,
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> Fraction:
    if prefix_bits < 0:
        raise GeometricArrivalLiveDominanceFrontierLawError('prefix bits must be nonnegative')
    if current_batch_length <= 0:
        raise GeometricArrivalLiveDominanceFrontierLawError('batch length must be positive')
    if nominal_horizon_ticks <= 0:
        raise GeometricArrivalLiveDominanceFrontierLawError('nominal horizon must be positive')

    arrival_probability = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    if arrival_probability <= 0 or arrival_probability > 1:
        raise GeometricArrivalLiveDominanceFrontierLawError('arrival probability must lie in (0, 1]')
    if hold_cost < 0:
        raise GeometricArrivalLiveDominanceFrontierLawError('hold cost must be nonnegative')

    capture = _capture_fraction(arrival_probability, nominal_horizon_ticks)
    prefix_budget = Fraction(prefix_bits, current_batch_length * (current_batch_length + 1))
    raw_ceiling = capture * (prefix_budget - hold_cost / arrival_probability)
    return max(Fraction(0, 1), raw_ceiling)


@lru_cache(maxsize=None)
def compute_prefix_live_dominance_profile(
    prefix_bits: int,
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
    if target_margin <= 0:
        raise GeometricArrivalLiveDominanceFrontierLawError('dominance frontier law is only stated here for positive realized margins')

    ceiling = _margin_ceiling_from_prefix_bits(
        prefix_bits,
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        nominal_horizon_ticks,
    )
    admitted = ceiling >= target_margin
    return {
        'state_prefix_bits': int(prefix_bits),
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': _effective_horizon(nominal_horizon_ticks),
        'maximum_preservable_margin_bits_per_script': _serialize_fraction(ceiling),
        'positive_same_deadline_live_promise_is_safe': admitted,
        'dominance_frontier_rule': (
            'for positive realized margins, same-deadline live promise safety is monotone under favorable '
            'coordinatewise dominance: more prefix bits, higher arrival hazard, and longer nominal deadline help, '
            'while larger batch length, larger hold cost, and larger promised margin hurt'
        ),
        'pareto_compression_rule': (
            'accepted contexts stay accepted under favorable dominance and rejected contexts stay rejected under '
            'unfavorable dominance, so frontier tables may be stored only on Pareto boundaries'
        ),
        'reason': (
            'positive_same_deadline_live_margin_ceiling_covers_the_promised_margin'
            if admitted
            else 'promised_positive_margin_exceeds_the_exact_same_deadline_live_margin_ceiling'
        ),
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_dominance_frontier_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    state_prefix_reduction_matches = 0
    universal_prefix_reduction_matches = 0
    admitted_state_contexts = 0
    rejected_state_contexts = 0
    admitted_universal_contexts = 0
    rejected_universal_contexts = 0

    prefix_step_certificates = 0
    batch_step_certificates = 0
    arrival_step_certificates = 0
    hold_cost_step_certificates = 0
    margin_step_certificates = 0
    deadline_step_certificates = 0

    strict_prefix_gains = 0
    strict_batch_penalties = 0
    strict_arrival_gains = 0
    strict_hold_cost_penalties = 0
    strict_margin_penalties = 0
    strict_deadline_gains = 0

    prefix_gain_example: dict[str, Any] | None = None
    batch_penalty_example: dict[str, Any] | None = None
    arrival_gain_example: dict[str, Any] | None = None
    hold_cost_penalty_example: dict[str, Any] | None = None
    margin_penalty_example: dict[str, Any] | None = None
    deadline_gain_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        prefix_bits = _state_prefix_bits(state)
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in POSITIVE_MARGIN_GRID:
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
                            abstract_profile = compute_prefix_live_dominance_profile(
                                prefix_bits,
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                nominal_horizon_ticks,
                            )
                            validated_state_contexts += 1
                            state_safe = bool(profile['live_countdown_preserves_original_margin'])
                            abstract_safe = bool(abstract_profile['positive_same_deadline_live_promise_is_safe'])
                            if state_safe != abstract_safe:
                                raise GeometricArrivalLiveDominanceFrontierLawError(
                                    f'state prefix reduction mismatch for state {state}, n={current_batch_length}, '
                                    f'p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )
                            state_prefix_reduction_matches += 1
                            if state_safe:
                                admitted_state_contexts += 1
                            else:
                                rejected_state_contexts += 1

    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in POSITIVE_MARGIN_GRID:
                    for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                        universal_profile = evaluate_universal_effective_horizon_profile(
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        abstract_profile = compute_prefix_live_dominance_profile(
                            7,
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        validated_universal_contexts += 1
                        universal_safe = bool(universal_profile['live_countdown_preserves_original_margin'])
                        abstract_safe = bool(abstract_profile['positive_same_deadline_live_promise_is_safe'])
                        if universal_safe != abstract_safe:
                            raise GeometricArrivalLiveDominanceFrontierLawError(
                                f'universal prefix reduction mismatch for n={current_batch_length}, p={arrival_probability}, '
                                f'c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                            )
                        universal_prefix_reduction_matches += 1
                        if universal_safe:
                            admitted_universal_contexts += 1
                        else:
                            rejected_universal_contexts += 1

    for prefix_bits in PREFIX_BITS_GRID:
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in POSITIVE_MARGIN_GRID:
                        for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                            current = compute_prefix_live_dominance_profile(
                                prefix_bits,
                                current_batch_length,
                                arrival_probability.numerator,
                                arrival_probability.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                nominal_horizon_ticks,
                            )
                            current_safe = bool(current['positive_same_deadline_live_promise_is_safe'])

                            if prefix_bits + 1 in PREFIX_BITS_GRID:
                                better = compute_prefix_live_dominance_profile(
                                    prefix_bits + 1,
                                    current_batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )
                                better_safe = bool(better['positive_same_deadline_live_promise_is_safe'])
                                prefix_step_certificates += 1
                                if current_safe and not better_safe:
                                    raise GeometricArrivalLiveDominanceFrontierLawError('prefix-step admission regressed under more prefix bits')
                                if (not current_safe) and better_safe:
                                    strict_prefix_gains += 1
                                    if prefix_gain_example is None:
                                        prefix_gain_example = {
                                            'from': current,
                                            'to': better,
                                        }

                            if current_batch_length + 1 in BATCH_GRID:
                                worse = compute_prefix_live_dominance_profile(
                                    prefix_bits,
                                    current_batch_length + 1,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )
                                worse_safe = bool(worse['positive_same_deadline_live_promise_is_safe'])
                                batch_step_certificates += 1
                                if worse_safe and not current_safe:
                                    raise GeometricArrivalLiveDominanceFrontierLawError('batch-step admission improved under a larger batch length')
                                if current_safe and not worse_safe:
                                    strict_batch_penalties += 1
                                    if batch_penalty_example is None:
                                        batch_penalty_example = {
                                            'from': current,
                                            'to': worse,
                                        }

                            arrival_index = ARRIVAL_GRID.index(arrival_probability)
                            if arrival_index + 1 < len(ARRIVAL_GRID):
                                better_p = ARRIVAL_GRID[arrival_index + 1]
                                better = compute_prefix_live_dominance_profile(
                                    prefix_bits,
                                    current_batch_length,
                                    better_p.numerator,
                                    better_p.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )
                                better_safe = bool(better['positive_same_deadline_live_promise_is_safe'])
                                arrival_step_certificates += 1
                                if current_safe and not better_safe:
                                    raise GeometricArrivalLiveDominanceFrontierLawError('arrival-step admission regressed under higher arrival hazard')
                                if (not current_safe) and better_safe:
                                    strict_arrival_gains += 1
                                    if arrival_gain_example is None:
                                        arrival_gain_example = {
                                            'from': current,
                                            'to': better,
                                        }

                            hold_index = HOLD_COST_GRID.index(hold_cost)
                            if hold_index + 1 < len(HOLD_COST_GRID):
                                worse_cost = HOLD_COST_GRID[hold_index + 1]
                                worse = compute_prefix_live_dominance_profile(
                                    prefix_bits,
                                    current_batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    worse_cost.numerator,
                                    worse_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks,
                                )
                                worse_safe = bool(worse['positive_same_deadline_live_promise_is_safe'])
                                hold_cost_step_certificates += 1
                                if worse_safe and not current_safe:
                                    raise GeometricArrivalLiveDominanceFrontierLawError('hold-cost-step admission improved under higher hold cost')
                                if current_safe and not worse_safe:
                                    strict_hold_cost_penalties += 1
                                    if hold_cost_penalty_example is None:
                                        hold_cost_penalty_example = {
                                            'from': current,
                                            'to': worse,
                                        }

                            margin_index = POSITIVE_MARGIN_GRID.index(target_margin)
                            if margin_index + 1 < len(POSITIVE_MARGIN_GRID):
                                worse_margin = POSITIVE_MARGIN_GRID[margin_index + 1]
                                worse = compute_prefix_live_dominance_profile(
                                    prefix_bits,
                                    current_batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    worse_margin.numerator,
                                    worse_margin.denominator,
                                    nominal_horizon_ticks,
                                )
                                worse_safe = bool(worse['positive_same_deadline_live_promise_is_safe'])
                                margin_step_certificates += 1
                                if worse_safe and not current_safe:
                                    raise GeometricArrivalLiveDominanceFrontierLawError('margin-step admission improved under a larger promised margin')
                                if current_safe and not worse_safe:
                                    strict_margin_penalties += 1
                                    if margin_penalty_example is None:
                                        margin_penalty_example = {
                                            'from': current,
                                            'to': worse,
                                        }

                            if nominal_horizon_ticks + 1 in NOMINAL_HORIZON_GRID:
                                better = compute_prefix_live_dominance_profile(
                                    prefix_bits,
                                    current_batch_length,
                                    arrival_probability.numerator,
                                    arrival_probability.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    nominal_horizon_ticks + 1,
                                )
                                better_safe = bool(better['positive_same_deadline_live_promise_is_safe'])
                                deadline_step_certificates += 1
                                if current_safe and not better_safe:
                                    raise GeometricArrivalLiveDominanceFrontierLawError('deadline-step admission regressed under a longer nominal deadline')
                                if (not current_safe) and better_safe:
                                    strict_deadline_gains += 1
                                    if deadline_gain_example is None:
                                        deadline_gain_example = {
                                            'from': current,
                                            'to': better,
                                        }

    if prefix_gain_example is None or batch_penalty_example is None or arrival_gain_example is None:
        raise GeometricArrivalLiveDominanceFrontierLawError('expected strict dominance examples were not found')
    if hold_cost_penalty_example is None or margin_penalty_example is None or deadline_gain_example is None:
        raise GeometricArrivalLiveDominanceFrontierLawError('expected strict penalty/gain examples were not found')

    return {
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'state_prefix_reduction_matches': state_prefix_reduction_matches,
        'universal_prefix_reduction_matches': universal_prefix_reduction_matches,
        'admitted_state_contexts': admitted_state_contexts,
        'rejected_state_contexts': rejected_state_contexts,
        'admitted_universal_contexts': admitted_universal_contexts,
        'rejected_universal_contexts': rejected_universal_contexts,
        'prefix_step_certificates': prefix_step_certificates,
        'batch_step_certificates': batch_step_certificates,
        'arrival_step_certificates': arrival_step_certificates,
        'hold_cost_step_certificates': hold_cost_step_certificates,
        'margin_step_certificates': margin_step_certificates,
        'deadline_step_certificates': deadline_step_certificates,
        'strict_prefix_gains': strict_prefix_gains,
        'strict_batch_penalties': strict_batch_penalties,
        'strict_arrival_gains': strict_arrival_gains,
        'strict_hold_cost_penalties': strict_hold_cost_penalties,
        'strict_margin_penalties': strict_margin_penalties,
        'strict_deadline_gains': strict_deadline_gains,
        'prefix_gain_example': prefix_gain_example,
        'batch_penalty_example': batch_penalty_example,
        'arrival_gain_example': arrival_gain_example,
        'hold_cost_penalty_example': hold_cost_penalty_example,
        'margin_penalty_example': margin_penalty_example,
        'deadline_gain_example': deadline_gain_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_dominance_frontier_snapshot() -> dict[str, Any]:
    validation_summary = build_geometric_arrival_live_dominance_frontier_validation_summary()
    return {
        'focus': 'same-deadline live positive-promise safety forms a favorable-coordinate dominance orthant and compresses to Pareto frontiers',
        'headline_findings': {
            'positive_live_dominance_rule': (
                'more prefix bits, higher arrival hazard, and longer nominal deadline only help, while larger batch '
                'length, larger hold cost, and larger promised positive margin only hurt'
            ),
            'state_reduction_rule': 'state identity collapses to shared-prefix bits for positive same-deadline live admission',
            'pareto_storage_rule': 'accepted and rejected tables can be stored only on dominance frontiers instead of dense grids',
        },
        'decision_rules': [
            'admit a positive same-deadline live promise whenever the exact margin ceiling at the given context covers the target margin',
            'reuse any admitted context for every favorable coordinate lift: more prefix bits, higher arrival hazard, or longer deadline',
            'reuse any rejection for every unfavorable coordinate move: larger batch, larger hold cost, or larger promised margin',
            'compress cached controller tables to Pareto frontiers because interior dominated points add no new information',
            'for universal guarantees, apply the same dominance law at the seven-bit lower envelope',
        ],
        'validation_summary': validation_summary,
        'prefix_gain_example': validation_summary['prefix_gain_example'],
        'batch_penalty_example': validation_summary['batch_penalty_example'],
        'arrival_gain_example': validation_summary['arrival_gain_example'],
        'hold_cost_penalty_example': validation_summary['hold_cost_penalty_example'],
        'margin_penalty_example': validation_summary['margin_penalty_example'],
        'deadline_gain_example': validation_summary['deadline_gain_example'],
        'source_reports': [
            'artifacts/reports/geometric_arrival_live_margin_ceiling_law_snapshot_20260316.json',
            'artifacts/reports/geometric_arrival_live_prefix_floor_law_snapshot_20260316.json',
            'artifacts/reports/geometric_arrival_live_arrival_floor_law_snapshot_20260316.json',
            'artifacts/reports/geometric_arrival_live_minimum_deadline_law_snapshot_20260316.json',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_dominance_frontier_law.py',
    }


def main() -> None:
    json.dump(build_geometric_arrival_live_dominance_frontier_snapshot(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
