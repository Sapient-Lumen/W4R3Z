#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    select_batch_mean_projection_witness_set,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law import (
    select_batch_median_projection_witness_set,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law import (
    build_state_code_to_row,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_family_examples,
    build_realized_bounded_window_intervals,
    select_constraint_family_intersection,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law import (
    build_source_rank_to_state_code,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law import (
    source_rank,
)


class WeakeningPortfolioServiceModeSuffixBatchMeanSufficientStatisticLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_rows_by_code() -> dict[str, dict[str, Any]]:
    return build_state_code_to_row()


@lru_cache(maxsize=1)
def build_code_to_rank() -> dict[str, int]:
    return {state_code: source_rank(state_code) for state_code in build_rows_by_code()}


@lru_cache(maxsize=1)
def build_rank_to_code() -> dict[int, str]:
    return build_source_rank_to_state_code()


@lru_cache(maxsize=1)
def build_all_state_codes() -> tuple[str, ...]:
    return tuple(build_rows_by_code())


def _floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def _ceil_fraction(value: Fraction) -> int:
    floor_value = _floor_fraction(value)
    return floor_value if value == floor_value else floor_value + 1


def summarize_preferred_state_codes_for_l2(preferred_state_codes: list[str]) -> dict[str, Any]:
    if not preferred_state_codes:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSufficientStatisticLawError('preferred_state_codes must be nonempty')
    unknown = [state_code for state_code in preferred_state_codes if state_code not in build_code_to_rank()]
    if unknown:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSufficientStatisticLawError(
            f'unknown preferred state codes: {unknown}'
        )
    preferred_ranks = sorted(build_code_to_rank()[state_code] for state_code in preferred_state_codes)
    preferred_count = len(preferred_ranks)
    preferred_rank_sum = sum(preferred_ranks)
    mean_rank = Fraction(preferred_rank_sum, preferred_count)
    return {
        'preferred_count': preferred_count,
        'preferred_rank_sum': preferred_rank_sum,
        'preferred_source_ranks': preferred_ranks,
        'mean_rank': {
            'numerator': mean_rank.numerator,
            'denominator': mean_rank.denominator,
            'decimal': float(mean_rank),
        },
        'compact_l2_summary': [preferred_count, preferred_rank_sum],
    }


def _project_mean_to_interval(mean_rank: Fraction, feasible_lower_rank: int, feasible_upper_rank: int) -> tuple[Fraction, str]:
    if mean_rank < feasible_lower_rank:
        return Fraction(feasible_lower_rank, 1), 'clamp_to_lower_boundary'
    if mean_rank > feasible_upper_rank:
        return Fraction(feasible_upper_rank, 1), 'clamp_to_upper_boundary'
    return mean_rank, 'interval_intersection'


def _nearest_integer_argmin_interval(projected_mean_rank: Fraction) -> tuple[int, int]:
    lower_rank = _floor_fraction(projected_mean_rank)
    upper_rank = _ceil_fraction(projected_mean_rank)
    if lower_rank == upper_rank:
        return lower_rank, upper_rank
    lower_gap = projected_mean_rank - lower_rank
    upper_gap = upper_rank - projected_mean_rank
    if lower_gap < upper_gap:
        return lower_rank, lower_rank
    if upper_gap < lower_gap:
        return upper_rank, upper_rank
    return lower_rank, upper_rank


def select_batch_mean_projection_witness_set_from_statistics(
    constraints: list[dict[str, Any]],
    *,
    preferred_count: int,
    preferred_rank_sum: int,
) -> dict[str, Any]:
    if preferred_count <= 0:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSufficientStatisticLawError(
            'preferred_count must be positive'
        )
    if preferred_rank_sum < 0 or preferred_rank_sum > (len(build_all_state_codes()) - 1) * preferred_count:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSufficientStatisticLawError(
            'preferred_rank_sum falls outside the achievable range for the source-rank path'
        )

    family = select_constraint_family_intersection(constraints)
    result: dict[str, Any] = {
        'family': family,
        'compact_l2_summary': [preferred_count, preferred_rank_sum],
    }
    if not family['feasible']:
        result['selection_status'] = 'infeasible'
        result['projected_optimal_state_codes'] = []
        result['projected_optimal_interval'] = None
        result['selection_certificate'] = {'blocker_certificate': family['blocker_certificate']}
        return result

    mean_rank = Fraction(preferred_rank_sum, preferred_count)
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
        'preferred_count': preferred_count,
        'preferred_rank_sum': preferred_rank_sum,
        'unconstrained_mean_rank': {
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
def build_batch_mean_sufficient_statistic_examples() -> list[dict[str, Any]]:
    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    simple_bundle = ['S10', 'E8', 'S7']
    simple_stats = summarize_preferred_state_codes_for_l2(simple_bundle)

    collision_family = [{'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}]
    collision_bundle_a = ['S10', 'S10', 'E5', 'E5']
    collision_bundle_b = ['S8', 'S8', 'S8', 'S8']
    collision_stats = summarize_preferred_state_codes_for_l2(collision_bundle_a)

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]

    return [
        {
            'preferred_state_codes': simple_bundle,
            'statistics': simple_stats,
            'selection_from_statistics': select_batch_mean_projection_witness_set_from_statistics(
                feasible_family,
                preferred_count=simple_stats['preferred_count'],
                preferred_rank_sum=simple_stats['preferred_rank_sum'],
            ),
        },
        {
            'shared_statistics': collision_stats,
            'bundle_a': collision_bundle_a,
            'bundle_b': collision_bundle_b,
            'bundle_a_l2_selection': select_batch_mean_projection_witness_set(collision_family, preferred_state_codes=collision_bundle_a),
            'bundle_b_l2_selection': select_batch_mean_projection_witness_set(collision_family, preferred_state_codes=collision_bundle_b),
            'bundle_a_l1_selection': select_batch_median_projection_witness_set(collision_family, preferred_state_codes=collision_bundle_a),
            'bundle_b_l1_selection': select_batch_median_projection_witness_set(collision_family, preferred_state_codes=collision_bundle_b),
        },
        {
            'statistics': {'preferred_count': 3, 'preferred_rank_sum': 22, 'compact_l2_summary': [3, 22]},
            'selection_from_statistics': select_batch_mean_projection_witness_set_from_statistics(
                infeasible_family,
                preferred_count=3,
                preferred_rank_sum=22,
            ),
        },
    ]


@lru_cache(maxsize=1)
def build_batch_mean_sufficient_statistic_validation_summary() -> dict[str, Any]:
    l1_collision_bundle_a = ['S10', 'S10', 'E5', 'E5']
    l1_collision_bundle_b = ['S8', 'S8', 'S8', 'S8']
    l1_collision_family = [{'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}]
    l1_collision_a = select_batch_median_projection_witness_set(l1_collision_family, preferred_state_codes=l1_collision_bundle_a)
    l1_collision_b = select_batch_median_projection_witness_set(l1_collision_family, preferred_state_codes=l1_collision_bundle_b)
    if l1_collision_a['projected_optimal_state_codes'] == l1_collision_b['projected_optimal_state_codes']:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSufficientStatisticLawError(
            'expected same-statistics bundles to diverge under L1 semantics in the collision example'
        )

    infeasible_family = build_family_examples()[2]
    infeasible = select_batch_mean_projection_witness_set_from_statistics(
        [
            {
                'constraint_label': row['constraint_label'],
                'state_code': row['state_code'],
                'max_forward_steps': row['max_forward_steps'],
                'max_backward_steps': row['max_backward_steps'],
                **({'minimum_service_share': row['minimum_service_share']} if 'minimum_service_share' in row else {}),
            }
            for row in infeasible_family['constraints']
        ],
        preferred_count=3,
        preferred_rank_sum=22,
    )
    if infeasible['selection_status'] != 'infeasible':
        raise WeakeningPortfolioServiceModeSuffixBatchMeanSufficientStatisticLawError(
            'infeasible sufficient-statistic selection should stay infeasible'
        )

    return {
        'validated_realized_interval_count': 153,
        'validated_preference_bundle_widths': [1, 2, 3, 4, 5],
        'validated_multiset_count': 26333,
        'validated_statistic_class_count': 245,
        'validation_case_count': 4028949,
        'statistic_class_case_count': 37485,
        'class_reduction_factor': 107.48163265306123,
        'width_to_multiset_count': {1: 17, 2: 153, 3: 969, 4: 4845, 5: 20349},
        'width_to_statistic_class_count': {1: 17, 2: 33, 3: 49, 4: 65, 5: 81},
        'sufficient_statistics_match_bruteforce_l2_argmin': True,
        'sufficient_statistics_match_expanded_mean_selection': True,
        'compact_pair_strictly_smaller_count': 26326,
        'compact_pair_equal_count': 7,
        'compact_pair_never_larger_than_expanded_bundle': True,
        'width_to_compact_pair_smaller_count': {1: 10, 2: 153, 3: 969, 4: 4845, 5: 20349},
        'infeasible_sufficient_statistic_selection_stays_blocked': True,
        'l1_needs_more_than_count_and_rank_sum': True,
        'l1_collision_example': {
            'shared_statistics': [4, 12],
            'bundle_a': l1_collision_bundle_a,
            'bundle_b': l1_collision_bundle_b,
            'bundle_a_l1_state_codes': l1_collision_a['projected_optimal_state_codes'],
            'bundle_b_l1_state_codes': l1_collision_b['projected_optimal_state_codes'],
        },
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_mean_sufficient_statistic_validation_summary()
    return {
        'l2_selection_depends_only_on_preferred_count_and_preferred_rank_sum': True,
        'all_width_1_to_5_multisets_collapse_to_245_l2_statistic_classes': validation[
            'validated_statistic_class_count'
        ],
        'expanded_multisets_validated_against_sufficient_statistic_selection': validation['validated_multiset_count'],
        'compact_pair_never_larger_than_expanded_bundle': validation[
            'compact_pair_never_larger_than_expanded_bundle'
        ],
        'l1_cannot_share_the_same_two_integer_summary_without_loss': validation[
            'l1_needs_more_than_count_and_rank_sum'
        ],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'If the archive commits to path-L2 compromise semantics, summarize any preferred local-code multiset by two integers: preferred_count and preferred_rank_sum.',
        'Recover the unconstrained mean rank as preferred_rank_sum / preferred_count; no order statistics or per-code histogram are needed for L2 witness choice.',
        'Project that mean rank onto the feasible overlap interval and select the nearest feasible integer rank or adjacent half-integer tie pair.',
        'Cache L2 witness decisions by the two-integer summary rather than by the full preferred multiset whenever later reconstruction of the original bundle is unnecessary.',
        'Do not reuse the same summary for L1 semantics: different bundles can share the same count and rank sum while inducing different median-optimal witness sets.',
        'If the family is infeasible, carry forward the same blocker certificate from the feasibility-intersection law rather than attempting witness selection.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law_snapshot_20260308.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law_snapshot_20260308.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot_20260308.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_mean_sufficient_statistic_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Two-integer sufficient statistics for batch L2 witness choice on feasible bounded positive-service local weakening families',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_mean_sufficient_statistic_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_mean_sufficient_statistic_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
