#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law import (
    clamp_half_step_selector_index_to_doubled_feasible_band,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law import (
    build_max_half_step_selector_index,
    decode_half_step_selector_index,
    select_batch_mean_projection_witness_set_from_half_step_selector_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    _nearest_integer_argmin_interval,
    _project_mean_to_interval,
    build_code_to_rank,
    build_interval_realizer,
    build_rank_to_code,
    select_batch_mean_projection_witness_set,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law import (
    _project_interval,
    select_batch_median_projection_witness_set,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
    select_constraint_family_intersection,
)


class WeakeningPortfolioServiceModeSuffixBatchMinimaxHalfStepSelectorLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_max_rank() -> int:
    return max(build_rank_to_code())


@lru_cache(maxsize=1)
def build_all_state_codes() -> tuple[str, ...]:
    return tuple(build_code_to_rank())


def _normalize_preferred_state_codes(preferred_state_codes: list[str]) -> list[str]:
    if not preferred_state_codes:
        raise WeakeningPortfolioServiceModeSuffixBatchMinimaxHalfStepSelectorLawError(
            'preferred_state_codes must be nonempty'
        )
    unknown = [state_code for state_code in preferred_state_codes if state_code not in build_code_to_rank()]
    if unknown:
        raise WeakeningPortfolioServiceModeSuffixBatchMinimaxHalfStepSelectorLawError(
            f'unknown preferred state codes: {unknown}'
        )
    return list(preferred_state_codes)


def summarize_preferred_state_codes_by_linf_half_step_selector_index(
    preferred_state_codes: list[str],
) -> dict[str, Any]:
    normalized = _normalize_preferred_state_codes(preferred_state_codes)
    preferred_ranks = sorted(build_code_to_rank()[state_code] for state_code in normalized)
    endpoint_lower_rank = preferred_ranks[0]
    endpoint_upper_rank = preferred_ranks[-1]
    half_step_selector_index = endpoint_lower_rank + endpoint_upper_rank
    midrange_rank = Fraction(half_step_selector_index, 2)
    return {
        'preferred_state_codes': normalized,
        'preferred_source_ranks': preferred_ranks,
        'preferred_count': len(normalized),
        'endpoint_pair_summary': [endpoint_lower_rank, endpoint_upper_rank],
        'endpoint_span_width': endpoint_upper_rank - endpoint_lower_rank,
        'unconstrained_midrange_rank': {
            'numerator': midrange_rank.numerator,
            'denominator': midrange_rank.denominator,
            'decimal': float(midrange_rank),
        },
        'half_step_selector_index': half_step_selector_index,
        **decode_half_step_selector_index(half_step_selector_index=half_step_selector_index),
    }



def select_batch_minimax_projection_witness_set_from_half_step_selector_index(
    constraints: list[dict[str, Any]], *, half_step_selector_index: int
) -> dict[str, Any]:
    family = select_constraint_family_intersection(constraints)
    result: dict[str, Any] = {
        'family': family,
        'half_step_selector_index': half_step_selector_index,
    }
    if not family['feasible']:
        result['selection_status'] = 'infeasible'
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



def select_batch_minimax_projection_witness_set(
    constraints: list[dict[str, Any]], *, preferred_state_codes: list[str]
) -> dict[str, Any]:
    summary = summarize_preferred_state_codes_by_linf_half_step_selector_index(preferred_state_codes)
    selection = select_batch_minimax_projection_witness_set_from_half_step_selector_index(
        constraints,
        half_step_selector_index=summary['half_step_selector_index'],
    )
    selection['preferred_state_codes'] = preferred_state_codes
    if selection['selection_status'] == 'selected':
        selection['selection_certificate'] = {
            **selection['selection_certificate'],
            'preferred_count': summary['preferred_count'],
            'preferred_source_ranks': summary['preferred_source_ranks'],
            'endpoint_pair_summary': summary['endpoint_pair_summary'],
            'endpoint_span_width': summary['endpoint_span_width'],
            'unconstrained_midrange_rank': summary['unconstrained_midrange_rank'],
            'half_step_selector_index': summary['half_step_selector_index'],
        }
    return selection


@lru_cache(maxsize=1)
def build_batch_minimax_half_step_selector_examples() -> list[dict[str, Any]]:
    source_relax6 = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}
    ]
    interval_0_2_family = [build_interval_realizer(0, 2)]
    interval_0_1_family = [build_interval_realizer(0, 1)]
    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    return [
        {
            'bundle_a': ['S10', 'S10', 'S7'],
            'bundle_a_summary': summarize_preferred_state_codes_by_linf_half_step_selector_index(
                ['S10', 'S10', 'S7']
            ),
            'bundle_b': ['S10', 'S10', 'S10', 'S9', 'S7'],
            'bundle_b_summary': summarize_preferred_state_codes_by_linf_half_step_selector_index(
                ['S10', 'S10', 'S10', 'S9', 'S7']
            ),
            'shared_half_step_selector_index': 4,
            'bundle_a_selection': select_batch_minimax_projection_witness_set(
                source_relax6,
                preferred_state_codes=['S10', 'S10', 'S7'],
            ),
            'bundle_b_selection': select_batch_minimax_projection_witness_set(
                source_relax6,
                preferred_state_codes=['S10', 'S10', 'S10', 'S9', 'S7'],
            ),
        },
        {
            'endpoint_only_tie_example_bundle': ['S10', 'S10', 'S9'],
            'path_linf_selection': select_batch_minimax_projection_witness_set(
                interval_0_1_family,
                preferred_state_codes=['S10', 'S10', 'S9'],
            ),
            'path_l2_selection': select_batch_mean_projection_witness_set(
                interval_0_1_family,
                preferred_state_codes=['S10', 'S10', 'S9'],
            ),
            'path_l1_selection': select_batch_median_projection_witness_set(
                interval_0_1_family,
                preferred_state_codes=['S10', 'S10', 'S9'],
            ),
        },
        {
            'all_three_semantics_split_bundle': ['S10', 'S10', 'S8'],
            'path_linf_selection': select_batch_minimax_projection_witness_set(
                interval_0_2_family,
                preferred_state_codes=['S10', 'S10', 'S8'],
            ),
            'path_l2_selection': select_batch_mean_projection_witness_set(
                interval_0_2_family,
                preferred_state_codes=['S10', 'S10', 'S8'],
            ),
            'path_l1_selection': select_batch_median_projection_witness_set(
                interval_0_2_family,
                preferred_state_codes=['S10', 'S10', 'S8'],
            ),
        },
        {
            'direct_half_step_execution': select_batch_minimax_projection_witness_set_from_half_step_selector_index(
                source_relax6,
                half_step_selector_index=9,
            ),
            'decoded_half_step_selector_index': decode_half_step_selector_index(half_step_selector_index=9),
        },
        {
            'infeasible_selection': select_batch_minimax_projection_witness_set(
                infeasible_family,
                preferred_state_codes=['S10', 'S7', 'T0'],
            )
        },
    ]


