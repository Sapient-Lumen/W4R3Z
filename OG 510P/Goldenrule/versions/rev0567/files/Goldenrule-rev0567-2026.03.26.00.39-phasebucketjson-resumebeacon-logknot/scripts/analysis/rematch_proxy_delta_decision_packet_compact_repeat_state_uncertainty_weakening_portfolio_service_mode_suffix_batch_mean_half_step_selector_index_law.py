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
    build_interval_realizer,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law import (
    select_batch_mean_projection_witness_set_from_reduced_mean,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law import (
    build_batch_mean_selector_interval_examples,
    build_batch_mean_selector_interval_validation_summary,
    build_max_rank,
    select_batch_mean_projection_witness_set_from_selector_interval,
    summarize_preferred_state_codes_by_l2_selector_interval,
    summarize_reduced_mean_by_selector_interval,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_realized_bounded_window_intervals,
)


class WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_max_half_step_selector_index() -> int:
    return 2 * build_max_rank()


def encode_selector_interval_as_half_step_selector_index(*, selector_lower_rank: int, selector_upper_rank: int) -> int:
    max_rank = build_max_rank()
    if selector_lower_rank < 0 or selector_upper_rank > max_rank or selector_lower_rank > selector_upper_rank:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
            'selector interval falls outside the source-rank path'
        )
    if selector_upper_rank - selector_lower_rank > 1:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
            'selector interval must be a singleton or one adjacent tie pair'
        )
    return selector_lower_rank + selector_upper_rank


def decode_half_step_selector_index(*, half_step_selector_index: int) -> dict[str, Any]:
    max_index = build_max_half_step_selector_index()
    if half_step_selector_index < 0 or half_step_selector_index > max_index:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
            'half-step selector index falls outside the source-rank path'
        )

    if half_step_selector_index % 2 == 0:
        selector_lower_rank = half_step_selector_index // 2
        selector_upper_rank = selector_lower_rank
    else:
        selector_lower_rank = half_step_selector_index // 2
        selector_upper_rank = selector_lower_rank + 1

    return {
        'half_step_selector_index': half_step_selector_index,
        'selector_interval_summary': [selector_lower_rank, selector_upper_rank],
        'selector_interval_cardinality': selector_upper_rank - selector_lower_rank + 1,
        'selector_interval_is_adjacent_tie_pair': selector_lower_rank != selector_upper_rank,
    }


def summarize_reduced_mean_by_half_step_selector_index(*, reduced_mean_numerator: int, reduced_mean_denominator: int) -> dict[str, Any]:
    selector = summarize_reduced_mean_by_selector_interval(
        reduced_mean_numerator=reduced_mean_numerator,
        reduced_mean_denominator=reduced_mean_denominator,
    )
    half_step_selector_index = encode_selector_interval_as_half_step_selector_index(
        selector_lower_rank=selector['selector_interval_summary'][0],
        selector_upper_rank=selector['selector_interval_summary'][1],
    )
    return {
        **selector,
        **decode_half_step_selector_index(half_step_selector_index=half_step_selector_index),
    }


def summarize_preferred_state_codes_by_half_step_selector_index(preferred_state_codes: list[str]) -> dict[str, Any]:
    selector = summarize_preferred_state_codes_by_l2_selector_interval(preferred_state_codes)
    half_step_selector_index = encode_selector_interval_as_half_step_selector_index(
        selector_lower_rank=selector['selector_interval_summary'][0],
        selector_upper_rank=selector['selector_interval_summary'][1],
    )
    return {
        **selector,
        **decode_half_step_selector_index(half_step_selector_index=half_step_selector_index),
    }


def select_batch_mean_projection_witness_set_from_half_step_selector_index(
    constraints: list[dict[str, Any]], *, half_step_selector_index: int
) -> dict[str, Any]:
    decoded = decode_half_step_selector_index(half_step_selector_index=half_step_selector_index)
    selection = select_batch_mean_projection_witness_set_from_selector_interval(
        constraints,
        selector_lower_rank=decoded['selector_interval_summary'][0],
        selector_upper_rank=decoded['selector_interval_summary'][1],
    )
    return {
        **selection,
        'half_step_selector_index': half_step_selector_index,
    }


@lru_cache(maxsize=1)
def build_adjacent_interval_realizers() -> list[dict[str, Any]]:
    return [build_interval_realizer(rank, rank + 1) for rank in range(build_max_rank())]


