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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law import (
    build_uniform_prefix_optimality_summary,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepEquiprobableEntropyHeadroomLawError(RuntimeError):
    pass


def _headroom_profile(*, total_bits: float, entropy_lower_bound_bits: float, represented_count: int) -> dict[str, Any]:
    represented_count = int(represented_count)
    if represented_count <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepEquiprobableEntropyHeadroomLawError(
            'equiprobable entropy headroom only applies to positive represented catalogs'
        )
    total_headroom_bits = float(total_bits) - float(entropy_lower_bound_bits)
    average_headroom_bits = total_headroom_bits / represented_count
    return {
        'represented_count': represented_count,
        'total_headroom_bits': total_headroom_bits,
        'mean_headroom_bits': average_headroom_bits,
        'catalogs_needed_to_save_one_whole_bit_at_mean_rate': math.ceil(1.0 / average_headroom_bits) if average_headroom_bits > 0.0 else None,
    }


@lru_cache(maxsize=1)
def build_equiprobable_entropy_headroom_summary() -> dict[str, Any]:
    optimality = build_uniform_prefix_optimality_summary()
    state_prefix = optimality['source_validation_reports']['state_prefix']
    global_exact_word_prefix = optimality['source_validation_reports']['global_exact_word_prefix']
    local_choice_prefix = optimality['source_validation_reports']['state_known_local_choice_prefix']
    local_choice_profiles = optimality['local_choice_family_optimal_profiles']

    state_profile = _headroom_profile(
        total_bits=optimality['state_prefix_total_optimal_bits'],
        entropy_lower_bound_bits=(
            state_prefix['represented_exact_interval_state_count']
            * state_prefix['exact_uniform_entropy_lower_bound_bits']
        ),
        represented_count=state_prefix['represented_exact_interval_state_count'],
    )
    global_exact_word_profile = _headroom_profile(
        total_bits=optimality['global_exact_word_prefix_total_optimal_bits'],
        entropy_lower_bound_bits=(
            global_exact_word_prefix['represented_exact_shortest_generator_word_count']
            * global_exact_word_prefix['exact_uniform_entropy_lower_bound_bits']
        ),
        represented_count=global_exact_word_prefix['represented_exact_shortest_generator_word_count'],
    )
    canonical_profile = dict(state_profile)

    unique_state_choice_profile = _headroom_profile(
        total_bits=(
            local_choice_profiles['unique_state']['family_count']
            * local_choice_profiles['unique_state']['optimal_total_bits_per_family']
        ),
        entropy_lower_bound_bits=(
            local_choice_profiles['unique_state']['family_count']
            * local_choice_profiles['unique_state']['family_size']
            * math.log2(local_choice_profiles['unique_state']['family_size'])
        ),
        represented_count=(
            local_choice_profiles['unique_state']['family_count']
            * local_choice_profiles['unique_state']['family_size']
        ),
    )
    interior_nonsingleton_choice_profile = _headroom_profile(
        total_bits=(
            local_choice_profiles['interior_nonsingleton']['family_count']
            * local_choice_profiles['interior_nonsingleton']['optimal_total_bits_per_family']
        ),
        entropy_lower_bound_bits=(
            local_choice_profiles['interior_nonsingleton']['family_count']
            * local_choice_profiles['interior_nonsingleton']['family_size']
            * math.log2(local_choice_profiles['interior_nonsingleton']['family_size'])
        ),
        represented_count=(
            local_choice_profiles['interior_nonsingleton']['family_count']
            * local_choice_profiles['interior_nonsingleton']['family_size']
        ),
    )
    interior_singleton_choice_profile = _headroom_profile(
        total_bits=(
            local_choice_profiles['interior_singleton']['family_count']
            * local_choice_profiles['interior_singleton']['optimal_total_bits_per_family']
        ),
        entropy_lower_bound_bits=(
            local_choice_profiles['interior_singleton']['family_count']
            * local_choice_profiles['interior_singleton']['family_size']
            * math.log2(local_choice_profiles['interior_singleton']['family_size'])
        ),
        represented_count=(
            local_choice_profiles['interior_singleton']['family_count']
            * local_choice_profiles['interior_singleton']['family_size']
        ),
    )
    local_choice_overall_profile = _headroom_profile(
        total_bits=optimality['state_known_local_choice_optimal_total_bits'],
        entropy_lower_bound_bits=(
            unique_state_choice_profile['represented_count'] * math.log2(1)
            + interior_nonsingleton_choice_profile['represented_count'] * math.log2(2)
            + interior_singleton_choice_profile['represented_count'] * math.log2(18)
        ),
        represented_count=local_choice_prefix['represented_exact_shortest_word_count'],
    )

    if unique_state_choice_profile['total_headroom_bits'] != 0.0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepEquiprobableEntropyHeadroomLawError(
            'size-1 local choice families should already be entropy-tight'
        )
    if interior_nonsingleton_choice_profile['total_headroom_bits'] != 0.0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepEquiprobableEntropyHeadroomLawError(
            'size-2 local choice families should already be entropy-tight'
        )
    if not math.isclose(
        interior_singleton_choice_profile['total_headroom_bits'],
        local_choice_overall_profile['total_headroom_bits'],
    ):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepEquiprobableEntropyHeadroomLawError(
            'all positive state-known local-choice headroom should be concentrated in the size-18 singleton families'
        )

    if not (global_exact_word_profile['total_headroom_bits'] < 1.0):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepEquiprobableEntropyHeadroomLawError(
            'the current 513-word global exact-script prefix should sit below one whole residual bit of equiprobable headroom'
        )

    max_mean_headroom_profile_name = max(
        {
            'state_prefix': state_profile['mean_headroom_bits'],
            'canonical_shortest_word_prefix': canonical_profile['mean_headroom_bits'],
            'global_exact_word_prefix': global_exact_word_profile['mean_headroom_bits'],
            'state_known_local_choice_prefix': local_choice_overall_profile['mean_headroom_bits'],
        }.items(),
        key=lambda item: item[1],
    )[0]

    return {
        'state_prefix_profile': state_profile,
        'canonical_shortest_word_prefix_profile': canonical_profile,
        'global_exact_word_prefix_profile': global_exact_word_profile,
        'state_known_local_choice_prefix_profile': local_choice_overall_profile,
        'state_known_local_choice_headroom_by_state_category': {
            'unique_state': unique_state_choice_profile,
            'interior_nonsingleton': interior_nonsingleton_choice_profile,
            'interior_singleton': interior_singleton_choice_profile,
        },
        'global_exact_word_prefix_has_less_than_one_total_residual_bit_over_uniform_entropy': True,
        'all_positive_state_known_local_choice_headroom_is_concentrated_in_interior_singleton_families': True,
        'size_1_and_size_2_local_choice_families_are_entropy_tight': True,
        'max_mean_headroom_profile_name': max_mean_headroom_profile_name,
        'changing_tree_shape_cannot_recover_more_bits_than_these_headroom_profiles_allow_under_equiprobable_models': True,
        'source_validation_reports': {
            'uniform_prefix_optimality': optimality,
        },
    }


@lru_cache(maxsize=1)
def build_equiprobable_entropy_headroom_examples() -> list[dict[str, Any]]:
    summary = build_equiprobable_entropy_headroom_summary()
    return [
        {
            'global_exact_word_prefix_is_almost_entropy_tight': {
                'represented_count': summary['global_exact_word_prefix_profile']['represented_count'],
                'total_headroom_bits': summary['global_exact_word_prefix_profile']['total_headroom_bits'],
                'mean_headroom_bits': summary['global_exact_word_prefix_profile']['mean_headroom_bits'],
                'catalogs_needed_to_save_one_whole_bit_at_mean_rate': summary['global_exact_word_prefix_profile']['catalogs_needed_to_save_one_whole_bit_at_mean_rate'],
            }
        },
        {
            'state_prefix_and_canonical_prefix_share_the_same_remaining_equiprobable_headroom': {
                'represented_count': summary['state_prefix_profile']['represented_count'],
                'total_headroom_bits': summary['state_prefix_profile']['total_headroom_bits'],
                'mean_headroom_bits': summary['state_prefix_profile']['mean_headroom_bits'],
                'catalogs_needed_to_save_one_whole_bit_at_mean_rate': summary['state_prefix_profile']['catalogs_needed_to_save_one_whole_bit_at_mean_rate'],
            }
        },
        {
            'state_known_local_choice_headroom_lives_only_in_the_size_18_singleton_families': {
                'overall_total_headroom_bits': summary['state_known_local_choice_prefix_profile']['total_headroom_bits'],
                'interior_singleton_total_headroom_bits': summary['state_known_local_choice_headroom_by_state_category']['interior_singleton']['total_headroom_bits'],
                'unique_state_total_headroom_bits': summary['state_known_local_choice_headroom_by_state_category']['unique_state']['total_headroom_bits'],
                'interior_nonsingleton_total_headroom_bits': summary['state_known_local_choice_headroom_by_state_category']['interior_nonsingleton']['total_headroom_bits'],
            }
        },
    ]


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    summary = build_equiprobable_entropy_headroom_summary()
    return {
        'state_prefix_total_residual_headroom_bits': summary['state_prefix_profile']['total_headroom_bits'],
        'global_exact_word_prefix_total_residual_headroom_bits': summary['global_exact_word_prefix_profile']['total_headroom_bits'],
        'state_known_local_choice_total_residual_headroom_bits': summary['state_known_local_choice_prefix_profile']['total_headroom_bits'],
        'global_exact_word_prefix_is_below_one_total_residual_bit': summary['global_exact_word_prefix_has_less_than_one_total_residual_bit_over_uniform_entropy'],
        'state_known_local_choice_headroom_is_concentrated_in_interior_singletons': summary['all_positive_state_known_local_choice_headroom_is_concentrated_in_interior_singleton_families'],
        'largest_remaining_mean_headroom_profile': summary['max_mean_headroom_profile_name'],
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    summary = build_equiprobable_entropy_headroom_summary()
    return [
        'Do not replace the current 513-word global exact shortest-script prefix with a more complex equiprobable codec just to save bits: its remaining residual headroom is below one whole bit over the full catalog, so any meaningful future gain must come from nonuniform statistics, batching, or a changed side-information regime.',
        f"Treat the 153-state interval prefix and the inherited canonical shortest-script prefix as the main remaining equiprobable transport opportunity only when many states are streamed: they still sit {summary['state_prefix_profile']['total_headroom_bits']:.12f} bits above the entropy bound, or {summary['state_prefix_profile']['mean_headroom_bits']:.12f} bits per state on average.",
        f"When interval state is already known and exact noncanonical shortest branches must survive, all positive equiprobable headroom lives inside the 15 interior singleton choice families: the size-1 and size-2 local choice families are already entropy-tight, while the singleton families still hold {summary['state_known_local_choice_headroom_by_state_category']['interior_singleton']['total_headroom_bits']:.12f} total residual bits across their 270 represented words.",
        'Use the current frontier unchanged unless you are willing to change assumptions: under equiprobable binary-prefix models the trees are already optimal, and under equiprobable non-prefix models the exact remaining gains are capped by the headroom numbers recorded here.',
        'If you do experiment with richer transports under equiprobable assumptions, focus first on the state prefix or the size-18 singleton local-choice families, not on the global exact-word prefix or the size-2 local-choice families.',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Quantify the exact remaining equiprobable entropy headroom after the archive\'s current optimal normalized half-step binary-prefix codecs, so future work only chases richer transports where nontrivial gains still exist.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'equiprobable_entropy_headroom_examples': build_equiprobable_entropy_headroom_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law_snapshot_20260309.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_snapshot(), indent=2, sort_keys=True))
