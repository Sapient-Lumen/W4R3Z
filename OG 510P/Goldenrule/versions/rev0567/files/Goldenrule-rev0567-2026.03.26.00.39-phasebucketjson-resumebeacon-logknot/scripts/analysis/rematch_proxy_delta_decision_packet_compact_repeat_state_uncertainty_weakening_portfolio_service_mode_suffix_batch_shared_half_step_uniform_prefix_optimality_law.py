#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law import (
    build_canonical_shortest_generator_word_prefix_validation_summary,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law import (
    build_feasible_interval_state_prefix_validation_summary,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law import (
    build_shortest_generator_word_choice_prefix_validation_summary,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law import (
    build_batch_shared_half_step_shortest_generator_word_family_validation_summary,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law import (
    build_shortest_generator_word_prefix_validation_summary,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(RuntimeError):
    pass


def _uniform_prefix_length_spectrum(catalog_size: int) -> dict[int, int]:
    catalog_size = int(catalog_size)
    if catalog_size <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'equiprobable prefix optimality only applies to positive catalog sizes'
        )
    if catalog_size == 1:
        return {0: 1}

    short_bit_length = math.floor(math.log2(catalog_size))
    long_bit_length = math.ceil(math.log2(catalog_size))
    if short_bit_length == long_bit_length:
        return {short_bit_length: catalog_size}

    short_code_count = 2**long_bit_length - catalog_size
    long_code_count = 2 * catalog_size - 2**long_bit_length
    spectrum = {}
    if short_code_count:
        spectrum[short_bit_length] = short_code_count
    if long_code_count:
        spectrum[long_bit_length] = long_code_count
    return spectrum


def _total_bits_from_spectrum(spectrum: dict[int, int]) -> int:
    return sum(int(bit_length) * int(code_count) for bit_length, code_count in spectrum.items())


@lru_cache(maxsize=1)
def build_uniform_prefix_optimality_summary() -> dict[str, Any]:
    state_prefix = build_feasible_interval_state_prefix_validation_summary()
    exact_word_prefix = build_shortest_generator_word_prefix_validation_summary()
    choice_prefix = build_shortest_generator_word_choice_prefix_validation_summary()
    family_summary = build_batch_shared_half_step_shortest_generator_word_family_validation_summary()
    canonical_prefix = build_canonical_shortest_generator_word_prefix_validation_summary()

    state_optimal_spectrum = _uniform_prefix_length_spectrum(state_prefix['represented_exact_interval_state_count'])
    state_actual_spectrum = {
        state_prefix['short_prefix_bit_length']: state_prefix['short_prefix_code_count'],
        state_prefix['long_prefix_bit_length']: state_prefix['long_prefix_code_count'],
    }
    if state_actual_spectrum != state_optimal_spectrum:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            f'state prefix spectrum mismatch: expected {state_optimal_spectrum}, got {state_actual_spectrum}'
        )
    if state_prefix['total_prefix_bits_over_exact_interval_catalog'] != _total_bits_from_spectrum(state_optimal_spectrum):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'state prefix total bits do not match the equiprobable optimum'
        )

    exact_word_optimal_spectrum = _uniform_prefix_length_spectrum(exact_word_prefix['represented_exact_shortest_generator_word_count'])
    exact_word_actual_spectrum = {
        exact_word_prefix['short_prefix_bit_length']: exact_word_prefix['short_prefix_code_count'],
        exact_word_prefix['long_prefix_bit_length']: exact_word_prefix['long_prefix_code_count'],
    }
    if exact_word_actual_spectrum != exact_word_optimal_spectrum:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            f'exact-word prefix spectrum mismatch: expected {exact_word_optimal_spectrum}, got {exact_word_actual_spectrum}'
        )
    if exact_word_prefix['total_prefix_bits_over_exact_catalog'] != _total_bits_from_spectrum(exact_word_optimal_spectrum):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'exact-word prefix total bits do not match the equiprobable optimum'
        )

    category_state_counts = family_summary['state_count_by_interval_category']
    unique_state_family_count = category_state_counts['identity'] + category_state_counts['one_sided_nonidentity']
    interior_nonsingleton_family_count = category_state_counts['interior_nonsingleton']
    interior_singleton_family_count = category_state_counts['interior_singleton']

    unique_state_family_spectrum = _uniform_prefix_length_spectrum(1)
    interior_nonsingleton_family_spectrum = _uniform_prefix_length_spectrum(2)
    interior_singleton_family_spectrum = _uniform_prefix_length_spectrum(18)

    if choice_prefix['choice_prefix_bit_length_spectrum_by_state_category']['unique_state'] != {
        bit_length: code_count * unique_state_family_count
        for bit_length, code_count in unique_state_family_spectrum.items()
    }:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'unique-state local choice prefix spectrum must match the size-1 equiprobable optimum over all families'
        )
    if choice_prefix['choice_prefix_bit_length_spectrum_by_state_category']['interior_nonsingleton'] != {
        bit_length: code_count * interior_nonsingleton_family_count
        for bit_length, code_count in interior_nonsingleton_family_spectrum.items()
    }:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'interior nonsingleton local choice prefix spectrum must match the size-2 equiprobable optimum over all families'
        )
    if choice_prefix['choice_prefix_bit_length_spectrum_by_state_category']['interior_singleton'] != {
        bit_length: code_count * interior_singleton_family_count
        for bit_length, code_count in interior_singleton_family_spectrum.items()
    }:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'interior singleton local choice prefix spectrum must match the size-18 equiprobable optimum over all families'
        )

    expected_choice_total_bits = (
        unique_state_family_count * _total_bits_from_spectrum(unique_state_family_spectrum)
        + interior_nonsingleton_family_count * _total_bits_from_spectrum(interior_nonsingleton_family_spectrum)
        + interior_singleton_family_count * _total_bits_from_spectrum(interior_singleton_family_spectrum)
    )
    if choice_prefix['total_choice_prefix_bits_over_exact_word_catalog'] != expected_choice_total_bits:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'state-known local choice prefix total bits do not match the sum of familywise equiprobable optima'
        )

    expected_family_total_spectrum = {
        _total_bits_from_spectrum(unique_state_family_spectrum): unique_state_family_count,
        _total_bits_from_spectrum(interior_nonsingleton_family_spectrum): interior_nonsingleton_family_count,
        _total_bits_from_spectrum(interior_singleton_family_spectrum): interior_singleton_family_count,
    }
    if choice_prefix['state_local_choice_family_total_prefix_bits_spectrum'] != expected_family_total_spectrum:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'familywise local-choice total-bit spectrum must match the familywise equiprobable optima'
        )

    canonical_state_actual_spectrum = state_actual_spectrum
    canonical_state_optimal_spectrum = _uniform_prefix_length_spectrum(canonical_prefix['represented_canonical_shortest_generator_word_count'])
    if canonical_state_actual_spectrum != canonical_state_optimal_spectrum:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'canonical shortest-word prefix must inherit the same equiprobable optimum as the state prefix'
        )
    if canonical_prefix['total_prefix_bits_over_canonical_catalog'] != _total_bits_from_spectrum(canonical_state_optimal_spectrum):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepUniformPrefixOptimalityLawError(
            'canonical shortest-word prefix total bits do not match the equiprobable optimum'
        )

    state_entropy_gap_bits = state_prefix['total_prefix_bits_over_exact_interval_catalog'] - (
        state_prefix['represented_exact_interval_state_count'] * state_prefix['exact_uniform_entropy_lower_bound_bits']
    )
    exact_word_entropy_gap_bits = exact_word_prefix['total_prefix_bits_over_exact_catalog'] - (
        exact_word_prefix['represented_exact_shortest_generator_word_count'] * exact_word_prefix['exact_uniform_entropy_lower_bound_bits']
    )
    interior_singleton_entropy_gap_bits_per_family = _total_bits_from_spectrum(interior_singleton_family_spectrum) - 18 * math.log2(18)

    return {
        'state_prefix_is_uniform_prefix_optimal': True,
        'global_exact_word_prefix_is_uniform_prefix_optimal': True,
        'state_known_local_choice_prefix_is_familywise_uniform_prefix_optimal': True,
        'canonical_shortest_word_prefix_inherits_uniform_prefix_optimality_from_state_prefix': True,
        'no_current_uniform_binary_prefix_catalog_can_lose_one_bit_without_leaving_the_prefix_or_equiprobable_regime': True,
        'state_prefix_optimal_length_spectrum': state_optimal_spectrum,
        'state_prefix_total_optimal_bits': _total_bits_from_spectrum(state_optimal_spectrum),
        'global_exact_word_prefix_optimal_length_spectrum': exact_word_optimal_spectrum,
        'global_exact_word_prefix_total_optimal_bits': _total_bits_from_spectrum(exact_word_optimal_spectrum),
        'local_choice_family_optimal_profiles': {
            'unique_state': {
                'family_count': unique_state_family_count,
                'family_size': 1,
                'optimal_length_spectrum_per_family': unique_state_family_spectrum,
                'optimal_total_bits_per_family': _total_bits_from_spectrum(unique_state_family_spectrum),
            },
            'interior_nonsingleton': {
                'family_count': interior_nonsingleton_family_count,
                'family_size': 2,
                'optimal_length_spectrum_per_family': interior_nonsingleton_family_spectrum,
                'optimal_total_bits_per_family': _total_bits_from_spectrum(interior_nonsingleton_family_spectrum),
            },
            'interior_singleton': {
                'family_count': interior_singleton_family_count,
                'family_size': 18,
                'optimal_length_spectrum_per_family': interior_singleton_family_spectrum,
                'optimal_total_bits_per_family': _total_bits_from_spectrum(interior_singleton_family_spectrum),
            },
        },
        'state_known_local_choice_optimal_total_bits': expected_choice_total_bits,
        'state_prefix_entropy_gap_bits_over_uniform_bound': state_entropy_gap_bits,
        'global_exact_word_prefix_entropy_gap_bits_over_uniform_bound': exact_word_entropy_gap_bits,
        'interior_singleton_choice_entropy_gap_bits_per_family': interior_singleton_entropy_gap_bits_per_family,
        'source_validation_reports': {
            'state_prefix': state_prefix,
            'global_exact_word_prefix': exact_word_prefix,
            'state_known_local_choice_prefix': choice_prefix,
            'canonical_shortest_word_prefix': canonical_prefix,
        },
    }


