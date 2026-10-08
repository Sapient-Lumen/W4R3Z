#!/usr/bin/env python3
from __future__ import annotations

import json
import math
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
from scripts.analysis.geometric_arrival_live_minimum_deadline_law import (
    compute_state_minimum_live_deadline,
    compute_universal_minimum_live_deadline,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law import (
    _state_prefix_bits,
)


class GeometricArrivalLiveDeadlineFormulaLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 13))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


@lru_cache(maxsize=None)
def _minimum_timeout_closed_form(arrival_probability: Fraction, required_capture: Fraction) -> int | None:
    if arrival_probability < 0 or arrival_probability > 1:
        raise GeometricArrivalLiveDeadlineFormulaLawError('arrival probability must lie in [0, 1]')
    if required_capture <= 0:
        return 1
    if arrival_probability == 0:
        return None
    if required_capture > 1:
        return None
    if required_capture == 1:
        return 1 if arrival_probability == 1 else None
    if arrival_probability == 1:
        return 1

    estimate = math.log1p(-float(required_capture)) / math.log1p(-float(arrival_probability))
    timeout_ticks = max(1, math.ceil(estimate - 1e-12))
    while Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** timeout_ticks < required_capture:
        timeout_ticks += 1
    while timeout_ticks > 1 and Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** (timeout_ticks - 1) >= required_capture:
        timeout_ticks -= 1
    return timeout_ticks