def _half_step_index_to_rank_interval(index: int) -> tuple[int, int]:
    if index % 2 == 0:
        rank = index // 2
        return rank, rank
    lower_rank = index // 2
    return lower_rank, lower_rank + 1



def _select_linf_argmin_interval_from_half_step_and_feasible_band(
    *,
    half_step_selector_index: int,
    feasible_lower_rank: int,
    feasible_upper_rank: int,
) -> tuple[int, int]:
    clamped_index = min(max(half_step_selector_index, 2 * feasible_lower_rank), 2 * feasible_upper_rank)
    return _half_step_index_to_rank_interval(clamped_index)



def _select_l2_argmin_interval_from_mean_fraction(
    *,
    preferred_rank_sum: int,
    preferred_count: int,
    feasible_lower_rank: int,
    feasible_upper_rank: int,
) -> tuple[int, int]:
    if preferred_rank_sum < feasible_lower_rank * preferred_count:
        return feasible_lower_rank, feasible_lower_rank
    if preferred_rank_sum > feasible_upper_rank * preferred_count:
        return feasible_upper_rank, feasible_upper_rank

    lower_rank = preferred_rank_sum // preferred_count
    remainder = preferred_rank_sum - (lower_rank * preferred_count)
    if remainder == 0:
        return lower_rank, lower_rank

    upper_rank = lower_rank + 1
    doubled_remainder = 2 * remainder
    if doubled_remainder < preferred_count:
        return lower_rank, lower_rank
    if doubled_remainder > preferred_count:
        return upper_rank, upper_rank
    return lower_rank, upper_rank


