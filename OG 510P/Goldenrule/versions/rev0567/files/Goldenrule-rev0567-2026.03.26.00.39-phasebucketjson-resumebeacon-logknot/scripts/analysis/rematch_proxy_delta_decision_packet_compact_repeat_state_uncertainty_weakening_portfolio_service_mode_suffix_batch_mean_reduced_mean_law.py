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
    _project_mean_to_interval,
    build_all_state_codes,
    build_interval_realizer,
    build_rank_to_code,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law import (
    select_batch_mean_projection_witness_set_from_statistics,
    summarize_preferred_state_codes_for_l2,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
    select_constraint_family_intersection,
)


class WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_max_rank() -> int:
    return len(build_all_state_codes()) - 1


def canonicalize_l2_summary_to_reduced_mean(*, preferred_count: int, preferred_rank_sum: int) -> dict[str, Any]:
    if preferred_count <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError('preferred_count must be positive')
    max_rank = build_max_rank()
    if preferred_rank_sum < 0 or preferred_rank_sum > max_rank * preferred_count:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError(
            'preferred_rank_sum falls outside the achievable range for the source-rank path'
        )

    mean_rank = Fraction(preferred_rank_sum, preferred_count)
    return {
        'preferred_count': preferred_count,
        'preferred_rank_sum': preferred_rank_sum,
        'unreduced_pair_summary': [preferred_count, preferred_rank_sum],
        'canonical_reduced_mean_summary': [mean_rank.numerator, mean_rank.denominator],
        'reduced_mean_rank': {
            'numerator': mean_rank.numerator,
            'denominator': mean_rank.denominator,
            'decimal': float(mean_rank),
        },
    }


def summarize_preferred_state_codes_by_canonical_l2_mean(preferred_state_codes: list[str]) -> dict[str, Any]:
    summary = summarize_preferred_state_codes_for_l2(preferred_state_codes)
    reduced = canonicalize_l2_summary_to_reduced_mean(
        preferred_count=summary['preferred_count'],
        preferred_rank_sum=summary['preferred_rank_sum'],
    )
    return {
        **summary,
        **reduced,
    }


def select_batch_mean_projection_witness_set_from_reduced_mean(
    constraints: list[dict[str, Any]],
    *,
    reduced_mean_numerator: int,
    reduced_mean_denominator: int,
) -> dict[str, Any]:
    if reduced_mean_denominator <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError(
            'reduced_mean_denominator must be positive'
        )

    mean_rank = Fraction(reduced_mean_numerator, reduced_mean_denominator)
    max_rank = build_max_rank()
    if mean_rank < 0 or mean_rank > max_rank:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError(
            'reduced mean rank falls outside the source-rank path'
        )

    family = select_constraint_family_intersection(constraints)
    result: dict[str, Any] = {
        'family': family,
        'canonical_reduced_mean_summary': [mean_rank.numerator, mean_rank.denominator],
    }
    if not family['feasible']:
        result['selection_status'] = 'infeasible'
        result['projected_optimal_state_codes'] = []
        result['projected_optimal_interval'] = None
        result['selection_certificate'] = {'blocker_certificate': family['blocker_certificate']}
        return result

    projected_mean_rank, projection_case = _project_mean_to_interval(
        mean_rank,
        family['lower_rank_bound'],
        family['upper_rank_bound'],
    )
    projected_lower_rank, projected_upper_rank = _nearest_integer_argmin_interval(projected_mean_rank)
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
        'reduced_mean_rank': {
            'numerator': mean_rank.numerator,
            'denominator': mean_rank.denominator,
            'decimal': float(mean_rank),
        },
        'projected_mean_rank': {
            'numerator': projected_mean_rank.numerator,
            'denominator': projected_mean_rank.denominator,
            'decimal': float(projected_mean_rank),
        },
        'half_integer_tie': projected_lower_rank != projected_upper_rank,
    }
    return result