def build_width_one_fingerprint(*, half_step_selector_index: int) -> dict[str, Any]:
    decoded = decode_half_step_selector_index(half_step_selector_index=half_step_selector_index)
    symbols: list[str] = []
    rows: list[dict[str, Any]] = []
    for interval_lower_rank, constraints in enumerate(build_adjacent_interval_realizers()):
        selection = select_batch_mean_projection_witness_set_from_half_step_selector_index(
            [constraints],
            half_step_selector_index=half_step_selector_index,
        )
        projected = selection['projected_optimal_interval']
        if projected['lower_rank'] == interval_lower_rank and projected['upper_rank'] == interval_lower_rank:
            symbol = 'L'
            meaning = 'lower_endpoint'
        elif projected['lower_rank'] == interval_lower_rank + 1 and projected['upper_rank'] == interval_lower_rank + 1:
            symbol = 'R'
            meaning = 'upper_endpoint'
        elif projected['lower_rank'] == interval_lower_rank and projected['upper_rank'] == interval_lower_rank + 1:
            symbol = 'B'
            meaning = 'both_endpoints'
        else:
            raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
                'width-1 projection should return the lower endpoint, upper endpoint, or both endpoints'
            )
        rows.append(
            {
                'adjacent_interval': [interval_lower_rank, interval_lower_rank + 1],
                'projected_optimal_interval': [projected['lower_rank'], projected['upper_rank']],
                'symbol': symbol,
                'meaning': meaning,
            }
        )
        symbols.append(symbol)

    selector_lower_rank, selector_upper_rank = decoded['selector_interval_summary']
    if selector_lower_rank == selector_upper_rank:
        expected_symbols = ('R' * selector_lower_rank) + ('L' * (build_max_rank() - selector_lower_rank))
    else:
        expected_symbols = (
            ('R' * selector_lower_rank)
            + 'B'
            + ('L' * (build_max_rank() - selector_upper_rank))
        )
    if ''.join(symbols) != expected_symbols:
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
            'width-1 fingerprint is not the expected monotone half-step word'
        )

    return {
        'half_step_selector_index': half_step_selector_index,
        'selector_interval_summary': decoded['selector_interval_summary'],
        'fingerprint_symbols': symbols,
        'fingerprint_word': ''.join(symbols),
        'fingerprint_rows': rows,
        'expected_monotone_word': expected_symbols,
    }


def _build_signature(
    *,
    half_step_selector_index: int,
    realized_intervals: list[dict[str, Any]],
) -> tuple[tuple[str, ...], ...]:
    signature: list[tuple[str, ...]] = []
    for row in realized_intervals:
        selection = select_batch_mean_projection_witness_set_from_half_step_selector_index(
            [build_interval_realizer(row['lower_rank'], row['upper_rank'])],
            half_step_selector_index=half_step_selector_index,
        )
        signature.append(tuple(selection['projected_optimal_state_codes']))
    return tuple(signature)


@lru_cache(maxsize=1)
def build_batch_mean_half_step_selector_index_examples() -> list[dict[str, Any]]:
    source_relax6 = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}
    ]
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

    return [
        {
            'bundle_a': ['S10', 'S10', 'S7'],
            'bundle_a_summary': summarize_preferred_state_codes_by_half_step_selector_index(['S10', 'S10', 'S7']),
            'bundle_b': ['S10', 'S10', 'S10', 'S10', 'S9'],
            'bundle_b_summary': summarize_preferred_state_codes_by_half_step_selector_index(
                ['S10', 'S10', 'S10', 'S10', 'S9']
            ),
            'shared_half_step_selector_index': 0,
            'bundle_a_selection': select_batch_mean_projection_witness_set_from_half_step_selector_index(
                source_relax6,
                half_step_selector_index=0,
            ),
            'bundle_b_selection': select_batch_mean_projection_witness_set_from_half_step_selector_index(
                source_relax6,
                half_step_selector_index=0,
            ),
        },
        {
            'selector_from_three_fifths': summarize_reduced_mean_by_half_step_selector_index(
                reduced_mean_numerator=3,
                reduced_mean_denominator=5,
            ),
            'selector_from_one': summarize_reduced_mean_by_half_step_selector_index(
                reduced_mean_numerator=1,
                reduced_mean_denominator=1,
            ),
            'shared_half_step_selector_index': 2,
            'three_fifths_selection': select_batch_mean_projection_witness_set_from_half_step_selector_index(
                feasible_family,
                half_step_selector_index=2,
            ),
            'one_selection': select_batch_mean_projection_witness_set_from_half_step_selector_index(
                feasible_family,
                half_step_selector_index=2,
            ),
        },
        {
            'decoded_boundary_tie': decode_half_step_selector_index(half_step_selector_index=1),
            'clipped_tie_selection': select_batch_mean_projection_witness_set_from_half_step_selector_index(
                interval_1_3_family,
                half_step_selector_index=1,
            ),
            'width_one_fingerprint': build_width_one_fingerprint(half_step_selector_index=1),
        },
        {
            'decoded_midpath_tie': decode_half_step_selector_index(half_step_selector_index=15),
            'width_one_fingerprint': build_width_one_fingerprint(half_step_selector_index=15),
        },
        {
            'selection_from_half_step_selector_index': select_batch_mean_projection_witness_set_from_half_step_selector_index(
                infeasible_family,
                half_step_selector_index=22,
            ),
        },
    ]


