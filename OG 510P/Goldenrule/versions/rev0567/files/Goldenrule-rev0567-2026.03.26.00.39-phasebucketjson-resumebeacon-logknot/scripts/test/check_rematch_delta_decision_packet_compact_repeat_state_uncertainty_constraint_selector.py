#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    cap_rows = {row['budget_or_requirement']: row['strongest_feasible_tier'] for row in report['axis_rows']['max_hard_cap']}
    checkpoint_rows = {row['budget_or_requirement']: row['strongest_feasible_tier'] for row in report['axis_rows']['max_checkpoints']}
    slack_rows = {row['budget_or_requirement']: row['strongest_feasible_tier'] for row in report['axis_rows']['min_anchor_slack']}
    width_rows = {row['budget_or_requirement']: row['strongest_feasible_tier'] for row in report['axis_rows']['min_band_width']}
    examples = {row['case']: row['selected_tier'] for row in report['selector_examples']}

    assert findings['positive_minimum_anchor_slack_requirement_rules_out_near_exact'] is True
    assert findings['strongest_feasible_tier_with_minimum_anchor_slack_zero'] == 'near_exact'
    assert findings['strongest_feasible_tier_with_minimum_anchor_slack_one'] == 'near_optimal'
    assert findings['strongest_feasible_tier_with_minimum_anchor_slack_six'] == 'lower_guarantee'
    assert findings['strongest_feasible_tier_with_minimum_anchor_slack_seven'] is None
    assert findings['minimum_band_width_requirements_demote_tiers_at_exact_cut_points'] == {
        '1': 'near_exact',
        '2': 'near_optimal',
        '12': 'lower_guarantee',
        '15': None,
    }

    assert tiers['near_exact']['exact_hard_cap'] == 11
    assert tiers['near_exact']['union_transition_checkpoint_count'] == 14
    assert tiers['near_exact']['minimum_anchor_slack_unique_appends'] == 0
    assert tiers['near_optimal']['exact_hard_cap'] == 5
    assert tiers['near_optimal']['union_transition_checkpoint_count'] == 8
    assert tiers['near_optimal']['minimum_anchor_slack_unique_appends'] == 5
    assert tiers['lower_guarantee']['exact_hard_cap'] == 3
    assert tiers['lower_guarantee']['union_transition_checkpoint_count'] == 5
    assert tiers['lower_guarantee']['minimum_anchor_slack_unique_appends'] == 6

    assert cap_rows[2] is None
    assert cap_rows[4] == 'lower_guarantee'
    assert cap_rows[5] == 'near_optimal'
    assert cap_rows[10] == 'near_optimal'
    assert cap_rows[11] == 'near_exact'

    assert checkpoint_rows[4] is None
    assert checkpoint_rows[5] == 'lower_guarantee'
    assert checkpoint_rows[7] == 'lower_guarantee'
    assert checkpoint_rows[8] == 'near_optimal'
    assert checkpoint_rows[13] == 'near_optimal'
    assert checkpoint_rows[14] == 'near_exact'

    assert slack_rows[0] == 'near_exact'
    assert slack_rows[1] == 'near_optimal'
    assert slack_rows[5] == 'near_optimal'
    assert slack_rows[6] == 'lower_guarantee'
    assert slack_rows[7] is None

    assert width_rows[1] == 'near_exact'
    assert width_rows[2] == 'near_optimal'
    assert width_rows[11] == 'near_optimal'
    assert width_rows[12] == 'lower_guarantee'
    assert width_rows[14] == 'lower_guarantee'
    assert width_rows[15] is None

    assert examples['precision_budget_exact'] == 'near_exact'
    assert examples['positive_slack_rules_out_near_exact'] == 'near_optimal'
    assert examples['moderate_budgets_keep_upgrade_knee'] == 'near_optimal'
    assert examples['checkpoint_bottleneck_demotes_to_lower'] == 'lower_guarantee'
    assert examples['slack_requirement_seven_leaves_no_exact_tier'] is None

    print('uncertainty constraint selector keeps the exact cut points: cap 11/5/3, checkpoints 14/8/5, and positive slack forbids the 0.99 precision tier')


if __name__ == '__main__':
    main()
