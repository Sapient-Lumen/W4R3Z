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
from scripts.analysis.geometric_arrival_live_margin_ceiling_law import (
    compute_state_live_margin_ceiling,
    compute_universal_live_margin_ceiling,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law import (
    _state_prefix_bits,
)


class GeometricArrivalLivePrefixFloorLawError(RuntimeError):
    pass


STATE_GRID = tuple(tuple(state) for state in build_all_realized_feasible_interval_states())
BATCH_GRID = tuple(range(1, 9))
ARRIVAL_GRID = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
HOLD_COST_GRID = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
TARGET_MARGIN_GRID = (Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
POSITIVE_TARGET_MARGIN_GRID = TARGET_MARGIN_GRID[1:]
NOMINAL_HORIZON_GRID = tuple(range(1, 9))
UNIVERSAL_PREFIX_BITS = 7


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


def _ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


@lru_cache(maxsize=None)
def compute_state_live_prefix_floor(
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
    p = Fraction(arrival_probability_numerator, arrival_probability_denominator)
    hold_cost = Fraction(hold_cost_bits_numerator, hold_cost_bits_denominator)
    target_margin = Fraction(target_margin_bits_numerator, target_margin_bits_denominator)
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)
    state_prefix_bits = _state_prefix_bits(state)

    result: dict[str, Any] = {
        'state': list(state),
        'state_prefix_bits': state_prefix_bits,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'raw_required_prefix_bits': None,
        'minimum_required_prefix_bits': 0,
        'state_meets_prefix_floor': True,
        'universal_seven_bit_floor_suffices': True,
        'positive_prefix_floor_formula': (
            'for positive realized margin floors m > 0, same-deadline stateless live control preserves the original promise iff '
            'state_prefix_bits >= ceil(n(n + 1) * (hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2))))'
        ),
        'zero_margin_formula': 'at zero margin floor, immediate close is already safe, so the required prefix floor collapses to 0 bits',
    }

    if target_margin == 0:
        result.update(
            {
                'reason': 'zero_margin_floor_makes_immediate_close_safe_so_no_positive_prefix_budget_is_required',
            }
        )
        return result

    capture_fraction = _capture_fraction(p, effective_horizon_ticks)
    raw_required_prefix_bits = Fraction(
        current_batch_length * (current_batch_length + 1),
        1,
    ) * (hold_cost / p + target_margin / capture_fraction)
    minimum_required_prefix_bits = _ceil_fraction(raw_required_prefix_bits)
    result.update(
        {
            'effective_capture_fraction': _serialize_fraction(capture_fraction),
            'raw_required_prefix_bits': _serialize_fraction(raw_required_prefix_bits),
            'minimum_required_prefix_bits': minimum_required_prefix_bits,
            'state_meets_prefix_floor': state_prefix_bits >= minimum_required_prefix_bits,
            'universal_seven_bit_floor_suffices': minimum_required_prefix_bits <= UNIVERSAL_PREFIX_BITS,
            'reason': (
                'state_prefix_budget_is_large_enough_to_preserve_the_positive_live_promise'
                if state_prefix_bits >= minimum_required_prefix_bits
                else 'state_prefix_budget_is_too_small_to_preserve_the_positive_live_promise'
            ),
        }
    )
    return result


@lru_cache(maxsize=None)
def compute_universal_live_prefix_floor(
    current_batch_length: int,
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
    effective_horizon_ticks = _effective_horizon(nominal_horizon_ticks)

    result: dict[str, Any] = {
        'guarantee_scope': 'all_realized_states',
        'guarantee_state_prefix_bits': UNIVERSAL_PREFIX_BITS,
        'current_batch_length': int(current_batch_length),
        'arrival_probability_per_tick': _serialize_fraction(p),
        'hold_cost_bits_per_script_per_tick': _serialize_fraction(hold_cost),
        'target_margin_bits_per_script': _serialize_fraction(target_margin),
        'nominal_live_deadline_ticks': int(nominal_horizon_ticks),
        'effective_blind_horizon_ticks': int(effective_horizon_ticks),
        'raw_required_prefix_bits': None,
        'minimum_required_prefix_bits': 0,
        'universal_seven_bit_floor_suffices': True,
        'positive_prefix_floor_formula': (
            'for positive realized margin floors m > 0, the universal seven-bit same-deadline live guarantee survives iff '
            '7 >= ceil(n(n + 1) * (hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2))))'
        ),
        'zero_margin_formula': 'at zero universal margin floor, immediate close is already safe, so the required prefix floor collapses to 0 bits',
    }

    if target_margin == 0:
        result.update(
            {
                'reason': 'zero_universal_margin_floor_makes_immediate_close_safe_so_no_positive_prefix_budget_is_required',
            }
        )
        return result

    capture_fraction = _capture_fraction(p, effective_horizon_ticks)
    raw_required_prefix_bits = Fraction(
        current_batch_length * (current_batch_length + 1),
        1,
    ) * (hold_cost / p + target_margin / capture_fraction)
    minimum_required_prefix_bits = _ceil_fraction(raw_required_prefix_bits)
    result.update(
        {
            'effective_capture_fraction': _serialize_fraction(capture_fraction),
            'raw_required_prefix_bits': _serialize_fraction(raw_required_prefix_bits),
            'minimum_required_prefix_bits': minimum_required_prefix_bits,
            'universal_seven_bit_floor_suffices': minimum_required_prefix_bits <= UNIVERSAL_PREFIX_BITS,
            'reason': (
                'the_universal_seven_bit_floor_is_large_enough_to_preserve_the_positive_live_promise'
                if minimum_required_prefix_bits <= UNIVERSAL_PREFIX_BITS
                else 'the_universal_seven_bit_floor_is_too_small_to_preserve_the_positive_live_promise'
            ),
        }
    )
    return result


@lru_cache(maxsize=1)
def build_geometric_arrival_live_prefix_floor_validation_summary() -> dict[str, Any]:
    validated_state_contexts = 0
    validated_universal_contexts = 0
    zero_margin_state_contexts = 0
    zero_margin_universal_contexts = 0
    positive_state_admissible_contexts = 0
    positive_state_rejected_contexts = 0
    positive_universal_admissible_contexts = 0
    positive_universal_rejected_contexts = 0
    state_odd_even_pair_plateaus = 0
    universal_odd_even_pair_plateaus = 0
    state_deadline_ladders = 0
    state_deadline_ladders_with_strict_odd_drops = 0
    universal_deadline_ladders = 0
    universal_deadline_ladders_with_strict_odd_drops = 0

    state_zero_example: dict[str, Any] | None = None
    state_admissible_example: dict[str, Any] | None = None
    state_rejected_example: dict[str, Any] | None = None
    universal_zero_example: dict[str, Any] | None = None
    universal_admissible_example: dict[str, Any] | None = None
    universal_rejected_example: dict[str, Any] | None = None

    for state in STATE_GRID:
        state_prefix_bits = _state_prefix_bits(state)
        for current_batch_length in BATCH_GRID:
            for p in ARRIVAL_GRID:
                for hold_cost in HOLD_COST_GRID:
                    for target_margin in TARGET_MARGIN_GRID:
                        prior_required_bits: int | None = None
                        saw_strict_odd_drop = False
                        for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                            profile = compute_state_live_prefix_floor(
                                state,
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                target_margin.numerator,
                                target_margin.denominator,
                                nominal_horizon_ticks,
                            )
                            ceiling_profile = compute_state_live_margin_ceiling(
                                state,
                                current_batch_length,
                                p.numerator,
                                p.denominator,
                                hold_cost.numerator,
                                hold_cost.denominator,
                                nominal_horizon_ticks,
                            )
                            validated_state_contexts += 1
                            ceiling_payload = ceiling_profile['maximum_preservable_nonnegative_margin_bits_per_script']
                            ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
                            actual = target_margin <= ceiling
                            required_bits = int(profile['minimum_required_prefix_bits'])

                            if target_margin == 0:
                                zero_margin_state_contexts += 1
                                if required_bits != 0:
                                    raise GeometricArrivalLivePrefixFloorLawError('zero-margin state prefix floor should be zero')
                                if not actual:
                                    raise GeometricArrivalLivePrefixFloorLawError('zero-margin state prefix floor unexpectedly failed live preservation')
                                if state_zero_example is None:
                                    state_zero_example = {
                                        'prefix_floor_profile': profile,
                                        'live_profile': evaluate_state_effective_horizon_profile(
                                            state,
                                            current_batch_length,
                                            p.numerator,
                                            p.denominator,
                                            hold_cost.numerator,
                                            hold_cost.denominator,
                                            target_margin.numerator,
                                            target_margin.denominator,
                                            nominal_horizon_ticks,
                                        ),
                                    }
                                continue

                            predicted = state_prefix_bits >= required_bits
                            if actual != predicted:
                                raise GeometricArrivalLivePrefixFloorLawError(
                                    f'state prefix-floor mismatch for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )

                            if prior_required_bits is not None:
                                if required_bits > prior_required_bits:
                                    raise GeometricArrivalLivePrefixFloorLawError(
                                        f'state prefix floor increased with more nominal horizon for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                    )
                                if nominal_horizon_ticks % 2 == 0:
                                    if required_bits != prior_required_bits:
                                        raise GeometricArrivalLivePrefixFloorLawError(
                                            f'state odd/even prefix-floor plateau failed for state {state}, n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                                        )
                                    state_odd_even_pair_plateaus += 1
                                elif nominal_horizon_ticks > 1 and required_bits < prior_required_bits:
                                    saw_strict_odd_drop = True

                            if predicted:
                                positive_state_admissible_contexts += 1
                                if state_admissible_example is None:
                                    state_admissible_example = {
                                        'prefix_floor_profile': profile,
                                        'live_profile': evaluate_state_effective_horizon_profile(
                                            state,
                                            current_batch_length,
                                            p.numerator,
                                            p.denominator,
                                            hold_cost.numerator,
                                            hold_cost.denominator,
                                            target_margin.numerator,
                                            target_margin.denominator,
                                            nominal_horizon_ticks,
                                        ),
                                    }
                            else:
                                positive_state_rejected_contexts += 1
                                if state_rejected_example is None:
                                    state_rejected_example = {
                                        'prefix_floor_profile': profile,
                                        'live_profile': evaluate_state_effective_horizon_profile(
                                            state,
                                            current_batch_length,
                                            p.numerator,
                                            p.denominator,
                                            hold_cost.numerator,
                                            hold_cost.denominator,
                                            target_margin.numerator,
                                            target_margin.denominator,
                                            nominal_horizon_ticks,
                                        ),
                                    }

                            prior_required_bits = required_bits

                        if target_margin > 0:
                            state_deadline_ladders += 1
                            if saw_strict_odd_drop:
                                state_deadline_ladders_with_strict_odd_drops += 1

    for current_batch_length in BATCH_GRID:
        for p in ARRIVAL_GRID:
            for hold_cost in HOLD_COST_GRID:
                for target_margin in TARGET_MARGIN_GRID:
                    prior_required_bits: int | None = None
                    saw_strict_odd_drop = False
                    for nominal_horizon_ticks in NOMINAL_HORIZON_GRID:
                        profile = compute_universal_live_prefix_floor(
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            target_margin.numerator,
                            target_margin.denominator,
                            nominal_horizon_ticks,
                        )
                        ceiling_profile = compute_universal_live_margin_ceiling(
                            current_batch_length,
                            p.numerator,
                            p.denominator,
                            hold_cost.numerator,
                            hold_cost.denominator,
                            nominal_horizon_ticks,
                        )
                        validated_universal_contexts += 1
                        ceiling_payload = ceiling_profile['maximum_preservable_nonnegative_margin_bits_per_script']
                        ceiling = Fraction(int(ceiling_payload['numerator']), int(ceiling_payload['denominator']))
                        actual = target_margin <= ceiling
                        required_bits = int(profile['minimum_required_prefix_bits'])

                        if target_margin == 0:
                            zero_margin_universal_contexts += 1
                            if required_bits != 0:
                                raise GeometricArrivalLivePrefixFloorLawError('zero-margin universal prefix floor should be zero')
                            if not actual:
                                raise GeometricArrivalLivePrefixFloorLawError('zero-margin universal prefix floor unexpectedly failed live preservation')
                            if universal_zero_example is None:
                                universal_zero_example = {
                                    'prefix_floor_profile': profile,
                                    'live_profile': evaluate_universal_effective_horizon_profile(
                                        current_batch_length,
                                        p.numerator,
                                        p.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        target_margin.numerator,
                                        target_margin.denominator,
                                        nominal_horizon_ticks,
                                    ),
                                }
                            continue

                        predicted = required_bits <= UNIVERSAL_PREFIX_BITS
                        if actual != predicted:
                            raise GeometricArrivalLivePrefixFloorLawError(
                                f'universal prefix-floor mismatch for n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                            )

                        if prior_required_bits is not None:
                            if required_bits > prior_required_bits:
                                raise GeometricArrivalLivePrefixFloorLawError(
                                    f'universal prefix floor increased with more nominal horizon for n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks}'
                                )
                            if nominal_horizon_ticks % 2 == 0:
                                if required_bits != prior_required_bits:
                                    raise GeometricArrivalLivePrefixFloorLawError(
                                        f'universal odd/even prefix-floor plateau failed for n={current_batch_length}, p={p}, c={hold_cost}, m={target_margin}, H={nominal_horizon_ticks-1}/{nominal_horizon_ticks}'
                                    )
                                universal_odd_even_pair_plateaus += 1
                            elif nominal_horizon_ticks > 1 and required_bits < prior_required_bits:
                                saw_strict_odd_drop = True

                        if predicted:
                            positive_universal_admissible_contexts += 1
                            if universal_admissible_example is None:
                                universal_admissible_example = {
                                    'prefix_floor_profile': profile,
                                    'live_profile': evaluate_universal_effective_horizon_profile(
                                        current_batch_length,
                                        p.numerator,
                                        p.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        target_margin.numerator,
                                        target_margin.denominator,
                                        nominal_horizon_ticks,
                                    ),
                                }
                        else:
                            positive_universal_rejected_contexts += 1
                            if universal_rejected_example is None:
                                universal_rejected_example = {
                                    'prefix_floor_profile': profile,
                                    'live_profile': evaluate_universal_effective_horizon_profile(
                                        current_batch_length,
                                        p.numerator,
                                        p.denominator,
                                        hold_cost.numerator,
                                        hold_cost.denominator,
                                        target_margin.numerator,
                                        target_margin.denominator,
                                        nominal_horizon_ticks,
                                    ),
                                }

                        prior_required_bits = required_bits

                    if target_margin > 0:
                        universal_deadline_ladders += 1
                        if saw_strict_odd_drop:
                            universal_deadline_ladders_with_strict_odd_drops += 1

    if (
        state_zero_example is None
        or state_admissible_example is None
        or state_rejected_example is None
        or universal_zero_example is None
        or universal_admissible_example is None
        or universal_rejected_example is None
    ):
        raise GeometricArrivalLivePrefixFloorLawError('missing witness example for live prefix-floor law')

    return {
        'audited_state_count': len(STATE_GRID),
        'audited_batch_lengths': list(BATCH_GRID),
        'audited_arrival_probabilities': [_serialize_fraction(value) for value in ARRIVAL_GRID],
        'audited_hold_costs': [_serialize_fraction(value) for value in HOLD_COST_GRID],
        'audited_target_margins': [_serialize_fraction(value) for value in TARGET_MARGIN_GRID],
        'audited_nominal_live_deadlines': list(NOMINAL_HORIZON_GRID),
        'validated_state_contexts': validated_state_contexts,
        'validated_universal_contexts': validated_universal_contexts,
        'zero_margin_state_contexts': zero_margin_state_contexts,
        'zero_margin_universal_contexts': zero_margin_universal_contexts,
        'positive_state_admissible_contexts': positive_state_admissible_contexts,
        'positive_state_rejected_contexts': positive_state_rejected_contexts,
        'positive_universal_admissible_contexts': positive_universal_admissible_contexts,
        'positive_universal_rejected_contexts': positive_universal_rejected_contexts,
        'state_odd_even_pair_plateaus': state_odd_even_pair_plateaus,
        'universal_odd_even_pair_plateaus': universal_odd_even_pair_plateaus,
        'state_deadline_ladders': state_deadline_ladders,
        'state_deadline_ladders_with_strict_odd_drops': state_deadline_ladders_with_strict_odd_drops,
        'universal_deadline_ladders': universal_deadline_ladders,
        'universal_deadline_ladders_with_strict_odd_drops': universal_deadline_ladders_with_strict_odd_drops,
        'state_zero_example': state_zero_example,
        'state_admissible_example': state_admissible_example,
        'state_rejected_example': state_rejected_example,
        'universal_zero_example': universal_zero_example,
        'universal_admissible_example': universal_admissible_example,
        'universal_rejected_example': universal_rejected_example,
    }


@lru_cache(maxsize=1)
def build_geometric_arrival_live_prefix_floor_snapshot() -> dict[str, Any]:
    summary = build_geometric_arrival_live_prefix_floor_validation_summary()
    return {
        'focus': 'turn same-deadline stateless live promise admission into a direct integer prefix-budget check so an implementor can compare state_prefix_bits to one exact floor and reuse the same floor against the universal seven-bit guardrail',
        'headline_findings': {
            'positive_live_prefix_floor_rule': 'for positive realized margin floors, same-deadline stateless live control preserves the original promise iff state_prefix_bits >= ceil(n(n + 1) * (hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2))))',
            'universal_seven_bit_rule': 'the all-state seven-bit live guarantee survives exactly when that same required prefix floor is at most 7',
            'zero_margin_rule': 'zero-margin floors require 0 prefix bits because immediate close is already safe',
            'odd_even_pair_rule': 'deadlines 2j - 1 and 2j have identical positive live prefix floors',
            'positive_state_admissible_contexts': summary['positive_state_admissible_contexts'],
            'positive_state_rejected_contexts': summary['positive_state_rejected_contexts'],
            'positive_universal_admissible_contexts': summary['positive_universal_admissible_contexts'],
            'positive_universal_rejected_contexts': summary['positive_universal_rejected_contexts'],
        },
        'decision_rules': [
            'Given batch length n, arrival hazard p, hold cost, target realized margin m, and nominal same-deadline live horizon H, reduce H to effective blind horizon floor((H + 1) / 2).',
            'If m = 0, admit immediately: the required prefix floor is 0 because closing now already preserves the nonnegative promise.',
            'If m > 0, compute required prefix bits ceil(n(n + 1) * (hold_cost / p + m / (1 - (1 - p)^floor((H + 1) / 2)))).',
            'Admit the live promise for a specific state exactly when state_prefix_bits meets or exceeds that integer floor.',
            'Admit the live promise under the seven-bit all-state guardrail exactly when the same required prefix floor is at most 7.',
            'Because the floor depends only on floor((H + 1) / 2), deadlines 2j - 1 and 2j are interchangeable for positive promise admission, and only the next odd rung can lower the required prefix budget.',
        ],
        'state_zero_example': summary['state_zero_example'],
        'state_admissible_example': summary['state_admissible_example'],
        'state_rejected_example': summary['state_rejected_example'],
        'universal_zero_example': summary['universal_zero_example'],
        'universal_admissible_example': summary['universal_admissible_example'],
        'universal_rejected_example': summary['universal_rejected_example'],
        'validation_summary': {key: value for key, value in summary.items() if 'example' not in key},
        'source_reports': [
            'artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.md',
            'artifacts/reports/geometric_arrival_live_hold_cost_ceiling_law_snapshot_20260316.md',
            'artifacts/reports/geometric_arrival_live_margin_ceiling_law_snapshot_20260316.md',
        ],
        'analysis_script': 'scripts/analysis/geometric_arrival_live_prefix_floor_law.py',
    }


def main() -> None:
    print(json.dumps(build_geometric_arrival_live_prefix_floor_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
