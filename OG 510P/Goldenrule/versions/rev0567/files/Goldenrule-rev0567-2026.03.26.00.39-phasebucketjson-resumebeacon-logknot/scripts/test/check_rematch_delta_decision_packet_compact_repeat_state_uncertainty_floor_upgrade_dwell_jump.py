#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    rows = {(row['start_region_label'], row['destination_region_label']): row for row in report['jump_rows']}
    witnesses = {row['example_label']: row['oracle_result'] for row in report['witness_examples']}

    assert findings['all_current_exact_floor_upgrades_from_live_regions_are_leftward_only'] is True
    assert findings['first_stronger_region_by_live_start_region'] == {
        '[19, 32]': '[8, 18]',
        '[8, 18]': '{2}',
        '{2}': None,
    }
    assert findings['required_left_shift_interval_unique_appends_by_upgrade_pair'] == {
        '[19, 32] -> [8, 18]': [1, 14],
        '[19, 32] -> {2}': [17, 30],
        '[8, 18] -> {2}': [6, 16],
    }
    assert findings['extra_exact_floor_unlocked_by_leftward_jump'] == {
        '[19, 32] -> [8, 18]': 0.109999,
        '[19, 32] -> {2}': 0.12934,
        '[8, 18] -> {2}': 0.019341,
    }
    assert findings['precision_upgrade_is_a_leftward_collapse_not_a_local_tune'] is True
    assert findings['neutral_band_is_the_last_live_region_before_precision_singleton'] is True
    assert findings['no_current_live_region_has_a_rightward_exact_floor_upgrade_path'] is True

    assert rows[('[19, 32]', '[8, 18]')]['required_gain_share_floor_interval_that_forces_this_jump'] == '(0.870482, 0.980481]'
    assert rows[('[19, 32]', '[8, 18]')]['representative_anchor_jump_unique_appends'] == [25, 18]
    assert rows[('[19, 32]', '[8, 18]')]['required_left_shift_interval_unique_appends'] == [1, 14]
    assert rows[('[19, 32]', '{2}')]['required_left_shift_interval_unique_appends'] == [17, 30]
    assert rows[('[19, 32]', '{2}')]['representative_anchor_jump_unique_appends'] == [25, 2]
    assert rows[('[8, 18]', '{2}')]['required_left_shift_interval_unique_appends'] == [6, 16]
    assert rows[('[8, 18]', '{2}')]['representative_anchor_jump_unique_appends'] == [13, 2]

    assert witnesses['relaxed_suffix_must_jump_left_into_neutral_band_for_floor_0_96']['status'] == 'no_current_exact_tier'
    assert witnesses['relaxed_suffix_must_jump_left_into_neutral_band_for_floor_0_96']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert witnesses['relaxed_suffix_must_jump_left_into_neutral_band_for_floor_0_96']['nearest_live_support_repair_for_target_dwell'] == 18

    assert witnesses['neutral_band_must_collapse_left_to_precision_singleton_for_floor_0_99']['status'] == 'no_current_exact_tier'
    assert witnesses['neutral_band_must_collapse_left_to_precision_singleton_for_floor_0_99']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert witnesses['neutral_band_must_collapse_left_to_precision_singleton_for_floor_0_99']['nearest_live_support_repair_for_target_dwell'] == 2

    print('uncertainty floor upgrades remain directional: every stronger current exact floor repair from live dwell support is a leftward jump, never a rightward sweep')


if __name__ == '__main__':
    main()
