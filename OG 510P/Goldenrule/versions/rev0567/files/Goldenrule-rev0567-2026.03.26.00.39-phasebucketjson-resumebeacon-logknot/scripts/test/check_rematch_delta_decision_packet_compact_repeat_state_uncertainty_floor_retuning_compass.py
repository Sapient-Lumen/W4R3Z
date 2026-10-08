#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    points = {row['dwell_unique_appends']: row for row in report['compass_points']}
    transitions = {(row['direction'], row['start_region_label'], row['target_floor_interval']): row for row in report['transition_rows']}
    examples = {row['example_label']: row for row in report['examples']}

    assert findings['four_point_compass_unique_appends'] == [2, 8, 18, 19]
    assert findings['strengthening_targets_unique_appends'] == [2, 18]
    assert findings['weakening_targets_unique_appends'] == [8, 19]
    assert findings['all_first_floor_driven_repairs_land_on_compass_points'] is True
    assert findings['full_live_support_points_unique_appends'] == 26
    assert findings['compressed_first_step_search_points_unique_appends'] == 4
    assert findings['search_compression_factor'] == 6.5
    assert findings['precision_singleton_is_terminal_strengthening_point'] is True
    assert findings['neutral_band_is_entered_at_8_and_exited_at_18_under_floor_changes'] is True
    assert findings['relaxed_suffix_is_entered_at_19_under_floor_weakening'] is True

    assert points[2]['role'] == 'precision_singleton'
    assert points[2]['exact_floor_ceiling'] == 0.999822
    assert points[2]['exact_hard_cap'] == 11
    assert points[8]['role'] == 'neutral_band_entry_boundary'
    assert points[8]['exact_floor_ceiling'] == 0.980481
    assert points[18]['role'] == 'neutral_band_exit_boundary_for_strengthening'
    assert points[19]['role'] == 'relaxed_suffix_entry_boundary'
    assert points[19]['exact_floor_ceiling'] == 0.870482

    assert transitions[('strengthen', '[19, 32]', '(0.870482, 0.980481]')]['first_compass_target_unique_appends'] == 18
    assert transitions[('strengthen', '[19, 32]', '(0.980481, 0.999822]')]['first_compass_target_unique_appends'] == 2
    assert transitions[('strengthen', '[8, 18]', '(0.980481, 0.999822]')]['first_compass_target_unique_appends'] == 2
    assert transitions[('weaken', '{2}', '(0.870482, 0.980481]')]['first_compass_target_unique_appends'] == 8
    assert transitions[('weaken', '[8, 18]', '[0, 0.870482]')]['first_compass_target_unique_appends'] == 19
    assert transitions[('weaken', '{2}', '[0, 0.870482]')]['first_compass_target_unique_appends'] == 8

    assert examples['stronger_floor_from_relaxed_suffix_mid_band_targets_18']['first_compass_target_unique_appends'] == 18
    assert examples['stronger_floor_beyond_neutral_band_targets_2']['first_compass_target_unique_appends'] == 2
    assert examples['weaker_floor_from_precision_targets_8']['first_compass_target_unique_appends'] == 8
    assert examples['weaker_floor_from_neutral_band_targets_19']['first_compass_target_unique_appends'] == 19

    print('floor-driven exact uncertainty retuning collapses to four boundary compass points: 2, 8, 18, and 19')


if __name__ == '__main__':
    main()
