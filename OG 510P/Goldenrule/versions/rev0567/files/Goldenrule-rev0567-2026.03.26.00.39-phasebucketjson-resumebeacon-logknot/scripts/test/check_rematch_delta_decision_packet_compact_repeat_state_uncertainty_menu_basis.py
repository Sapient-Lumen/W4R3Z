#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    witnesses = {row['tier']: row for row in report['basis_witness_rows']}
    removals = {row['removed_tier']: row for row in report['removal_rows']}

    assert findings['exact_tier_count'] == 3
    assert findings['removable_tier_count_without_losing_current_exact_request_region'] == 0
    assert findings['lower_guarantee_unique_basis_region']['max_hard_cap'] == 3
    assert abs(findings['lower_guarantee_unique_basis_region']['required_floor_ceiling'] - 0.870482) < 1e-9
    assert findings['near_optimal_unique_basis_region']['required_floor_interval'] == '(0.870482, 0.980481]'
    assert findings['near_optimal_unique_basis_region']['minimum_anchor_slack_unique_appends'] == 1
    assert findings['near_optimal_unique_basis_region']['minimum_band_width_unique_appends'] == 2
    assert findings['near_exact_unique_basis_region']['required_floor_interval'] == '(0.980481, 0.999822]'
    assert findings['near_exact_unique_basis_region']['max_hard_cap'] == 11
    assert findings['near_exact_unique_basis_region']['pre_amortization_checkpoint_budget'] == 14
    assert findings['near_optimal_is_only_positive_slack_exact_bridge_above_lower_guarantee_floor'] is True

    assert abs(tiers['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.870482) < 1e-9
    assert tiers['lower_guarantee']['exact_hard_cap'] == 3
    assert tiers['lower_guarantee']['minimum_anchor_slack_unique_appends'] == 6
    assert tiers['lower_guarantee']['exact_dwell_band_width_unique_appends'] == 14

    assert abs(tiers['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.980481) < 1e-9
    assert tiers['near_optimal']['exact_hard_cap'] == 5
    assert tiers['near_optimal']['minimum_anchor_slack_unique_appends'] == 5
    assert tiers['near_optimal']['exact_dwell_band_width_unique_appends'] == 11

    assert abs(tiers['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.999822) < 1e-9
    assert tiers['near_exact']['exact_hard_cap'] == 11
    assert tiers['near_exact']['mode_specific_checkpoint_count'] == 14
    assert tiers['near_exact']['minimum_anchor_slack_unique_appends'] == 0
    assert tiers['near_exact']['exact_dwell_band_width_unique_appends'] == 1

    assert witnesses['lower_guarantee']['required_gain_share_floor_interval'] == '[0, 0.870482]'
    assert witnesses['lower_guarantee']['max_hard_cap'] == 3
    assert witnesses['lower_guarantee']['selected_tier'] == 'lower_guarantee'

    assert witnesses['near_optimal']['required_gain_share_floor_interval'] == '(0.870482, 0.980481]'
    assert witnesses['near_optimal']['max_hard_cap'] == 11
    assert witnesses['near_optimal']['min_anchor_slack_unique_appends'] == 1
    assert witnesses['near_optimal']['min_band_width_unique_appends'] == 2
    assert witnesses['near_optimal']['selected_tier'] == 'near_optimal'

    assert witnesses['near_exact']['required_gain_share_floor_interval'] == '(0.980481, 0.999822]'
    assert witnesses['near_exact']['max_hard_cap'] == 11
    assert witnesses['near_exact']['pre_amortization_checkpoint_budget'] == 14
    assert witnesses['near_exact']['selected_tier'] == 'near_exact'

    assert removals['lower_guarantee']['surviving_exact_tier'] is None
    assert removals['near_optimal']['surviving_exact_tier'] is None
    assert removals['near_exact']['surviving_exact_tier'] is None
    assert removals['near_optimal']['witness_request']['min_anchor_slack_unique_appends'] == 1
    assert removals['near_optimal']['witness_request']['min_band_width_unique_appends'] == 2
    assert removals['near_exact']['witness_request']['pre_amortization_checkpoint_budget'] == 14

    print('uncertainty menu basis stays irreducible: each current exact tier owns a live request region that no other surviving tier can cover')


if __name__ == '__main__':
    main()
