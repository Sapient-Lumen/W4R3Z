#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    boundaries = {row['boundary_case']: row for row in report['boundary_rows']}
    infeasible = {row['case']: row for row in report['infeasibility_rows']}
    supporting = report['supporting_constraints']

    assert findings['no_current_exact_tier_if_max_hard_cap_below'] == 3
    assert findings['no_current_exact_tier_if_pre_amortization_checkpoint_budget_below'] == 5
    assert abs(findings['no_current_exact_tier_if_required_floor_above'] - 0.999822) < 1e-9
    assert findings['no_current_exact_tier_if_minimum_anchor_slack_at_least'] == 7
    assert findings['no_current_exact_tier_if_minimum_band_width_at_least'] == 15
    assert abs(findings['no_current_exact_positive_slack_tier_above_required_floor'] - 0.980481) < 1e-9
    assert findings['exact_dwell_support_inside_current_menu_unique_appends'] == [[2, 2], [8, 32]]
    assert findings['largest_internal_exact_dwell_gap_unique_appends'] == [3, 4, 5, 6, 7]

    assert tiers['lower_guarantee']['exact_hard_cap'] == 3
    assert tiers['lower_guarantee']['pre_amortization_checkpoint_budget'] == 5
    assert tiers['lower_guarantee']['minimum_anchor_slack_unique_appends'] == 6
    assert tiers['lower_guarantee']['exact_dwell_band_width_unique_appends'] == 14
    assert abs(tiers['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.870482) < 1e-9

    assert tiers['near_optimal']['exact_hard_cap'] == 5
    assert tiers['near_optimal']['minimum_anchor_slack_unique_appends'] == 5
    assert tiers['near_optimal']['exact_dwell_band_width_unique_appends'] == 11
    assert abs(tiers['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.980481) < 1e-9

    assert tiers['near_exact']['exact_hard_cap'] == 11
    assert tiers['near_exact']['pre_amortization_checkpoint_budget'] == 14
    assert tiers['near_exact']['minimum_anchor_slack_unique_appends'] == 0
    assert tiers['near_exact']['exact_dwell_band_width_unique_appends'] == 1
    assert tiers['near_exact']['representative_anchor_minimum_dwell_unique_appends'] == 2
    assert abs(tiers['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.999822) < 1e-9

    assert boundaries['minimum_live_hard_cap']['selected_exact_tier'] == 'lower_guarantee'
    assert boundaries['minimum_live_hard_cap']['request_bundle']['max_hard_cap_budget_inclusive'] == 3
    assert boundaries['minimum_live_pre_amortization_checkpoint_budget']['selected_exact_tier'] == 'lower_guarantee'
    assert boundaries['minimum_live_pre_amortization_checkpoint_budget']['request_bundle']['max_pre_amortization_checkpoint_budget_inclusive'] == 5
    assert boundaries['maximum_live_minimum_anchor_slack']['selected_exact_tier'] == 'lower_guarantee'
    assert boundaries['maximum_live_minimum_anchor_slack']['request_bundle']['minimum_anchor_slack_unique_appends'] == 6
    assert boundaries['maximum_live_minimum_band_width']['selected_exact_tier'] == 'lower_guarantee'
    assert boundaries['maximum_live_minimum_band_width']['request_bundle']['minimum_band_width_unique_appends'] == 14
    assert boundaries['maximum_live_certified_floor']['selected_exact_tier'] == 'near_exact'
    assert boundaries['maximum_live_certified_floor']['request_bundle']['requested_exact_dwell_unique_appends_interval'] == '[2, 2]'
    assert boundaries['largest_non_fragile_floor']['selected_exact_tier'] == 'near_optimal'
    assert boundaries['largest_non_fragile_floor']['request_bundle']['minimum_anchor_slack_unique_appends'] == 1
    assert boundaries['largest_non_fragile_floor']['request_bundle']['minimum_band_width_unique_appends'] == 2

    assert infeasible['hard_cap_underflow']['surviving_exact_tier'] is None
    assert infeasible['hard_cap_underflow']['request_bundle']['max_hard_cap_budget_inclusive'] == 2
    assert infeasible['pre_amortization_checkpoint_underflow']['surviving_exact_tier'] is None
    assert infeasible['pre_amortization_checkpoint_underflow']['request_bundle']['max_pre_amortization_checkpoint_budget_inclusive'] == 4
    assert infeasible['certified_floor_overflow']['surviving_exact_tier'] is None
    assert infeasible['certified_floor_overflow']['blocking_boundary'] == 'required floor > 0.999822'
    assert infeasible['high_floor_positive_slack_conflict']['surviving_exact_tier'] is None
    assert infeasible['high_floor_positive_slack_conflict']['request_bundle']['minimum_anchor_slack_unique_appends'] == 1
    assert infeasible['high_floor_bandwidth_conflict']['surviving_exact_tier'] is None
    assert infeasible['high_floor_bandwidth_conflict']['request_bundle']['minimum_band_width_unique_appends'] == 2
    assert infeasible['slack_overflow']['surviving_exact_tier'] is None
    assert infeasible['slack_overflow']['request_bundle']['minimum_anchor_slack_unique_appends'] == 7
    assert infeasible['bandwidth_overflow']['surviving_exact_tier'] is None
    assert infeasible['bandwidth_overflow']['request_bundle']['minimum_band_width_unique_appends'] == 15
    assert infeasible['internal_dwell_gap_request']['surviving_exact_tier'] is None
    assert infeasible['internal_dwell_gap_request']['request_bundle']['requested_exact_dwell_unique_appends_interval'] == '[3, 7]'
    assert infeasible['outside_current_exact_dwell_menu']['surviving_exact_tier'] is None
    assert infeasible['outside_current_exact_dwell_menu']['request_bundle']['requested_exact_dwell_unique_appends_sets'] == ['(-inf, 1]', '[33, +inf)']

    assert supporting['minimum_live_hard_cap_tier'] == 'lower_guarantee'
    assert supporting['minimum_live_pre_amortization_checkpoint_tier'] == 'lower_guarantee'
    assert supporting['maximum_live_minimum_slack_tier'] == 'lower_guarantee'
    assert supporting['maximum_live_minimum_band_width_tier'] == 'lower_guarantee'
    assert supporting['positive_slack_rules_out_near_exact_above_required_floor'] is True

    print('uncertainty infeasibility screen stays exact: fail-fast boundaries match the saved selector, gate, and dwell-topology evidence')


if __name__ == '__main__':
    main()
