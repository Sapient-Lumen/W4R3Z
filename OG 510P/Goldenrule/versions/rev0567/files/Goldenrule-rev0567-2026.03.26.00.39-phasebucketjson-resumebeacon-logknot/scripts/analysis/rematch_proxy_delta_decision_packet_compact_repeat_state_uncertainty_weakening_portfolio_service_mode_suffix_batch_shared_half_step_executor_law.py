#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law import (
    clamp_half_step_selector_index_to_doubled_feasible_band,
    select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law import (
    decode_half_step_selector_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    build_interval_realizer,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law import (
    select_batch_minimax_projection_witness_set,
    select_batch_minimax_projection_witness_set_from_half_step_selector_index,
    summarize_preferred_state_codes_by_linf_half_step_selector_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law import (
    summarize_preferred_state_codes_by_l2_selector_interval,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
    select_constraint_family_intersection,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(RuntimeError):
    pass



def select_batch_shared_half_step_witness_set(
    constraints: list[dict[str, Any]], *, half_step_selector_index: int
) -> dict[str, Any]:
    family = select_constraint_family_intersection(constraints)
    result: dict[str, Any] = {
        'family': family,
        'half_step_selector_index': half_step_selector_index,
    }
    if not family['feasible']:
        result['selection_status'] = 'infeasible'
        result['projected_half_step_witness_index'] = None
        result['projected_optimal_state_codes'] = []
        result['projected_optimal_interval'] = None
        result['selection_certificate'] = {'blocker_certificate': family['blocker_certificate']}
        return result

    clamped = clamp_half_step_selector_index_to_doubled_feasible_band(
        half_step_selector_index=half_step_selector_index,
        feasible_lower_rank=family['lower_rank_bound'],
        feasible_upper_rank=family['upper_rank_bound'],
    )
    result['selection_status'] = 'selected'
    result['projected_half_step_witness_index'] = clamped['projected_half_step_witness_index']
    result['projected_optimal_interval'] = clamped['projected_optimal_interval']
    result['projected_optimal_state_codes'] = clamped['projected_optimal_state_codes']
    result['selection_certificate'] = {
        'doubled_feasible_band': clamped['doubled_feasible_band'],
        'clamp_case': clamped['clamp_case'],
        'projected_half_step_witness_index': clamped['projected_half_step_witness_index'],
    }
    return result


@lru_cache(maxsize=1)
def build_batch_shared_half_step_executor_examples() -> list[dict[str, Any]]:
    interval_0_2_family = [build_interval_realizer(0, 2)]
    interval_6_9_family = [build_interval_realizer(6, 9)]
    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    l2_bundle = ['S10', 'S10', 'S8']
    linf_bundle = ['S10', 'E8']
    l2_summary = summarize_preferred_state_codes_by_l2_selector_interval(l2_bundle)
    linf_summary = summarize_preferred_state_codes_by_linf_half_step_selector_index(linf_bundle)
    l2_half_step_selector_index = sum(l2_summary['selector_interval_summary'])
    if l2_half_step_selector_index != linf_summary['half_step_selector_index']:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
            'example bundles should share one half-step selector index'
        )
    shared_index = l2_half_step_selector_index
    return [
        {
            'same_half_step_index_from_distinct_semantics': {
                'l2_bundle': l2_bundle,
                'l2_summary': l2_summary,
                'linf_bundle': linf_bundle,
                'linf_summary': linf_summary,
                'shared_half_step_selector_index': shared_index,
                'shared_executor_selection': select_batch_shared_half_step_witness_set(
                    interval_0_2_family,
                    half_step_selector_index=shared_index,
                ),
                'path_l2_selection': select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                    interval_0_2_family,
                    half_step_selector_index=shared_index,
                ),
                'path_linf_selection': select_batch_minimax_projection_witness_set_from_half_step_selector_index(
                    interval_0_2_family,
                    half_step_selector_index=shared_index,
                ),
            }
        },
        {
            'same_low_boundary_collapse_for_both_semantics': {
                'input_half_step_selector_index': 3,
                'decoded_input_selector_interval': decode_half_step_selector_index(half_step_selector_index=3),
                'shared_executor_selection': select_batch_shared_half_step_witness_set(
                    interval_6_9_family,
                    half_step_selector_index=3,
                ),
                'path_l2_selection': select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                    interval_6_9_family,
                    half_step_selector_index=3,
                ),
                'path_linf_selection': select_batch_minimax_projection_witness_set_from_half_step_selector_index(
                    interval_6_9_family,
                    half_step_selector_index=3,
                ),
            }
        },
        {
            'full_bundle_vs_endpoint_summary_inputs': {
                'path_l2_bundle_selection': select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                    interval_0_2_family,
                    half_step_selector_index=sum(
                        summarize_preferred_state_codes_by_l2_selector_interval(['S10', 'S9', 'S8'])['selector_interval_summary']
                    ),
                ),
                'path_linf_bundle_selection': select_batch_minimax_projection_witness_set(
                    interval_0_2_family,
                    preferred_state_codes=['S10', 'S8'],
                ),
            }
        },
        {
            'infeasible_selection': select_batch_shared_half_step_witness_set(
                infeasible_family,
                half_step_selector_index=15,
            )
        },
    ]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_executor_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    validation_case_count = 0
    preserve_within_band_case_count = 0
    clamp_up_to_lower_boundary_case_count = 0
    clamp_down_to_upper_boundary_case_count = 0
    distinct_projected_half_step_witness_indices: set[int] = set()

    for half_step_selector_index in range(33):
        for row in realized:
            validation_case_count += 1
            constraints = [build_interval_realizer(row['lower_rank'], row['upper_rank'])]
            shared_selection = select_batch_shared_half_step_witness_set(
                constraints,
                half_step_selector_index=half_step_selector_index,
            )
            path_l2_selection = select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                constraints,
                half_step_selector_index=half_step_selector_index,
            )
            path_linf_selection = select_batch_minimax_projection_witness_set_from_half_step_selector_index(
                constraints,
                half_step_selector_index=half_step_selector_index,
            )

            if shared_selection['projected_optimal_state_codes'] != path_l2_selection['projected_optimal_state_codes']:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
                    'shared executor mismatch against path-L2 half-step clamp law'
                )
            if shared_selection['projected_optimal_state_codes'] != path_linf_selection['projected_optimal_state_codes']:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
                    'shared executor mismatch against path-Linf half-step selection law'
                )
            if shared_selection['projected_half_step_witness_index'] != path_l2_selection['projected_half_step_witness_index']:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
                    'shared executor witness index mismatch against path-L2'
                )
            if shared_selection['projected_half_step_witness_index'] != path_linf_selection['projected_half_step_witness_index']:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
                    'shared executor witness index mismatch against path-Linf'
                )

            expected_index = min(max(half_step_selector_index, 2 * row['lower_rank']), 2 * row['upper_rank'])
            if shared_selection['projected_half_step_witness_index'] != expected_index:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
                    'shared executor witness index does not equal doubled-band clamp formula'
                )
            distinct_projected_half_step_witness_indices.add(expected_index)

            clamp_case = shared_selection['selection_certificate']['clamp_case']
            if clamp_case == 'preserve_within_band':
                preserve_within_band_case_count += 1
            elif clamp_case == 'clamp_up_to_lower_boundary':
                clamp_up_to_lower_boundary_case_count += 1
            elif clamp_case == 'clamp_down_to_upper_boundary':
                clamp_down_to_upper_boundary_case_count += 1
            else:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
                    'unexpected clamp case label'
                )

    if len(distinct_projected_half_step_witness_indices) != 33:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepExecutorLawError(
            'shared executor should realize the full 33-class output lattice'
        )

    return {
        'validated_realized_interval_count': len(realized),
        'validated_half_step_selector_index_class_count': 33,
        'half_step_selector_index_range': [0, 32],
        'validated_selection_case_count': validation_case_count,
        'shared_executor_matches_path_l2_half_step_clamp_law': True,
        'shared_executor_matches_path_linf_half_step_selection_law': True,
        'shared_executor_validation_pair_count': validation_case_count * 2,
        'distinct_projected_half_step_witness_index_count': len(distinct_projected_half_step_witness_indices),
        'projected_half_step_witness_index_range': [
            min(distinct_projected_half_step_witness_indices),
            max(distinct_projected_half_step_witness_indices),
        ],
        'preserve_within_band_case_count': preserve_within_band_case_count,
        'clamp_up_to_lower_boundary_case_count': clamp_up_to_lower_boundary_case_count,
        'clamp_down_to_upper_boundary_case_count': clamp_down_to_upper_boundary_case_count,
        'path_l2_and_path_linf_share_the_same_feasible_executor_once_half_step_selector_index_is_fixed': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_shared_half_step_executor_validation_summary()
    return {
        'once_batch_compromise_is_encoded_as_one_half_step_selector_index_path_l2_and_path_linf_share_one_exact_feasible_executor': validation[
            'path_l2_and_path_linf_share_the_same_feasible_executor_once_half_step_selector_index_is_fixed'
        ],
        'validated_half_step_selector_index_and_interval_pairs': validation['validated_selection_case_count'],
        'validated_semantics_specific_equivalence_checks': validation['shared_executor_validation_pair_count'],
        'shared_executor_still_uses_the_full_33_class_output_lattice': validation[
            'distinct_projected_half_step_witness_index_count'
        ],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'Once a batch compromise request has already been reduced to one half_step_selector_index, stop branching on whether that index came from path-L2 means or path-Linf endpoints.',
        'For both semantics, compute feasibility first; if the overlap interval is [a, b], the selected witness class is always clamp(half_step_selector_index, 2a, 2b) on the shared half-step lattice.',
        'Treat the semantic difference between path-L2 and path-Linf as an input-side issue only: path-L2 derives the selector index from the preferred mean, while path-Linf derives it from the preferred extrema.',
        'Keep the existing path-L2 fingerprint and audit surfaces for any request already normalized to half_step_selector_index, because the feasible executor and output vocabulary are identical for path-Linf.',
        'Do not extend this shared-executor shortcut to path-L1: median semantics can disagree with the half-step selector even when the feasible interval is the same.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_executor_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Once batch compromise is normalized to one half-step selector index, path-L2 and path-Linf share the same exact feasible witness executor.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_shared_half_step_executor_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law.py',
    }



def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_executor_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
