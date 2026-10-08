#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    _nearest_integer_argmin_interval,
    build_all_state_codes,
    build_interval_realizer,
    build_rank_to_code,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law import (
    canonicalize_l2_summary_to_reduced_mean,
    select_batch_mean_projection_witness_set_from_reduced_mean,
    summarize_preferred_state_codes_by_canonical_l2_mean,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
    select_constraint_family_intersection,
)


class WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_max_rank() -> int:
    return len(build_all_state_codes()) - 1


def summarize_reduced_mean_by_selector_interval(*, reduced_mean_numerator: int, reduced_mean_denominator: int) -> dict[str, Any]:
    if reduced_mean_denominator <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
            'reduced_mean_denominator must be positive'
        )

    mean_rank = Fraction(reduced_mean_numerator, reduced_mean_denominator)
    max_rank = build_max_rank()
    if mean_rank < 0 or mean_rank > max_rank:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
            'reduced mean rank falls outside the source-rank path'
        )

    selector_lower_rank, selector_upper_rank = _nearest_integer_argmin_interval(mean_rank)
    selector_state_codes = [
        build_rank_to_code()[rank] for rank in range(selector_lower_rank, selector_upper_rank + 1)
    ]
    return {
        'canonical_reduced_mean_summary': [mean_rank.numerator, mean_rank.denominator],
        'reduced_mean_rank': {
            'numerator': mean_rank.numerator,
            'denominator': mean_rank.denominator,
            'decimal': float(mean_rank),
        },
        'unconstrained_selector_interval': {
            'lower_rank': selector_lower_rank,
            'upper_rank': selector_upper_rank,
            'cardinality': selector_upper_rank - selector_lower_rank + 1,
            'state_codes': selector_state_codes,
        },
        'selector_interval_summary': [selector_lower_rank, selector_upper_rank],
        'selector_interval_is_adjacent_tie_pair': selector_lower_rank != selector_upper_rank,
    }


def summarize_l2_statistics_by_selector_interval(*, preferred_count: int, preferred_rank_sum: int) -> dict[str, Any]:
    reduced = canonicalize_l2_summary_to_reduced_mean(
        preferred_count=preferred_count,
        preferred_rank_sum=preferred_rank_sum,
    )
    selector = summarize_reduced_mean_by_selector_interval(
        reduced_mean_numerator=reduced['canonical_reduced_mean_summary'][0],
        reduced_mean_denominator=reduced['canonical_reduced_mean_summary'][1],
    )
    return {
        **reduced,
        **selector,
    }


def summarize_preferred_state_codes_by_l2_selector_interval(preferred_state_codes: list[str]) -> dict[str, Any]:
    reduced = summarize_preferred_state_codes_by_canonical_l2_mean(preferred_state_codes)
    selector = summarize_reduced_mean_by_selector_interval(
        reduced_mean_numerator=reduced['canonical_reduced_mean_summary'][0],
        reduced_mean_denominator=reduced['canonical_reduced_mean_summary'][1],
    )
    return {
        **reduced,
        **selector,
    }


def _project_selector_interval_to_feasible_interval(
    *,
    selector_lower_rank: int,
    selector_upper_rank: int,
    feasible_lower_rank: int,
    feasible_upper_rank: int,
) -> tuple[int, int, str]:
    if selector_lower_rank < 0 or selector_upper_rank > build_max_rank() or selector_lower_rank > selector_upper_rank:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
            'selector interval falls outside the source-rank path'
        )
    if selector_upper_rank - selector_lower_rank > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
            'selector interval must be a singleton or one adjacent tie pair'
        )
    if feasible_lower_rank > feasible_upper_rank:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
            'feasible interval must be nonempty'
        )

    if selector_upper_rank < feasible_lower_rank:
        return feasible_lower_rank, feasible_lower_rank, 'clamp_selector_up_to_lower_boundary'
    if selector_lower_rank > feasible_upper_rank:
        return feasible_upper_rank, feasible_upper_rank, 'clamp_selector_down_to_upper_boundary'
    return (
        max(selector_lower_rank, feasible_lower_rank),
        min(selector_upper_rank, feasible_upper_rank),
        'selector_interval_intersection',
    )