@lru_cache(maxsize=1)
def build_batch_mean_reduced_mean_examples() -> list[dict[str, Any]]:
    source_relax6 = [{'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}]
    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    width_two_bundle = ['S10', 'S9']
    width_four_bundle = ['S10', 'S10', 'S9', 'S9']
    width_two_summary = summarize_preferred_state_codes_by_canonical_l2_mean(width_two_bundle)
    width_four_summary = summarize_preferred_state_codes_by_canonical_l2_mean(width_four_bundle)

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]

    return [
        {
            'width_two_bundle': width_two_bundle,
            'width_two_summary': width_two_summary,
            'width_four_bundle': width_four_bundle,
            'width_four_summary': width_four_summary,
            'shared_reduced_mean_summary': width_two_summary['canonical_reduced_mean_summary'],
            'width_two_selection': select_batch_mean_projection_witness_set_from_reduced_mean(
                source_relax6,
                reduced_mean_numerator=width_two_summary['canonical_reduced_mean_summary'][0],
                reduced_mean_denominator=width_two_summary['canonical_reduced_mean_summary'][1],
            ),
            'width_four_selection': select_batch_mean_projection_witness_set_from_reduced_mean(
                source_relax6,
                reduced_mean_numerator=width_four_summary['canonical_reduced_mean_summary'][0],
                reduced_mean_denominator=width_four_summary['canonical_reduced_mean_summary'][1],
            ),
        },
        {
            'bundle': ['S10', 'E8', 'S7'],
            'summary': summarize_preferred_state_codes_by_canonical_l2_mean(['S10', 'E8', 'S7']),
            'selection_from_reduced_mean': select_batch_mean_projection_witness_set_from_reduced_mean(
                feasible_family,
                reduced_mean_numerator=3,
                reduced_mean_denominator=3,
            ),
        },
        {
            'canonical_reduced_mean_summary': [11, 3],
            'selection_from_reduced_mean': select_batch_mean_projection_witness_set_from_reduced_mean(
                infeasible_family,
                reduced_mean_numerator=11,
                reduced_mean_denominator=3,
            ),
        },
    ]


@lru_cache(maxsize=1)
def build_batch_mean_reduced_mean_validation_summary() -> dict[str, Any]:
    max_rank = build_max_rank()
    realized = build_realized_bounded_window_intervals()
    width_to_multiset_count: dict[int, int] = {}
    width_to_pair_class_count: dict[int, int] = {}
    width_to_reduced_mean_class_count: dict[int, int] = {}
    width_to_new_canonical_mean_class_count: dict[int, int] = {}
    pair_classes: set[tuple[int, int]] = set()
    reduced_mean_classes: set[Fraction] = set()
    cumulative_reduced_means: set[Fraction] = set()
    reduced_mean_to_widths: dict[Fraction, set[int]] = defaultdict(set)

    for width in range(1, 6):
        width_pairs: set[tuple[int, int]] = set()
        width_means: set[Fraction] = set()
        multiset_count = 0
        for preferred_ranks_tuple in combinations_with_replacement(range(max_rank + 1), width):
            multiset_count += 1
            rank_sum = sum(preferred_ranks_tuple)
            mean_rank = Fraction(rank_sum, width)
            width_pairs.add((width, rank_sum))
            width_means.add(mean_rank)
            reduced_mean_to_widths[mean_rank].add(width)
        width_to_multiset_count[width] = multiset_count
        width_to_pair_class_count[width] = len(width_pairs)
        width_to_reduced_mean_class_count[width] = len(width_means)
        width_to_new_canonical_mean_class_count[width] = len(width_means - cumulative_reduced_means)
        pair_classes.update(width_pairs)
        reduced_mean_classes.update(width_means)
        cumulative_reduced_means.update(width_means)

    cross_width_overlap_means = {mean: widths for mean, widths in reduced_mean_to_widths.items() if len(widths) > 1}
    integer_overlap_count = sum(1 for mean in cross_width_overlap_means if mean.denominator == 1)
    half_integer_overlap_count = sum(1 for mean in cross_width_overlap_means if mean.denominator == 2)

    reduced_mean_validation_case_count = 0
    reduced_mean_matches_rational_bruteforce = True
    pair_to_mean_selection_case_count = 0
    reduced_mean_matches_two_integer_selection = True

    for mean_rank in sorted(reduced_mean_classes):
        canonical_summary = [mean_rank.numerator, mean_rank.denominator]
        for row in realized:
            reduced_mean_validation_case_count += 1
            constraints = [build_interval_realizer(row['lower_rank'], row['upper_rank'])]
            interval_ranks = list(range(row['lower_rank'], row['upper_rank'] + 1))
            brute_costs = {rank: (Fraction(rank, 1) - mean_rank) ** 2 for rank in interval_ranks}
            best_cost = min(brute_costs.values())
            brute_argmin = [rank for rank, cost in brute_costs.items() if cost == best_cost]
            selection = select_batch_mean_projection_witness_set_from_reduced_mean(
                constraints,
                reduced_mean_numerator=canonical_summary[0],
                reduced_mean_denominator=canonical_summary[1],
            )
            selected_ranks = [
                rank for rank in range(
                    selection['projected_optimal_interval']['lower_rank'],
                    selection['projected_optimal_interval']['upper_rank'] + 1,
                )
            ]
            if selected_ranks != brute_argmin:
                reduced_mean_matches_rational_bruteforce = False
                raise WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError(
                    'reduced mean selection mismatch against rational brute-force argmin'
                )

    for preferred_count, preferred_rank_sum in sorted(pair_classes):
        reduced = canonicalize_l2_summary_to_reduced_mean(
            preferred_count=preferred_count,
            preferred_rank_sum=preferred_rank_sum,
        )
        for row in realized:
            pair_to_mean_selection_case_count += 1
            constraints = [build_interval_realizer(row['lower_rank'], row['upper_rank'])]
            pair_selection = select_batch_mean_projection_witness_set_from_statistics(
                constraints,
                preferred_count=preferred_count,
                preferred_rank_sum=preferred_rank_sum,
            )
            mean_selection = select_batch_mean_projection_witness_set_from_reduced_mean(
                constraints,
                reduced_mean_numerator=reduced['canonical_reduced_mean_summary'][0],
                reduced_mean_denominator=reduced['canonical_reduced_mean_summary'][1],
            )
            if pair_selection['projected_optimal_state_codes'] != mean_selection['projected_optimal_state_codes']:
                reduced_mean_matches_two_integer_selection = False
                raise WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError(
                    'reduced mean selection mismatch against two-integer sufficient-statistic selection'
                )

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    infeasible = select_batch_mean_projection_witness_set_from_reduced_mean(
        infeasible_family,
        reduced_mean_numerator=11,
        reduced_mean_denominator=3,
    )
    if infeasible['selection_status'] != 'infeasible':
        raise WeakeningPortfolioServiceModeSuffixBatchMeanReducedMeanLawError(
            'infeasible reduced-mean selection should stay infeasible'
        )

    return {
        'validated_realized_interval_count': len(realized),
        'validated_preference_bundle_widths': [1, 2, 3, 4, 5],
        'validated_multiset_count': sum(width_to_multiset_count.values()),
        'validated_two_integer_class_count': len(pair_classes),
        'validated_reduced_mean_class_count': len(reduced_mean_classes),
        'reduced_mean_validation_case_count': reduced_mean_validation_case_count,
        'two_integer_comparison_case_count': pair_to_mean_selection_case_count,
        'bundle_to_reduced_mean_reduction_factor': sum(width_to_multiset_count.values()) / len(reduced_mean_classes),
        'two_integer_to_reduced_mean_reduction_factor': len(pair_classes) / len(reduced_mean_classes),
        'width_to_multiset_count': width_to_multiset_count,
        'width_to_two_integer_class_count': width_to_pair_class_count,
        'width_to_reduced_mean_class_count': width_to_reduced_mean_class_count,
        'width_to_new_canonical_mean_class_count': width_to_new_canonical_mean_class_count,
        'cross_width_overlap_class_count': len(cross_width_overlap_means),
        'cross_width_overlap_only_integer_or_half_integer': all(
            mean.denominator in (1, 2) for mean in cross_width_overlap_means
        ),
        'integer_overlap_class_count': integer_overlap_count,
        'half_integer_overlap_class_count': half_integer_overlap_count,
        'duplicate_width_specific_class_count_removed_by_canonicalization': len(pair_classes) - len(reduced_mean_classes),
        'duplicate_width_specific_classes_exactly_explained_by_integer_and_half_integer_overlap': (
            len(pair_classes) - len(reduced_mean_classes)
            == integer_overlap_count * 4 + half_integer_overlap_count
        ),
        'reduced_mean_matches_rational_bruteforce_l2_argmin': reduced_mean_matches_rational_bruteforce,
        'reduced_mean_matches_two_integer_selection': reduced_mean_matches_two_integer_selection,
        'infeasible_reduced_mean_selection_stays_blocked': True,
        'cross_width_overlap_examples': {
            'integer_mean_3': {'canonical_reduced_mean_summary': [3, 1], 'realizable_widths': [1, 2, 3, 4, 5]},
            'half_integer_mean_1_over_2': {'canonical_reduced_mean_summary': [1, 2], 'realizable_widths': [2, 4]},
            'third_mean_1_over_3': {'canonical_reduced_mean_summary': [1, 3], 'realizable_widths': [3]},
        },
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_mean_reduced_mean_validation_summary()
    return {
        'l2_selection_depends_only_on_the_canonical_reduced_mean_rank': True,
        'two_integer_l2_summaries_collapse_further_to_161_reduced_mean_classes': validation[
            'validated_reduced_mean_class_count'
        ],
        'cross_width_overlap_only_occurs_for_integers_and_half_integers': validation[
            'cross_width_overlap_only_integer_or_half_integer'
        ],
        'duplicate_width_specific_classes_removed_by_canonicalization': validation[
            'duplicate_width_specific_class_count_removed_by_canonicalization'
        ],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'If only path-L2 witness choice matters, canonicalize any [preferred_count, preferred_rank_sum] summary to the reduced mean fraction preferred_rank_sum / preferred_count.',
        'Persist that reduced mean as two coprime integers [reduced_mean_numerator, reduced_mean_denominator] rather than retaining the unreduced width-dependent pair.',
        'Project the reduced mean rank onto the feasible overlap interval and select the nearest feasible integer rank or adjacent half-step tie pair.',
        'Treat width as operational metadata, not selection semantics: on the audited width-1..5 catalog, cross-width cache collisions occur only for integers and half-integers.',
        'Do not reuse the reduced-mean summary for L1 semantics or for any downstream logic that must reconstruct bundle cardinality.',
        'If the family is infeasible, carry forward the same blocker certificate from the feasibility-intersection law rather than attempting witness selection.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law_snapshot_20260308.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_mean_reduced_mean_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Canonical reduced-mean summaries for batch L2 witness choice on feasible bounded positive-service local weakening families',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_mean_reduced_mean_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_mean_reduced_mean_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
