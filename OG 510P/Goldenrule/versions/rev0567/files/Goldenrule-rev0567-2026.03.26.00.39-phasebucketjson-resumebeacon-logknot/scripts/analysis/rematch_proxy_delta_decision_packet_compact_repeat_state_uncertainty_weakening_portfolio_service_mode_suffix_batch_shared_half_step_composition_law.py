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
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law import (
    build_monotone_fingerprint_word_catalog,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    build_interval_realizer,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law import (
    select_batch_shared_half_step_witness_set,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_half_step_fingerprint_lookup() -> dict[int, str]:
    return {
        row['half_step_selector_index']: row['fingerprint_word']
        for row in build_monotone_fingerprint_word_catalog()
    }



def _normalize_interval(interval: list[int] | tuple[int, int]) -> tuple[int, int]:
    if len(interval) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
            'interval must contain exactly two ranks'
        )
    lower_rank = int(interval[0])
    upper_rank = int(interval[1])
    if lower_rank < 0 or upper_rank < lower_rank:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
            'interval must be a nonempty rank interval'
        )
    return lower_rank, upper_rank



def intersect_rank_intervals(
    first_interval: list[int] | tuple[int, int],
    second_interval: list[int] | tuple[int, int],
) -> dict[str, Any]:
    first_lower_rank, first_upper_rank = _normalize_interval(first_interval)
    second_lower_rank, second_upper_rank = _normalize_interval(second_interval)
    overlap_lower_rank = max(first_lower_rank, second_lower_rank)
    overlap_upper_rank = min(first_upper_rank, second_upper_rank)
    if overlap_lower_rank <= overlap_upper_rank:
        return {
            'overlap_exists': True,
            'intersection_interval': [overlap_lower_rank, overlap_upper_rank],
        }
    return {
        'overlap_exists': False,
        'intersection_interval': None,
        'gap_certificate': {
            'first_interval': [first_lower_rank, first_upper_rank],
            'second_interval': [second_lower_rank, second_upper_rank],
            'gap_lower_rank': overlap_upper_rank + 1,
            'gap_upper_rank': overlap_lower_rank - 1,
        },
    }



def apply_shared_half_step_interval_kernel(
    interval: list[int] | tuple[int, int],
    *,
    half_step_selector_index: int,
) -> dict[str, Any]:
    lower_rank, upper_rank = _normalize_interval(interval)
    clamped = clamp_half_step_selector_index_to_doubled_feasible_band(
        half_step_selector_index=half_step_selector_index,
        feasible_lower_rank=lower_rank,
        feasible_upper_rank=upper_rank,
    )
    fingerprint_lookup = build_half_step_fingerprint_lookup()
    projected_half_step_witness_index = clamped['projected_half_step_witness_index']
    return {
        'interval': [lower_rank, upper_rank],
        'input_half_step_selector_index': half_step_selector_index,
        'input_fingerprint_word': fingerprint_lookup[half_step_selector_index],
        'projected_half_step_witness_index': projected_half_step_witness_index,
        'projected_fingerprint_word': fingerprint_lookup[projected_half_step_witness_index],
        'projected_optimal_interval': clamped['projected_optimal_interval'],
        'projected_optimal_state_codes': clamped['projected_optimal_state_codes'],
        'clamp_case': clamped['clamp_case'],
        'doubled_feasible_band': clamped['doubled_feasible_band'],
    }



def compose_shared_half_step_interval_kernels(
    first_interval: list[int] | tuple[int, int],
    second_interval: list[int] | tuple[int, int],
    *,
    half_step_selector_index: int,
) -> dict[str, Any]:
    first_pass = apply_shared_half_step_interval_kernel(
        first_interval,
        half_step_selector_index=half_step_selector_index,
    )
    second_pass = apply_shared_half_step_interval_kernel(
        second_interval,
        half_step_selector_index=first_pass['projected_half_step_witness_index'],
    )
    overlap = intersect_rank_intervals(first_interval, second_interval)
    result: dict[str, Any] = {
        'input_half_step_selector_index': half_step_selector_index,
        'first_interval': list(_normalize_interval(first_interval)),
        'second_interval': list(_normalize_interval(second_interval)),
        'first_pass': first_pass,
        'second_pass': second_pass,
        'overlap': overlap,
    }
    if overlap['overlap_exists']:
        direct = apply_shared_half_step_interval_kernel(
            overlap['intersection_interval'],
            half_step_selector_index=half_step_selector_index,
        )
        result['composition_status'] = 'feasible_overlap'
        result['direct_intersection_kernel'] = direct
        result['composition_matches_direct_intersection_kernel'] = (
            second_pass['projected_half_step_witness_index'] == direct['projected_half_step_witness_index']
        )
    else:
        result['composition_status'] = 'disjoint_order_sensitive'
        result['direct_intersection_kernel'] = None
        result['composition_matches_direct_intersection_kernel'] = None
    return result


