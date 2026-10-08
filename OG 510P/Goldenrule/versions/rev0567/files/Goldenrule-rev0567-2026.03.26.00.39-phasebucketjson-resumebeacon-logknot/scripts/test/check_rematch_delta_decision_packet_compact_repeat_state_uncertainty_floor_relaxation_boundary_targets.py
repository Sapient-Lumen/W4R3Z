#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    rows = {
        (row['start_region_label'], row['start_required_gain_share_floor_interval'], row['weakened_required_gain_share_floor_interval']): row
        for row in report['relaxation_boundary_rows']
    }
    examples = {row['example_label']: row for row in report['examples']}

    assert findings['all_one_notch_floor_relaxations_reduce_to_boundary_targets'] is True
    assert findings['unique_boundary_targets_for_one_notch_relaxations_unique_appends'] == [8, 19]
    assert findings['boundary_target_count_for_one_notch_relaxations'] == 2
    assert findings['post_precision_widening_target_unique_appends'] == 8
    assert findings['post_neutral_widening_target_unique_appends'] == 19
    assert findings['newly_unlocked_support_points_across_one_notch_relaxations_unique_appends'] == 25
    assert findings['compressed_one_notch_relaxation_target_set_points_unique_appends'] == 2
    assert findings['precision_relaxation_first_lands_on_neutral_boundary_not_interior'] is True
    assert findings['near_optimal_relaxation_first_lands_on_relaxed_suffix_boundary_not_interior'] is True
    assert findings['full_relaxation_from_precision_still_starts_at_boundary_8'] is True

    precision = rows[('{2}', '(0.980481, 0.999822]', '(0.870482, 0.980481]')]
    assert precision['nearest_newly_unlocked_support_boundary_target_unique_appends'] == 8
    assert precision['nearest_newly_unlocked_support_boundary_target_region'] == '[8, 18]'
    assert precision['minimal_right_shift_interval_unique_appends'] == [6, 6]
    assert precision['representative_anchor_jump_unique_appends'] == [2, 8]
    assert precision['dominated_interior_search_interval_unique_appends'] == [9, 18]
    assert precision['newly_unlocked_support_count_unique_appends'] == 11

    neutral = rows[('[8, 18]', '(0.870482, 0.980481]', '[0, 0.870482]')]
    assert neutral['nearest_newly_unlocked_support_boundary_target_unique_appends'] == 19
    assert neutral['nearest_newly_unlocked_support_boundary_target_region'] == '[19, 32]'
    assert neutral['minimal_right_shift_interval_unique_appends'] == [1, 11]
    assert neutral['representative_anchor_jump_unique_appends'] == [13, 19]
    assert neutral['dominated_interior_search_interval_unique_appends'] == [20, 32]
    assert neutral['newly_unlocked_support_count_unique_appends'] == 14

    full = rows[('{2}', '(0.980481, 0.999822]', '[0, 0.870482]')]
    assert full['nearest_newly_unlocked_support_boundary_target_unique_appends'] == 8
    assert full['nearest_newly_unlocked_support_boundary_target_region'] == '[8, 18]'
    assert full['newly_unlocked_support_count_unique_appends'] == 25
    assert full['dominated_interior_search_interval_unique_appends'] == [9, 32]

    assert examples['precision_singleton_weakens_one_notch_to_neutral_boundary_8']['after']['nearest_newly_unlocked_support_boundary_target_unique_appends'] == 8
    assert examples['neutral_band_weakens_one_notch_to_relaxed_boundary_19']['after']['nearest_newly_unlocked_support_boundary_target_unique_appends'] == 19
    assert examples['precision_full_relaxation_still_starts_at_boundary_8']['after']['first_newly_unlocked_support_boundary_target_unique_appends'] == 8

    print('one-notch weaker-floor widening repairs collapse to exact boundary targets 8 and 19')


if __name__ == '__main__':
    main()
