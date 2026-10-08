#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law import (
    build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile,
    summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    FeasibleIntervalKernelState,
    serialize_feasible_interval_kernel_state,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptAffineMarginLawError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def _normalize_feasible_interval_state(
    state: tuple[int, int] | list[int],
) -> FeasibleIntervalKernelState:
    if len(state) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptAffineMarginLawError(
            'feasible interval state must contain exactly two ranks'
        )
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > 16:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptAffineMarginLawError(
            'feasible interval state must stay within the realized 17-rank path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=None)
def classify_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_family(
    state: tuple[int, int] | list[int],
) -> str:
    state = _normalize_feasible_interval_state(state)
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile(state)
    category = str(profile['state_category'])
    state_prefix_bit_length = int(profile['state_prefix_bit_length'])
    family_cardinality = int(profile['family_cardinality'])
    total_local_choice_prefix_bits = int(profile['total_local_choice_prefix_bits'])
    total_global_exact_word_prefix_bits = int(profile['total_global_exact_word_prefix_bits'])

    signature = (
        category,
        state_prefix_bit_length,
        family_cardinality,
        total_local_choice_prefix_bits,
        total_global_exact_word_prefix_bits,
    )
    signature_to_family = {
        ('identity', 7, 1, 0, 9): 'seven_bit_unique_word_margin',
        ('one_sided_nonidentity', 7, 1, 0, 9): 'seven_bit_unique_word_margin',
        ('one_sided_nonidentity', 8, 1, 0, 9): 'eight_bit_unique_word_margin',
        ('interior_nonsingleton', 7, 2, 2, 18): 'seven_bit_interior_nonsingleton_margin',
        ('interior_nonsingleton', 8, 2, 2, 18): 'eight_bit_interior_nonsingleton_margin',
        ('interior_singleton', 7, 18, 76, 162): 'seven_bit_regular_interior_singleton_margin',
        ('interior_singleton', 8, 18, 76, 162): 'eight_bit_regular_interior_singleton_margin',
        ('interior_singleton', 8, 18, 76, 164): 'fifteen_fifteen_exception_margin',
    }
    try:
        return signature_to_family[signature]
    except KeyError as exc:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptAffineMarginLawError(
            f'unrecognized affine-margin signature for state {state}: {signature}'
        ) from exc


AFFINE_MARGIN_FAMILY_FORMULAS: dict[str, dict[str, Any]] = {
    'seven_bit_unique_word_margin': {
        'slope_numerator': 9,
        'slope_denominator': 1,
        'intercept_numerator': -7,
        'formula': '9n - 7',
        'state_class_description': 'identity and 7-bit one-sided unique-word states',
    },
    'eight_bit_unique_word_margin': {
        'slope_numerator': 9,
        'slope_denominator': 1,
        'intercept_numerator': -8,
        'formula': '9n - 8',
        'state_class_description': '8-bit one-sided unique-word states',
    },
    'seven_bit_interior_nonsingleton_margin': {
        'slope_numerator': 8,
        'slope_denominator': 1,
        'intercept_numerator': -7,
        'formula': '8n - 7',
        'state_class_description': '7-bit interior nonsingleton states',
    },
    'eight_bit_interior_nonsingleton_margin': {
        'slope_numerator': 8,
        'slope_denominator': 1,
        'intercept_numerator': -8,
        'formula': '8n - 8',
        'state_class_description': '8-bit interior nonsingleton states',
    },
    'seven_bit_regular_interior_singleton_margin': {
        'slope_numerator': 43,
        'slope_denominator': 9,
        'intercept_numerator': -7,
        'formula': '43n/9 - 7',
        'state_class_description': '7-bit interior singleton states except the [15,15] edge',
    },
    'eight_bit_regular_interior_singleton_margin': {
        'slope_numerator': 43,
        'slope_denominator': 9,
        'intercept_numerator': -8,
        'formula': '43n/9 - 8',
        'state_class_description': '8-bit interior singleton states except [15,15]',
    },
    'fifteen_fifteen_exception_margin': {
        'slope_numerator': 44,
        'slope_denominator': 9,
        'intercept_numerator': -8,
        'formula': '44n/9 - 8',
        'state_class_description': 'the lone [15,15] interior singleton whose global exact-word family includes two 10-bit words',
    },
}


@lru_cache(maxsize=None)
def build_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_profile(
    state: tuple[int, int] | list[int],
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    threshold_profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile(state)
    affine_family = classify_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_family(state)
    formula = AFFINE_MARGIN_FAMILY_FORMULAS[affine_family]
    slope = Fraction(formula['slope_numerator'], formula['slope_denominator'])
    intercept = Fraction(formula['intercept_numerator'], 1)
    return {
        **threshold_profile,
        'affine_margin_family': affine_family,
        'affine_margin_formula': formula['formula'],
        'affine_margin_state_class_description': formula['state_class_description'],
        'equiprobable_margin_slope_bits_per_script': {
            'numerator': slope.numerator,
            'denominator': slope.denominator,
            'decimal': float(slope),
        },
        'equiprobable_margin_intercept_bits': {
            'numerator': intercept.numerator,
            'denominator': intercept.denominator,
            'decimal': float(intercept),
        },
    }


@lru_cache(maxsize=None)
def evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(
    state: tuple[int, int] | list[int],
    batch_length: int,
) -> dict[str, Any]:
    state = _normalize_feasible_interval_state(state)
    batch_length = int(batch_length)
    if batch_length <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptAffineMarginLawError(
            'batch length must be positive'
        )
    profile = build_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_profile(state)
    slope = Fraction(
        int(profile['equiprobable_margin_slope_bits_per_script']['numerator']),
        int(profile['equiprobable_margin_slope_bits_per_script']['denominator']),
    )
    intercept = Fraction(int(profile['equiprobable_margin_intercept_bits']['numerator']), 1)
    affine_margin = slope * batch_length + intercept
    return {
        **profile,
        'batch_length': batch_length,
        'affine_equiprobable_margin_bits': {
            'numerator': affine_margin.numerator,
            'denominator': affine_margin.denominator,
            'decimal': float(affine_margin),
        },
    }


@lru_cache(maxsize=1)
def build_affine_margin_family_summary() -> dict[str, Any]:
    states = build_all_realized_feasible_interval_states()
    family_counts: Counter[str] = Counter()
    representative_states: dict[str, list[int]] = {}
    for raw_state in states:
        state = tuple(raw_state)
        family = classify_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_family(state)
        family_counts[family] += 1
        representative_states.setdefault(family, list(state))

    ordered_families = []
    for family_name in [
        'seven_bit_unique_word_margin',
        'eight_bit_unique_word_margin',
        'seven_bit_interior_nonsingleton_margin',
        'eight_bit_interior_nonsingleton_margin',
        'seven_bit_regular_interior_singleton_margin',
        'eight_bit_regular_interior_singleton_margin',
        'fifteen_fifteen_exception_margin',
    ]:
        formula = AFFINE_MARGIN_FAMILY_FORMULAS[family_name]
        ordered_families.append({
            'family_name': family_name,
            'state_count': family_counts[family_name],
            'representative_state': serialize_feasible_interval_kernel_state(tuple(representative_states[family_name])),
            'affine_margin_formula': formula['formula'],
            'state_class_description': formula['state_class_description'],
        })

    return {
        'family_count': len(family_counts),
        'families': ordered_families,
        'catalog_state_count': sum(family_counts.values()),
    }


@lru_cache(maxsize=1)
def build_affine_margin_validation_summary() -> dict[str, Any]:
    states = [tuple(state) for state in build_all_realized_feasible_interval_states()]
    audited_batch_lengths = list(range(1, 9))
    matched_cases = 0
    mismatch_examples: list[dict[str, Any]] = []
    for state in states:
        for batch_length in audited_batch_lengths:
            affine_margin = Fraction(
                *[
                    int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, batch_length)['affine_equiprobable_margin_bits'][key])
                    for key in ('numerator', 'denominator')
                ]
            )
            direct_summary = summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean(state, batch_length)
            direct_margin = Fraction(
                int(direct_summary['equiprobable_mean_winning_margin_bits']['numerator']),
                int(direct_summary['equiprobable_mean_winning_margin_bits']['denominator']),
            )
            if affine_margin != direct_margin:
                mismatch_examples.append({
                    'state': serialize_feasible_interval_kernel_state(state),
                    'batch_length': batch_length,
                    'affine_margin': {'numerator': affine_margin.numerator, 'denominator': affine_margin.denominator},
                    'direct_margin': {'numerator': direct_margin.numerator, 'denominator': direct_margin.denominator},
                })
            matched_cases += 1
    if mismatch_examples:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepSharedIntervalStateEquiprobableExactShortestScriptAffineMarginLawError(
            f'affine margin mismatches detected: {mismatch_examples[:3]}'
        )

    minima_by_batch_length = []
    for batch_length in audited_batch_lengths:
        margins = [
            Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, batch_length)['affine_equiprobable_margin_bits']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, batch_length)['affine_equiprobable_margin_bits']['denominator']),
            )
            for state in states
        ]
        minimum_margin = min(margins)
        minimizers = [
            state for state in states
            if Fraction(
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, batch_length)['affine_equiprobable_margin_bits']['numerator']),
                int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, batch_length)['affine_equiprobable_margin_bits']['denominator']),
            ) == minimum_margin
        ]
        minima_by_batch_length.append({
            'batch_length': batch_length,
            'minimum_margin_bits': {
                'numerator': minimum_margin.numerator,
                'denominator': minimum_margin.denominator,
                'decimal': float(minimum_margin),
            },
            'minimizer_count': len(minimizers),
            'representative_minimizer_state': serialize_feasible_interval_kernel_state(minimizers[0]),
            'minimizer_affine_family': classify_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_family(minimizers[0]),
        })

    one_word_tie_states = [
        serialize_feasible_interval_kernel_state(state)
        for state in states
        if Fraction(
            int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, 1)['affine_equiprobable_margin_bits']['numerator']),
            int(evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, 1)['affine_equiprobable_margin_bits']['denominator']),
        ) == 0
    ]

    return {
        'audited_state_count': len(states),
        'audited_batch_lengths': audited_batch_lengths,
        'validated_state_batch_pairs': matched_cases,
        'one_word_tie_state_count': len(one_word_tie_states),
        'representative_one_word_tie_state': one_word_tie_states[0],
        'minimum_margin_by_batch_length': minima_by_batch_length,
        'universal_lower_envelope_formula': '43n/9 - 8',
        'universal_lower_envelope_family': 'eight_bit_regular_interior_singleton_margin',
        'strict_expected_universal_switch_batch_length': 2,
    }


