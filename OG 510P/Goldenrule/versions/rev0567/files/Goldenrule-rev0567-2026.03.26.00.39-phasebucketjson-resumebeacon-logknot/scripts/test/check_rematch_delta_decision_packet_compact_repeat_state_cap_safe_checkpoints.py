#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.json'
GUARDRAIL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
CHECKPOINT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    guardrail = _load(GUARDRAIL_REPORT)
    checkpoints = _load(CHECKPOINT_REPORT)

    findings = report['headline_findings']
    guardrail_findings = guardrail['headline_findings']
    checkpoint_findings = checkpoints['headline_findings']

    assert findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends'] == guardrail_findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends']
    assert findings['near_optimal_certified_band_wide_hard_cap'] == guardrail_findings['near_optimal_certified_band_wide_hard_cap']
    assert findings['uncertainty_default_anchor_minimum_dwell_unique_appends'] == checkpoint_findings['default_robust_minimum_dwell_unique_appends']
    assert findings['uncertainty_default_union_transition_checkpoints_unique_appends'] == checkpoint_findings['default_robust_union_transition_checkpoints_unique_appends']
    assert findings['checkpoint_union_matches_uncertainty_default'] is True
    assert findings['cap_safe_union_transition_checkpoints_unique_appends'] == [24, 47, 63, 111, 143, 159, 230, 239]
    assert findings['cap_safe_union_transition_checkpoint_count'] == 8
    assert findings['focal_selected_transition_count'] == 5

    rows = report['cap_safe_boundary_rows']
    assert [row['expected_repeat_lookups'] for row in rows] == [0.15, 0.18, 0.25]
    assert rows[0]['transition_boundaries_unique_appends'] == [230, 239]
    assert rows[1]['transition_boundaries_unique_appends'] == [24, 63, 111, 159, 239]
    assert rows[2]['transition_boundaries_unique_appends'] == [47, 111, 143, 239]

    print('cap-safe checkpoint schedule is consistent with the guardrail and checkpoint reports')


if __name__ == '__main__':
    main()
