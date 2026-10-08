#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
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


class WeakeningPortfolioServiceModeSuffixBatchMedianProjectionLawError(RuntimeError):
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
        raise WeakeningPortfolioServiceModeSuffixBatchMedianProjectionLawError('preferred_state_codes must be nonempty')
    unknown = [state_code for state_code in preferred_state_codes if state_code not in build_code_to_rank()]
    if unknown:
        raise WeakeningPortfolioServiceModeSuffixBatchMedianProjectionLawError(f'unknown preferred state codes: {unknown}')
    return list(preferred_state_codes)


def _median_rank_interval(preferred_state_codes: list[str]) -> tuple[int, int, list[int]]:
    normalized = _normalize_preferred_state_codes(preferred_state_codes)
    preferred_ranks = sorted(build_code_to_rank()[state_code] for state_code in normalized)
    count = len(preferred_ranks)
    lower_median_rank = preferred_ranks[(count - 1) // 2]
    upper_median_rank = preferred_ranks[count // 2]
    return lower_median_rank, upper_median_rank, preferred_ranks


def _project_interval(median_lower_rank: int, median_upper_rank: int, feasible_lower_rank: int, feasible_upper_rank: int) -> tuple[int, int, str]:
    if median_upper_rank < feasible_lower_rank:
        return feasible_lower_rank, feasible_lower_rank, 'clamp_to_lower_boundary'
    if median_lower_rank > feasible_upper_rank:
        return feasible_upper_rank, feasible_upper_rank, 'clamp_to_upper_boundary'
    return max(median_lower_rank, feasible_lower_rank), min(median_upper_rank, feasible_upper_rank), 'interval_intersection'


def select_batch_median_projection_witness_set(
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

    median_lower_rank, median_upper_rank, preferred_ranks = _median_rank_interval(preferred_state_codes)
    projected_lower_rank, projected_upper_rank, projection_case = _project_interval(
        median_lower_rank,
        median_upper_rank,
        family['lower_rank_bound'],
        family['upper_rank_bound'],
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
        'preferred_count': len(preferred_state_codes),
        'preferred_source_ranks': preferred_ranks,
        'unconstrained_median_interval': {
            'lower_rank': median_lower_rank,
            'upper_rank': median_upper_rank,
            'cardinality': median_upper_rank - median_lower_rank + 1,
        },
    }
    return result


@lru_cache(maxsize=1)
def build_batch_median_projection_examples() -> list[dict[str, Any]]:
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
    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    return [
        select_batch_median_projection_witness_set(
            feasible_family,
            preferred_state_codes=['S10', 'E8', 'S7'],
        ),
        select_batch_median_projection_witness_set(
            feasible_family,
            preferred_state_codes=['S10', 'T0'],
        ),
        select_batch_median_projection_witness_set(
            singleton_family,
            preferred_state_codes=['E1', 'S1', 'S2', 'E3'],
        ),
        select_batch_median_projection_witness_set(
            infeasible_family,
            preferred_state_codes=['S8', 'E5', 'T0'],
        ),
    ]


@lru_cache(maxsize=1)
def build_batch_median_projection_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    ranks = list(range(len(build_all_state_codes())))
    validation_case_count = 0
    unique_optimum_count = 0
    tie_interval_count = 0
    even_width_tie_count = 0
    odd_width_tie_count = 0
    max_tie_cardinality_by_preference_count: dict[int, int] = {}

    # Exhaustively validate all realized feasible intervals against all unique preferred-code bundles up to width 5.
    for width in range(1, 6):
        for preferred_ranks_tuple in combinations(ranks, width):
            preferred_codes = [build_rank_to_code()[rank] for rank in preferred_ranks_tuple]
            median_lower_rank = preferred_ranks_tuple[(width - 1) // 2]
            median_upper_rank = preferred_ranks_tuple[width // 2]
            for row in realized:
                validation_case_count += 1
                projected = select_batch_median_projection_witness_set(
                    [
                        {
                            'constraint_label': row['interval_key'],
                            'state_code': row['first_realizer']['state_code'],
                            'max_forward_steps': row['first_realizer']['max_forward_steps'],
                            'max_backward_steps': row['first_realizer']['max_backward_steps'],
                        }
                    ],
                    preferred_state_codes=preferred_codes,
                )
                interval_ranks = list(range(row['lower_rank'], row['upper_rank'] + 1))
                brute_costs = {
                    rank: sum(abs(rank - preferred_rank) for preferred_rank in preferred_ranks_tuple)
                    for rank in interval_ranks
                }
                best_cost = min(brute_costs.values())
                brute_argmin = [rank for rank, cost in brute_costs.items() if cost == best_cost]
                projected_interval = projected['projected_optimal_interval']
                if projected['selection_status'] != 'selected':
                    raise WeakeningPortfolioServiceModeSuffixBatchMedianProjectionLawError('realized interval should be feasible')
                if projected_interval['lower_rank'] != brute_argmin[0] or projected_interval['upper_rank'] != brute_argmin[-1]:
                    raise WeakeningPortfolioServiceModeSuffixBatchMedianProjectionLawError('projected median interval mismatch')
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
                # Sanity-check the closed-form projection case against the precomputed medians.
                projected_lower_rank, projected_upper_rank, _ = _project_interval(
                    median_lower_rank,
                    median_upper_rank,
                    row['lower_rank'],
                    row['upper_rank'],
                )
                if projected_interval['lower_rank'] != projected_lower_rank or projected_interval['upper_rank'] != projected_upper_rank:
                    raise WeakeningPortfolioServiceModeSuffixBatchMedianProjectionLawError('closed-form projection mismatch')

    infeasible_family = build_family_examples()[2]
    infeasible = select_batch_median_projection_witness_set(
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
        raise WeakeningPortfolioServiceModeSuffixBatchMedianProjectionLawError('infeasible batch projection should stay infeasible')

    return {
        'validated_realized_interval_count': len(realized),
        'validated_preference_bundle_widths': [1, 2, 3, 4, 5],
        'validation_case_count': validation_case_count,
        'unique_optimum_count': unique_optimum_count,
        'tie_interval_count': tie_interval_count,
        'odd_width_tie_count': odd_width_tie_count,
        'even_width_tie_count': even_width_tie_count,
        'max_tie_cardinality_by_preference_count': max_tie_cardinality_by_preference_count,
        'projected_median_interval_matches_bruteforce_argmin': True,
        'all_ties_come_from_even_preference_widths': odd_width_tie_count == 0,
        'infeasible_batch_projection_stays_blocked': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_median_projection_validation_summary()
    return {
        'l1_optimal_feasible_witness_set_is_projected_median_interval': True,
        'ties_only_appear_for_even_preference_bundle_widths': validation['all_ties_come_from_even_preference_widths'],
        'max_tie_cardinality_by_preference_count_up_to_width_5': validation['max_tie_cardinality_by_preference_count'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'Merge the bounded local requirement family to its feasible overlap interval as in the feasibility-intersection law.',
        'Map every preferred local code to its source-rank coordinate and sort the preferred ranks.',
        'Take the unconstrained L1 median interval: singleton for odd preference count, closed interval between the two middle ranks for even preference count.',
        'Project that median interval onto the feasible overlap interval; the resulting closed rank interval is exactly the full feasible argmin set for total absolute rank distance.',
        'If the family is infeasible, carry forward the same two-window blocker certificate rather than attempting witness selection.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law_snapshot_20260308.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot_20260308.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law_snapshot_20260308.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_median_projection_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Batch L1 witness choice for feasible bounded positive-service local weakening families',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_median_projection_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_median_projection_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