@lru_cache(maxsize=1)
def build_batch_mean_half_step_selector_index_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    selector_validation = build_batch_mean_selector_interval_validation_summary()
    reduced_mean_classes: set[Fraction] = set()
    for width in selector_validation['width_to_reduced_mean_class_count']:
        for preferred_ranks_tuple in combinations_with_replacement(range(build_max_rank() + 1), width):
            reduced_mean_classes.add(Fraction(sum(preferred_ranks_tuple), width))

    half_step_indices = list(range(build_max_half_step_selector_index() + 1))
    selector_intervals = [decode_half_step_selector_index(half_step_selector_index=index)['selector_interval_summary'] for index in half_step_indices]
    if len({tuple(summary) for summary in selector_intervals}) != len(half_step_indices):
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
            'half-step selector index should be bijective with selector intervals'
        )

    reduced_mean_to_half_step_case_count = 0
    half_step_matches_reduced_mean_selection = True
    half_step_matches_rational_bruteforce = True
    for mean_rank in sorted(reduced_mean_classes):
        summary = summarize_reduced_mean_by_half_step_selector_index(
            reduced_mean_numerator=mean_rank.numerator,
            reduced_mean_denominator=mean_rank.denominator,
        )
        for row in realized:
            reduced_mean_to_half_step_case_count += 1
            constraints = [build_interval_realizer(row['lower_rank'], row['upper_rank'])]
            index_selection = select_batch_mean_projection_witness_set_from_half_step_selector_index(
                constraints,
                half_step_selector_index=summary['half_step_selector_index'],
            )
            reduced_mean_selection = select_batch_mean_projection_witness_set_from_reduced_mean(
                constraints,
                reduced_mean_numerator=mean_rank.numerator,
                reduced_mean_denominator=mean_rank.denominator,
            )
            if index_selection['projected_optimal_state_codes'] != reduced_mean_selection['projected_optimal_state_codes']:
                half_step_matches_reduced_mean_selection = False
                raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
                    'half-step selector index selection mismatch against reduced mean selection'
                )
            interval_ranks = list(range(row['lower_rank'], row['upper_rank'] + 1))
            brute_l2_costs = {rank: (rank - mean_rank) ** 2 for rank in interval_ranks}
            minimum_cost = min(brute_l2_costs.values())
            brute_argmin = [rank for rank, cost in brute_l2_costs.items() if cost == minimum_cost]
            selected_ranks = list(
                range(
                    index_selection['projected_optimal_interval']['lower_rank'],
                    index_selection['projected_optimal_interval']['upper_rank'] + 1,
                )
            )
            if selected_ranks != brute_argmin:
                half_step_matches_rational_bruteforce = False
                raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
                    'half-step selector index selection mismatch against rational brute-force argmin'
                )

    full_signatures = {
        index: _build_signature(half_step_selector_index=index, realized_intervals=realized)
        for index in half_step_indices
    }
    full_signature_count = len(set(full_signatures.values()))
    if full_signature_count != len(half_step_indices):
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
            'distinct half-step selector indices should remain behaviorally distinct over realized intervals'
        )

    adjacent_realized = [
        {'lower_rank': rank, 'upper_rank': rank + 1}
        for rank in range(build_max_rank())
    ]
    adjacent_signatures = {
        index: _build_signature(half_step_selector_index=index, realized_intervals=adjacent_realized)
        for index in half_step_indices
    }
    adjacent_signature_count = len(set(adjacent_signatures.values()))
    if adjacent_signature_count != len(half_step_indices):
        raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
            'adjacent width-1 intervals should separate all half-step selector indices'
        )

    every_omitted_adjacent_interval_breaks_separation = True
    for omitted_rank in range(build_max_rank()):
        subset = [row for row in adjacent_realized if row['lower_rank'] != omitted_rank]
        subset_signatures = {
            index: _build_signature(half_step_selector_index=index, realized_intervals=subset)
            for index in half_step_indices
        }
        if len(set(subset_signatures.values())) == len(half_step_indices):
            every_omitted_adjacent_interval_breaks_separation = False
            raise WeakeningPortfolioServiceModeSuffixBatchMeanHalfStepSelectorIndexLawError(
                'every proper 15-interval subset of adjacent width-1 intervals should fail to separate at least one class pair'
            )

    fingerprint_examples = {
        'boundary_singleton_index_0': build_width_one_fingerprint(half_step_selector_index=0)['fingerprint_word'],
        'interior_singleton_index_14': build_width_one_fingerprint(half_step_selector_index=14)['fingerprint_word'],
        'interior_tie_index_15': build_width_one_fingerprint(half_step_selector_index=15)['fingerprint_word'],
        'boundary_singleton_index_32': build_width_one_fingerprint(half_step_selector_index=32)['fingerprint_word'],
    }

    return {
        'validated_realized_interval_count': len(realized),
        'validated_reduced_mean_class_count': len(reduced_mean_classes),
        'validated_half_step_selector_index_class_count': len(half_step_indices),
        'half_step_selector_index_range': [0, build_max_half_step_selector_index()],
        'singleton_even_index_count': sum(1 for index in half_step_indices if index % 2 == 0),
        'adjacent_tie_odd_index_count': sum(1 for index in half_step_indices if index % 2 == 1),
        'reduced_mean_to_half_step_selector_index_validation_case_count': reduced_mean_to_half_step_case_count,
        'half_step_selector_index_matches_reduced_mean_selection': half_step_matches_reduced_mean_selection,
        'half_step_selector_index_matches_rational_bruteforce_l2_argmin': half_step_matches_rational_bruteforce,
        'one_integer_code_is_bijective_with_selector_interval_classes': True,
        'distinct_behavioral_signature_count_over_all_realized_intervals': full_signature_count,
        'selector_classes_are_behaviorally_irreducible_over_all_realized_intervals': True,
        'adjacent_width_one_interval_count': len(adjacent_realized),
        'distinct_behavioral_signature_count_over_adjacent_width_one_intervals': adjacent_signature_count,
        'adjacent_width_one_intervals_form_a_complete_separating_family': True,
        'adjacent_width_one_intervals_are_minimal_by_single_omission': every_omitted_adjacent_interval_breaks_separation,
        'monotone_width_one_fingerprint_examples': fingerprint_examples,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_mean_half_step_selector_index_validation_summary()
    return {
        'path_l2_selector_classes_can_be_keyed_by_one_half_step_integer': validation[
            'validated_half_step_selector_index_class_count'
        ],
        'one_integer_code_is_bijective_with_the_33_selector_interval_classes': validation[
            'one_integer_code_is_bijective_with_selector_interval_classes'
        ],
        'selector_classes_remain_behaviorally_irreducible_over_realized_intervals': validation[
            'selector_classes_are_behaviorally_irreducible_over_all_realized_intervals'
        ],
        'adjacent_width_one_intervals_form_a_minimal_complete_separating_family': [
            validation['adjacent_width_one_interval_count'],
            validation['distinct_behavioral_signature_count_over_adjacent_width_one_intervals'],
        ],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'If only path-L2 witness choice matters, store the selector class as one integer half_step_selector_index = selector_lower_rank + selector_upper_rank.',
        'Decode even indices 2k as singleton selector intervals [k, k] and odd indices 2k+1 as adjacent tie selectors [k, k+1].',
        'Recover the feasible witness set by decoding the half-step selector index back to its selector interval and projecting that interval onto the feasible overlap interval.',
        'Use the width-1 adjacent feasible intervals [0,1] through [15,16] as a compact regression basis: together they separate all 33 selector classes, but omitting any one of them merges at least one pair.',
        'Expect the width-1 fingerprint to be a monotone ternary word: singleton classes are R^kL^(16-k) and tie classes are R^kBL^(15-k), where R picks the upper endpoint, L the lower endpoint, and B both endpoints.',
        'Do not use the half-step selector index to reconstruct exact mean magnitude, bundle width, or any non-L2 downstream quantity; it is only a witness-selection key.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_mean_half_step_selector_index_snapshot() -> dict[str, Any]:
    return {
        'focus': 'One-integer half-step selector keys for batch L2 witness choice on feasible bounded positive-service local weakening families',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'selection_examples': build_batch_mean_half_step_selector_index_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_mean_half_step_selector_index_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
