#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    rows = report['post_amortization_selector_rows']
    examples = {row['case']: row for row in report['selector_examples']}

    assert findings['full_master_audit_checkpoint_count'] == 17
    assert findings['pre_registering_full_master_calendar_removes_checkpoint_budget_from_current_exact_selector'] is True
    assert findings['strongest_future_proof_tier_with_cap_11_and_zero_slack'] == 'near_exact'
    assert findings['strongest_future_proof_tier_with_cap_11_and_positive_slack'] == 'near_optimal'
    assert findings['strongest_future_proof_tier_with_cap_11_and_minimum_anchor_slack_six'] == 'lower_guarantee'
    assert findings['strongest_future_proof_tier_with_cap_4_and_positive_slack'] == 'lower_guarantee'
    assert findings['strongest_future_proof_tier_with_cap_11_and_minimum_anchor_slack_seven'] is None
    assert findings['near_optimal_is_strongest_non_fragile_future_proof_tier'] is True
    assert findings['minimum_band_width_two_already_rules_out_near_exact'] is True

    for tier in tiers.values():
        assert tier['post_amortized_checkpoint_count'] == 17

    assert tiers['near_exact']['mode_specific_checkpoint_count'] == 14
    assert tiers['near_optimal']['mode_specific_checkpoint_count'] == 8
    assert tiers['lower_guarantee']['mode_specific_checkpoint_count'] == 5

    assert [row['strongest_feasible_tier'] for row in rows['max_hard_cap_with_zero_slack']] == [None, 'lower_guarantee', 'lower_guarantee', 'near_optimal', 'near_optimal', 'near_exact']
    assert [row['strongest_feasible_tier'] for row in rows['max_hard_cap_with_positive_slack']] == [None, 'lower_guarantee', 'lower_guarantee', 'near_optimal', 'near_optimal', 'near_optimal']
    assert [row['strongest_feasible_tier'] for row in rows['min_anchor_slack_with_cap_11']] == ['near_exact', 'near_optimal', 'near_optimal', 'lower_guarantee', None]
    assert [row['strongest_feasible_tier'] for row in rows['min_band_width_with_cap_11']] == ['near_exact', 'near_optimal', 'near_optimal', 'lower_guarantee', 'lower_guarantee', None]

    assert examples['full_future_proof_precision']['selected_tier'] == 'near_exact'
    assert examples['full_future_proof_non_fragile_default']['selected_tier'] == 'near_optimal'
    assert examples['full_future_proof_high_slack_relaxation']['selected_tier'] == 'lower_guarantee'
    assert examples['full_future_proof_cap_limited_relaxation']['selected_tier'] == 'lower_guarantee'
    assert examples['full_future_proof_no_exact_tier_left']['selected_tier'] is None

    print('post-amortization selector stays exact: once the 17-point master calendar is sunk cost, the current exact tier choice collapses to cap and tolerance, with near-optimal as the strongest non-fragile future-proof tier')


if __name__ == '__main__':
    main()
