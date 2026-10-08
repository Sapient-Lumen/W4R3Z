#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    gates = {row['case']: row for row in report['gate_rows']}

    assert abs(findings['near_exact_only_needed_when_required_floor_exceeds'] - 0.980481) < 1e-9
    assert abs(findings['near_exact_exact_floor_ceiling'] - 0.999822) < 1e-9
    assert findings['precision_escalation_requires_hard_cap_at_least'] == 11
    assert findings['precision_escalation_requires_pre_amortization_checkpoint_budget_at_least'] == 14
    assert findings['precision_escalation_requires_zero_minimum_anchor_slack'] is True
    assert findings['precision_escalation_requires_band_width_one'] is True
    assert findings['positive_minimum_slack_above_near_optimal_floor_leaves_no_current_exact_tier'] is True
    assert findings['pre_registering_master_calendar_removes_only_the_checkpoint_blocker'] is True

    assert tiers['near_optimal']['exact_hard_cap'] == 5
    assert tiers['near_optimal']['mode_specific_checkpoint_count'] == 8
    assert abs(tiers['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.980481) < 1e-9
    assert tiers['near_optimal']['minimum_anchor_slack_unique_appends'] == 5
    assert tiers['near_optimal']['exact_dwell_band_width_unique_appends'] == 11

    assert tiers['near_exact']['exact_hard_cap'] == 11
    assert tiers['near_exact']['mode_specific_checkpoint_count'] == 14
    assert tiers['near_exact']['post_amortized_checkpoint_count'] == 17
    assert abs(tiers['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings'] - 0.999822) < 1e-9
    assert tiers['near_exact']['minimum_anchor_slack_unique_appends'] == 0
    assert tiers['near_exact']['exact_dwell_band_width_unique_appends'] == 1

    assert gates['pre_amortization_precision_escalation_gate']['required_gain_share_floor_interval'] == '(0.980481, 0.999822]'
    assert gates['pre_amortization_precision_escalation_gate']['minimum_required_checkpoint_budget'] == 14
    assert gates['pre_amortization_precision_escalation_gate']['selected_tier'] == 'near_exact'

    assert gates['post_amortization_precision_escalation_gate']['required_gain_share_floor_interval'] == '(0.980481, 0.999822]'
    assert gates['post_amortization_precision_escalation_gate']['minimum_required_checkpoint_budget'] is None
    assert gates['post_amortization_precision_escalation_gate']['selected_tier'] == 'near_exact'

    assert gates['high_floor_but_positive_slack_leaves_no_current_exact_tier']['minimum_anchor_slack_unique_appends'] == 1
    assert gates['high_floor_but_positive_slack_leaves_no_current_exact_tier']['minimum_band_width_unique_appends'] == 2
    assert gates['high_floor_but_positive_slack_leaves_no_current_exact_tier']['selected_tier'] is None

    assert gates['high_cap_precision_looking_but_no_floor_pressure_stays_near_optimal']['required_gain_share_floor_interval'] == '[0, 0.980481]'
    assert gates['high_cap_precision_looking_but_no_floor_pressure_stays_near_optimal']['selected_tier'] == 'near_optimal'

    print('uncertainty precision escalation gate stays exact: the 0.99 tier is only justified above floor 0.980481 and only for a single-point zero-slack dwell mode, with checkpoint budget 14 required before calendar amortization')


if __name__ == '__main__':
    main()
