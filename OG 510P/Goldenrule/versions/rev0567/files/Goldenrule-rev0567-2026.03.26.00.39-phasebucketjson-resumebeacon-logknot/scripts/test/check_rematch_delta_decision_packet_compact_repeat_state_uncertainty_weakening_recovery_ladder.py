#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder import (
    base_weakening_cases,
    build_threshold_band_progression,
    build_weakening_recovery_ladder_snapshot,
)



def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    base_cases = base_weakening_cases()
    _assert_equal(len(base_cases), 5, 'base weakening case count')
    _assert_equal(
        [case['one_shot_shift_unique_appends'] for case in base_cases],
        [7, 11, 12, 17, 23],
        'base weakening one-shot shifts',
    )

    report = build_weakening_recovery_ladder_snapshot()
    _assert_equal(report['headline_findings']['serial_recovery'], True, 'serial recovery flag')
    _assert_equal(
        report['headline_findings']['recovery_breakpoints_unique_appends'],
        [7, 11, 12, 17, 23],
        'recovery breakpoints',
    )
    _assert_equal(
        report['headline_findings']['recovered_case_counts_by_threshold_band'],
        {'0–6': 0, '7–10': 1, '11–11': 2, '12–16': 3, '17–22': 4, '23–∞': 5},
        'recovered case counts by threshold band',
    )
    _assert_equal(
        report['headline_findings']['remaining_deferred_case_counts_by_threshold_band'],
        {'0–6': 5, '7–10': 4, '11–11': 3, '12–16': 2, '17–22': 1, '23–∞': 0},
        'remaining deferred case counts by threshold band',
    )
    _assert_equal(
        report['headline_findings']['recovery_kinds_in_order'],
        [
            'suffix_only_relaxed_release',
            'middle_band_precision_relief',
            'neutral_anchor_relaxed_release',
            'direct_entry_boundary_relaxed_release',
            'direct_precision_relaxed_release',
        ],
        'recovery kinds in order',
    )

    progression = build_threshold_band_progression()
    _assert_equal(len(progression), 6, 'threshold band progression length')
    _assert_equal(progression[0]['newly_recovered_cases'], [], 'lowest band should recover nothing')
    _assert_equal(progression[-1]['remaining_deferred_case_count'], 0, 'highest band should defer nothing')
    _assert_equal(progression[1]['newly_recovered_cases'], [{'current_state_unique_appends': 18, 'required_gain_share_floor': '0.84'}], 'threshold 7 newly recovered case')
    _assert_equal(progression[2]['newly_recovered_cases'], [{'current_state_unique_appends': 2, 'required_gain_share_floor': '0.95'}], 'threshold 11 newly recovered case')
    _assert_equal(progression[3]['newly_recovered_cases'], [{'current_state_unique_appends': 13, 'required_gain_share_floor': '0.84'}], 'threshold 12 newly recovered case')
    _assert_equal(progression[4]['newly_recovered_cases'], [{'current_state_unique_appends': 8, 'required_gain_share_floor': '0.84'}], 'threshold 17 newly recovered case')
    _assert_equal(progression[5]['newly_recovered_cases'], [{'current_state_unique_appends': 2, 'required_gain_share_floor': '0.84'}], 'threshold 23 newly recovered case')

    print('weakening recovery ladder checks passed')


if __name__ == '__main__':
    main()
