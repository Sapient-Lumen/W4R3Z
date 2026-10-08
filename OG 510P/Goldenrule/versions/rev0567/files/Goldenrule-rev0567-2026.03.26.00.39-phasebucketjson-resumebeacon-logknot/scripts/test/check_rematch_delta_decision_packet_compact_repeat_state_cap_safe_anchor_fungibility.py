#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot_20260308.json'
MIN_DWELL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
ANCHOR_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.json'
UNCERTAINTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
GUARDRAIL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
CHECKPOINT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'
CAP_SAFE_CHECKPOINT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    min_dwell = _load(MIN_DWELL_REPORT)
    anchor = _load(ANCHOR_REPORT)
    uncertainty = _load(UNCERTAINTY_REPORT)
    guardrail = _load(GUARDRAIL_REPORT)
    checkpoints = _load(CHECKPOINT_REPORT)
    cap_safe_checkpoints = _load(CAP_SAFE_CHECKPOINT_REPORT)

    findings = report['headline_findings']
    band = report['cap_safe_band_row']
    neighbors = {row['position']: row for row in report['neighbor_rows']}

    assert findings['target_minimum_gain_share_of_full_dynamic_savings'] == 0.95
    assert findings['cap_safe_band_start_unique_appends'] == 8
    assert findings['cap_safe_band_end_unique_appends'] == 18
    assert findings['cap_safe_band_width_unique_appends'] == 11
    assert findings['representative_anchor_minimum_dwell_unique_appends'] == 13
    assert findings['representative_anchor_margin_unique_appends'] == 5
    assert findings['uncertainty_default_anchor_minimum_dwell_unique_appends'] == 9
    assert findings['uncertainty_default_anchor_is_inside_cap_safe_band'] is True
    assert findings['focal_selected_transition_count'] == 5
    assert findings['focal_gain_share_of_full_dynamic_savings'] == 0.980481
    assert findings['focal_transition_checkpoints_unique_appends'] == [24, 63, 111, 159, 239]
    assert findings['uncertainty_default_focal_checkpoints_match_cap_safe_band'] is True
    assert findings['representative_anchor_focal_checkpoints_match_default_anchor'] is True
    assert findings['left_boundary_transition_count_before_cap_safe_band'] == 9
    assert findings['right_boundary_transition_count_after_cap_safe_band'] == 3

    plateau = next(row for row in min_dwell['frontier_rows'] if row['minimum_dwell_start_unique_appends'] == 8)
    assert band['interval_summary'] == plateau['interval_summary']
    assert band['selected_transition_count'] == plateau['selected_transition_count']

    assert anchor['headline_findings']['ninety_five_percent_anchor_minimum_dwell_unique_appends'] == 13
    assert anchor['headline_findings']['ninety_five_percent_anchor_margin_unique_appends'] == 5
    uncertainty_row = next(row for row in uncertainty['uncertainty_rows'] if row['minimum_gain_share_of_full_dynamic_savings'] == 0.95)
    assert uncertainty_row['anchor_minimum_dwell_unique_appends'] == 9
    assert guardrail['headline_findings']['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends'] == 13

    checkpoint_default = next(
        row for row in checkpoints['mode_boundary_rows']
        if row['mode'] == 'uncertainty_robust_default' and row['expected_repeat_lookups'] == 0.18
    )
    checkpoint_cap_safe = next(
        row for row in cap_safe_checkpoints['cap_safe_boundary_rows']
        if row['expected_repeat_lookups'] == 0.18
    )
    assert checkpoint_default['transition_boundaries_unique_appends'] == [24, 63, 111, 159, 239]
    assert checkpoint_default['transition_boundaries_unique_appends'] == checkpoint_cap_safe['transition_boundaries_unique_appends']

    assert neighbors['left_boundary_before_cap_safe_band']['minimum_dwell_start_unique_appends'] == 7
    assert neighbors['right_boundary_after_cap_safe_band']['minimum_dwell_start_unique_appends'] == 19

    print('cap-safe anchor fungibility report is consistent with the saved frontier and checkpoint reports')


if __name__ == '__main__':
    main()
