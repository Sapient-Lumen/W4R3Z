#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


class WeakeningPortfolioServiceModeSuffixBatchMeanProjectionLawError(RuntimeError):
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


def _normalize_preferred_state_codes(preferred_state_codes: list[str]) -> list[str]:
    if not preferred_state_codes:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanProjectionLawError('preferred_state_codes must be nonempty')
    unknown = [state_code for state_code in preferred_state_codes if state_code not in build_code_to_rank()]
    if unknown:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanProjectionLawError(f'unknown preferred state codes: {unknown}')
    return list(preferred_state_codes)


def _floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def _ceil_fraction(value: Fraction) -> int:
    floor_value = _floor_fraction(value)
    return floor_value if value == floor_value else floor_value + 1


def _mean_rank(preferred_state_codes: list[str]) -> tuple[Fraction, list[int]]:
    normalized = _normalize_preferred_state_codes(preferred_state_codes)
    preferred_ranks = sorted(build_code_to_rank()[state_code] for state_code in normalized)
    return Fraction(sum(preferred_ranks), len(preferred_ranks)), preferred_ranks


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


def select_batch_mean_projection_witness_set(
    constraints: list[dict[str, Any]],
    *,
    preferred_state_codes: list[str],
) -> dict[str, Any]:
    family = select_constraint_family_intersection(constraints)
    result: dict[str, Any] = {
        'family': family,
        'preferred_state_codes': preferred_state_codes,
    }
    if not family['feasible']:
        result['selection_status'] = 'infeasible'
        result['projected_optimal_state_codes'] = []
        result['projected_optimal_interval'] = None
        result['selection_certificate'] = {'blocker_certificate': family['blocker_certificate']}
        return result

    mean_rank, preferred_ranks = _mean_rank(preferred_state_codes)
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
        'preferred_count': len(preferred_state_codes),
        'preferred_source_ranks': preferred_ranks,
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
def build_interval_realizer(lower_rank: int, upper_rank: int) -> dict[str, Any]:
    for row in build_realized_bounded_window_intervals():
        if row['lower_rank'] == lower_rank and row['upper_rank'] == upper_rank:
            first_realizer = row['first_realizer']
            return {
                'constraint_label': row['interval_key'],
                'state_code': first_realizer['state_code'],
                'max_forward_steps': first_realizer['max_forward_steps'],
                'max_backward_steps': first_realizer['max_backward_steps'],
            }
    raise WeakeningPortfolioServiceModeSuffixBatchMeanProjectionLawError(
        f'no realized interval found for ranks [{lower_rank}, {upper_rank}]'
    )


@lru_cache(maxsize=1)
def build_batch_mean_projection_examples() -> list[dict[str, Any]]:
    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    singleton_family = [
        {'constraint_label': 'share_0_02', 'state_code': 'D2', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'tail_exact', 'state_code': 'E1', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'singleton_s2', 'state_code': 'S2', 'max_forward_steps': 0, 'max_backward_steps': 0},
    ]
    skewed_interval_family = [build_interval_realizer(0, 2)]
    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    return [
        select_batch_mean_projection_witness_set(
            feasible_family,
            preferred_state_codes=['S10', 'E8', 'S7'],
        ),
        select_batch_mean_projection_witness_set(
            feasible_family,
            preferred_state_codes=['E8', 'S6'],
        ),
        select_batch_mean_projection_witness_set(
            singleton_family,
            preferred_state_codes=['S10', 'S8', 'S7', 'S6'],
        ),
        select_batch_mean_projection_witness_set(
            skewed_interval_family,
            preferred_state_codes=['S10', 'S9', 'S7'],
        ),
        select_batch_mean_projection_witness_set(
            infeasible_family,
            preferred_state_codes=['S8', 'E5', 'T0'],
        ),
    ]


