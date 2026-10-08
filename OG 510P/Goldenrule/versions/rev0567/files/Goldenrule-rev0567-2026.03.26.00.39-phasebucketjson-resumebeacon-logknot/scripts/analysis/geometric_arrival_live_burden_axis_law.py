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

from scripts.analysis.geometric_arrival_live_prefix_floor_law import (
    compute_state_live_prefix_floor,
    compute_universal_live_prefix_floor,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law import (
    _state_prefix_bits,
)


class GeometricArrivalLiveBurdenAxisLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
NOMINAL_HORIZON_GRID = tuple(range(1, 9))


def _serialize_fraction(value: Fraction | None) -> dict[str, int | float] | None:
    if value is None:
        return None
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _effective_horizon(nominal_horizon_ticks: int) -> int:
    return (nominal_horizon_ticks + 1) // 2


def _capture_fraction(arrival_probability: Fraction, effective_horizon_ticks: int) -> Fraction:
    return Fraction(1, 1) - (Fraction(1, 1) - arrival_probability) ** effective_horizon_ticks


def _ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


@lru_cache(maxsize=None)
def _compute_live_burden(
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)

    if p <= 0 or p > 1:
        raise GeometricArrivalLiveBurdenAxisLawError('arrival probability must lie in (0, 1] for the live burden axis law')
    if hold_cost < 0:
        raise GeometricArrivalLiveBurdenAxisLawError('hold cost must be nonnegative')
    if target_margin < 0:
        raise GeometricArrivalLiveBurdenAxisLawError('target margin must be nonnegative')

    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    capture_fraction = _capture_fraction(p, effective_horizon_ticks)
    if target_margin == 0:
        burden = Fraction(0, 1)
        reason = 'zero_margin_promises_collapse_to_zero_live_burden_because_immediate_close_is_already_safe'
    else:
        burden = hold_cost / p + target_margin / capture_fraction
        reason = 'positive_live_promises_pay_one_exact_burden_axis_equal_to_hold_cost_over_p_plus_margin_over_effective_capture'

    return {
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'effective_capture_fraction': _serialize_fraction(capture_fraction),
        'live_burden_bits_per_effective_prefix_budget': _serialize_fraction(burden),
        'live_burden_axis_formula': (
            'for same-deadline stateless live control, collapse hold cost and promised realized margin to one scalar burden: '
            'b_live = 0 when m = 0, else hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2)); '
            'preserve the promise exactly iff state_prefix_bits / (n(n + 1)) >= b_live'
        ),
        'positive_exchange_rule': (
            'at fixed arrival hazard and deadline, positive promised margin bits trade against hold-cost bits at exact rate '
            '(1 - (1 - p)^floor((H + 1) / 2)) / p'
        ),
        'reason': reason,
    }


@lru_cache(maxsize=None)
def compute_state_live_burden_profile(
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
    burden_profile = _compute_live_burden(
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
        nominal_horizon_ticks,
    )
    state_prefix_bits = _state_prefix_bits(state)
    burden_payload = burden_profile['live_burden_bits_per_effective_prefix_budget']
    burden = Fraction(int(burden_payload['numerator']), int(burden_payload['denominator']))
    state_prefix_budget = Fraction(state_prefix_bits, current_batch_length * (current_batch_length + 1))
    minimum_required_prefix_bits = _ceil_fraction(
        Fraction(current_batch_length * (current_batch_length + 1), 1) * burden
    )
    preserves = state_prefix_budget >= burden
    universal_suffices = 7 >= minimum_required_prefix_bits

    return {
        'state': list(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': int(current_batch_length),
        'state_prefix_budget_bits_per_script': _serialize_fraction(state_prefix_budget),
        'minimum_required_prefix_bits': int(minimum_required_prefix_bits),
        'state_preserves_original_margin': bool(preserves),
        'universal_seven_bit_guardrail_preserves_original_margin': bool(universal_suffices),
        **burden_profile,
    }


@lru_cache(maxsize=None)
def compute_universal_live_burden_profile(
    current_batch_length: int,
    arrival_probability_numerator: int,
    arrival_probability_denominator: int,
    hold_cost_bits_numerator: int,
    hold_cost_bits_denominator: int,
    target_margin_bits_numerator: int,
    target_margin_bits_denominator: int,
    nominal_horizon_ticks: int,
) -> dict[str, Any]:
    burden_profile = _compute_live_burden(
        arrival_probability_numerator,
        arrival_probability_denominator,
        hold_cost_bits_numerator,
        hold_cost_bits_denominator,
        target_margin_bits_numerator,
        target_margin_bits_denominator,
        nominal_horizon_ticks,
    )
    burden_payload = burden_profile['live_burden_bits_per_effective_prefix_budget']
    burden = Fraction(int(burden_payload['numerator']), int(burden_payload['denominator']))
    universal_prefix_budget = Fraction(7, current_batch_length * (current_batch_length + 1))
    minimum_required_prefix_bits = _ceil_fraction(
        Fraction(current_batch_length * (current_batch_length + 1), 1) * burden
    )
    preserves = universal_prefix_budget >= burden

    return {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': 7,
        'current_batch_length': int(current_batch_length),
        'guarantee_prefix_budget_bits_per_script': _serialize_fraction(universal_prefix_budget),
        'minimum_required_prefix_bits': int(minimum_required_prefix_bits),
        'universal_preserves_original_margin': bool(preserves),
        **burden_profile,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_burden_axis_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    nonnegative_state_admitted_contexts = 0
    nonnegative_state_rejected_contexts = 0
    nonnegative_universal_admitted_contexts = 0
    nonnegative_universal_rejected_contexts = 0
    zero_burden_state_contexts = 0
    zero_burden_universal_contexts = 0
    state_equivalent_member_checks = 0
    universal_equivalent_member_checks = 0
    state_burden_ladders = 0
    state_burden_ladders_with_strict_drop = 0
    universal_burden_ladders = 0
    universal_burden_ladders_with_strict_drop = 0
    burden_spectrum_pair_plateaus = 0
    minimum_unique_burden_classes_per_hazard_deadline: int | None = None
    maximum_unique_burden_classes_per_hazard_deadline = 0
    maximum_raw_contexts_per_single_burden_class = 0

    state_positive_equivalent_example: dict[str, Any] | None = None
    state_zero_burden_example: dict[str, Any] | None = None
    universal_positive_equivalent_example: dict[str, Any] | None = None
    universal_zero_burden_example: dict[str, Any] | None = None

    prior_burden_spectrum_by_arrival: dict[Fraction, tuple[Fraction, ...]] = {}

    for arrival_probability in ARRIVAL_GRID:
        for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
            spectrum = tuple(
                sorted(
                    {
                        Fraction(0, 1)
                        if target_margin == 0
                        else hold_cost / arrival_probability
                        + target_margin / _capture_fraction(arrival_probability, _effective_horizon(nominal_horizon_ticks))
                        for hold_cost in HOLD_COST_GRID
                        for target_margin in TARGET_MARGIN_GRID
                    }
                )
            )
            unique_classes = len(spectrum)
            minimum_unique_burden_classes_per_hazard_deadline = (
                unique_classes
                if minimum_unique_burden_classes_per_hazard_deadline is None
                else min(minimum_unique_burden_classes_per_hazard_deadline, unique_classes)
            )
            maximum_unique_burden_classes_per_hazard_deadline = max(
                maximum_unique_burden_classes_per_hazard_deadline,
                unique_classes,
            )
            if nominal_horizon_ticks % 2 == 0:
                prior = prior_burden_spectrum_by_arrival[arrival_probability]
                if spectrum != prior:
                    raise GeometricArrivalLiveBurdenAxisLawError(
                        f'burden spectrum changed across odd/even pair for p={arrival_probability}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                    )
                burden_spectrum_pair_plateaus += 1
            prior_burden_spectrum_by_arrival[arrival_probability] = spectrum

    for state in STATE_GRID:
        state_prefix_bits = _state_prefix_bits(state)
        for current_batch_length in BATCH_GRID:
            for arrival_probability in ARRIVAL_GRID:
                for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                    grouped_profiles: dict[Fraction, list[dict[str, Any]]] = {}
                    for hold_cost in HOLD_COST_GRID:
                        for target_margin in TARGET_MARGIN_GRID:
                            profile = compute_state_live_burden_profile(
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
                            prefix_floor_profile = compute_state_live_prefix_floor(
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
                            validated_state_contexts += 1
                            burden_payload = profile['live_burden_bits_per_effective_prefix_budget']
                            burden = Fraction(int(burden_payload['numerator']), int(burden_payload['denominator']))
                            expected_required_prefix_bits = _ceil_fraction(
                                Fraction(current_batch_length * (current_batch_length + 1), 1) * burden
                            )
                            if int(profile['minimum_required_prefix_bits']) != expected_required_prefix_bits:
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state burden floor mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )
                            if int(prefix_floor_profile['minimum_required_prefix_bits']) != expected_required_prefix_bits:
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state prefix-floor mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )
                            if bool(profile['state_preserves_original_margin']) != bool(prefix_floor_profile['state_meets_prefix_floor']):
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state admission mismatch against prefix-floor law for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )
                            if bool(profile['universal_seven_bit_guardrail_preserves_original_margin']) != bool(
                                prefix_floor_profile['universal_seven_bit_floor_suffices']
                            ):
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state universal-guardrail mismatch for state {state}, n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )

                            if bool(profile['state_preserves_original_margin']):
                                nonnegative_state_admitted_contexts += 1
                            else:
                                nonnegative_state_rejected_contexts += 1
                            if target_margin == 0:
                                zero_burden_state_contexts += 1
                            grouped_profiles.setdefault(burden, []).append(
                                {
                                    'burden_profile': profile,
                                    'prefix_floor_profile': prefix_floor_profile,
                                    'hold_cost': hold_cost,
                                    'target_margin': target_margin,
                                }
                            )

                    unique_burdens = tuple(sorted(grouped_profiles))
                    prior_admission: bool | None = None
                    saw_strict_drop = False
                    state_burden_ladders += 1
                    for burden in unique_burdens:
                        group = grouped_profiles[burden]
                        maximum_raw_contexts_per_single_burden_class = max(
                            maximum_raw_contexts_per_single_burden_class,
                            len(group),
                        )
                        representative = group[0]
                        representative_profile = representative['burden_profile']
                        admission = bool(representative_profile['state_preserves_original_margin'])
                        if prior_admission is not None and admission and not prior_admission:
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'state burden admission ladder improved with larger burden for state {state}, n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}'
                            )
                        if prior_admission is not None and prior_admission and not admission:
                            saw_strict_drop = True
                        prior_admission = admission

                        for other in group[1:]:
                            state_equivalent_member_checks += 1
                            other_profile = other['burden_profile']
                            other_floor = other['prefix_floor_profile']
                            representative_floor = representative['prefix_floor_profile']
                            if int(other_profile['minimum_required_prefix_bits']) != int(representative_profile['minimum_required_prefix_bits']):
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state equal-burden class changed required prefix floor for state {state}, n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                                )
                            if bool(other_profile['state_preserves_original_margin']) != admission:
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state equal-burden class changed admission for state {state}, n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                                )
                            if int(other_floor['minimum_required_prefix_bits']) != int(representative_floor['minimum_required_prefix_bits']):
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state equal-burden class changed prefix-floor output for state {state}, n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                                )
                            if bool(other_floor['state_meets_prefix_floor']) != bool(representative_floor['state_meets_prefix_floor']):
                                raise GeometricArrivalLiveBurdenAxisLawError(
                                    f'state equal-burden class changed prefix-floor admission for state {state}, n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                                )
                            if burden > 0 and state_positive_equivalent_example is None:
                                state_positive_equivalent_example = {
                                    'state': list(state),
                                    'state_prefix_bits': state_prefix_bits,
                                    'current_batch_length': int(current_batch_length),
                                    'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
                                    'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
                                    'live_burden_bits_per_effective_prefix_budget': _serialize_fraction(burden),
                                    'first_context': {
                                        'hold_cost_bits_per_script_per_tick': _serialize_fraction(representative['hold_cost']),
                                        'target_margin_bits_per_script': _serialize_fraction(representative['target_margin']),
                                    },
                                    'second_context': {
                                        'hold_cost_bits_per_script_per_tick': _serialize_fraction(other['hold_cost']),
                                        'target_margin_bits_per_script': _serialize_fraction(other['target_margin']),
                                    },
                                    'shared_required_prefix_bits': int(representative_profile['minimum_required_prefix_bits']),
                                    'shared_admission_result': bool(admission),
                                }

                        if burden == 0 and state_zero_burden_example is None:
                            state_zero_burden_example = {
                                'state': list(state),
                                'state_prefix_bits': state_prefix_bits,
                                'current_batch_length': int(current_batch_length),
                                'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
                                'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
                                'live_burden_bits_per_effective_prefix_budget': _serialize_fraction(burden),
                                'raw_contexts_in_zero_burden_class': [
                                    {
                                        'hold_cost_bits_per_script_per_tick': _serialize_fraction(entry['hold_cost']),
                                        'target_margin_bits_per_script': _serialize_fraction(entry['target_margin']),
                                    }
                                    for entry in group
                                ],
                                'shared_required_prefix_bits': int(representative_profile['minimum_required_prefix_bits']),
                                'shared_admission_result': bool(admission),
                            }

                    if saw_strict_drop:
                        state_burden_ladders_with_strict_drop += 1

    for current_batch_length in BATCH_GRID:
        for arrival_probability in ARRIVAL_GRID:
            for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                grouped_profiles: dict[Fraction, list[dict[str, Any]]] = {}
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        profile = compute_universal_live_burden_profile(
                            current_batch_length,
                            arrival_probability.numerator,
                            arrival_probability.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        prefix_floor_profile = compute_universal_live_prefix_floor(
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
                        burden_payload = profile['live_burden_bits_per_effective_prefix_budget']
                        burden = Fraction(int(burden_payload['numerator']), int(burden_payload['denominator']))
                        expected_required_prefix_bits = _ceil_fraction(
                            Fraction(current_batch_length * (current_batch_length + 1), 1) * burden
                        )
                        if int(profile['minimum_required_prefix_bits']) != expected_required_prefix_bits:
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'universal burden floor mismatch for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                            )
                        if int(prefix_floor_profile['minimum_required_prefix_bits']) != expected_required_prefix_bits:
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'universal prefix-floor mismatch for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                            )
                        if bool(profile['universal_preserves_original_margin']) != bool(prefix_floor_profile['universal_seven_bit_floor_suffices']):
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'universal admission mismatch against prefix-floor law for n={current_batch_length}, p={arrival_probability}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                            )

                        if bool(profile['universal_preserves_original_margin']):
                            nonnegative_universal_admitted_contexts += 1
                        else:
                            nonnegative_universal_rejected_contexts += 1
                        if target_margin == 0:
                            zero_burden_universal_contexts += 1
                        grouped_profiles.setdefault(burden, []).append(
                            {
                                'burden_profile': profile,
                                'prefix_floor_profile': prefix_floor_profile,
                                'hold_cost': hold_cost,
                                'target_margin': target_margin,
                            }
                        )

                unique_burdens = tuple(sorted(grouped_profiles))
                prior_admission: bool | None = None
                saw_strict_drop = False
                universal_burden_ladders += 1
                for burden in unique_burdens:
                    group = grouped_profiles[burden]
                    representative = group[0]
                    representative_profile = representative['burden_profile']
                    admission = bool(representative_profile['universal_preserves_original_margin'])
                    if prior_admission is not None and admission and not prior_admission:
                        raise GeometricArrivalLiveBurdenAxisLawError(
                            f'universal burden admission ladder improved with larger burden for n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}'
                        )
                    if prior_admission is not None and prior_admission and not admission:
                        saw_strict_drop = True
                    prior_admission = admission

                    for other in group[1:]:
                        universal_equivalent_member_checks += 1
                        other_profile = other['burden_profile']
                        other_floor = other['prefix_floor_profile']
                        representative_floor = representative['prefix_floor_profile']
                        if int(other_profile['minimum_required_prefix_bits']) != int(representative_profile['minimum_required_prefix_bits']):
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'universal equal-burden class changed required prefix floor for n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                            )
                        if bool(other_profile['universal_preserves_original_margin']) != admission:
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'universal equal-burden class changed admission for n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                            )
                        if int(other_floor['minimum_required_prefix_bits']) != int(representative_floor['minimum_required_prefix_bits']):
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'universal equal-burden class changed prefix-floor output for n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                            )
                        if bool(other_floor['universal_seven_bit_floor_suffices']) != bool(representative_floor['universal_seven_bit_floor_suffices']):
                            raise GeometricArrivalLiveBurdenAxisLawError(
                                f'universal equal-burden class changed prefix-floor admission for n={current_batch_length}, p={arrival_probability}, H={nominal_horizon_ticks}, burden={burden}'
                            )
                            
                        if burden > 0 and universal_positive_equivalent_example is None:
                            universal_positive_equivalent_example = {
                                'current_batch_length': int(current_batch_length),
                                'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
                                'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
                                'guarantee_state_prefix_bits': 7,
                                'live_burden_bits_per_effective_prefix_budget': _serialize_fraction(burden),
                                'first_context': {
                                    'hold_cost_bits_per_script_per_tick': _serialize_fraction(representative['hold_cost']),
                                    'target_margin_bits_per_script': _serialize_fraction(representative['target_margin']),
                                },
                                'second_context': {
                                    'hold_cost_bits_per_script_per_tick': _serialize_fraction(other['hold_cost']),
                                    'target_margin_bits_per_script': _serialize_fraction(other['target_margin']),
                                },
                                'shared_required_prefix_bits': int(representative_profile['minimum_required_prefix_bits']),
                                'shared_admission_result': bool(admission),
                            }

                    if burden == 0 and universal_zero_burden_example is None:
                        universal_zero_burden_example = {
                            'current_batch_length': int(current_batch_length),
                            'arrival_probability_per_tick': _serialize_fraction(arrival_probability),
                            'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
                            'guarantee_state_prefix_bits': 7,
                            'live_burden_bits_per_effective_prefix_budget': _serialize_fraction(burden),
                            'raw_contexts_in_zero_burden_class': [
                                {
                                    'hold_cost_bits_per_script_per_tick': _serialize_fraction(entry['hold_cost']),
                                    'target_margin_bits_per_script': _serialize_fraction(entry['target_margin']),
                                }
                                for entry in group
                            ],
                            'shared_required_prefix_bits': int(representative_profile['minimum_required_prefix_bits']),
                            'shared_admission_result': bool(admission),
                        }

                if saw_strict_drop:
                    universal_burden_ladders_with_strict_drop += 1

    if state_positive_equivalent_example is None or state_zero_burden_example is None:
        raise GeometricArrivalLiveBurdenAxisLawError('failed to capture representative state burden-axis examples')
    if universal_positive_equivalent_example is None or universal_zero_burden_example is None:
        raise GeometricArrivalLiveBurdenAxisLawError('failed to capture representative universal burden-axis examples')
    if minimum_unique_burden_classes_per_hazard_deadline is None:
        raise GeometricArrivalLiveBurdenAxisLawError('failed to compute burden-class spectrum size')

    return {
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'nonnegative_state_admitted_contexts': nonnegative_state_admitted_contexts,
        'nonnegative_state_rejected_contexts': nonnegative_state_rejected_contexts,
        'nonnegative_universal_admitted_contexts': nonnegative_universal_admitted_contexts,
        'nonnegative_universal_rejected_contexts': nonnegative_universal_rejected_contexts,
        'zero_burden_state_contexts': zero_burden_state_contexts,
        'zero_burden_universal_contexts': zero_burden_universal_contexts,
        'state_equivalent_member_checks': state_equivalent_member_checks,
        'universal_equivalent_member_checks': universal_equivalent_member_checks,
        'state_burden_ladders': state_burden_ladders,
        'state_burden_ladders_with_strict_drop': state_burden_ladders_with_strict_drop,
        'universal_burden_ladders': universal_burden_ladders,
        'universal_burden_ladders_with_strict_drop': universal_burden_ladders_with_strict_drop,
        'burden_spectrum_pair_plateaus': burden_spectrum_pair_plateaus,
        'minimum_unique_burden_classes_per_hazard_deadline': minimum_unique_burden_classes_per_hazard_deadline,
        'maximum_unique_burden_classes_per_hazard_deadline': maximum_unique_burden_classes_per_hazard_deadline,
        'maximum_raw_contexts_per_single_burden_class': maximum_raw_contexts_per_single_burden_class,
        'state_positive_equivalent_example': state_positive_equivalent_example,
        'state_zero_burden_example': state_zero_burden_example,
        'universal_positive_equivalent_example': universal_positive_equivalent_example,
        'universal_zero_burden_example': universal_zero_burden_example,
    }


def build_geometric_arrival_live_burden_axis_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_burden_axis_validation_summary()
    return {
        'focus': 'collapse hold cost and promised realized margin to one exact live burden axis so future inheritors can key same-deadline live promise admission on a single scalar instead of a two-dimensional cost-margin table',
        'headline_findings': {
            'live_burden_rule': 'for same-deadline stateless live control, collapse hold cost and promised realized margin to one scalar burden b_live = 0 when m = 0, else hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2)); preserve exactly iff state_prefix_bits / (n(n + 1)) >= b_live',
            'equal_burden_equivalence_rule': 'for fixed batch length, arrival hazard, and nominal live deadline, any two contexts with the same live burden are exactly admission-equivalent',
            'universal_guardrail_rule': 'the all-state seven-bit guarantee survives exactly when 7 / (n(n + 1)) >= b_live',
            'odd_even_pair_rule': 'deadlines 2j - 1 and 2j induce the same burden spectrum because they share the same effective blind horizon j',
            'minimum_unique_burden_classes_per_hazard_deadline': summary['minimum_unique_burden_classes_per_hazard_deadline'],
            'maximum_unique_burden_classes_per_hazard_deadline': summary['maximum_unique_burden_classes_per_hazard_deadline'],
            'maximum_raw_contexts_per_single_burden_class': summary['maximum_raw_contexts_per_single_burden_class'],
            'nonnegative_state_admitted_contexts': summary['nonnegative_state_admitted_contexts'],
            'nonnegative_state_rejected_contexts': summary['nonnegative_state_rejected_contexts'],
            'nonnegative_universal_admitted_contexts': summary['nonnegative_universal_admitted_contexts'],
            'nonnegative_universal_rejected_contexts': summary['nonnegative_universal_rejected_contexts'],
        },
        'decision_rules': [
            'Given batch length n, arrival hazard p, hold cost, promised realized margin m, and nominal same-deadline live horizon H, reduce H to effective blind horizon floor((H + 1) / 2).',
            'Collapse the cost-margin pair to one scalar burden: use 0 when m = 0, else hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2)).',
            'Admit a state-specific same-deadline live promise exactly when state_prefix_bits / (n(n + 1)) is at least that burden, or equivalently when state_prefix_bits >= ceil(n(n + 1) * burden).',
            'Admit the promise under the seven-bit all-state guardrail exactly when 7 / (n(n + 1)) is at least the same burden.',
            'Cache or search frontiers over burden instead of over separate hold-cost and promised-margin axes; equal-burden contexts are exact substitutes for admission.',
            'Because the burden uses floor((H + 1) / 2), deadlines 2j - 1 and 2j are interchangeable and only the next odd rung changes the cost-margin frontier.',
        ],
        'state_positive_equivalent_example': summary['state_positive_equivalent_example'],
        'state_zero_burden_example': summary['state_zero_burden_example'],
        'universal_positive_equivalent_example': summary['universal_positive_equivalent_example'],
        'universal_zero_burden_example': summary['universal_zero_burden_example'],
        'validation_summary': summary,
        'audited_batch_lengths': list(BATCH_GRID),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in ARRIVAL_GRID],
        'audited_hold_costs': [_serialize_fraction(value) for value in HOLD_COST_GRID],
        'audited_target_margins': [_serialize_fraction(value) for value in TARGET_MARGIN_GRID],
        'audited_nominal_live_deadlines': list(NOMINAL_HORIZON_GRID),
        'analysis_script': 'scripts/analysis/geometric_arrival_live_burden_axis_law.py',
        'source_reports': [
            'artifacts/reports/geometric_arrival_live_prefix_floor_law_snapshot_20260316.json',
            'artifacts/reports/geometric_arrival_live_dominance_frontier_law_snapshot_20260316.json',
            'artifacts/reports/geometric_arrival_live_margin_ceiling_law_snapshot_20260316.json',
        ],
    }


def main() -> None:
    print(json.dumps(build_geometric_arrival_live_burden_axis_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
