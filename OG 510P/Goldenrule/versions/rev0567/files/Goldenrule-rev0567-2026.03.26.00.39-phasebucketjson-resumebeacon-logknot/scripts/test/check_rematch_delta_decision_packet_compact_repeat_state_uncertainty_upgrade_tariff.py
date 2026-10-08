#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    upgrades = {(row['from_tier'], row['to_tier']): row for row in report['upgrade_rows']}

    assert findings['near_optimal_is_current_upgrade_knee'] is True
    assert findings['lower_to_near_optimal_hard_cap_delta'] == 2
    assert findings['lower_to_near_optimal_net_checkpoint_count_delta'] == 3
    assert findings['lower_to_near_optimal_realized_worst_case_gain_share_delta'] == 0.109999
    assert findings['near_optimal_to_near_exact_hard_cap_delta'] == 6
    assert findings['near_optimal_to_near_exact_net_checkpoint_count_delta'] == 6
    assert findings['near_optimal_to_near_exact_realized_worst_case_gain_share_delta'] == 0.019341
    assert findings['direct_lower_to_near_exact_hard_cap_delta'] == 8
    assert findings['direct_lower_to_near_exact_net_checkpoint_count_delta'] == 9
    assert findings['direct_lower_to_near_exact_realized_worst_case_gain_share_delta'] == 0.12934
    assert findings['master_audit_calendar_checkpoint_count'] == 17

    assert tiers['near_exact']['exact_hard_cap'] == 11
    assert tiers['near_exact']['exact_dwell_band_width_unique_appends'] == 1
    assert tiers['near_exact']['union_transition_checkpoint_count'] == 14
    assert tiers['near_optimal']['exact_hard_cap'] == 5
    assert tiers['near_optimal']['exact_dwell_band_width_unique_appends'] == 11
    assert tiers['near_optimal']['union_transition_checkpoint_count'] == 8
    assert tiers['lower_guarantee']['exact_hard_cap'] == 3
    assert tiers['lower_guarantee']['exact_dwell_band_width_unique_appends'] == 14
    assert tiers['lower_guarantee']['union_transition_checkpoint_count'] == 5

    lower_to_near_optimal = upgrades[('lower_guarantee', 'near_optimal')]
    assert lower_to_near_optimal['checkpoints_added_unique_appends'] == [24, 63, 230, 239]
    assert lower_to_near_optimal['checkpoints_dropped_unique_appends'] == [56]
    assert lower_to_near_optimal['representative_anchor_shift_unique_appends'] == -12
    assert lower_to_near_optimal['dwell_band_width_delta_unique_appends'] == -3

    near_optimal_to_near_exact = upgrades[('near_optimal', 'near_exact')]
    assert near_optimal_to_near_exact['checkpoints_added_unique_appends'] == [9, 15, 31, 38, 54, 255]
    assert near_optimal_to_near_exact['checkpoints_dropped_unique_appends'] == []
    assert near_optimal_to_near_exact['representative_anchor_shift_unique_appends'] == -11
    assert near_optimal_to_near_exact['dwell_band_width_delta_unique_appends'] == -10

    lower_to_near_exact = upgrades[('lower_guarantee', 'near_exact')]
    assert lower_to_near_exact['checkpoints_added_unique_appends'] == [9, 15, 24, 31, 38, 54, 63, 230, 239, 255]
    assert lower_to_near_exact['checkpoints_dropped_unique_appends'] == [56]
    assert lower_to_near_exact['representative_anchor_shift_unique_appends'] == -23
    assert lower_to_near_exact['dwell_band_width_delta_unique_appends'] == -13

    print('uncertainty upgrade tariff report preserves the exact tier deltas and keeps the 0.95 lane as the current upgrade knee')


if __name__ == '__main__':
    main()
