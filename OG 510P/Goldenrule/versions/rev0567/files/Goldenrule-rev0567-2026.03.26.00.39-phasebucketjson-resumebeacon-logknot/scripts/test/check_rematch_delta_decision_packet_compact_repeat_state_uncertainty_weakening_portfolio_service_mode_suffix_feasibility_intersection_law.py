#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_family_examples,
    build_feasibility_intersection_validation_summary,
    build_service_mode_suffix_feasibility_intersection_snapshot,
    select_constraint_family_intersection,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_feasibility_intersection_validation_summary()
    snapshot = build_service_mode_suffix_feasibility_intersection_snapshot()

    _assert_equal(validation['catalog_interval_count'], 153, 'catalog interval count mismatch')
    _assert_equal(validation['expected_closed_interval_count'], 153, 'expected interval count mismatch')
    _assert_equal(validation['realized_bounded_window_interval_count'], 153, 'realized interval count mismatch')
    _assert_equal(validation['all_closed_rank_intervals_realized'], True, 'closed interval realization mismatch')
    _assert_equal(validation['pair_validation_count'], 11628, 'pair validation count mismatch')
    _assert_equal(validation['infeasible_pair_count'], 3876, 'infeasible pair count mismatch')
    _assert_equal(validation['triple_validation_count'], 585276, 'triple validation count mismatch')
    _assert_equal(validation['pairwise_overlap_implies_global_feasibility_for_all_triples'], True, 'triple Helly mismatch')

    feasible = select_constraint_family_intersection([
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ])
    _assert_equal(feasible['feasible'], True, 'feasible family status mismatch')
    _assert_equal(feasible['pairwise_overlap'], True, 'feasible family pairwise overlap mismatch')
    _assert_equal(feasible['witness_state_codes'], ['S8', 'S7'], 'feasible family witness mismatch')
    _assert_equal(feasible['intersection_cardinality'], 2, 'feasible family intersection size mismatch')

    singleton = select_constraint_family_intersection([
        {'constraint_label': 'share_0_02', 'state_code': 'D2', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'tail_exact', 'state_code': 'E1', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'singleton_s2', 'state_code': 'S2', 'max_forward_steps': 0, 'max_backward_steps': 0},
    ])
    _assert_equal(singleton['feasible'], True, 'singleton family status mismatch')
    _assert_equal(singleton['witness_state_codes'], ['S2'], 'singleton witness mismatch')

    infeasible = select_constraint_family_intersection([
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ])
    _assert_equal(infeasible['feasible'], False, 'infeasible family status mismatch')
    _assert_equal(infeasible['pairwise_overlap'], False, 'infeasible family pairwise overlap mismatch')
    _assert_equal(infeasible['blocker_certificate']['left_interval_key'], '[15,16]', 'infeasible blocker left interval mismatch')
    _assert_equal(infeasible['blocker_certificate']['right_interval_key'], '[2,5]', 'infeasible blocker right interval mismatch')
    _assert_equal(infeasible['blocker_certificate']['gap_size_in_rank_units'], 9, 'infeasible blocker gap mismatch')

    examples = build_family_examples()
    _assert_equal([row['feasible'] for row in examples], [True, True, False], 'family example feasibility pattern mismatch')
    _assert_equal(snapshot['headline_findings']['validation_summary']['catalog_interval_count'], 153, 'snapshot interval count mismatch')

    print('ok')


if __name__ == '__main__':
    main()
