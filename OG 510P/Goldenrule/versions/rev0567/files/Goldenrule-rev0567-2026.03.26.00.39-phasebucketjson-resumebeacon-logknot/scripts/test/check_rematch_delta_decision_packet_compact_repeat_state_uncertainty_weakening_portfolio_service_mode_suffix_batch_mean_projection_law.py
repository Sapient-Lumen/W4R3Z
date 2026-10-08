#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    build_batch_mean_projection_examples,
    build_batch_mean_projection_validation_summary,
    build_service_mode_suffix_batch_mean_projection_snapshot,
    select_batch_mean_projection_witness_set,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_mean_projection_validation_summary()
    snapshot = build_service_mode_suffix_batch_mean_projection_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'validated realized interval count mismatch')
    _assert_equal(validation['validated_preference_bundle_widths'], [1, 2, 3, 4, 5], 'validated widths mismatch')
    _assert_equal(validation['validation_case_count'], 1438353, 'validation case count mismatch')
    _assert_equal(validation['unique_optimum_count'], 1393381, 'unique optimum count mismatch')
    _assert_equal(validation['tie_interval_count'], 44972, 'tie interval count mismatch')
    _assert_equal(validation['odd_width_tie_count'], 0, 'odd width tie count mismatch')
    _assert_equal(validation['even_width_tie_count'], 44972, 'even width tie count mismatch')
    _assert_equal(validation['max_tie_cardinality_by_preference_count'], {2: 2, 4: 2}, 'max tie cardinality mismatch')
    _assert_equal(validation['projected_mean_interval_matches_bruteforce_argmin'], True, 'batch mean law mismatch')
    _assert_equal(validation['all_ties_come_from_even_preference_widths'], True, 'tie parity law mismatch')
    _assert_equal(validation['ties_never_exceed_two_adjacent_states'], True, 'adjacent tie bound mismatch')
    _assert_equal(validation['same_as_l1_count'], 879793, 'same-as-l1 count mismatch')
    _assert_equal(validation['differs_from_l1_count'], 558560, 'differs-from-l1 count mismatch')
    _assert_equal(validation['differing_case_count_by_preference_width'], {2: 11504, 3: 34800, 4: 195154, 5: 317102}, 'difference-by-width mismatch')
    _assert_equal(validation['l1_tie_interval_count'], 207536, 'l1 tie count mismatch')
    _assert_equal(validation['both_l1_and_l2_tie_count'], 43116, 'shared tie count mismatch')
    _assert_equal(validation['l2_tie_reduction_against_l1'], 162564, 'tie reduction mismatch')
    _assert_equal(validation['infeasible_batch_projection_stays_blocked'], True, 'infeasible batch carry-forward mismatch')

    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    odd_bundle = select_batch_mean_projection_witness_set(feasible_family, preferred_state_codes=['S10', 'E8', 'S7'])
    _assert_equal(odd_bundle['projected_optimal_state_codes'], ['S8'], 'odd bundle optimum mismatch')
    even_bundle = select_batch_mean_projection_witness_set(feasible_family, preferred_state_codes=['E8', 'S6'])
    _assert_equal(even_bundle['projected_optimal_state_codes'], ['S8', 'S7'], 'even bundle tie interval mismatch')
    _assert_equal(even_bundle['selection_certificate']['half_integer_tie'], True, 'half-integer tie flag mismatch')

    singleton_family = [
        {'constraint_label': 'share_0_02', 'state_code': 'D2', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'tail_exact', 'state_code': 'E1', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'singleton_s2', 'state_code': 'S2', 'max_forward_steps': 0, 'max_backward_steps': 0},
    ]
    clipped = select_batch_mean_projection_witness_set(singleton_family, preferred_state_codes=['S10', 'S8', 'S7', 'S6'])
    _assert_equal(clipped['projected_optimal_state_codes'], ['S2'], 'lower-bound clamp mismatch')
    _assert_equal(clipped['selection_certificate']['projection_case'], 'clamp_to_lower_boundary', 'lower-bound clamp case mismatch')

    skewed_interval = select_batch_mean_projection_witness_set(
        [{'constraint_label': '0_2', 'state_code': 'S10', 'max_forward_steps': 2, 'max_backward_steps': 0}],
        preferred_state_codes=['S10', 'S9', 'S7'],
    )
    _assert_equal(skewed_interval['projected_optimal_state_codes'], ['E8'], 'skewed l2 optimum mismatch')

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    infeasible = select_batch_mean_projection_witness_set(infeasible_family, preferred_state_codes=['S8', 'E5', 'T0'])
    _assert_equal(infeasible['selection_status'], 'infeasible', 'infeasible batch status mismatch')
    _assert_equal(infeasible['selection_certificate']['blocker_certificate']['gap_size_in_rank_units'], 9, 'infeasible batch gap mismatch')

    examples = build_batch_mean_projection_examples()
    _assert_equal([row['selection_status'] for row in examples], ['selected', 'selected', 'selected', 'selected', 'infeasible'], 'example status pattern mismatch')
    _assert_equal(snapshot['headline_findings']['validation_summary']['validation_case_count'], 1438353, 'snapshot validation case count mismatch')

    print('ok')


if __name__ == '__main__':
    main()
