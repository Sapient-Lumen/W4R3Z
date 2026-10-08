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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_all_realized_feasible_interval_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law import (
    AFFINE_MARGIN_FAMILY_FORMULAS,
    build_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_profile,
    classify_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_family,
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_state(state: tuple[int, int] | list[int]) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


def _normalize_target_margin(target_margin: int | Fraction | tuple[int, int] | list[int] | dict[str, Any]) -> Fraction:
    if isinstance(target_margin, Fraction):
        return target_margin
    if isinstance(target_margin, int):
        return Fraction(target_margin, 1)
    if isinstance(target_margin, (tuple, list)):
        if len(target_margin) != 2:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
                'tuple/list target margin must contain exactly numerator and denominator'
            )
        return Fraction(int(target_margin[0]), int(target_margin[1]))
    if isinstance(target_margin, dict):
        return Fraction(int(target_margin['numerator']), int(target_margin['denominator']))
    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
        f'unsupported target margin payload: {target_margin!r}'
    )


def _serialize_fraction(value: Fraction) -> dict[str, int | float]:
    return {
        'numerator': value.numerator,
        'denominator': value.denominator,
        'decimal': float(value),
    }


def _family_slope_and_intercept(family_name: str) -> tuple[Fraction, Fraction]:
    try:
        formula = AFFINE_MARGIN_FAMILY_FORMULAS[family_name]
    except KeyError as exc:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
            f'unknown affine family: {family_name}'
        ) from exc
    slope = Fraction(int(formula['slope_numerator']), int(formula['slope_denominator']))
    intercept = Fraction(int(formula['intercept_numerator']), 1)
    return slope, intercept


def _ceil_fraction(value: Fraction) -> int:
    return math.ceil(value.numerator / value.denominator)


@lru_cache(maxsize=None)
def compute_min_batch_length_for_affine_family_target_margin(
    family_name: str,
    target_margin_numerator: int,
    target_margin_denominator: int = 1,
) -> dict[str, Any]:
    target_margin = Fraction(int(target_margin_numerator), int(target_margin_denominator))
    slope, intercept = _family_slope_and_intercept(family_name)
    required = _ceil_fraction((target_margin - intercept) / slope)
    minimum_batch_length = max(1, required)
    achieved_margin = slope * minimum_batch_length + intercept
    previous_margin = slope * (minimum_batch_length - 1) + intercept if minimum_batch_length > 1 else None
    return {
        'affine_margin_family': family_name,
        'affine_margin_formula': AFFINE_MARGIN_FAMILY_FORMULAS[family_name]['formula'],
        'target_margin_bits': _serialize_fraction(target_margin),
        'minimum_batch_length': minimum_batch_length,
        'achieved_margin_bits': _serialize_fraction(achieved_margin),
        'previous_margin_bits': _serialize_fraction(previous_margin) if previous_margin is not None else None,
    }


@lru_cache(maxsize=None)
def compute_min_batch_length_for_state_target_margin(
    state: tuple[int, int] | list[int],
    target_margin_numerator: int,
    target_margin_denominator: int = 1,
) -> dict[str, Any]:
    state = _normalize_state(state)
    family_name = classify_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_family(state)
    family_summary = compute_min_batch_length_for_affine_family_target_margin(
        family_name,
        int(target_margin_numerator),
        int(target_margin_denominator),
    )
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_profile(state)
    return {
        **family_summary,
        'interval_kernel_state': profile['interval_kernel_state'],
        'state_category': profile['state_category'],
        'state_prefix_bit_length': profile['state_prefix_bit_length'],
        'family_cardinality': profile['family_cardinality'],
    }


@lru_cache(maxsize=None)
def compute_universal_min_batch_length_for_target_margin(
    target_margin_numerator: int,
    target_margin_denominator: int = 1,
) -> dict[str, Any]:
    target_margin = Fraction(int(target_margin_numerator), int(target_margin_denominator))
    family_summary = compute_min_batch_length_for_affine_family_target_margin(
        'eight_bit_regular_interior_singleton_margin',
        target_margin.numerator,
        target_margin.denominator,
    )
    return {
        **family_summary,
        'guarantee_scope': 'all_realized_states',
        'guarantee_family': 'eight_bit_regular_interior_singleton_margin',
        'guarantee_formula': '43n/9 - 8',
    }