def select_batch_mean_projection_witness_set_from_selector_interval(
    constraints: list[dict[str, Any]],
    *,
    selector_lower_rank: int,
    selector_upper_rank: int,
) -> dict[str, Any]:
    family = select_constraint_family_intersection(constraints)
    result: dict[str, Any] = {
        'family': family,
        'selector_interval_summary': [selector_lower_rank, selector_upper_rank],
    }
    if not family['feasible']:
        result['selection_status'] = 'infeasible'
        result['projected_optimal_state_codes'] = []
        result['projected_optimal_interval'] = None
        result['selection_certificate'] = {'blocker_certificate': family['blocker_certificate']}
        return result

    projected_lower_rank, projected_upper_rank, projection_case = _project_selector_interval_to_feasible_interval(
        selector_lower_rank=selector_lower_rank,
        selector_upper_rank=selector_upper_rank,
        feasible_lower_rank=family['lower_rank_bound'],
        feasible_upper_rank=family['upper_rank_bound'],
    )
    projected_optimal_state_codes = [
        build_rank_to_code()[rank] for rank in range(projected_lower_rank, projected_upper_rank + 1)
    ]
    result['selection_status'] = 'selected'
    result['projected_optimal_interval'] = {
        'lower_rank': projected_lower_rank,
        'upper_rank': projected_upper_rank,
        'cardinality': projected_upper_rank - projected_lower_rank + 1,
        'state_codes': projected_optimal_state_codes,
    }
    result['projected_optimal_state_codes'] = projected_optimal_state_codes
    result['selection_certificate'] = {
        'projection_case': projection_case,
        'selector_interval': {
            'lower_rank': selector_lower_rank,
            'upper_rank': selector_upper_rank,
            'cardinality': selector_upper_rank - selector_lower_rank + 1,
            'state_codes': [
                build_rank_to_code()[rank] for rank in range(selector_lower_rank, selector_upper_rank + 1)
            ],
        },
    }
    return result


