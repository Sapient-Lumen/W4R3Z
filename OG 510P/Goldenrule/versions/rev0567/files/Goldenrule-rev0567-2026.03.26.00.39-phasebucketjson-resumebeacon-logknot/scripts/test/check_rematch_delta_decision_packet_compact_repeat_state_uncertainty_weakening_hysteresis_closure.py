#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure import (
    build_floor_relaxation_release_table,
    build_threshold_closure_matrix,
    simulate_persistent_request_under_fixed_weakening_threshold,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    staged = simulate_persistent_request_under_fixed_weakening_threshold(
        current_dwell_unique_appends=8,
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=12,
    )
    _assert_equal(staged['final_state_unique_appends'], 25, 'threshold 12 final anchor from 8 at relaxed floor')
    _assert_equal(staged['settled_after_cycles'], 3, 'threshold 12 cycles from 8 at relaxed floor')
    _assert_equal([step['action_family'] for step in staged['sequence']], ['stabilize', 'weaken', 'hold'], 'threshold 12 action chain')

    direct = simulate_persistent_request_under_fixed_weakening_threshold(
        current_dwell_unique_appends=8,
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=17,
    )
    _assert_equal(direct['final_state_unique_appends'], 25, 'threshold 17 final anchor from 8 at relaxed floor')
    _assert_equal(direct['settled_after_cycles'], 2, 'threshold 17 cycles from 8 at relaxed floor')
    _assert_equal([step['action_family'] for step in direct['sequence']], ['weaken', 'hold'], 'threshold 17 action chain')

    sticky_precision = simulate_persistent_request_under_fixed_weakening_threshold(
        current_dwell_unique_appends=2,
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=11,
    )
    _assert_equal(sticky_precision['final_state_unique_appends'], 2, 'threshold 11 keeps precision under relaxed floor')
    _assert_equal(sticky_precision['settled_after_cycles'], 1, 'threshold 11 precision cycles')

    full_release = simulate_persistent_request_under_fixed_weakening_threshold(
        current_dwell_unique_appends=2,
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=23,
    )
    _assert_equal(full_release['final_state_unique_appends'], 25, 'threshold 23 releases precision under relaxed floor')
    _assert_equal([step['action_family'] for step in full_release['sequence']], ['weaken', 'hold'], 'threshold 23 precision chain')

    release_table = {row['current_state_unique_appends']: row for row in build_floor_relaxation_release_table()}
    expected_eventual = {2: 23, 8: 12, 13: 12, 18: 7, 19: 0, 25: 0}
    expected_direct = {2: 23, 8: 17, 13: 12, 18: 7, 19: 0, 25: 0}
    _assert_equal(
        {state: row['minimum_threshold_for_eventual_relaxed_anchor'] for state, row in release_table.items()},
        expected_eventual,
        'eventual relaxed thresholds',
    )
    _assert_equal(
        {state: row['minimum_threshold_for_direct_relaxed_anchor'] for state, row in release_table.items()},
        expected_direct,
        'direct relaxed thresholds',
    )

    closure_bands = {row['threshold_band_label']: row for row in build_threshold_closure_matrix()}
    _assert_equal(closure_bands['0–6']['final_anchor_counts'], {'2': 8, '13': 8, '25': 2}, 'lowest threshold final anchor counts')
    _assert_equal(closure_bands['12–16']['final_anchor_counts'], {'2': 7, '13': 6, '25': 5}, 'threshold 12-16 final anchor counts')
    _assert_equal(closure_bands['12–16']['max_cycles_to_settle'], 3, 'threshold 12-16 max cycles')
    _assert_equal(closure_bands['17–22']['final_anchor_counts'], {'2': 7, '13': 6, '25': 5}, 'threshold 17-22 final anchor counts')
    _assert_equal(closure_bands['17–22']['max_cycles_to_settle'], 2, 'threshold 17-22 max cycles')
    _assert_equal(closure_bands['23–∞']['final_anchor_counts'], {'2': 6, '13': 6, '25': 6}, 'highest threshold final anchor counts')

    print('weakening hysteresis closure checks passed')


if __name__ == '__main__':
    main()