@lru_cache(maxsize=1)
def build_target_margin_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_targets = [Fraction(0, 1), Fraction(1, 1), Fraction(2, 1), Fraction(5, 1), Fraction(10, 1), Fraction(20, 1)]
    state_target_matches = 0
    universal_matches = 0
    family_counts: dict[str, int] = {}

    for raw_state in states:
        family_name = classify_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_family(raw_state)
        family_counts[family_name] = family_counts.get(family_name, 0) + 1
        for target in audited_targets:
            predicted = compute_min_batch_length_for_state_target_margin(raw_state, target.numerator, target.denominator)
            n = int(predicted['minimum_batch_length'])
            margin_at_n = Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n)['affine_equiprobable_margin_bits']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n)['affine_equiprobable_margin_bits']['denominator']),
            )
            if margin_at_n < target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
                    f'predicted threshold misses target for state {raw_state}, target {target}, batch length {n}'
                )
            if n > 1:
                previous_margin = Fraction(
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n - 1)['affine_equiprobable_margin_bits']['numerator']),
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n - 1)['affine_equiprobable_margin_bits']['denominator']),
                )
                if previous_margin >= target:
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
                        f'predicted threshold is not minimal for state {raw_state}, target {target}, batch length {n}'
                    )
            state_target_matches += 1

    for target in audited_targets:
        predicted = compute_universal_min_batch_length_for_target_margin(target.numerator, target.denominator)
        n = int(predicted['minimum_batch_length'])
        for raw_state in states:
            margin_at_n = Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n)['affine_equiprobable_margin_bits']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n)['affine_equiprobable_margin_bits']['denominator']),
            )
            if margin_at_n < target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
                    f'universal threshold misses target {target} at state {raw_state}'
                )
        if n > 1:
            previous_guaranteed = min(
                Fraction(
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n - 1)['affine_equiprobable_margin_bits']['numerator']),
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(raw_state, n - 1)['affine_equiprobable_margin_bits']['denominator']),
                )
                for raw_state in states
            )
            if previous_guaranteed >= target:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptTargetMarginLawError(
                    f'universal threshold is not minimal for target {target}'
                )
        universal_matches += 1

    examples = []
    for target in audited_targets:
        summary = compute_universal_min_batch_length_for_target_margin(target.numerator, target.denominator)
        examples.append({
            'target_margin_bits': summary['target_margin_bits'],
            'minimum_batch_length': summary['minimum_batch_length'],
            'achieved_margin_bits': summary['achieved_margin_bits'],
        })

    return {
        'audited_state_count': len(states),
        'audited_target_count': len(audited_targets),
        'validated_state_target_pairs': state_target_matches,
        'validated_universal_targets': universal_matches,
        'audited_targets_bits': [_serialize_fraction(target) for target in audited_targets],
        'family_counts': family_counts,
        'universal_examples': examples,
        'universal_guarantee_formula': 'ceil(9(target_bits + 8) / 43)',
    }


@lru_cache(maxsize=1)
def build_target_margin_examples() -> list[dict[str, Any]]:
    examples = []
    for state, target in [
        ((0, 16), Fraction(10, 1)),
        ((7, 12), Fraction(1, 1)),
        ((8, 8), Fraction(2, 1)),
        ((15, 15), Fraction(2, 1)),
        ((1, 2), Fraction(8, 1)),
    ]:
        summary = compute_min_batch_length_for_state_target_margin(state, target.numerator, target.denominator)
        examples.append({
            'interval_kernel_state': summary['interval_kernel_state'],
            'target_margin_bits': summary['target_margin_bits'],
            'affine_margin_family': summary['affine_margin_family'],
            'minimum_batch_length': summary['minimum_batch_length'],
            'achieved_margin_bits': summary['achieved_margin_bits'],
            'previous_margin_bits': summary['previous_margin_bits'],
        })
    return examples


@lru_cache(maxsize=1)
def build_target_margin_headline_findings() -> dict[str, Any]:
    return {
        'catalog_state_count': 153,
        'family_count': 7,
        'universal_guarantee_formula': 'ceil(9(target_bits + 8) / 43)',
        'universal_target_0_bits_batch_length': 2,
        'universal_target_1_bit_batch_length': 2,
        'universal_target_2_bits_batch_length': 3,
        'universal_target_5_bits_batch_length': 3,
        'universal_target_10_bits_batch_length': 4,
        'universal_target_20_bits_batch_length': 6,
    }


@lru_cache(maxsize=1)
def build_target_margin_decision_rules() -> list[str]:
    return [
        'When shared-state exact-shortest-script batches are modeled as equiprobable within-state branches, invert the affine expected-margin law instead of scanning batch lengths.',
        'Per state, compute the minimum batch length for target margin `t` bits as `max(1, ceil((t - intercept_bits) / slope_bits_per_script))` from the state\'s affine family.',
        'For a universal guarantee over all currently realized states, use the lower-envelope inversion `ceil(9(target_bits + 8) / 43)`; it is exact on the current path because the regular eight-bit interior singleton family remains the worst affine case.',
        'Use this batch-sizing rule only for the equiprobable shared-state exact regime; keep the earlier worst-case safe/strict thresholds for adversarial or branch-sensitive transport planning.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_snapshot() -> dict[str, Any]:
    universal_targets = [Fraction(0, 1), Fraction(1, 1), Fraction(2, 1), Fraction(5, 1), Fraction(10, 1), Fraction(20, 1)]
    return {
        'focus': 'Under the equiprobable shared-state exact regime, desired expected savings targets invert directly to minimum batch lengths by affine family, with one exact universal worst-family formula over all realized states.',
        'headline_findings': build_target_margin_headline_findings(),
        'decision_rules': build_target_margin_decision_rules(),
        'universal_target_schedule': [
            compute_universal_min_batch_length_for_target_margin(target.numerator, target.denominator)
            for target in universal_targets
        ],
        'state_examples': build_target_margin_examples(),
        'validation_summary': build_target_margin_validation_summary(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_snapshot(), indent=2, sort_keys=True))
