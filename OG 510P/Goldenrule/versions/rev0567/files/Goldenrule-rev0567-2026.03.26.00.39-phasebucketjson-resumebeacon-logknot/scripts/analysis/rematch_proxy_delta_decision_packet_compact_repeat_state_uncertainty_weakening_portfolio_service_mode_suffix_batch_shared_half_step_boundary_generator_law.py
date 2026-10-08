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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law import (
    apply_shared_half_step_interval_kernel,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(RuntimeError):
    pass


MAX_SOURCE_RANK = 16


def _normalize_interval(interval: list[int] | tuple[int, int]) -> tuple[int, int]:
    if len(interval) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(
            'interval must contain exactly two ranks'
        )
    lower_rank = int(interval[0])
    upper_rank = int(interval[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(
            'interval must be a nonempty source-rank interval inside the realized path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=1)
def build_lower_floor_generator_catalog() -> list[dict[str, Any]]:
    return [
        {
            'generator_kind': 'lower_floor',
            'boundary_rank': lower_rank,
            'generator_interval': [lower_rank, MAX_SOURCE_RANK],
            'missing_interval_cone_if_omitted_size': MAX_SOURCE_RANK - lower_rank + 1,
        }
        for lower_rank in range(MAX_SOURCE_RANK + 1)
    ]


@lru_cache(maxsize=1)
def build_upper_cap_generator_catalog() -> list[dict[str, Any]]:
    return [
        {
            'generator_kind': 'upper_cap',
            'boundary_rank': upper_rank,
            'generator_interval': [0, upper_rank],
            'missing_interval_cone_if_omitted_size': upper_rank + 1,
        }
        for upper_rank in range(MAX_SOURCE_RANK + 1)
    ]


@lru_cache(maxsize=1)
def build_distinct_one_sided_generator_intervals() -> list[list[int]]:
    distinct = {
        (row['generator_interval'][0], row['generator_interval'][1])
        for row in build_lower_floor_generator_catalog() + build_upper_cap_generator_catalog()
    }
    return [list(interval) for interval in sorted(distinct)]


@lru_cache(maxsize=1)
def build_realized_interval_catalog() -> list[list[int]]:
    return [
        [row['lower_rank'], row['upper_rank']]
        for row in build_realized_bounded_window_intervals()
    ]


@lru_cache(maxsize=1)
def build_realized_interval_set() -> set[tuple[int, int]]:
    return {tuple(interval) for interval in build_realized_interval_catalog()}



def intersect_intervals(
    first_interval: list[int] | tuple[int, int],
    second_interval: list[int] | tuple[int, int],
) -> list[int] | None:
    first_lower_rank, first_upper_rank = _normalize_interval(first_interval)
    second_lower_rank, second_upper_rank = _normalize_interval(second_interval)
    overlap_lower_rank = max(first_lower_rank, second_lower_rank)
    overlap_upper_rank = min(first_upper_rank, second_upper_rank)
    if overlap_lower_rank <= overlap_upper_rank:
        return [overlap_lower_rank, overlap_upper_rank]
    return None



def factorize_shared_half_step_kernel(
    interval: list[int] | tuple[int, int],
) -> dict[str, Any]:
    lower_rank, upper_rank = _normalize_interval(interval)
    lower_floor_generator_interval = [lower_rank, MAX_SOURCE_RANK]
    upper_cap_generator_interval = [0, upper_rank]
    return {
        'factored_interval': [lower_rank, upper_rank],
        'lower_floor_generator_interval': lower_floor_generator_interval,
        'upper_cap_generator_interval': upper_cap_generator_interval,
        'generator_identity_overlap_interval': [0, MAX_SOURCE_RANK],
        'factorization_by_intersection': intersect_intervals(
            lower_floor_generator_interval,
            upper_cap_generator_interval,
        ),
        'is_identity_kernel': lower_rank == 0 and upper_rank == MAX_SOURCE_RANK,
    }



def apply_shared_half_step_boundary_generator_factorization(
    interval: list[int] | tuple[int, int],
    *,
    half_step_selector_index: int,
) -> dict[str, Any]:
    factorization = factorize_shared_half_step_kernel(interval)
    lower_floor_first = apply_shared_half_step_interval_kernel(
        factorization['lower_floor_generator_interval'],
        half_step_selector_index=half_step_selector_index,
    )
    lower_floor_then_upper_cap = apply_shared_half_step_interval_kernel(
        factorization['upper_cap_generator_interval'],
        half_step_selector_index=lower_floor_first['projected_half_step_witness_index'],
    )
    upper_cap_first = apply_shared_half_step_interval_kernel(
        factorization['upper_cap_generator_interval'],
        half_step_selector_index=half_step_selector_index,
    )
    upper_cap_then_lower_floor = apply_shared_half_step_interval_kernel(
        factorization['lower_floor_generator_interval'],
        half_step_selector_index=upper_cap_first['projected_half_step_witness_index'],
    )
    direct = apply_shared_half_step_interval_kernel(
        factorization['factored_interval'],
        half_step_selector_index=half_step_selector_index,
    )
    return {
        'input_half_step_selector_index': half_step_selector_index,
        'factorization': factorization,
        'lower_floor_first': lower_floor_first,
        'lower_floor_then_upper_cap': lower_floor_then_upper_cap,
        'upper_cap_first': upper_cap_first,
        'upper_cap_then_lower_floor': upper_cap_then_lower_floor,
        'direct_interval_kernel': direct,
        'factorization_matches_direct_interval_kernel': (
            lower_floor_then_upper_cap['projected_half_step_witness_index']
            == direct['projected_half_step_witness_index']
            == upper_cap_then_lower_floor['projected_half_step_witness_index']
        ),
    }



def build_generator_closure(
    distinct_generator_intervals: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    closure = set(distinct_generator_intervals or {tuple(row) for row in build_distinct_one_sided_generator_intervals()})
    changed = True
    while changed:
        changed = False
        current = list(closure)
        for first_interval in current:
            for second_interval in current:
                overlap = intersect_intervals(first_interval, second_interval)
                if overlap is None:
                    continue
                overlap_tuple = (overlap[0], overlap[1])
                if overlap_tuple not in closure:
                    closure.add(overlap_tuple)
                    changed = True
    return closure


@lru_cache(maxsize=1)
def build_boundary_generator_omission_catalog() -> list[dict[str, Any]]:
    realized = build_realized_interval_set()
    generators = {tuple(row) for row in build_distinct_one_sided_generator_intervals()}
    rows: list[dict[str, Any]] = []
    for omitted in sorted(generators):
        retained = set(generators)
        retained.remove(omitted)
        closure = build_generator_closure(retained)
        missing_intervals = sorted(realized - closure)
        if not missing_intervals:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(
                'every distinct one-sided generator should be essential on the current path'
            )
        lower_rank, upper_rank = omitted
        if lower_rank == 0 and upper_rank == MAX_SOURCE_RANK:
            omission_kind = 'shared_identity'
            expected_missing = [[0, MAX_SOURCE_RANK]]
        elif lower_rank == 0:
            omission_kind = 'upper_cap'
            expected_missing = [[candidate_lower_rank, upper_rank] for candidate_lower_rank in range(upper_rank + 1)]
        elif upper_rank == MAX_SOURCE_RANK:
            omission_kind = 'lower_floor'
            expected_missing = [[lower_rank, candidate_upper_rank] for candidate_upper_rank in range(lower_rank, MAX_SOURCE_RANK + 1)]
        else:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(
                'unexpected one-sided generator interval shape'
            )
        if expected_missing != [list(interval) for interval in missing_intervals]:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(
                'generator omission should delete exactly its aligned interval cone'
            )
        rows.append(
            {
                'omitted_generator_interval': [lower_rank, upper_rank],
                'omission_kind': omission_kind,
                'missing_interval_count': len(missing_intervals),
                'missing_intervals': [list(interval) for interval in missing_intervals],
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_batch_shared_half_step_boundary_generator_examples() -> list[dict[str, Any]]:
    return [
        {
            'canonical_factorization_of_interval_kernel': apply_shared_half_step_boundary_generator_factorization(
                [3, 8],
                half_step_selector_index=1,
            )
        },
        {
            'identity_kernel_is_the_shared_generator_overlap': factorize_shared_half_step_kernel([0, 16])
        },
        {
            'omitting_upper_cap_generator_deletes_exact_upper_boundary_cone': next(
                row for row in build_boundary_generator_omission_catalog() if row['omitted_generator_interval'] == [0, 4]
            )
        },
        {
            'omitting_lower_floor_generator_deletes_exact_lower_boundary_cone': next(
                row for row in build_boundary_generator_omission_catalog() if row['omitted_generator_interval'] == [12, 16]
            )
        },
    ]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_boundary_generator_validation_summary() -> dict[str, Any]:
    realized = build_realized_interval_catalog()
    distinct_generators = build_distinct_one_sided_generator_intervals()
    closure = build_generator_closure({tuple(row) for row in distinct_generators})
    omission_catalog = build_boundary_generator_omission_catalog()

    factorization_case_count = 0
    factorization_equivalence_check_count = 0
    for interval in realized:
        factorization = factorize_shared_half_step_kernel(interval)
        if factorization['factorization_by_intersection'] != interval:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(
                'factorization intersection must equal the target interval'
            )
        for half_step_selector_index in range(33):
            factorization_case_count += 1
            execution = apply_shared_half_step_boundary_generator_factorization(
                interval,
                half_step_selector_index=half_step_selector_index,
            )
            if not execution['factorization_matches_direct_interval_kernel']:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepBoundaryGeneratorLawError(
                    'one-sided generator factorization should match the direct interval kernel in both orders'
                )
            factorization_equivalence_check_count += 2

    lower_floor_omission_counts = [
        row['missing_interval_count']
        for row in omission_catalog
        if row['omission_kind'] == 'lower_floor'
    ]
    upper_cap_omission_counts = [
        row['missing_interval_count']
        for row in omission_catalog
        if row['omission_kind'] == 'upper_cap'
    ]
    identity_omission_counts = [
        row['missing_interval_count']
        for row in omission_catalog
        if row['omission_kind'] == 'shared_identity'
    ]

    return {
        'validated_realized_interval_count': len(realized),
        'validated_half_step_selector_index_class_count': 33,
        'half_step_selector_index_range': [0, 32],
        'distinct_lower_floor_generator_count': len(build_lower_floor_generator_catalog()),
        'distinct_upper_cap_generator_count': len(build_upper_cap_generator_catalog()),
        'distinct_one_sided_generator_interval_count': len(distinct_generators),
        'shared_identity_generator_interval': [0, 16],
        'generator_closure_interval_count': len(closure),
        'generator_closure_reconstructs_full_realized_interval_catalog': closure == build_realized_interval_set(),
        'canonical_factorization_count': len(realized),
        'factorization_validation_case_count': factorization_case_count,
        'factorization_equivalence_check_count': factorization_equivalence_check_count,
        'lower_floor_then_upper_cap_matches_direct_interval_kernel': True,
        'upper_cap_then_lower_floor_matches_direct_interval_kernel': True,
        'factorization_orders_commute_for_every_feasible_interval': True,
        'generator_omission_case_count': len(omission_catalog),
        'every_one_sided_generator_is_essential': True,
        'identity_omission_missing_interval_count': identity_omission_counts[0],
        'lower_floor_omission_missing_interval_count_range': [
            min(lower_floor_omission_counts),
            max(lower_floor_omission_counts),
        ],
        'upper_cap_omission_missing_interval_count_range': [
            min(upper_cap_omission_counts),
            max(upper_cap_omission_counts),
        ],
        'one_sided_generators_form_a_minimal_generating_family_for_realized_feasible_kernels': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_shared_half_step_boundary_generator_validation_summary()
    return {
        'every_realized_normalized_batch_l2_and_batch_linf_interval_kernel_factors_canonically_into_one_lower_floor_and_one_upper_cap_generator': True,
        'distinct_one_sided_generator_interval_count': validation['distinct_one_sided_generator_interval_count'],
        'generator_closure_interval_count': validation['generator_closure_interval_count'],
        'factorization_validation_case_count': validation['factorization_validation_case_count'],
        'factorization_equivalence_check_count': validation['factorization_equivalence_check_count'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'After a batch path-L2 or path-Linf request is normalized to half_step_selector_index, treat every feasible interval kernel K_[a,b] as the canonical composition of one lower-floor generator K_[a,16] and one upper-cap generator K_[0,b].',
        'Implement streaming feasible-state accumulation by updating only the current floor a and cap b; the downstream witness executor can always recover the full feasible kernel by composing those two one-sided generators in either order.',
        'Use the 33 distinct one-sided generator intervals [a,16] and [0,b] as the normalized generator basis for the full 153-kernel feasible catalog; [0,16] is the shared identity generator counted by both sides.',
        'Do not drop any nonidentity one-sided generator from that basis on the current path: omitting K_[0,b] deletes exactly the upper-b boundary cone {[l,b] : 0 <= l <= b}, omitting K_[a,16] deletes exactly the lower-a boundary cone {[a,u] : a <= u <= 16}, and omitting the shared identity deletes [0,16] itself.',
        'This generator factorization is a normalized-kernel result only; it does not replace the semantics-specific front-end normalizers that derive half_step_selector_index from path-L2 means or path-Linf extrema.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_boundary_generator_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Every realized normalized batch path-L2 and path-Linf feasible interval kernel factors canonically into one lower-floor generator and one upper-cap generator.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'factorization_examples': build_batch_shared_half_step_boundary_generator_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law.py',
    }



def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_boundary_generator_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
