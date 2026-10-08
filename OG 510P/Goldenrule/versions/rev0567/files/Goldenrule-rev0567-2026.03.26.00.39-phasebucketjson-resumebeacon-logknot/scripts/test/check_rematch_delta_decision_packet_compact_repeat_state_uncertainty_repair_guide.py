#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    repairs = {row['case']: row for row in report['repair_rows']}

    assert findings['single_notch_local_repairs']['hard_cap_underflow'] == '+1 hard-cap step restores the exact 0.85 lane'
    assert findings['single_notch_local_repairs']['pre_amortization_checkpoint_underflow'] == '+1 checkpoint restores the exact 0.85 lane'
    assert findings['single_notch_local_repairs']['slack_overflow'] == '-1 slack demand restores the exact 0.85 lane'
    assert findings['single_notch_local_repairs']['bandwidth_overflow'] == '-1 dwell-band-width demand restores the exact 0.85 lane'
    assert findings['dwell_gap_repair_choices'] == {'precision_point': 2, 'non_fragile_band_start': 8}
    assert findings['largest_no_local_structural_repair_case'] == 'required floor > 0.999822'
    assert findings['global_checkpoint_repair_available_before_amortization'] is True
    assert findings['master_calendar_repairs_pre_amortization_checkpoint_underflow_without_raising_mode_budget'] is True
    assert abs(findings['maximum_live_floor_after_local_requirement_clip'] - 0.999822) < 1e-9

    assert tiers['lower_guarantee']['exact_hard_cap'] == 3
    assert tiers['lower_guarantee']['mode_specific_checkpoint_count'] == 5
    assert tiers['lower_guarantee']['minimum_anchor_slack_unique_appends'] == 6
    assert tiers['lower_guarantee']['exact_dwell_band_width_unique_appends'] == 14
    assert abs(tiers['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.870482) < 1e-9

    assert tiers['near_optimal']['exact_hard_cap'] == 5
    assert tiers['near_optimal']['minimum_anchor_slack_unique_appends'] == 5
    assert tiers['near_optimal']['exact_dwell_band_width_unique_appends'] == 11
    assert abs(tiers['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.980481) < 1e-9

    assert tiers['near_exact']['exact_hard_cap'] == 11
    assert tiers['near_exact']['mode_specific_checkpoint_count'] == 14
    assert tiers['near_exact']['minimum_anchor_slack_unique_appends'] == 0
    assert tiers['near_exact']['exact_dwell_band_width_unique_appends'] == 1
    assert tiers['near_exact']['representative_anchor_minimum_dwell_unique_appends'] == 2
    assert abs(tiers['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.999822) < 1e-9

    assert repairs['hard_cap_underflow']['primary_repair']['new_value'] == 3
    assert repairs['hard_cap_underflow']['primary_repair']['delta'] == 1
    assert repairs['hard_cap_underflow']['primary_repair']['recovered_exact_tier'] == 'lower_guarantee'

    assert repairs['pre_amortization_checkpoint_underflow']['primary_repair']['new_value'] == 5
    assert repairs['pre_amortization_checkpoint_underflow']['alternative_repair']['new_value'] is True
    assert repairs['pre_amortization_checkpoint_underflow']['alternative_repair']['recovered_exact_tier'] == 'lower_guarantee'

    assert repairs['certified_floor_overflow']['primary_repair']['new_ceiling'] == 0.999822
    assert repairs['certified_floor_overflow']['primary_repair']['recovered_exact_tier'] == 'near_exact'
    assert repairs['certified_floor_overflow']['alternative_repair']['recovered_exact_tier'] is None

    assert repairs['high_floor_positive_slack_conflict']['primary_repair']['new_ceiling'] == 0.980481
    assert repairs['high_floor_positive_slack_conflict']['alternative_repair']['new_value'] == 0
    assert repairs['high_floor_positive_slack_conflict']['primary_repair']['recovered_exact_tier'] == 'near_optimal'
    assert repairs['high_floor_positive_slack_conflict']['alternative_repair']['recovered_exact_tier'] == 'near_exact'

    assert repairs['high_floor_bandwidth_conflict']['primary_repair']['new_ceiling'] == 0.980481
    assert repairs['high_floor_bandwidth_conflict']['alternative_repair']['new_value'] == 1
    assert repairs['high_floor_bandwidth_conflict']['primary_repair']['recovered_exact_tier'] == 'near_optimal'
    assert repairs['high_floor_bandwidth_conflict']['alternative_repair']['recovered_exact_tier'] == 'near_exact'

    assert repairs['slack_overflow']['primary_repair']['new_value'] == 6
    assert repairs['slack_overflow']['primary_repair']['delta'] == -1
    assert repairs['slack_overflow']['primary_repair']['recovered_exact_tier'] == 'lower_guarantee'

    assert repairs['bandwidth_overflow']['primary_repair']['new_value'] == 14
    assert repairs['bandwidth_overflow']['primary_repair']['delta'] == -1
    assert repairs['bandwidth_overflow']['primary_repair']['recovered_exact_tier'] == 'lower_guarantee'

    assert repairs['internal_dwell_gap_request']['primary_repair']['new_live_support'] == 8
    assert repairs['internal_dwell_gap_request']['alternative_repair']['new_live_support'] == 2
    assert repairs['internal_dwell_gap_request']['primary_repair']['recovered_exact_tier'] == 'near_optimal'
    assert repairs['internal_dwell_gap_request']['alternative_repair']['recovered_exact_tier'] == 'near_exact'

    assert repairs['below_current_exact_dwell_menu']['primary_repair']['new_live_support'] == 2
    assert repairs['below_current_exact_dwell_menu']['alternative_repair']['new_live_support'] == 8
    assert repairs['below_current_exact_dwell_menu']['primary_repair']['recovered_exact_tier'] == 'near_exact'
    assert repairs['below_current_exact_dwell_menu']['alternative_repair']['recovered_exact_tier'] == 'near_optimal'

    assert repairs['above_current_exact_dwell_menu']['primary_repair']['new_live_support'] == 32
    assert repairs['above_current_exact_dwell_menu']['primary_repair']['recovered_exact_tier'] == 'lower_guarantee'

    print('uncertainty repair guide stays exact: impossible bundles now come with smallest current-menu repairs instead of only fail-fast rejection')


if __name__ == '__main__':
    main()
