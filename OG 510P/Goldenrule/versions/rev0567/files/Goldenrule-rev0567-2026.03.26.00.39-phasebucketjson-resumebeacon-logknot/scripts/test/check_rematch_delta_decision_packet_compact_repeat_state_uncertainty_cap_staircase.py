#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.json'
GUARDRAIL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
CAP_SAFE_CHECKPOINT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.json'
LOWER_GUARANTEE_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    guardrail = _load(GUARDRAIL_REPORT)
    cap_safe_checkpoints = _load(CAP_SAFE_CHECKPOINT_REPORT)
    lower = _load(LOWER_GUARANTEE_REPORT)

    findings = report['headline_findings']
    rows = {row['tier']: row for row in report['tier_rows']}
    guardrail_rows = {row['minimum_gain_share_of_full_dynamic_savings']: row for row in guardrail['guardrail_rows']}
    lower_findings = lower['headline_findings']

    assert findings['exact_tier_count'] == 3
    assert findings['exact_hard_caps_descending_by_guarantee'] == [11, 5, 3]
    assert findings['largest_exact_hard_cap'] == 11
    assert findings['smallest_exact_hard_cap'] == 3
    assert findings['near_exact_exact_hard_cap'] == 11
    assert findings['near_optimal_exact_hard_cap'] == 5
    assert findings['lower_guarantee_exact_hard_cap'] == 3
    assert findings['near_optimal_checkpoint_union_matches_uncertainty_default'] is True
    assert findings['stale_guardrail_lower_guarantee_cap'] == 4
    assert findings['stale_guardrail_lower_guarantee_status'] == 'planning_inference'
    assert findings['stale_guardrail_lower_guarantee_has_been_superseded'] is True

    near_exact = rows['near_exact']
    assert near_exact['minimum_gain_share_of_full_dynamic_savings'] == 0.99
    assert near_exact['exact_hard_cap'] == guardrail_rows[0.99]['certified_band_wide_feasible_hard_cap']
    assert near_exact['exact_dwell_band_start_unique_appends'] == 2
    assert near_exact['exact_dwell_band_end_unique_appends'] == 2
    assert near_exact['representative_anchor_minimum_dwell_unique_appends'] == 2
    assert near_exact['representative_anchor_margin_unique_appends'] == 0
    assert near_exact['focal_selected_transition_count'] == 11
    assert near_exact['focal_gain_share_of_full_dynamic_savings'] == 0.999822

    near_optimal = rows['near_optimal']
    assert near_optimal['minimum_gain_share_of_full_dynamic_savings'] == 0.95
    assert near_optimal['exact_hard_cap'] == guardrail_rows[0.95]['certified_band_wide_feasible_hard_cap']
    assert near_optimal['exact_dwell_band_start_unique_appends'] == 8
    assert near_optimal['exact_dwell_band_end_unique_appends'] == 18
    assert near_optimal['representative_anchor_minimum_dwell_unique_appends'] == 13
    assert near_optimal['representative_anchor_margin_unique_appends'] == 5
    assert near_optimal['focal_selected_transition_count'] == 5
    assert near_optimal['focal_gain_share_of_full_dynamic_savings'] == 0.980481
    assert near_optimal['union_transition_checkpoints_unique_appends'] == cap_safe_checkpoints['headline_findings']['cap_safe_union_transition_checkpoints_unique_appends']
    assert near_optimal['checkpoint_union_matches_uncertainty_default'] is True

    lower_guarantee = rows['lower_guarantee']
    assert lower_guarantee['minimum_gain_share_of_full_dynamic_savings'] == 0.85
    assert lower_guarantee['exact_hard_cap'] == lower_findings['promoted_exact_band_wide_hard_cap']
    assert lower_guarantee['exact_dwell_band_start_unique_appends'] == 19
    assert lower_guarantee['exact_dwell_band_end_unique_appends'] == 32
    assert lower_guarantee['representative_anchor_minimum_dwell_unique_appends'] == 25
    assert lower_guarantee['representative_anchor_margin_unique_appends'] == 6
    assert lower_guarantee['focal_selected_transition_count'] == 3
    assert lower_guarantee['focal_gain_share_of_full_dynamic_savings'] == lower_findings['anchor_worst_case_gain_share_of_full_dynamic_savings']
    assert lower_guarantee['union_transition_checkpoints_unique_appends'] == lower_findings['anchor_union_transition_checkpoints_unique_appends']
    assert lower_guarantee['anchor_transition_range'] == lower_findings['anchor_transition_range']

    print('uncertainty-cap staircase report is consistent with the exact tier reports and supersedes the stale lower-guarantee guardrail row')


if __name__ == '__main__':
    main()
