#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot_20260308.json'
OPERATING_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.json'
UNCERTAINTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
TRANSITION_BUDGET_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json'
SWITCH_PENALTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot_20260307.json'
FIXED_POLICY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    operating = _load(OPERATING_REPORT)
    uncertainty = _load(UNCERTAINTY_REPORT)
    transition_budget = _load(TRANSITION_BUDGET_REPORT)
    switch_penalty = _load(SWITCH_PENALTY_REPORT)
    fixed_policy = _load(FIXED_POLICY_REPORT)

    findings = report['headline_findings']
    operating_findings = operating['headline_findings']
    uncertainty_findings = uncertainty['headline_findings']
    transition_findings = transition_budget['headline_findings']
    switch_findings = switch_penalty['headline_findings']
    fixed_findings = fixed_policy['headline_findings']

    assert findings['default_mode'] == operating_findings['default_operating_mode']
    assert findings['default_minimum_dwell_unique_appends'] == operating_findings['default_anchor_minimum_dwell_unique_appends']
    assert findings['default_worst_case_gain_share_of_full_dynamic_savings'] == operating_findings['default_worst_case_gain_share_of_full_dynamic_savings']
    assert findings['rewrite_budget_transition_ceiling'] == operating_findings['rewrite_budget_mode_transition_ceiling']
    assert findings['rewrite_budget_gain_share_of_full_dynamic_savings'] == operating_findings['rewrite_budget_mode_gain_share_of_full_dynamic_savings']
    assert findings['micro_churn_ceiling_bytes_per_transition'] == switch_findings['micro_churn_ceiling_bytes']
    assert findings['freeze_break_even_bytes_per_transition'] == operating_findings['fixed_route_blocks_switch_cost_break_even_per_transition_bytes']
    assert findings['freeze_repeat_budget_threshold'] == operating_findings['fixed_route_blocks_first_exact_repeat_budget']
    assert findings['full_dynamic_transition_count'] == operating_findings['full_dynamic_transition_count']

    support = report['supporting_measures']
    assert support['first_switch_gain_vs_fixed_route_blocks_bytes'] == transition_findings['first_switch_gain_vs_fixed_route_blocks_bytes']
    assert support['first_four_switch_gain_share_of_full_dynamic_savings'] == transition_findings['first_four_switch_gain_share_of_full_dynamic_savings']
    assert support['fixed_policy_regret_vs_dynamic_bytes'] == fixed_findings['focal_best_fixed_regret_vs_dynamic']
    assert support['micro_churn_regime_count_at_or_above_ceiling'] == switch_findings['practical_regime_count_at_or_above_micro_churn_ceiling']
    assert support['uncertainty_simplicity_dwell'] == uncertainty_findings['eighty_five_percent_anchor_minimum_dwell_unique_appends']
    assert support['uncertainty_simplicity_worst_case_gain_share'] == uncertainty_findings['eighty_five_percent_worst_case_gain_share_of_full_dynamic_savings']

    rows = report['control_rows']
    assert [row['priority'] for row in rows] == [1, 2, 3, 4, 5]
    assert rows[0]['selected_mode'] == 'fixed_route_blocks'
    assert rows[1]['selected_mode'] == 'rewrite_budgeted'
    assert rows[2]['selected_mode'] == 'uncertainty_robust_default'
    assert rows[3]['selected_mode'] == 'priced_switch_frontier'
    assert rows[4]['selected_mode'] == 'exact_dynamic'
    assert len(report['observables']) == 5
    assert len(report['source_reports']) == 5

    print('compact repeat-state control card is consistent with its source reports')


if __name__ == '__main__':
    main()