@lru_cache(maxsize=1)
def build_batch_mean_selector_interval_examples() -> list[dict[str, Any]]:
    source_relax6 = [{'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}]
    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    interval_1_3_family = [build_interval_realizer(1, 3)]
    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]

    three_fifths = summarize_reduced_mean_by_selector_interval(reduced_mean_numerator=3, reduced_mean_denominator=5)
    one = summarize_reduced_mean_by_selector_interval(reduced_mean_numerator=1, reduced_mean_denominator=1)
    half = summarize_reduced_mean_by_selector_interval(reduced_mean_numerator=1, reduced_mean_denominator=2)

    return [
        {
            'bundle_a': ['S10', 'S10', 'S7'],
            'bundle_a_summary': summarize_preferred_state_codes_by_l2_selector_interval(['S10', 'S10', 'S7']),
            'bundle_b': ['S10', 'S10', 'S10', 'S10', 'S9'],
            'bundle_b_summary': summarize_preferred_state_codes_by_l2_selector_interval(['S10', 'S10', 'S10', 'S10', 'S9']),
            'shared_selector_interval_summary': [0, 0],
            'bundle_a_selection': select_batch_mean_projection_witness_set_from_selector_interval(
                source_relax6,
                selector_lower_rank=0,
                selector_upper_rank=0,
            ),
            'bundle_b_selection': select_batch_mean_projection_witness_set_from_selector_interval(
                source_relax6,
                selector_lower_rank=0,
                selector_upper_rank=0,
            ),
        },
        {
            'selector_from_three_fifths': three_fifths,
            'selector_from_one': one,
            'shared_selector_interval_summary': [1, 1],
            'three_fifths_selection': select_batch_mean_projection_witness_set_from_selector_interval(
                feasible_family,
                selector_lower_rank=1,
                selector_upper_rank=1,
            ),
            'one_selection': select_batch_mean_projection_witness_set_from_selector_interval(
                feasible_family,
                selector_lower_rank=1,
                selector_upper_rank=1,
            ),
        },
        {
            'selector_from_half': half,
            'clipped_tie_selection': select_batch_mean_projection_witness_set_from_selector_interval(
                interval_1_3_family,
                selector_lower_rank=0,
                selector_upper_rank=1,
            ),
        },
        {
            'selector_interval_summary': [11, 11],
            'selection_from_selector_interval': select_batch_mean_projection_witness_set_from_selector_interval(
                infeasible_family,
                selector_lower_rank=11,
                selector_upper_rank=11,
            ),
        },
    ]


@lru_cache(maxsize=1)
def build_batch_mean_selector_interval_validation_summary() -> dict[str, Any]:
    max_rank = build_max_rank()
    realized = build_realized_bounded_window_intervals()
    width_to_multiset_count: dict[int, int] = {}
    width_to_reduced_mean_class_count: dict[int, int] = {}
    width_to_selector_interval_class_count: dict[int, int] = {}
    selector_interval_to_widths: dict[tuple[int, int], set[int]] = defaultdict(set)
    selector_interval_to_mean_count: dict[tuple[int, int], int] = defaultdict(int)
    reduced_mean_classes: set[Fraction] = set()
    selector_interval_classes: set[tuple[int, int]] = set()

    for width in range(1, 6):
        multiset_count = 0
        width_means: set[Fraction] = set()
        width_selector_classes: set[tuple[int, int]] = set()
        for preferred_ranks_tuple in combinations_with_replacement(range(max_rank + 1), width):
            multiset_count += 1
            mean_rank = Fraction(sum(preferred_ranks_tuple), width)
            selector_interval = _nearest_integer_argmin_interval(mean_rank)
            width_means.add(mean_rank)
            width_selector_classes.add(selector_interval)
            selector_interval_to_widths[selector_interval].add(width)
        width_to_multiset_count[width] = multiset_count
        width_to_reduced_mean_class_count[width] = len(width_means)
        width_to_selector_interval_class_count[width] = len(width_selector_classes)
        reduced_mean_classes.update(width_means)
        selector_interval_classes.update(width_selector_classes)

    reduced_mean_to_selector_case_count = 0
    selector_matches_reduced_mean_selection = True
    selector_matches_rational_bruteforce = True
    for mean_rank in sorted(reduced_mean_classes):
        selector_interval = _nearest_integer_argmin_interval(mean_rank)
        selector_interval_to_mean_count[selector_interval] += 1
        selector_summary = summarize_reduced_mean_by_selector_interval(
            reduced_mean_numerator=mean_rank.numerator,
            reduced_mean_denominator=mean_rank.denominator,
        )
        for row in realized:
            reduced_mean_to_selector_case_count += 1
            constraints = [build_interval_realizer(row['lower_rank'], row['upper_rank'])]
            selector_selection = select_batch_mean_projection_witness_set_from_selector_interval(
                constraints,
                selector_lower_rank=selector_summary['selector_interval_summary'][0],
                selector_upper_rank=selector_summary['selector_interval_summary'][1],
            )
            reduced_mean_selection = select_batch_mean_projection_witness_set_from_reduced_mean(
                constraints,
                reduced_mean_numerator=mean_rank.numerator,
                reduced_mean_denominator=mean_rank.denominator,
            )
            if selector_selection['projected_optimal_state_codes'] != reduced_mean_selection['projected_optimal_state_codes']:
                selector_matches_reduced_mean_selection = False
                raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
                    'selector interval selection mismatch against reduced mean selection'
                )

            interval_ranks = list(range(row['lower_rank'], row['upper_rank'] + 1))
            brute_l2_costs = {
                rank: (rank - mean_rank) ** 2 for rank in interval_ranks
            }
            minimum_cost = min(brute_l2_costs.values())
            brute_argmin = [rank for rank, cost in brute_l2_costs.items() if cost == minimum_cost]
            selected_ranks = [
                rank for rank in range(
                    selector_selection['projected_optimal_interval']['lower_rank'],
                    selector_selection['projected_optimal_interval']['upper_rank'] + 1,
                )
            ]
            if selected_ranks != brute_argmin:
                selector_matches_rational_bruteforce = False
                raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
                    'selector interval selection mismatch against rational brute-force argmin'
                )

    singleton_selector_classes = sorted(
        selector_interval for selector_interval in selector_interval_classes if selector_interval[0] == selector_interval[1]
    )
    adjacent_tie_selector_classes = sorted(
        selector_interval for selector_interval in selector_interval_classes if selector_interval[0] != selector_interval[1]
    )
    boundary_singleton_mean_class_count = selector_interval_to_mean_count[(0, 0)] + selector_interval_to_mean_count[(max_rank, max_rank)]
    interior_singleton_mean_class_count = selector_interval_to_mean_count[(1, 1)]

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    infeasible = select_batch_mean_projection_witness_set_from_selector_interval(
        infeasible_family,
        selector_lower_rank=11,
        selector_upper_rank=11,
    )
    if infeasible['selection_status'] != 'infeasible':
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSelectorIntervalLawError(
            'infeasible selector interval selection should stay infeasible'
        )

    return {
        'validated_realized_interval_count': len(realized),
        'validated_preference_bundle_widths': [1, 2, 3, 4, 5],
        'validated_multiset_count': sum(width_to_multiset_count.values()),
        'validated_reduced_mean_class_count': len(reduced_mean_classes),
        'validated_selector_interval_class_count': len(selector_interval_classes),
        'selector_interval_validation_case_count': reduced_mean_to_selector_case_count,
        'bundle_to_selector_interval_reduction_factor': sum(width_to_multiset_count.values()) / len(selector_interval_classes),
        'reduced_mean_to_selector_interval_reduction_factor': len(reduced_mean_classes) / len(selector_interval_classes),
        'width_to_multiset_count': width_to_multiset_count,
        'width_to_reduced_mean_class_count': width_to_reduced_mean_class_count,
        'width_to_selector_interval_class_count': width_to_selector_interval_class_count,
        'singleton_selector_class_count': len(singleton_selector_classes),
        'adjacent_tie_selector_class_count': len(adjacent_tie_selector_classes),
        'every_selector_class_is_cross_width_shared': all(
            len(widths) > 1 for widths in selector_interval_to_widths.values()
        ),
        'singleton_selector_classes_realizable_widths': sorted(selector_interval_to_widths[(1, 1)]),
        'adjacent_tie_selector_classes_realizable_widths': sorted(selector_interval_to_widths[(0, 1)]),
        'boundary_singleton_selector_mean_class_count': boundary_singleton_mean_class_count // 2,
        'interior_singleton_selector_mean_class_count': interior_singleton_mean_class_count,
        'tie_selector_mean_class_count': selector_interval_to_mean_count[(0, 1)],
        'selector_projection_matches_reduced_mean_selection': selector_matches_reduced_mean_selection,
        'selector_projection_matches_rational_bruteforce_l2_argmin': selector_matches_rational_bruteforce,
        'infeasible_selector_interval_selection_stays_blocked': True,
        'example_selector_classes': {
            'boundary_singleton_rank_0': {
                'selector_interval_summary': [0, 0],
                'realizable_widths': sorted(selector_interval_to_widths[(0, 0)]),
                'collapsed_reduced_mean_class_count': selector_interval_to_mean_count[(0, 0)],
            },
            'interior_singleton_rank_1': {
                'selector_interval_summary': [1, 1],
                'realizable_widths': sorted(selector_interval_to_widths[(1, 1)]),
                'collapsed_reduced_mean_class_count': selector_interval_to_mean_count[(1, 1)],
            },
            'adjacent_tie_rank_0_1': {
                'selector_interval_summary': [0, 1],
                'realizable_widths': sorted(selector_interval_to_widths[(0, 1)]),
                'collapsed_reduced_mean_class_count': selector_interval_to_mean_count[(0, 1)],
            },
        },
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_mean_selector_interval_validation_summary()
    return {
        'l2_selection_depends_only_on_the_unconstrained_nearest_integer_selector_interval': True,
        'reduced_mean_l2_summaries_collapse_further_to_33_selector_interval_classes': validation[
            'validated_selector_interval_class_count'
        ],
        'every_selector_class_is_cross_width_shared_on_the_audited_catalog': validation[
            'every_selector_class_is_cross_width_shared'
        ],
        'selector_classes_split_into_17_singletons_and_16_adjacent_tie_pairs': [
            validation['singleton_selector_class_count'],
            validation['adjacent_tie_selector_class_count'],
        ],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'If only path-L2 witness choice matters, reduce any canonical mean summary further to its unconstrained nearest-integer selector interval [selector_lower_rank, selector_upper_rank].',
        'That selector interval is always either a singleton [k, k] or one adjacent tie pair [k, k+1] on the source-rank path.',
        'To recover the feasible L2 witness set for any feasible family, project the selector interval onto the feasible overlap interval.',
        'Cache path-L2 witness requests by selector interval rather than by exact reduced mean whenever later reconstruction of the original mean rank is unnecessary.',
        'Interpret selector intervals as witness-selection semantics only: they do not preserve bundle width, exact mean magnitude, or any non-L2 downstream quantity.',
        'If the family is infeasible, carry forward the same blocker certificate from the feasibility-intersection law rather than attempting witness selection.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot_20260308.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_mean_selector_interval_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Selector-interval summaries for batch L2 witness choice on feasible bounded positive-service local weakening families',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_mean_selector_interval_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_mean_selector_interval_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