@lru_cache(maxsize=1)
def build_batch_mean_projection_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    ranks = list(range(len(build_all_state_codes())))
    validation_case_count = 0
    unique_optimum_count = 0
    tie_interval_count = 0
    even_width_tie_count = 0
    odd_width_tie_count = 0
    max_tie_cardinality_by_preference_count: dict[int, int] = {}
    same_as_l1_count = 0
    differs_from_l1_count = 0
    l1_tie_interval_count = 0
    both_l1_and_l2_tie_count = 0
    differing_case_count_by_preference_width: dict[int, int] = {}

    for width in range(1, 6):
        for preferred_ranks_tuple in combinations(ranks, width):
            preferred_codes = [build_rank_to_code()[rank] for rank in preferred_ranks_tuple]
            mean_rank = Fraction(sum(preferred_ranks_tuple), width)
            for row in realized:
                validation_case_count += 1
                interval_ranks = list(range(row['lower_rank'], row['upper_rank'] + 1))
                brute_l2_costs = {
                    rank: sum((rank - preferred_rank) ** 2 for preferred_rank in preferred_ranks_tuple)
                    for rank in interval_ranks
                }
                best_l2_cost = min(brute_l2_costs.values())
                brute_l2_argmin = [rank for rank, cost in brute_l2_costs.items() if cost == best_l2_cost]
                projected_mean_rank, _ = _project_mean_to_interval(mean_rank, row['lower_rank'], row['upper_rank'])
                projected_lower_rank, projected_upper_rank = _nearest_integer_argmin_interval(projected_mean_rank)
                if projected_lower_rank != brute_l2_argmin[0] or projected_upper_rank != brute_l2_argmin[-1]:
                    raise WeakeningPortfolioServiceModeSuffixBatchMeanProjectionLawError('projected mean interval mismatch')
                projected_interval = {
                    'lower_rank': projected_lower_rank,
                    'upper_rank': projected_upper_rank,
                    'cardinality': projected_upper_rank - projected_lower_rank + 1,
                }

                brute_l1_costs = {
                    rank: sum(abs(rank - preferred_rank) for preferred_rank in preferred_ranks_tuple)
                    for rank in interval_ranks
                }
                best_l1_cost = min(brute_l1_costs.values())
                brute_l1_argmin = [rank for rank, cost in brute_l1_costs.items() if cost == best_l1_cost]
                if brute_l1_argmin == brute_l2_argmin:
                    same_as_l1_count += 1
                else:
                    differs_from_l1_count += 1
                    differing_case_count_by_preference_width[width] = differing_case_count_by_preference_width.get(width, 0) + 1
                if len(brute_l1_argmin) > 1:
                    l1_tie_interval_count += 1
                tie_cardinality = projected_interval['cardinality']
                if tie_cardinality == 1:
                    unique_optimum_count += 1
                else:
                    tie_interval_count += 1
                    if width % 2 == 0:
                        even_width_tie_count += 1
                    else:
                        odd_width_tie_count += 1
                    max_tie_cardinality_by_preference_count[width] = max(
                        max_tie_cardinality_by_preference_count.get(width, 0),
                        tie_cardinality,
                    )
                if len(brute_l1_argmin) > 1 and tie_cardinality > 1:
                    both_l1_and_l2_tie_count += 1

    infeasible_family = build_family_examples()[2]
    infeasible = select_batch_mean_projection_witness_set(
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
        preferred_state_codes=['S8', 'E5', 'T0'],
    )
    if infeasible['selection_status'] != 'infeasible':
        raise WeakeningPortfolioServiceModeSuffixBatchMeanProjectionLawError('infeasible batch projection should stay infeasible')

    return {
        'validated_realized_interval_count': len(realized),
        'validated_preference_bundle_widths': [1, 2, 3, 4, 5],
        'validation_case_count': validation_case_count,
        'unique_optimum_count': unique_optimum_count,
        'tie_interval_count': tie_interval_count,
        'odd_width_tie_count': odd_width_tie_count,
        'even_width_tie_count': even_width_tie_count,
        'max_tie_cardinality_by_preference_count': max_tie_cardinality_by_preference_count,
        'projected_mean_interval_matches_bruteforce_argmin': True,
        'all_ties_come_from_even_preference_widths': odd_width_tie_count == 0,
        'ties_never_exceed_two_adjacent_states': max(max_tie_cardinality_by_preference_count.values(), default=1) <= 2,
        'same_as_l1_count': same_as_l1_count,
        'differs_from_l1_count': differs_from_l1_count,
        'differing_case_count_by_preference_width': differing_case_count_by_preference_width,
        'l1_tie_interval_count': l1_tie_interval_count,
        'both_l1_and_l2_tie_count': both_l1_and_l2_tie_count,
        'l2_tie_reduction_against_l1': l1_tie_interval_count - tie_interval_count,
        'infeasible_batch_projection_stays_blocked': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_mean_projection_validation_summary()
    return {
        'l2_optimal_feasible_witness_set_is_nearest_integer_projection_of_the_clamped_mean': True,
        'ties_only_appear_for_even_preference_bundle_widths': validation['all_ties_come_from_even_preference_widths'],
        'ties_never_exceed_two_adjacent_states': validation['ties_never_exceed_two_adjacent_states'],
        'l2_reduces_tie_cases_against_l1': validation['l2_tie_reduction_against_l1'],
        'l2_differs_from_l1_on_many_feasible_families': validation['differs_from_l1_count'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'Merge the bounded local requirement family to its feasible overlap interval as in the feasibility-intersection law.',
        'Map every preferred local code to its source-rank coordinate and compute the arithmetic mean rank.',
        'Project that mean rank onto the feasible overlap interval.',
        'Select the feasible integer rank(s) nearest to the projected mean rank; that singleton or adjacent pair is exactly the full feasible argmin set for total squared rank distance.',
        'If the family is infeasible, carry forward the same two-window blocker certificate rather than attempting witness selection.',
        'Treat the result as a distinct compromise objective from the L1 median law: it shrinks tie burden, but it can move the chosen witness toward outliers.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law_snapshot_20260308.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law_snapshot_20260308.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot_20260308.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_mean_projection_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Batch L2 witness choice for feasible bounded positive-service local weakening families',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_mean_projection_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_mean_projection_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
