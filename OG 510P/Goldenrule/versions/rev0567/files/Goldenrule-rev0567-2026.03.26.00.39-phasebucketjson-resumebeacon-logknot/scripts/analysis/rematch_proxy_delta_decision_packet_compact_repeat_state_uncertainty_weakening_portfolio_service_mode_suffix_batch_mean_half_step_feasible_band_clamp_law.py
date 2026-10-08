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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law import (
    build_max_half_step_selector_index,
    decode_half_step_selector_index,
    select_batch_mean_projection_witness_set_from_half_step_selector_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    build_interval_realizer,
    build_rank_to_code,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
    select_constraint_family_intersection,
)


class WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(RuntimeError):
    pass



def clamp_half_step_selector_index_to_doubled_feasible_band(
    *,
    half_step_selector_index: int,
    feasible_lower_rank: int,
    feasible_upper_rank: int,
) -> dict[str, Any]:
    max_index = build_max_half_step_selector_index()
    if half_step_selector_index < 0 or half_step_selector_index > max_index:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(
            'half-step selector index falls outside the source-rank path'
        )
    if feasible_lower_rank > feasible_upper_rank:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(
            'feasible interval must be nonempty'
        )

    doubled_feasible_lower_bound = 2 * feasible_lower_rank
    doubled_feasible_upper_bound = 2 * feasible_upper_rank
    clamped_half_step_witness_index = min(
        max(half_step_selector_index, doubled_feasible_lower_bound),
        doubled_feasible_upper_bound,
    )

    if clamped_half_step_witness_index == half_step_selector_index:
        clamp_case = 'preserve_within_band'
    elif clamped_half_step_witness_index == doubled_feasible_lower_bound:
        clamp_case = 'clamp_up_to_lower_boundary'
    elif clamped_half_step_witness_index == doubled_feasible_upper_bound:
        clamp_case = 'clamp_down_to_upper_boundary'
    else:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(
            'clamped half-step witness index should either be preserved or land on a doubled feasible boundary'
        )

    decoded = decode_half_step_selector_index(half_step_selector_index=clamped_half_step_witness_index)
    projected_lower_rank, projected_upper_rank = decoded['selector_interval_summary']
    projected_optimal_state_codes = [
        build_rank_to_code()[rank] for rank in range(projected_lower_rank, projected_upper_rank + 1)
    ]
    return {
        'input_half_step_selector_index': half_step_selector_index,
        'doubled_feasible_band': [doubled_feasible_lower_bound, doubled_feasible_upper_bound],
        'projected_half_step_witness_index': clamped_half_step_witness_index,
        'clamp_case': clamp_case,
        'projected_optimal_interval': {
            'lower_rank': projected_lower_rank,
            'upper_rank': projected_upper_rank,
            'cardinality': projected_upper_rank - projected_lower_rank + 1,
            'state_codes': projected_optimal_state_codes,
        },
        'projected_optimal_state_codes': projected_optimal_state_codes,
    }



def select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
    constraints: list[dict[str, Any]],
    *,
    half_step_selector_index: int,
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
def build_batch_mean_half_step_feasible_band_clamp_examples() -> list[dict[str, Any]]:
    interval_1_3_family = [build_interval_realizer(1, 3)]
    interval_6_9_family = [build_interval_realizer(6, 9)]
    interval_4_11_family = [build_interval_realizer(4, 11)]
    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    return [
        {
            'boundary_tie_input_index': 1,
            'interval_1_3_selection': select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                interval_1_3_family,
                half_step_selector_index=1,
            ),
        },
        {
            'midpath_tie_input_index': 15,
            'interval_6_9_selection': select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                interval_6_9_family,
                half_step_selector_index=15,
            ),
        },
        {
            'upper_skew_input_index': 27,
            'interval_4_11_selection': select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                interval_4_11_family,
                half_step_selector_index=27,
            ),
        },
        {
            'low_inputs_collapse_to_same_boundary': [0, 3, 9],
            'interval_6_9_output_indices': [
                select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                    interval_6_9_family,
                    half_step_selector_index=index,
                )['projected_half_step_witness_index']
                for index in [0, 3, 9]
            ],
        },
        {
            'infeasible_selection': select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                infeasible_family,
                half_step_selector_index=15,
            ),
        },
    ]