@lru_cache(maxsize=None)
def _compute_live_deadline_formula_from_prefix_bits(
    prefix_bits: int,
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    prefix_bits = int(prefix_bits)
    current_batch_length = int(current_batch_length)
    if prefix_bits < 0:
        raise GeometricArrivalLiveDeadlineFormulaLawError('prefix bits must be nonnegative')
    if current_batch_length <= 0:
        raise GeometricArrivalLiveDeadlineFormulaLawError('current batch length must be positive')

    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    if p < 0 or p > 1:
        raise GeometricArrivalLiveDeadlineFormulaLawError('arrival probability must lie in [0, 1]')
    if hold_cost < 0:
        raise GeometricArrivalLiveDeadlineFormulaLawError('hold cost must be nonnegative')
    if target_margin < 0:
        raise GeometricArrivalLiveDeadlineFormulaLawError('target margin must be nonnegative')

    prefix_budget = Fraction(prefix_bits, current_batch_length * (current_batch_length + 1))
    sign_invariant_term = p * prefix_budget - hold_cost
    result: dict[str, Any] = {
        'prefix_bits': prefix_bits,
        'current_batch_length': current_batch_length,
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'state_prefix_budget_bits_per_script': _serialize_fraction(prefix_budget),
        'sign_invariant_term_bits_per_script_per_tick': _serialize_fraction(sign_invariant_term),
        'required_capture_fraction': None,
        'blind_minimum_timeout_ticks': None,
        'minimum_nominal_live_deadline_ticks': None,
        'schedule_class': None,
        'closed_form_live_deadline_rule': (
            'let delta = p * prefix_bits / (n(n+1)) - hold_cost and alpha = p * target_margin / delta when delta > 0; '
            'then the minimum same-deadline live deadline is 1 at zero margin, 1 when p = 1 and alpha <= 1, '
            '2 * ceil(log(1 - alpha) / log(1 - p)) - 1 when 0 < alpha < 1 and p < 1, '
            'asymptotic-only when alpha = 1 with p < 1, and impossible when delta <= 0 or alpha > 1'
        ),
    }

    if target_margin == 0:
        result.update(
            {
                'required_capture_fraction': _serialize_fraction(Fraction(0, 1)),
                'blind_minimum_timeout_ticks': 1,
                'minimum_nominal_live_deadline_ticks': 1,
                'schedule_class': 'finite',
                'reason': 'zero_margin_floor_makes_immediate_close_safe_so_the_live_deadline_floor_is_one_tick',
            }
        )
        return result

    if p == 0:
        result.update(
            {
                'schedule_class': 'impossible',
                'reason': 'zero_arrival_probability_cannot_support_positive_same_deadline_live_promises',
            }
        )
        return result

    if sign_invariant_term <= 0:
        result.update(
            {
                'schedule_class': 'impossible',
                'reason': 'nonpositive_asymptotic_wait_value_cannot_support_positive_same_deadline_live_promises',
            }
        )
        return result

    required_capture = p * target_margin / sign_invariant_term
    result['required_capture_fraction'] = _serialize_fraction(required_capture)

    if required_capture > 1:
        result.update(
            {
                'schedule_class': 'impossible',
                'reason': 'target_margin_exceeds_asymptotic_positive_wait_value_so_no_same_deadline_live_deadline_exists',
            }
        )
        return result

    blind_timeout = _minimum_timeout_closed_form(p, required_capture)
    if blind_timeout is None:
        result.update(
            {
                'schedule_class': 'asymptotic_only',
                'reason': 'target_margin_equals_full_asymptotic_upside_but_finite_live_deadline_requires_certain_arrival',
            }
        )
        return result

    result.update(
        {
            'blind_minimum_timeout_ticks': blind_timeout,
            'minimum_nominal_live_deadline_ticks': 2 * blind_timeout - 1,
            'schedule_class': 'finite',
            'reason': 'positive_same_deadline_live_deadline_is_the_odd_image_of_the_direct_closed_form_blind_timeout',
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_state_live_deadline_formula(
    state: tuple[int, int],
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    formula = _compute_live_deadline_formula_from_prefix_bits(
        _state_prefix_bits(state),
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    return {
        'state': list(state),
        'state_prefix_bits': int(formula['prefix_bits']),
        **{k: v for k, v in formula.items() if k != 'prefix_bits'},
    }


@lru_cache(maxsize=None)
def compute_universal_live_deadline_formula(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
) -> dict[str, Any]:
    formula = _compute_live_deadline_formula_from_prefix_bits(
        7,
        current_batch_length,
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
    )
    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        **{k: v for k, v in formula.items() if k != 'prefix_bits'},
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_deadline_formula_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    matched_previous_state_contexts = 0
    matched_previous_universal_contexts = 0
    state_boundary_checks = 0
    universal_boundary_checks = 0
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

    state_zero_example: dict[str, Any] | None = None
    state_finite_example: dict[str, Any] | None = None
    state_asymptotic_example: dict[str, Any] | None = None
    state_impossible_example: dict[str, Any] | None = None
    universal_zero_example: dict[str, Any] | None = None
    universal_finite_example: dict[str, Any] | None = None
    universal_asymptotic_example: dict[str, Any] | None = None
    universal_impossible_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        for current_batch_length in BATCH_GRID:
            for p in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        profile = compute_state_live_deadline_formula(
                            state,
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        prior = compute_state_minimum_live_deadline(
                            state,
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                        )
                        validated_state_contexts += 1
                        if target_margin == 0:
                            if profile['minimum_nominal_live_deadline_ticks'] != prior['minimum_nominal_live_deadline_ticks']:
                                raise GeometricArrivalLiveDeadlineFormulaLawError(
                                    f'state zero-margin direct formula disagreed with prior live minimum deadline for state {state}, n={current_batch_length}, p={p}, c={hold_cost}'
                                )
                        else:
                            if (
                                profile['schedule_class'] != prior['blind_commit_schedule_class']
                                or profile['minimum_nominal_live_deadline_ticks'] != prior['minimum_nominal_live_deadline_ticks']
                            ):
                                raise GeometricArrivalLiveDeadlineFormulaLawError(
                                    f'state direct formula disagreed with prior live minimum law for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                                )
                        matched_previous_state_contexts += 1

                        if target_margin == 0:
                            zero_margin_state_contexts += 1
                            if state_zero_example is None:
                                state_zero_example = {
                                    'direct_formula_profile': profile,
                                    'prior_live_minimum_profile': prior,
                                }
                            continue

                        if profile['schedule_class'] == 'finite':
                            positive_finite_state_contexts += 1
                            minimum_live_deadline_ticks = int(profile['minimum_nominal_live_deadline_ticks'])
                            if minimum_live_deadline_ticks % 2 != 1:
                                raise GeometricArrivalLiveDeadlineFormulaLawError(
                                    f'state positive finite live minimum deadline was not odd for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                                )
                            odd_minimum_state_deadlines += 1
                            at_boundary = evaluate_state_effective_horizon_profile(
                                state,
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                minimum_live_deadline_ticks,
                            )
                            if not bool(at_boundary['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveDeadlineFormulaLawError(
                                    f'state direct-formula boundary failed at minimum live deadline for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                                )
                            state_boundary_checks += 1
                            if minimum_live_deadline_ticks > 1:
                                below_boundary = evaluate_state_effective_horizon_profile(
                                    state,
                                    current_batch_length,
                                    p.numerator,
                                    p.denominator,
                                    hold_cost.numerator,
                                    hold_cost.denominator,
                                    target_margin.numerator,
                                    target_margin.denominator,
                                    minimum_live_deadline_ticks - 1,
                                )
                                if bool(below_boundary['live_countdown_preserves_original_margin']):
                                    raise GeometricArrivalLiveDeadlineFormulaLawError(
                                        f'state direct-formula predecessor unexpectedly preserved original margin for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                                    )
                                state_boundary_checks += 1
                            if state_finite_example is None:
                                state_finite_example = {
                                    'direct_formula_profile': profile,
                                    'prior_live_minimum_profile': prior,
                                    'at_boundary_effective_horizon_profile': at_boundary,
                                }
                        elif profile['schedule_class'] == 'asymptotic_only':
                            positive_asymptotic_state_contexts += 1
                            if state_asymptotic_example is None:
                                state_asymptotic_example = {
                                    'direct_formula_profile': profile,
                                    'prior_live_minimum_profile': prior,
                                }
                        else:
                            positive_impossible_state_contexts += 1
                            if state_impossible_example is None:
                                state_impossible_example = {
                                    'direct_formula_profile': profile,
                                    'prior_live_minimum_profile': prior,
                                }

    for current_batch_length in BATCH_GRID:
        for p in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    profile = compute_universal_live_deadline_formula(
                        current_batch_length,
                        p.numerator,
                        p.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    prior = compute_universal_minimum_live_deadline(
                        current_batch_length,
                        p.numerator,
                        p.denominator,
                        hold_cost.numerator,
                        hold_cost.denominator,
                        target_margin.numerator,
                        target_margin.denominator,
                    )
                    validated_universal_contexts += 1
                    if target_margin == 0:
                        if profile['minimum_nominal_live_deadline_ticks'] != prior['minimum_nominal_live_deadline_ticks']:
                            raise GeometricArrivalLiveDeadlineFormulaLawError(
                                f'universal zero-margin direct formula disagreed with prior live minimum deadline for n={current_batch_length}, p={p}, c={hold_cost}'
                            )
                    else:
                        if (
                            profile['schedule_class'] != prior['blind_commit_schedule_class']
                            or profile['minimum_nominal_live_deadline_ticks'] != prior['minimum_nominal_live_deadline_ticks']
                        ):
                            raise GeometricArrivalLiveDeadlineFormulaLawError(
                                f'universal direct formula disagreed with prior live minimum law for n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                            )
                    matched_previous_universal_contexts += 1

                    if target_margin == 0:
                        zero_margin_universal_contexts += 1
                        if universal_zero_example is None:
                            universal_zero_example = {
                                'direct_formula_profile': profile,
                                'prior_live_minimum_profile': prior,
                            }
                        continue

                    if profile['schedule_class'] == 'finite':
                        positive_finite_universal_contexts += 1
                        minimum_live_deadline_ticks = int(profile['minimum_nominal_live_deadline_ticks'])
                        if minimum_live_deadline_ticks % 2 != 1:
                            raise GeometricArrivalLiveDeadlineFormulaLawError(
                                f'universal positive finite live minimum deadline was not odd for n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                            )
                        odd_minimum_universal_deadlines += 1
                        at_boundary = evaluate_universal_effective_horizon_profile(
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            minimum_live_deadline_ticks,
                        )
                        if not bool(at_boundary['live_countdown_preserves_original_margin']):
                            raise GeometricArrivalLiveDeadlineFormulaLawError(
                                f'universal direct-formula boundary failed at minimum live deadline for n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                            )
                        universal_boundary_checks += 1
                        if minimum_live_deadline_ticks > 1:
                            below_boundary = evaluate_universal_effective_horizon_profile(
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                minimum_live_deadline_ticks - 1,
                            )
                            if bool(below_boundary['live_countdown_preserves_original_margin']):
                                raise GeometricArrivalLiveDeadlineFormulaLawError(
                                    f'universal direct-formula predecessor unexpectedly preserved original margin for n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}'
                                )
                            universal_boundary_checks += 1
                        if universal_finite_example is None:
                            universal_finite_example = {
                                'direct_formula_profile': profile,
                                'prior_live_minimum_profile': prior,
                                'at_boundary_effective_horizon_profile': at_boundary,
                            }
                    elif profile['schedule_class'] == 'asymptotic_only':
                        positive_asymptotic_universal_contexts += 1
                        if universal_asymptotic_example is None:
                            universal_asymptotic_example = {
                                'direct_formula_profile': profile,
                                'prior_live_minimum_profile': prior,
                            }
                    else:
                        positive_impossible_universal_contexts += 1
                        if universal_impossible_example is None:
                            universal_impossible_example = {
                                'direct_formula_profile': profile,
                                'prior_live_minimum_profile': prior,
                            }

    if None in (
        state_zero_example,
        state_finite_example,
        state_asymptotic_example,
        state_impossible_example,
        universal_zero_example,
        universal_finite_example,
        universal_asymptotic_example,
        universal_impossible_example,
    ):
        raise GeometricArrivalLiveDeadlineFormulaLawError('expected all direct-formula example classes to be populated')

    return {
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'matched_previous_state_contexts': matched_previous_state_contexts,
        'matched_previous_universal_contexts': matched_previous_universal_contexts,
        'state_boundary_checks': state_boundary_checks,
        'universal_boundary_checks': universal_boundary_checks,
        'zero_margin_state_contexts': zero_margin_state_contexts,
        'zero_margin_universal_contexts': zero_margin_universal_contexts,
        'positive_finite_state_contexts': positive_finite_state_contexts,
        'positive_asymptotic_state_contexts': positive_asymptotic_state_contexts,
        'positive_impossible_state_contexts': positive_impossible_state_contexts,
        'positive_finite_universal_contexts': positive_finite_universal_contexts,
        'positive_asymptotic_universal_contexts': positive_asymptotic_universal_contexts,
        'positive_impossible_universal_contexts': positive_impossible_universal_contexts,
        'odd_minimum_state_deadlines': odd_minimum_state_deadlines,
        'odd_minimum_universal_deadlines': odd_minimum_universal_deadlines,
        'state_zero_example': state_zero_example,
        'state_finite_example': state_finite_example,
        'state_asymptotic_example': state_asymptotic_example,
        'state_impossible_example': state_impossible_example,
        'universal_zero_example': universal_zero_example,
        'universal_finite_example': universal_finite_example,
        'universal_asymptotic_example': universal_asymptotic_example,
        'universal_impossible_example': universal_impossible_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_deadline_formula_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_deadline_formula_validation_summary()
    return {
        'focus': 'direct closed-form minimum same-deadline live deadline from primitive batch, hazard, cost, margin, and prefix inputs',
        'headline_findings': {
            'state_contexts_validated': summary['validated_state_contexts'],
            'universal_contexts_validated': summary['validated_universal_contexts'],
            'state_matches_previous_live_minimum_law': summary['matched_previous_state_contexts'],
            'universal_matches_previous_live_minimum_law': summary['matched_previous_universal_contexts'],
            'positive_finite_state_contexts': summary['positive_finite_state_contexts'],
            'positive_finite_universal_contexts': summary['positive_finite_universal_contexts'],
            'positive_asymptotic_state_contexts': summary['positive_asymptotic_state_contexts'],
            'positive_impossible_state_contexts': summary['positive_impossible_state_contexts'],
        },
        'decision_rules': [
            'let delta = p * state_prefix_bits / (n(n + 1)) - hold_cost and alpha = p * margin_floor / delta when delta > 0',
            'if margin_floor = 0 then the minimum same-deadline live deadline is 1 because immediate close already preserves the promise',
            'if delta <= 0 or alpha > 1 then no positive same-deadline live deadline exists',
            'if alpha = 1 and p < 1 then the positive promise is asymptotic-only under both blind and same-deadline live control',
            'if p = 1 and alpha <= 1 then one tick already captures the full asymptotic upside so the minimum same-deadline live deadline is 1',
            'if 0 < alpha < 1 and p < 1 then the minimum same-deadline live deadline is 2 * ceil(log(1 - alpha) / log(1 - p)) - 1',
            'the all-state guardrail uses the same formula with state_prefix_bits replaced by 7',
        ],
        'state_zero_example': summary['state_zero_example'],
        'state_positive_finite_example': summary['state_finite_example'],
        'state_positive_asymptotic_example': summary['state_asymptotic_example'],
        'state_positive_impossible_example': summary['state_impossible_example'],
        'universal_zero_example': summary['universal_zero_example'],
        'universal_positive_finite_example': summary['universal_finite_example'],
        'universal_positive_asymptotic_example': summary['universal_asymptotic_example'],
        'universal_positive_impossible_example': summary['universal_impossible_example'],
        'validation_summary': summary,
        'source_reports': [
            'artifacts/reports/geometric_arrival_live_minimum_deadline_law_snapshot_20260316.json',
            'artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.json',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_deadline_formula_law.py',
    }


def main() -> None:
    print(json.dumps(build_geometric_arrival_live_deadline_formula_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
