#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    rows = {(row['start_region_label'], row['required_gain_share_floor_interval']): row for row in report['upgrade_boundary_rows']}
    witnesses = {row['example_label']: row['oracle_result'] for row in report['witness_examples']}

    assert findings['all_current_stronger_floor_repairs_reduce_to_boundary_targets'] is True
    assert findings['unique_boundary_targets_for_all_current_stronger_floor_repairs_unique_appends'] == [2, 18]
    assert findings['boundary_target_count'] == 2
    assert findings['first_non_precision_strengthening_target_unique_appends'] == 18
    assert findings['precision_collapse_target_unique_appends'] == 2
    assert findings['relaxed_suffix_first_stronger_target_is_boundary_not_band_interior'] is True
    assert findings['neutral_band_has_no_stronger_boundary_target_except_precision_singleton'] is True
    assert findings['full_live_search_space_points_unique_appends'] == 26
    assert findings['compressed_upgrade_target_set_points_unique_appends'] == 2

    mid = rows[('[19, 32]', '(0.870482, 0.980481]')]
    assert mid['nearest_stronger_live_support_boundary_target_unique_appends'] == 18
    assert mid['nearest_stronger_live_support_boundary_target_region'] == '[8, 18]'
    assert mid['minimal_left_shift_interval_unique_appends'] == [1, 14]
    assert mid['representative_anchor_jump_unique_appends'] == [25, 18]
    assert mid['dominated_interior_search_interval_unique_appends'] == [8, 17]

    high_relaxed = rows[('[19, 32]', '(0.980481, 0.999822]')]
    assert high_relaxed['nearest_stronger_live_support_boundary_target_unique_appends'] == 2
    assert high_relaxed['nearest_stronger_live_support_boundary_target_region'] == '{2}'
    assert high_relaxed['minimal_left_shift_interval_unique_appends'] == [17, 30]
    assert high_relaxed['representative_anchor_jump_unique_appends'] == [25, 2]

    high_neutral = rows[('[8, 18]', '(0.980481, 0.999822]')]
    assert high_neutral['nearest_stronger_live_support_boundary_target_unique_appends'] == 2
    assert high_neutral['nearest_stronger_live_support_boundary_target_region'] == '{2}'
    assert high_neutral['minimal_left_shift_interval_unique_appends'] == [6, 16]
    assert high_neutral['representative_anchor_jump_unique_appends'] == [13, 2]

    assert witnesses['relaxed_suffix_mid_floor_upgrade_targets_boundary_18']['status'] == 'no_current_exact_tier'
    assert witnesses['relaxed_suffix_mid_floor_upgrade_targets_boundary_18']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert witnesses['relaxed_suffix_mid_floor_upgrade_targets_boundary_18']['nearest_live_support_repair_for_target_dwell'] == 18

    assert witnesses['relaxed_suffix_high_floor_upgrade_targets_precision_2']['status'] == 'no_current_exact_tier'
    assert witnesses['relaxed_suffix_high_floor_upgrade_targets_precision_2']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert witnesses['relaxed_suffix_high_floor_upgrade_targets_precision_2']['nearest_live_support_repair_for_target_dwell'] == 2

    assert witnesses['neutral_band_high_floor_upgrade_targets_precision_2']['status'] == 'no_current_exact_tier'
    assert witnesses['neutral_band_high_floor_upgrade_targets_precision_2']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert witnesses['neutral_band_high_floor_upgrade_targets_precision_2']['nearest_live_support_repair_for_target_dwell'] == 2

    print('uncertainty stronger-floor repairs collapse to two exact boundary targets: 18 for the first non-precision upgrade and 2 for precision')


if __name__ == '__main__':
    main()