@lru_cache(maxsize=1)
def build_batch_mean_half_step_feasible_band_clamp_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    validation_case_count = 0
    preserve_within_band_case_count = 0
    clamp_up_to_lower_boundary_case_count = 0
    clamp_down_to_upper_boundary_case_count = 0
    distinct_projected_half_step_witness_indices: set[int] = set()

    for half_step_selector_index in range(build_max_half_step_selector_index() + 1):
        for row in realized:
            validation_case_count += 1
            constraints = [build_interval_realizer(row['lower_rank'], row['upper_rank'])]
            clamped_selection = select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
                constraints,
                half_step_selector_index=half_step_selector_index,
            )
            selector_projection_selection = select_batch_mean_projection_witness_set_from_half_step_selector_index(
                constraints,
                half_step_selector_index=half_step_selector_index,
            )
            if (
                clamped_selection['projected_optimal_state_codes']
                != selector_projection_selection['projected_optimal_state_codes']
            ):
                raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(
                    'half-step feasible-band clamp selection mismatch against selector-interval projection'
                )

            expected_index = min(
                max(half_step_selector_index, 2 * row['lower_rank']),
                2 * row['upper_rank'],
            )
            if clamped_selection['projected_half_step_witness_index'] != expected_index:
                raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(
                    'projected half-step witness index does not equal the doubled-band clamp formula'
                )
            distinct_projected_half_step_witness_indices.add(expected_index)

            clamp_case = clamped_selection['selection_certificate']['clamp_case']
            if clamp_case == 'preserve_within_band':
                preserve_within_band_case_count += 1
            elif clamp_case == 'clamp_up_to_lower_boundary':
                clamp_up_to_lower_boundary_case_count += 1
            elif clamp_case == 'clamp_down_to_upper_boundary':
                clamp_down_to_upper_boundary_case_count += 1
            else:
                raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(
                    'unexpected clamp case label'
                )

    projected_index_range = [
        min(distinct_projected_half_step_witness_indices),
        max(distinct_projected_half_step_witness_indices),
    ]
    if len(distinct_projected_half_step_witness_indices) != build_max_half_step_selector_index() + 1:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepFeasibleBandClampLawError(
            'projected half-step witness indices should still realize the full half-step lattice'
        )

    return {
        'validated_realized_interval_count': len(realized),
        'validated_half_step_selector_index_class_count': build_max_half_step_selector_index() + 1,
        'half_step_selector_index_range': [0, build_max_half_step_selector_index()],
        'validated_selection_case_count': validation_case_count,
        'clamp_formula_matches_selector_interval_projection': True,
        'projected_half_step_witness_indices_share_the_same_33_class_lattice': True,
        'distinct_projected_half_step_witness_index_count': len(distinct_projected_half_step_witness_indices),
        'projected_half_step_witness_index_range': projected_index_range,
        'preserve_within_band_case_count': preserve_within_band_case_count,
        'clamp_up_to_lower_boundary_case_count': clamp_up_to_lower_boundary_case_count,
        'clamp_down_to_upper_boundary_case_count': clamp_down_to_upper_boundary_case_count,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_mean_half_step_feasible_band_clamp_validation_summary()
    return {
        'path_l2_witness_choice_is_a_one_integer_clamp_over_the_half_step_lattice': validation[
            'clamp_formula_matches_selector_interval_projection'
        ],
        'validated_selection_case_count': validation['validated_selection_case_count'],
        'input_and_output_share_the_same_33_half_step_classes': validation[
            'distinct_projected_half_step_witness_index_count'
        ],
        'clamp_case_partition': {
            'preserve_within_band': validation['preserve_within_band_case_count'],
            'clamp_up_to_lower_boundary': validation['clamp_up_to_lower_boundary_case_count'],
            'clamp_down_to_upper_boundary': validation['clamp_down_to_upper_boundary_case_count'],
        },
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'If a path-L2 compromise request is already encoded as half_step_selector_index = h and the feasible overlap interval is [a, b], compute the witness class directly as clamp(h, 2a, 2b).',
        'Interpret even witness indices 2k as singleton outputs [k, k] and odd witness indices 2k+1 as adjacent tie outputs [k, k+1].',
        'Stay on the same half-step lattice for both request classes and witness classes; selector decoding is optional bookkeeping, not required execution logic.',
        'Read the clamp cases literally: preserve the selector inside the doubled feasible band, otherwise snap to the lower boundary 2a or upper boundary 2b.',
        'Reuse the usual blocker certificate unchanged for infeasible families; the clamp law only applies after feasibility has already been certified.',
        'Do not treat the clamped witness index as an exact mean or bundle summary; it is only the feasible L2 witness class.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Direct half-step clamp execution for batch L2 witness choice on feasible bounded positive-service local weakening families',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_mean_half_step_feasible_band_clamp_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law.py',
    }



def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