@lru_cache(maxsize=1)
def build_batch_shared_half_step_composition_examples() -> list[dict[str, Any]]:
    overlap_forward = compose_shared_half_step_interval_kernels(
        [0, 5],
        [3, 8],
        half_step_selector_index=3,
    )
    overlap_reverse = compose_shared_half_step_interval_kernels(
        [3, 8],
        [0, 5],
        half_step_selector_index=3,
    )
    idempotent_once = apply_shared_half_step_interval_kernel([4, 9], half_step_selector_index=2)
    idempotent_twice = apply_shared_half_step_interval_kernel(
        [4, 9],
        half_step_selector_index=idempotent_once['projected_half_step_witness_index'],
    )
    disjoint_forward = compose_shared_half_step_interval_kernels(
        [0, 2],
        [5, 7],
        half_step_selector_index=17,
    )
    disjoint_reverse = compose_shared_half_step_interval_kernels(
        [5, 7],
        [0, 2],
        half_step_selector_index=17,
    )
    intersection_constraints = [build_interval_realizer(3, 5)]
    return [
        {
            'overlap_composition_is_order_independent': {
                'forward': overlap_forward,
                'reverse': overlap_reverse,
                'shared_executor_on_intersection': select_batch_shared_half_step_witness_set(
                    intersection_constraints,
                    half_step_selector_index=3,
                ),
            }
        },
        {
            'single_interval_idempotence': {
                'first_application': idempotent_once,
                'second_application': idempotent_twice,
            }
        },
        {
            'disjoint_intervals_are_totally_order_sensitive': {
                'forward': disjoint_forward,
                'reverse': disjoint_reverse,
            }
        },
    ]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_composition_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    intervals = [(row['lower_rank'], row['upper_rank']) for row in realized]
    fingerprint_lookup = build_half_step_fingerprint_lookup()

    feasible_overlap_ordered_pair_count = 0
    feasible_overlap_composition_case_count = 0
    disjoint_ordered_pair_count = 0
    disjoint_order_sensitive_case_count = 0
    idempotence_validation_case_count = 0
    equivalence_check_count = 0
    distinct_intersection_intervals: set[tuple[int, int]] = set()
    distinct_transition_pairs: set[tuple[int, int]] = set()
    distinct_transition_pairs_preserve: set[tuple[int, int]] = set()
    distinct_transition_pairs_lower_boundary: set[tuple[int, int]] = set()
    distinct_transition_pairs_upper_boundary: set[tuple[int, int]] = set()

    for interval in intervals:
        for half_step_selector_index in range(33):
            idempotence_validation_case_count += 1
            once = apply_shared_half_step_interval_kernel(interval, half_step_selector_index=half_step_selector_index)
            twice = apply_shared_half_step_interval_kernel(
                interval,
                half_step_selector_index=once['projected_half_step_witness_index'],
            )
            if once['projected_half_step_witness_index'] != twice['projected_half_step_witness_index']:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
                    'single-interval kernel should be idempotent'
                )
            if once['projected_fingerprint_word'] != twice['projected_fingerprint_word']:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
                    'single-interval idempotence should preserve the projected fingerprint word'
                )

    for first_interval in intervals:
        for second_interval in intervals:
            overlap = intersect_rank_intervals(first_interval, second_interval)
            if overlap['overlap_exists']:
                feasible_overlap_ordered_pair_count += 1
                distinct_intersection_intervals.add(tuple(overlap['intersection_interval']))
            else:
                disjoint_ordered_pair_count += 1

            for half_step_selector_index in range(33):
                forward = compose_shared_half_step_interval_kernels(
                    first_interval,
                    second_interval,
                    half_step_selector_index=half_step_selector_index,
                )
                reverse = compose_shared_half_step_interval_kernels(
                    second_interval,
                    first_interval,
                    half_step_selector_index=half_step_selector_index,
                )
                forward_output = forward['second_pass']['projected_half_step_witness_index']
                reverse_output = reverse['second_pass']['projected_half_step_witness_index']
                distinct_transition_pairs.add((half_step_selector_index, forward_output))
                if forward_output == half_step_selector_index:
                    distinct_transition_pairs_preserve.add((half_step_selector_index, forward_output))
                elif forward_output > half_step_selector_index:
                    distinct_transition_pairs_lower_boundary.add((half_step_selector_index, forward_output))
                else:
                    distinct_transition_pairs_upper_boundary.add((half_step_selector_index, forward_output))

                if overlap['overlap_exists']:
                    feasible_overlap_composition_case_count += 1
                    direct = forward['direct_intersection_kernel']
                    equivalence_check_count += 2
                    if forward_output != direct['projected_half_step_witness_index']:
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
                            'forward composition should equal the direct intersection kernel on feasible overlaps'
                        )
                    if reverse_output != direct['projected_half_step_witness_index']:
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
                            'reverse composition should equal the direct intersection kernel on feasible overlaps'
                        )
                    if forward_output != reverse_output:
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
                            'feasible-overlap compositions should commute'
                        )
                    if fingerprint_lookup[forward_output] != direct['projected_fingerprint_word']:
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
                            'direct intersection kernel should preserve the shared fingerprint codec'
                        )
                else:
                    if forward_output == reverse_output:
                        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
                            'disjoint interval compositions should stay order-sensitive on every half-step class'
                        )
                    disjoint_order_sensitive_case_count += 1

    if len(distinct_intersection_intervals) != len(intervals):
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepCompositionLawError(
            'all realized intervals should reappear as pairwise intersections of realized intervals'
        )

    return {
        'validated_realized_interval_count': len(intervals),
        'validated_half_step_selector_index_class_count': 33,
        'half_step_selector_index_range': [0, 32],
        'idempotence_validation_case_count': idempotence_validation_case_count,
        'feasible_overlap_ordered_interval_pair_count': feasible_overlap_ordered_pair_count,
        'feasible_overlap_composition_case_count': feasible_overlap_composition_case_count,
        'feasible_overlap_composition_equivalence_check_count': equivalence_check_count,
        'disjoint_ordered_interval_pair_count': disjoint_ordered_pair_count,
        'disjoint_order_sensitive_case_count': disjoint_order_sensitive_case_count,
        'distinct_pairwise_intersection_interval_count': len(distinct_intersection_intervals),
        'distinct_input_to_output_transition_pair_count': len(distinct_transition_pairs),
        'distinct_transition_pair_breakdown': {
            'preserve_within_band': len(distinct_transition_pairs_preserve),
            'clamp_up_to_lower_boundary': len(distinct_transition_pairs_lower_boundary),
            'clamp_down_to_upper_boundary': len(distinct_transition_pairs_upper_boundary),
        },
        'feasible_overlap_compositions_equal_direct_intersection_kernel': True,
        'feasible_overlap_compositions_commute': True,
        'single_interval_kernels_are_idempotent': True,
        'disjoint_interval_compositions_are_totally_order_sensitive': True,
        'pairwise_intersections_regenerate_the_full_realized_interval_catalog': True,
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_composition_snapshot() -> dict[str, Any]:
    validation = build_batch_shared_half_step_composition_validation_summary()
    examples = build_batch_shared_half_step_composition_examples()
    return {
        'focus': 'batch shared half-step kernel composition over realized feasible intervals',
        'headline_findings': {
            'once_batch_requests_are_normalized_to_half_step_selector_index_feasible_interval_kernels_compose_by_interval_intersection': True,
            'feasible_overlap_compositions_commute': validation['feasible_overlap_compositions_commute'],
            'single_interval_kernels_are_idempotent': validation['single_interval_kernels_are_idempotent'],
            'disjoint_interval_compositions_are_totally_order_sensitive': validation['disjoint_interval_compositions_are_totally_order_sensitive'],
            'feasible_overlap_ordered_interval_pair_count': validation['feasible_overlap_ordered_interval_pair_count'],
            'feasible_overlap_composition_case_count': validation['feasible_overlap_composition_case_count'],
            'disjoint_order_sensitive_case_count': validation['disjoint_order_sensitive_case_count'],
            'distinct_input_to_output_transition_pair_count': validation['distinct_input_to_output_transition_pair_count'],
            'distinct_transition_pair_breakdown': validation['distinct_transition_pair_breakdown'],
        },
        'decision_rules': [
            'Model each feasible interval family as one shared half-step kernel K_[a,b](h) = clamp(h, 2a, 2b).',
            'If two interval families overlap, compose them in any order and replace the pair by the direct intersection kernel K_[max(a,c), min(b,d)].',
            'Reapplying the same feasible interval kernel changes nothing after the first pass because K_[a,b] is idempotent.',
            'Do not reuse this order-independence shortcut once intervals are disjoint; disjoint kernel composition is order-sensitive on every half-step class and should instead be treated as infeasibility evidence.',
        ],
        'composition_examples': examples,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law_snapshot_20260309.md',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law_snapshot_20260309.md',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_composition_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
