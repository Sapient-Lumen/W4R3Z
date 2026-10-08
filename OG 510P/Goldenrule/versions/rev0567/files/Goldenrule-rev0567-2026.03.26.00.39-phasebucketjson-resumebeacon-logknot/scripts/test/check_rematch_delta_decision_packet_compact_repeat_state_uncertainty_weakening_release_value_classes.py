#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes import (
    build_marginal_release_steps,
    build_value_classes,
    build_weakening_release_value_classes_snapshot,
)



def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    steps = build_marginal_release_steps()
    _assert_equal(len(steps), 5, 'marginal release step count')
    _assert_equal([row['budget_step'] for row in steps], [1, 2, 3, 4, 5], 'budget steps')
    _assert_equal([row['threshold_unique_appends'] for row in steps], [7, 11, 12, 17, 23], 'thresholds')
    _assert_equal([row['released_route_shift_unique_appends'] for row in steps], [7, 11, 12, 17, 23], 'route shifts')
    _assert_equal(
        [row['value_class_label'] for row in steps],
        [
            'relaxed_suffix_savings_bundle',
            'middle_precision_relief_bundle',
            'relaxed_suffix_savings_bundle',
            'relaxed_suffix_savings_bundle',
            'full_precision_relaxed_release_bundle',
        ],
        'value class sequence',
    )

    value_classes = build_value_classes()
    _assert_equal(len(value_classes), 3, 'value class count')
    repeated = value_classes[0]
    _assert_equal(repeated['value_class_label'], 'relaxed_suffix_savings_bundle', 'repeated value class label')
    _assert_equal(repeated['member_budget_steps'], [1, 3, 4], 'repeated value class budget steps')
    _assert_equal(repeated['member_route_shifts_unique_appends'], [7, 12, 17], 'repeated value class route shifts')
    _assert_equal(repeated['member_thresholds_unique_appends'], [7, 12, 17], 'repeated value class thresholds')
    _assert_equal(repeated['recovered_steady_state_savings_vector'], {
        'exact_hard_cap_units': 2,
        'mode_specific_checkpoint_units': 3,
        'minimum_anchor_slack_units': 1,
        'exact_dwell_band_width_units': 3,
    }, 'repeated value class savings vector')
    _assert_equal(repeated['is_shift_ordered_within_class'], True, 'repeated value class shift ordering')

    report = build_weakening_release_value_classes_snapshot()
    _assert_equal(report['headline_findings']['release_value_class_count'], 3, 'headline value class count')
    _assert_equal(report['headline_findings']['repeated_value_class_label'], 'relaxed_suffix_savings_bundle', 'headline repeated class')
    _assert_equal(report['headline_findings']['repeated_value_class_budget_steps'], [1, 3, 4], 'headline repeated budget steps')
    _assert_equal(report['headline_findings']['repeated_value_class_is_cheapest_shift_first'], True, 'headline repeated shift ordering')

    print('weakening release value classes checks passed')


if __name__ == '__main__':
    main()
