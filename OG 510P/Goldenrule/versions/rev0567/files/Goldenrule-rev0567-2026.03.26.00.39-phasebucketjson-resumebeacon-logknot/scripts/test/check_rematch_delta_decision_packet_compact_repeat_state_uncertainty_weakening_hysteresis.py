#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis import (
    decide_saved_state_with_weakening_hysteresis,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')


def main() -> None:
    cases = [
        {
            'label': 'defer_anchor_weakening',
            'input': dict(
                current_dwell_unique_appends=13,
                required_gain_share_floor='0.84',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
                max_forced_weakening_shift_unique_appends=10,
            ),
            'expected_status': 'defer_weakening_keep_current_anchor',
            'expected_action': 'hold',
            'expected_route': None,
            'expected_deferred': True,
            'expected_avoided_shift': 12,
        },
        {
            'label': 'defer_boundary_weakening_into_stabilize',
            'input': dict(
                current_dwell_unique_appends=8,
                required_gain_share_floor='0.84',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
                max_forced_weakening_shift_unique_appends=10,
            ),
            'expected_status': 'defer_weakening_stabilize_current_stronger_band',
            'expected_action': 'stabilize',
            'expected_route': [8, 13],
            'expected_deferred': True,
            'expected_avoided_shift': 17,
        },
        {
            'label': 'allow_smallest_weakening',
            'input': dict(
                current_dwell_unique_appends=18,
                required_gain_share_floor='0.84',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
                max_forced_weakening_shift_unique_appends=10,
            ),
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'weaken',
            'expected_route': [18, 19, 25],
            'expected_deferred': False,
            'expected_avoided_shift': 0,
        },
        {
            'label': 'mandatory_strengthening_ignores_overlay',
            'input': dict(
                current_dwell_unique_appends=25,
                required_gain_share_floor='0.95',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
                max_forced_weakening_shift_unique_appends=0,
            ),
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'strengthen',
            'expected_route': [25, 18, 13],
            'expected_deferred': False,
            'expected_avoided_shift': 0,
        },
        {
            'label': 'infeasible_request_preserved',
            'input': dict(
                current_dwell_unique_appends=18,
                required_gain_share_floor='0.99',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=1,
                minimum_band_width_unique_appends=1,
                master_calendar_pre_registered=True,
                max_forced_weakening_shift_unique_appends=0,
            ),
            'expected_status': 'no_saved_state_resolution',
            'expected_action': 'infeasible',
            'expected_route': None,
            'expected_deferred': False,
            'expected_avoided_shift': 0,
        },
    ]

    for case in cases:
        decision = decide_saved_state_with_weakening_hysteresis(**case['input'])
        _assert_equal(decision['status'], case['expected_status'], f"{case['label']} status")
        _assert_equal(decision['action_family'], case['expected_action'], f"{case['label']} action")
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        _assert_equal(route, case['expected_route'], f"{case['label']} route")
        _assert_equal(decision['deferred_weaken'], case['expected_deferred'], f"{case['label']} deferred flag")
        _assert_equal(decision['avoided_one_shot_shift_unique_appends'], case['expected_avoided_shift'], f"{case['label']} avoided shift")

    threshold_counts = {}
    for threshold in [0, 7, 11, 12, 17, 23]:
        action_counts = {'hold': 0, 'stabilize': 0, 'weaken': 0, 'strengthen': 0}
        for current_dwell in [2, 8, 13, 18, 19, 25]:
            for floor in ['0.84', '0.95', '0.99']:
                decision = decide_saved_state_with_weakening_hysteresis(
                    current_dwell_unique_appends=current_dwell,
                    required_gain_share_floor=floor,
                    max_hard_cap_budget_inclusive=11,
                    minimum_anchor_slack_unique_appends=0,
                    minimum_band_width_unique_appends=1,
                    max_pre_amortization_checkpoint_budget_inclusive=14,
                    max_forced_weakening_shift_unique_appends=threshold,
                )
                action_counts[decision['action_family']] += 1
        threshold_counts[threshold] = action_counts

    _assert_equal(
        threshold_counts,
        {
            0: {'hold': 6, 'stabilize': 5, 'weaken': 0, 'strengthen': 7},
            7: {'hold': 6, 'stabilize': 4, 'weaken': 1, 'strengthen': 7},
            11: {'hold': 5, 'stabilize': 4, 'weaken': 2, 'strengthen': 7},
            12: {'hold': 4, 'stabilize': 4, 'weaken': 3, 'strengthen': 7},
            17: {'hold': 4, 'stabilize': 3, 'weaken': 4, 'strengthen': 7},
            23: {'hold': 3, 'stabilize': 3, 'weaken': 5, 'strengthen': 7},
        },
        'threshold action counts',
    )
    print('weakening hysteresis checks passed')


if __name__ == '__main__':
    main()
