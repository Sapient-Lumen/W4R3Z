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


class GeometricArrivalLiveMarginCeilingLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
NOMINAL_HORIZON_GRID = tuple(range(1, 9))
BOUNDARY_EPSILON = Fraction(1, 1_000_000)


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
def compute_state_live_margin_ceiling(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    state_prefix_bits = _state_prefix_bits(state)
    capture_fraction = _capture_fraction(p, effective_horizon_ticks)
    gain_slope = Fraction(state_prefix_bits, current_batch_length * (current_batch_length + 1)) - hold_cost / p
    raw_ceiling = capture_fraction * gain_slope
    ceiling = max(Fraction(0, 1), raw_ceiling)

    return {
        'state': list(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'effective_capture_fraction': _serialize_fraction(capture_fraction),
        'raw_effective_blind_value_bits_per_script': _serialize_fraction(raw_ceiling),
        'maximum_preservable_nonnegative_margin_bits_per_script': _serialize_fraction(ceiling),
        'positive_margin_possible': ceiling > 0,
        'margin_ceiling_formula': (
            'same-deadline stateless live control can preserve original realized margin promises exactly up to '
            'max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p))'
        ),
        'effective_horizon_rule': (
            'the live margin ceiling is exactly the better-of-close-or-blind value at effective blind horizon '
            'floor((H + 1) / 2)'
        ),
        'reason': (
            'positive_live_margin_promises_are_available_up_to_the_exact_closed_form_ceiling'
            if ceiling > 0
            else 'same_deadline_live_control_can_only_preserve_zero_margin_because_close_now_is_the_only_safe_nonnegative_option'
        ),
    }


@lru_cache(maxsize=None)
def compute_universal_live_margin_ceiling(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    capture_fraction = _capture_fraction(p, effective_horizon_ticks)
    gain_slope = Fraction(7, current_batch_length * (current_batch_length + 1)) - hold_cost / p
    raw_ceiling = capture_fraction * gain_slope
    ceiling = max(Fraction(0, 1), raw_ceiling)

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'effective_capture_fraction': _serialize_fraction(capture_fraction),
        'raw_effective_blind_value_bits_per_script': _serialize_fraction(raw_ceiling),
        'maximum_preservable_nonnegative_margin_bits_per_script': _serialize_fraction(ceiling),
        'positive_margin_possible': ceiling > 0,
        'margin_ceiling_formula': (
            'same-deadline universal stateless live control can preserve realized margin promises exactly up to '
            'max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (7 / (n(n + 1)) - hold_cost / p))'
        ),
        'effective_horizon_rule': (
            'the universal live margin ceiling is exactly the better-of-close-or-blind value at effective blind horizon '
            'floor((H + 1) / 2)'
        ),
        'reason': (
            'positive_universal_live_margin_promises_are_available_up_to_the_exact_closed_form_ceiling'
            if ceiling > 0
            else 'same_deadline_universal_live_control_can_only_preserve_zero_margin_because_close_now_is_the_only_safe_nonnegative_option'
        ),
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_margin_ceiling_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    positive_state_ceiling_contexts = 0
    zero_only_state_contexts = 0
    positive_universal_ceiling_contexts = 0
    zero_only_universal_contexts = 0
    validated_state_boundary_checks = 0
    validated_universal_boundary_checks = 0
    state_deadline_ladders = 0
    state_deadline_ladders_with_strict_odd_growth = 0
    universal_deadline_ladders = 0
    universal_deadline_ladders_with_strict_odd_growth = 0
    state_odd_even_pair_plateaus = 0
    universal_odd_even_pair_plateaus = 0

    state_positive_example: dict[str, Any] | None = None
    state_zero_only_example: dict[str, Any] | None = None
    universal_positive_example: dict[str, Any] | None = None
    universal_zero_only_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for p in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    prior_ceiling: Fraction | None = None
                    saw_strict_odd_growth = False
                    for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                        profile = compute_state_live_margin_ceiling(
                            state,
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            nominal_horizon_ticks,
                        )
                        validated_state_contexts += 1
                        ceiling_payload = profile['maximum_preservable_nonnegative_margin_bits_per_script']
                        ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
                        raw_payload = profile['raw_effective_blind_value_bits_per_script']
                        raw_ceiling = Fraction(int(raw_payload['numerator']), int(raw_payload['denominator']))

                        if prior_ceiling is not None and ceiling < prior_ceiling:
                            raise GeometricArrivalLiveMarginCeilingLawError(
                                f'state margin ceiling ladder decreased for state {state}, n={current_batch_length}, p={p}, c={hold_cost}'
                            )
                        if nominal_horizon_ticks % 2 == 0:
                            if prior_ceiling is None or ceiling != prior_ceiling:
                                raise GeometricArrivalLiveMarginCeilingLawError(
                                    f'state odd/even margin ceiling plateau failed for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                                )
                            state_odd_even_pair_plateaus += 1
                        elif nominal_horizon_ticks > 1 and p < 1 and raw_ceiling > 0:
                            if prior_ceiling is None or ceiling <= prior_ceiling:
                                raise GeometricArrivalLiveMarginCeilingLawError(
                                    f'state live margin ceiling failed strict odd-step growth for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks-1}->{nominal_horizon_ticks}'
                                )
                            saw_strict_odd_growth = True

                        at_boundary = evaluate_state_effective_horizon_profile(
                            state,
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            ceiling.numerator,
                            ceiling.denominator,
                            nominal_horizon_ticks,
                        )
                        if not bool(at_boundary['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveMarginCeilingLawError(
                                f'state boundary margin unexpectedly failed for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks}'
                            )
                        above_boundary_margin = ceiling + BOUNDARY_EPSILON
                        above_boundary = evaluate_state_effective_horizon_profile(
                            state,
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            above_boundary_margin.numerator,
                            above_boundary_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        if bool(above_boundary['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveMarginCeilingLawError(
                                f'state above-boundary margin unexpectedly preserved for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks}'
                            )
                        validated_state_boundary_checks += 2

                        if ceiling > 0:
                            positive_state_ceiling_contexts += 1
                            if state_positive_example is None:
                                state_positive_example = {
                                    'margin_ceiling_profile': profile,
                                    'boundary_live_profile': at_boundary,
                                    'above_boundary_margin_bits_per_script': _serialize_fraction(above_boundary_margin),
                                    'above_boundary_live_profile': above_boundary,
                                }
                        else:
                            zero_only_state_contexts += 1
                            if state_zero_only_example is None:
                                state_zero_only_example = {
                                    'margin_ceiling_profile': profile,
                                    'boundary_live_profile': at_boundary,
                                    'above_boundary_margin_bits_per_script': _serialize_fraction(above_boundary_margin),
                                    'above_boundary_live_profile': above_boundary,
                                }

                        prior_ceiling = ceiling

                    state_deadline_ladders += 1
                    if saw_strict_odd_growth:
                        state_deadline_ladders_with_strict_odd_growth += 1

    for current_batch_length in BATCH_GRID:
        for p in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                prior_ceiling: Fraction | None = None
                saw_strict_odd_growth = False
                for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                    profile = compute_universal_live_margin_ceiling(
                        current_batch_length,
                        p.numerator,
                        p.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        nominal_horizon_ticks,
                    )
                    validated_universal_contexts += 1
                    ceiling_payload = profile['maximum_preservable_nonnegative_margin_bits_per_script']
                    ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
                    raw_payload = profile['raw_effective_blind_value_bits_per_script']
                    raw_ceiling = Fraction(int(raw_payload['numerator']), int(raw_payload['denominator']))

                    if prior_ceiling is not None and ceiling < prior_ceiling:
                        raise GeometricArrivalLiveMarginCeilingLawError(
                            f'universal margin ceiling ladder decreased for n={current_batch_length}, p={p}, c={hold_cost}'
                        )
                    if nominal_horizon_ticks % 2 == 0:
                        if prior_ceiling is None or ceiling != prior_ceiling:
                            raise GeometricArrivalLiveMarginCeilingLawError(
                                f'universal odd/even margin ceiling plateau failed for n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                            )
                        universal_odd_even_pair_plateaus += 1
                    elif nominal_horizon_ticks > 1 and p < 1 and raw_ceiling > 0:
                        if prior_ceiling is None or ceiling <= prior_ceiling:
                            raise GeometricArrivalLiveMarginCeilingLawError(
                                f'universal live margin ceiling failed strict odd-step growth for n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks-1}->{nominal_horizon_ticks}'
                            )
                        saw_strict_odd_growth = True

                    at_boundary = evaluate_universal_effective_horizon_profile(
                        current_batch_length,
                        p.numerator,
                        p.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        ceiling.numerator,
                        ceiling.denominator,
                        nominal_horizon_ticks,
                    )
                    if not bool(at_boundary['live_countdown_preserves_original_margin']):
                        raise GeometricArrivalLiveMarginCeilingLawError(
                            f'universal boundary margin unexpectedly failed for n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks}'
                        )
                    above_boundary_margin = ceiling + BOUNDARY_EPSILON
                    above_boundary = evaluate_universal_effective_horizon_profile(
                        current_batch_length,
                        p.numerator,
                        p.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        above_boundary_margin.numerator,
                        above_boundary_margin.denominator,
                        nominal_horizon_ticks,
                    )
                    if bool(above_boundary['live_countdown_preserves_original_margin']):
                        raise GeometricArrivalLiveMarginCeilingLawError(
                            f'universal above-boundary margin unexpectedly preserved for n={current_batch_length}, p={p}, c={hold_cost}, H={nominal_horizon_ticks}'
                        )
                    validated_universal_boundary_checks += 2

                    if ceiling > 0:
                        positive_universal_ceiling_contexts += 1
                        if universal_positive_example is None:
                            universal_positive_example = {
                                'margin_ceiling_profile': profile,
                                'boundary_live_profile': at_boundary,
                                'above_boundary_margin_bits_per_script': _serialize_fraction(above_boundary_margin),
                                'above_boundary_live_profile': above_boundary,
                            }
                    else:
                        zero_only_universal_contexts += 1
                        if universal_zero_only_example is None:
                            universal_zero_only_example = {
                                'margin_ceiling_profile': profile,
                                'boundary_live_profile': at_boundary,
                                'above_boundary_margin_bits_per_script': _serialize_fraction(above_boundary_margin),
                                'above_boundary_live_profile': above_boundary,
                            }

                    prior_ceiling = ceiling

                universal_deadline_ladders += 1
                if saw_strict_odd_growth:
                    universal_deadline_ladders_with_strict_odd_growth += 1

    if state_positive_example is None or state_zero_only_example is None:
        raise GeometricArrivalLiveMarginCeilingLawError('missing state witness example')
    if universal_positive_example is None or universal_zero_only_example is None:
        raise GeometricArrivalLiveMarginCeilingLawError('missing universal witness example')

    return {
        'audited_state_count': len(STATE_GRID),
        'audited_batch_lengths': list(BATCH_GRID),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in ARRIVAL_GRID],
        'audited_hold_costs': [_serialize_fraction(value) for value in HOLD_COST_GRID],
        'audited_nominal_live_deadlines': list(NOMINAL_HORIZON_GRID),
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'positive_state_ceiling_contexts': positive_state_ceiling_contexts,
        'zero_only_state_contexts': zero_only_state_contexts,
        'positive_universal_ceiling_contexts': positive_universal_ceiling_contexts,
        'zero_only_universal_contexts': zero_only_universal_contexts,
        'validated_state_boundary_checks': validated_state_boundary_checks,
        'validated_universal_boundary_checks': validated_universal_boundary_checks,
        'state_deadline_ladders': state_deadline_ladders,
        'state_deadline_ladders_with_strict_odd_growth': state_deadline_ladders_with_strict_odd_growth,
        'universal_deadline_ladders': universal_deadline_ladders,
        'universal_deadline_ladders_with_strict_odd_growth': universal_deadline_ladders_with_strict_odd_growth,
        'state_odd_even_pair_plateaus': state_odd_even_pair_plateaus,
        'universal_odd_even_pair_plateaus': universal_odd_even_pair_plateaus,
        'state_positive_example': state_positive_example,
        'state_zero_only_example': state_zero_only_example,
        'universal_positive_example': universal_positive_example,
        'universal_zero_only_example': universal_zero_only_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_margin_ceiling_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_margin_ceiling_validation_summary()
    return {
        'focus': 'turn same-deadline stateless live control into a direct promise-quoting margin ceiling so an implementor can tell exactly how much realized upside may be promised without re-solving timeout, batch, or hold-cost tables online',
        'headline_findings': {
            'live_margin_ceiling_rule': 'same-deadline stateless live control preserves realized margin promises exactly up to max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p))',
            'effective_horizon_rule': 'the live margin ceiling is exactly the better-of-close-or-blind value at effective blind horizon floor((H + 1) / 2)',
            'odd_even_plateau_rule': 'deadlines 2j - 1 and 2j have identical nonnegative live margin ceilings',
            'zero_only_rule': 'when the raw effective blind value is nonpositive, same-deadline live control can preserve only zero margin because immediate close is the unique safe nonnegative option',
            'positive_state_ceiling_contexts': summary['positive_state_ceiling_contexts'],
            'zero_only_state_contexts': summary['zero_only_state_contexts'],
            'positive_universal_ceiling_contexts': summary['positive_universal_ceiling_contexts'],
            'zero_only_universal_contexts': summary['zero_only_universal_contexts'],
        },
        'decision_rules': [
            'Given batch length n, arrival hazard p, hold cost, and nominal live deadline H, reduce H to effective blind horizon floor((H + 1) / 2) and compute the nonnegative margin ceiling max(0, (1 - (1 - p)^floor((H + 1) / 2)) * (state_prefix_bits / (n(n + 1)) - hold_cost / p)).',
            'A same-deadline live controller can safely quote any original realized margin promise up to that ceiling, and it will fail immediately above it.',
            'If the ceiling is strictly positive, positive promise classes exist up to that exact threshold; if the ceiling is zero, the controller can preserve only the zero-margin promise by closing immediately when waiting is not worthwhile.',
            'Deadlines 2j - 1 and 2j share the same nonnegative live margin ceiling, so promise-quoting capacity only improves when the nominal deadline climbs to the next odd rung.',
            'The same law holds under the seven-bit all-state lower envelope after replacing state_prefix_bits by 7.',
        ],
        'state_positive_example': summary['state_positive_example'],
        'state_zero_only_example': summary['state_zero_only_example'],
        'universal_positive_example': summary['universal_positive_example'],
        'universal_zero_only_example': summary['universal_zero_only_example'],
        'validation_summary': {key: value for key, value in summary.items() if 'example' not in key},
        'source_reports': [
            'artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.md',
            'artifacts/reports/geometric_arrival_live_hold_cost_ceiling_law_snapshot_20260316.md',
            'artifacts/reports/geometric_arrival_live_minimum_deadline_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_margin_ceiling_law.py',
    }


def main() -> None:
    print(json.dumps(build_geometric_arrival_live_margin_ceiling_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