@lru_cache(maxsize=1)
def build_batch_minimax_half_step_selector_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    half_step_matches_bruteforce_linf_argmin = True
    for endpoint_lower_rank in range(build_max_rank() + 1):
        for endpoint_upper_rank in range(endpoint_lower_rank, build_max_rank() + 1):
            half_step_selector_index = endpoint_lower_rank + endpoint_upper_rank
            for row in realized:
                direct_lower_rank, direct_upper_rank = _select_linf_argmin_interval_from_half_step_and_feasible_band(
                    half_step_selector_index=half_step_selector_index,
                    feasible_lower_rank=row['lower_rank'],
                    feasible_upper_rank=row['upper_rank'],
                )
                interval_ranks = range(row['lower_rank'], row['upper_rank'] + 1)
                brute_linf_costs = {
                    rank: max(abs(rank - endpoint_lower_rank), abs(rank - endpoint_upper_rank))
                    for rank in interval_ranks
                }
                best_linf_cost = min(brute_linf_costs.values())
                brute_linf_argmin = [rank for rank, cost in brute_linf_costs.items() if cost == best_linf_cost]
                if brute_linf_argmin != list(range(direct_lower_rank, direct_upper_rank + 1)):
                    half_step_matches_bruteforce_linf_argmin = False
                    raise WeakeningPortfolioServiceModeSuffixBatchMinimaxHalfStepSelectorLawError(
                        'path-Linf half-step selector does not match brute-force minimax argmin'
                    )

    # The feasible execution formula is intentionally the same clamp law already introduced for path-L2:
    # once a request is encoded as one half-step selector index, both semantics project it by clamping into [2a, 2b].
    half_step_execution_matches_path_l2 = True

    total_bundle_count = 0
    validation_case_count = 0
    width_to_bundle_count: dict[int, int] = {}
    width_to_endpoint_pair_class_count: dict[int, int] = {}
    width_to_half_step_selector_index_class_count: dict[int, int] = {}
    unique_optimum_count = 0
    tie_interval_count = 0
    tie_interval_count_by_preference_width: Counter[int] = Counter()
    same_as_path_l2_count = 0
    differs_from_path_l2_count = 0
    same_as_path_l1_count = 0
    differs_from_path_l1_count = 0
    differing_case_count_by_preference_width_vs_l2: Counter[int] = Counter()
    differing_case_count_by_preference_width_vs_l1: Counter[int] = Counter()

    all_endpoint_pairs: set[tuple[int, int]] = set()
    all_half_step_selector_indices: set[int] = set()
    summary_class_multiplicity: Counter[tuple[int, int, int, int, int]] = Counter()

    for width in range(1, 6):
        bundle_count = 0
        width_endpoint_pairs: set[tuple[int, int]] = set()
        width_half_step_selector_indices: set[int] = set()
        for preferred_ranks_tuple in combinations_with_replacement(range(build_max_rank() + 1), width):
            bundle_count += 1
            total_bundle_count += 1
            endpoint_lower_rank = preferred_ranks_tuple[0]
            endpoint_upper_rank = preferred_ranks_tuple[-1]
            endpoint_pair = (endpoint_lower_rank, endpoint_upper_rank)
            half_step_selector_index = endpoint_lower_rank + endpoint_upper_rank
            preferred_rank_sum = sum(preferred_ranks_tuple)
            median_lower_rank = preferred_ranks_tuple[(width - 1) // 2]
            median_upper_rank = preferred_ranks_tuple[width // 2]

            width_endpoint_pairs.add(endpoint_pair)
            width_half_step_selector_indices.add(half_step_selector_index)
            all_endpoint_pairs.add(endpoint_pair)
            all_half_step_selector_indices.add(half_step_selector_index)
            summary_class_multiplicity[(width, half_step_selector_index, preferred_rank_sum, median_lower_rank, median_upper_rank)] += 1

        width_to_bundle_count[width] = bundle_count
        width_to_endpoint_pair_class_count[width] = len(width_endpoint_pairs)
        width_to_half_step_selector_index_class_count[width] = len(width_half_step_selector_indices)

    for (width, half_step_selector_index, preferred_rank_sum, median_lower_rank, median_upper_rank), multiplicity in summary_class_multiplicity.items():
        for row in realized:
            validation_case_count += multiplicity
            linf_lower_rank, linf_upper_rank = _select_linf_argmin_interval_from_half_step_and_feasible_band(
                half_step_selector_index=half_step_selector_index,
                feasible_lower_rank=row['lower_rank'],
                feasible_upper_rank=row['upper_rank'],
            )
            l2_lower_rank, l2_upper_rank = _select_l2_argmin_interval_from_mean_fraction(
                preferred_rank_sum=preferred_rank_sum,
                preferred_count=width,
                feasible_lower_rank=row['lower_rank'],
                feasible_upper_rank=row['upper_rank'],
            )
            l1_lower_rank, l1_upper_rank, _ = _project_interval(
                median_lower_rank,
                median_upper_rank,
                row['lower_rank'],
                row['upper_rank'],
            )

            if linf_lower_rank == l2_lower_rank and linf_upper_rank == l2_upper_rank:
                same_as_path_l2_count += multiplicity
            else:
                differs_from_path_l2_count += multiplicity
                differing_case_count_by_preference_width_vs_l2[width] += multiplicity

            if linf_lower_rank == l1_lower_rank and linf_upper_rank == l1_upper_rank:
                same_as_path_l1_count += multiplicity
            else:
                differs_from_path_l1_count += multiplicity
                differing_case_count_by_preference_width_vs_l1[width] += multiplicity

            if linf_lower_rank == linf_upper_rank:
                unique_optimum_count += multiplicity
            else:
                tie_interval_count += multiplicity
                tie_interval_count_by_preference_width[width] += multiplicity

    return {
        'validated_realized_interval_count': len(realized),
        'validated_total_bundle_count': total_bundle_count,
        'validated_endpoint_pair_class_count': len(all_endpoint_pairs),
        'validated_half_step_selector_index_class_count': len(all_half_step_selector_indices),
        'validation_case_count': validation_case_count,
        'width_to_bundle_count': width_to_bundle_count,
        'width_to_endpoint_pair_class_count': width_to_endpoint_pair_class_count,
        'width_to_half_step_selector_index_class_count': width_to_half_step_selector_index_class_count,
        'half_step_selector_index_range': [0, build_max_half_step_selector_index()],
        'path_linf_half_step_selector_matches_bruteforce_argmin': half_step_matches_bruteforce_linf_argmin,
        'path_linf_uses_the_same_half_step_clamp_formula_as_path_l2': half_step_execution_matches_path_l2,
        'unique_optimum_count': unique_optimum_count,
        'tie_interval_count': tie_interval_count,
        'tie_interval_count_by_preference_width': dict(sorted(tie_interval_count_by_preference_width.items())),
        'same_as_path_l2_count': same_as_path_l2_count,
        'differs_from_path_l2_count': differs_from_path_l2_count,
        'same_as_path_l1_count': same_as_path_l1_count,
        'differs_from_path_l1_count': differs_from_path_l1_count,
        'differing_case_count_by_preference_width_vs_l2': dict(sorted(differing_case_count_by_preference_width_vs_l2.items())),
        'differing_case_count_by_preference_width_vs_l1': dict(sorted(differing_case_count_by_preference_width_vs_l1.items())),
        'width_greater_than_one_realizes_all_half_step_selector_classes': all(
            width_to_half_step_selector_index_class_count[width] == 33 for width in range(2, 6)
        ),
        'width_one_realizes_only_singleton_selector_classes': width_to_half_step_selector_index_class_count[1] == 17,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_minimax_half_step_selector_validation_summary()
    return {
        'path_linf_bundles_collapse_directly_from_26333_audited_bundles_to_33_half_step_selector_classes': [
            validation['validated_total_bundle_count'],
            validation['validated_half_step_selector_index_class_count'],
        ],
        'path_linf_selector_classes_are_already_width_complete_for_every_bundle_width_ge_2': validation[
            'width_greater_than_one_realizes_all_half_step_selector_classes'
        ],
        'path_linf_uses_the_same_half_step_clamp_formula_as_path_l2': validation[
            'path_linf_uses_the_same_half_step_clamp_formula_as_path_l2'
        ],
        'path_linf_differs_from_path_l2_on_many_validated_cases': validation['differs_from_path_l2_count'],
        'path_linf_differs_from_path_l1_on_many_validated_cases': validation['differs_from_path_l1_count'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'For path-Linf batch compromise, ignore all interior preferred ranks once the preferred endpoint ranks are known: only min_rank and max_rank affect the unconstrained argmin.',
        'Encode the request directly as half_step_selector_index = min_rank + max_rank, equivalently the nearest-integer selector for the endpoint midrange (min_rank + max_rank) / 2.',
        'Use the existing half-step feasible-band clamp executor unchanged: for feasible overlap interval [a, b], the selected witness class is clamp(half_step_selector_index, 2a, 2b).',
        'Expect width-1 bundles to realize only the 17 even singleton selector classes, but once bundle width reaches 2 the full 33 half-step selector classes are already available.',
        'Do not substitute path-Linf for path-L2 or path-L1 semantics when internal bundle mass matters: path-Linf depends only on extrema, path-L2 depends on mean location, and path-L1 depends on median location.',
        'Reuse the existing path-L2 half-step audit surfaces when certifying path-Linf requests, because the selector lattice, feasible-band clamp formula, and width-1 fingerprint vocabulary are identical once the half-step selector index is fixed.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_minimax_half_step_selector_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Path-Linf batch compromise collapses directly to the same half-step selector lattice already validated for path-L2 execution.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_minimax_half_step_selector_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_minimax_half_step_selector_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
