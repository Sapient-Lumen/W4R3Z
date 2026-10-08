#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law import (
    build_service_mode_suffix_feasible_witness_selector_snapshot,
    build_witness_selector_examples,
    build_witness_selector_validation_summary,
    select_feasible_witness,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_witness_selector_validation_summary()
    snapshot = build_service_mode_suffix_feasible_witness_selector_snapshot()

    _assert_equal(validation['realized_interval_count'], 153, 'realized interval count mismatch')
    _assert_equal(validation['nearest_projection_validation_count'], 2601, 'nearest projection validation count mismatch')
    _assert_equal(validation['earliest_latest_validation_count'], 153, 'earliest/latest validation count mismatch')
    _assert_equal(validation['lower_median_validation_count'], 153, 'lower median validation count mismatch')
    _assert_equal(validation['upper_median_validation_count'], 153, 'upper median validation count mismatch')
    _assert_equal(validation['all_feasible_nearest_witnesses_match_interval_clamp'], True, 'nearest clamp law mismatch')
    _assert_equal(validation['infeasible_selection_stays_blocked'], True, 'infeasible carry-forward mismatch')

    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    earliest = select_feasible_witness(feasible_family, policy='earliest')
    _assert_equal(earliest['selected_state_code'], 'S8', 'earliest witness mismatch')
    latest = select_feasible_witness(feasible_family, policy='latest')
    _assert_equal(latest['selected_state_code'], 'S7', 'latest witness mismatch')
    toward_source = select_feasible_witness(feasible_family, policy='nearest_preferred', preferred_state_code='S10')
    _assert_equal(toward_source['selected_state_code'], 'S8', 'source projection mismatch')
    _assert_equal(toward_source['selection_certificate']['projection_distance_in_rank_units'], 3, 'source projection distance mismatch')
    toward_terminal = select_feasible_witness(feasible_family, policy='nearest_preferred', preferred_state_code='T0')
    _assert_equal(toward_terminal['selected_state_code'], 'S7', 'terminal projection mismatch')
    _assert_equal(toward_terminal['selection_certificate']['projection_distance_in_rank_units'], 12, 'terminal projection distance mismatch')

    singleton_family = [
        {'constraint_label': 'share_0_02', 'state_code': 'D2', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'tail_exact', 'state_code': 'E1', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'singleton_s2', 'state_code': 'S2', 'max_forward_steps': 0, 'max_backward_steps': 0},
    ]
    singleton = select_feasible_witness(singleton_family, policy='nearest_preferred', preferred_state_code='E1')
    _assert_equal(singleton['selected_state_code'], 'S2', 'singleton witness mismatch')
    _assert_equal(singleton['selected_source_rank'], 12, 'singleton witness rank mismatch')

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    infeasible = select_feasible_witness(infeasible_family, policy='nearest_preferred', preferred_state_code='S8')
    _assert_equal(infeasible['selection_status'], 'infeasible', 'infeasible status mismatch')
    _assert_equal(infeasible['selection_certificate']['blocker_certificate']['gap_size_in_rank_units'], 9, 'infeasible gap mismatch')

    examples = build_witness_selector_examples()
    _assert_equal([row['selection_status'] for row in examples], ['selected', 'selected', 'selected', 'selected', 'selected', 'infeasible'], 'example status pattern mismatch')
    _assert_equal(snapshot['headline_findings']['validation_summary']['nearest_projection_validation_count'], 2601, 'snapshot validation count mismatch')

    print('ok')


if __name__ == '__main__':
    main()