@lru_cache(maxsize=1)
def build_uniform_prefix_optimality_examples() -> list[dict[str, Any]]:
    summary = build_uniform_prefix_optimality_summary()
    return [
        {
            'state_catalog_153_forces_the_103x7_plus_50x8_split': {
                'catalog_size': 153,
                'optimal_length_spectrum': summary['state_prefix_optimal_length_spectrum'],
                'optimal_total_bits': summary['state_prefix_total_optimal_bits'],
            }
        },
        {
            'exact_word_catalog_513_forces_the_511x9_plus_2x10_split': {
                'catalog_size': 513,
                'optimal_length_spectrum': summary['global_exact_word_prefix_optimal_length_spectrum'],
                'optimal_total_bits': summary['global_exact_word_prefix_total_optimal_bits'],
            }
        },
        {
            'state_known_singleton_choice_families_force_the_14x4_plus_4x5_split': {
                'family_count': summary['local_choice_family_optimal_profiles']['interior_singleton']['family_count'],
                'family_size': summary['local_choice_family_optimal_profiles']['interior_singleton']['family_size'],
                'optimal_length_spectrum_per_family': summary['local_choice_family_optimal_profiles']['interior_singleton']['optimal_length_spectrum_per_family'],
                'optimal_total_bits_per_family': summary['local_choice_family_optimal_profiles']['interior_singleton']['optimal_total_bits_per_family'],
            }
        },
    ]


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    summary = build_uniform_prefix_optimality_summary()
    return {
        'state_prefix_is_already_uniform_prefix_optimal': summary['state_prefix_is_uniform_prefix_optimal'],
        'global_exact_word_prefix_is_already_uniform_prefix_optimal': summary['global_exact_word_prefix_is_uniform_prefix_optimal'],
        'state_known_local_choice_prefix_is_already_familywise_uniform_prefix_optimal': summary['state_known_local_choice_prefix_is_familywise_uniform_prefix_optimal'],
        'further_savings_require_nonuniform_or_nonprefix_assumptions': summary['no_current_uniform_binary_prefix_catalog_can_lose_one_bit_without_leaving_the_prefix_or_equiprobable_regime'],
        'state_prefix_total_optimal_bits': summary['state_prefix_total_optimal_bits'],
        'global_exact_word_prefix_total_optimal_bits': summary['global_exact_word_prefix_total_optimal_bits'],
        'state_known_local_choice_optimal_total_bits': summary['state_known_local_choice_optimal_total_bits'],
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'Do not spend research effort searching for a strictly shorter binary prefix code for the current uniform 153-state normalized feasible-interval catalog: the existing split of 103 seven-bit leaves and 50 eight-bit leaves is already the equiprobable optimum.',
        'Do not search for a strictly shorter binary prefix code for the current uniform 513-word exact shortest-generator-word catalog either: the existing split of 511 nine-bit leaves and 2 ten-bit leaves is already the equiprobable optimum.',
        'When the decoder already knows interval state and the exact shortest branch must survive, keep using the current local choice prefix. Its three family types already match the familywise equiprobable optima: size-1 families use 0 bits, size-2 families use 1 bit per branch, and size-18 singleton families use the forced 14x4 plus 4x5 split.',
        'Treat the canonical shortest-word prefix as already certified by inheritance: because canonical standalone script transport collapses to interval-state transport, its uniform prefix optimum is exactly the same 153-state optimum.',
        'Any further bit savings now require changing assumptions rather than retuning tree shape: use a nonuniform source model, a different side-information regime, canonical reconstruction, or a non-prefix transport family.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Current normalized half-step prefix codecs are already optimal under the archive\'s equiprobable binary-prefix catalog assumptions.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'uniform_prefix_optimality_examples': build_uniform_prefix_optimality_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_snapshot(), indent=2, sort_keys=True))
