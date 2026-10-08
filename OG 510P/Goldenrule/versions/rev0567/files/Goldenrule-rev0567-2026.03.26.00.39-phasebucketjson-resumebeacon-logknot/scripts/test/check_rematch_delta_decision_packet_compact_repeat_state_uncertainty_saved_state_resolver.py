#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver import (
    decide_saved_state_resolution,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')


def main() -> None:
    cases = [
        {
            'label': 'anchor_hold',
            'input': dict(
                current_dwell_unique_appends=13,
                required_gain_share_floor='0.95',
                max_hard_cap_budget_inclusive=5,
                minimum_anchor_slack_unique_appends=2,
                minimum_band_width_unique_appends=4,
                max_pre_amortization_checkpoint_budget_inclusive=8,
            ),
            'expected_status': 'hold_current_anchor',
            'expected_action': 'hold',
            'expected_route': None,
        },
        {
            'label': 'boundary_stabilize',
            'input': dict(
                current_dwell_unique_appends=8,
                required_gain_share_floor='0.95',
                max_hard_cap_budget_inclusive=5,
                minimum_anchor_slack_unique_appends=2,
                minimum_band_width_unique_appends=4,
                max_pre_amortization_checkpoint_budget_inclusive=8,
            ),
            'expected_status': 'stabilize_current_band',
            'expected_action': 'stabilize',
            'expected_route': [8, 13],
        },
        {
            'label': 'direct_strengthen_from_boundary',
            'input': dict(
                current_dwell_unique_appends=19,
                required_gain_share_floor='0.99',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
            ),
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'strengthen',
            'expected_route': [19, 2],
        },
        {
            'label': 'weaken_from_boundary',
            'input': dict(
                current_dwell_unique_appends=18,
                required_gain_share_floor='0.84',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
            ),
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'weaken',
            'expected_route': [18, 19, 25],
        },
        {
            'label': 'oracle_blocker_preserved',
            'input': dict(
                current_dwell_unique_appends=18,
                required_gain_share_floor='0.99',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=1,
                minimum_band_width_unique_appends=1,
                master_calendar_pre_registered=True,
            ),
            'expected_status': 'no_saved_state_resolution',
            'expected_action': 'infeasible',
            'expected_route': None,
            'expected_blocker': 'high_floor_positive_slack_conflict',
        },
    ]

    for case in cases:
        decision = decide_saved_state_resolution(**case['input'])
        _assert_equal(decision['status'], case['expected_status'], f"{case['label']} status")
        _assert_equal(decision['action_family'], case['expected_action'], f"{case['label']} action")
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        _assert_equal(route, case['expected_route'], f"{case['label']} route")
        if 'expected_blocker' in case:
            _assert_equal(decision['blocking_summary'], case['expected_blocker'], f"{case['label']} blocker")

    # Default floor-only matrix should contain 3 holds, 3 stabilizations, 5 weakenings, and 7 strengthenings.
    action_counts = {'hold': 0, 'stabilize': 0, 'weaken': 0, 'strengthen': 0}
    for current_dwell in [2, 8, 13, 18, 19, 25]:
        for floor in ['0.84', '0.95', '0.99']:
            decision = decide_saved_state_resolution(
                current_dwell_unique_appends=current_dwell,
                required_gain_share_floor=floor,
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
            )
            action_counts[decision['action_family']] += 1

    _assert_equal(action_counts, {'hold': 3, 'stabilize': 3, 'weaken': 5, 'strengthen': 7}, 'default action counts')
    print('saved-state resolver checks passed')


if __name__ == '__main__':
    main()