@lru_cache(maxsize=1)
def build_affine_margin_examples() -> list[dict[str, Any]]:
    examples = []
    for state in [(0, 16), (7, 16), (1, 2), (7, 12), (1, 1), (8, 8), (15, 15)]:
        profile = build_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_profile(state)
        margins = {
            str(batch_length): evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin(state, batch_length)['affine_equiprobable_margin_bits']
            for batch_length in (1, 2, 3)
        }
        examples.append({
            'interval_kernel_state': profile['interval_kernel_state'],
            'affine_margin_family': profile['affine_margin_family'],
            'affine_margin_formula': profile['affine_margin_formula'],
            'margin_bits_by_batch_length': margins,
        })
    return examples


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    return {
        'catalog_state_count': 153,
        'affine_margin_family_count': 7,
        'universal_lower_envelope_formula': '43n/9 - 8',
        'universal_strict_expected_switch_batch_length': 2,
        'one_word_expected_tie_state_count': 32,
        'exception_state': serialize_feasible_interval_kernel_state((15, 15)),
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'When exact shortest scripts share one feasible interval state and equiprobable within-state branch frequency is the active source model, evaluate the expected shared-state transport advantage by one affine family formula instead of re-summing family totals.',
        'Use `43n/9 - 8` as the current universal lower envelope for expected shared-state margin over all realized states; it is already positive at `n = 2`, so every realized state is a strict expected winner by batch length 2.',
        'Treat the 32 eight-bit interior nonsingletons as the only one-word expected ties because their affine law is `8n - 8`.',
        'Treat `[15,15]` as the lone affine-family exception because its exact-word family includes two 10-bit global codes, giving slope `44/9` instead of `43/9`.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Under the equiprobable shared-state exact-branch model, expected transport advantage collapses from 153 per-state profiles to seven affine margin families with one universal lower envelope.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'affine_margin_family_summary': build_affine_margin_family_summary(),
        'affine_margin_examples': build_affine_margin_examples(),
        'validation_summary': build_affine_margin_validation_summary(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_snapshot(), indent=2, sort_keys=True))
