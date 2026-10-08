#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    upgrades = {(row['from_tier'], row['to_tier']): row for row in report['support_tariff_rows']}

    assert findings['near_optimal_is_last_exact_tier_with_continuous_non_precision_support'] is True
    assert findings['lower_to_near_optimal_lost_live_dwell_count_unique_appends'] == 14
    assert findings['lower_to_near_optimal_realized_worst_case_gain_share_delta'] == 0.109999
    assert findings['lower_to_near_optimal_realized_worst_case_gain_share_delta_per_lost_live_dwell'] == 0.007857
    assert findings['lower_to_near_optimal_retained_live_dwell_fraction'] == 0.461538
    assert findings['near_optimal_to_near_exact_lost_live_dwell_count_unique_appends'] == 11
    assert findings['near_optimal_to_near_exact_realized_worst_case_gain_share_delta'] == 0.019341
    assert findings['near_optimal_to_near_exact_realized_worst_case_gain_share_delta_per_lost_live_dwell'] == 0.001758
    assert findings['near_optimal_to_near_exact_retained_live_dwell_fraction'] == 0.083333
    assert findings['first_upgrade_support_efficiency_advantage_over_second'] == 4.469283
    assert findings['direct_lower_to_near_exact_lost_live_dwell_count_unique_appends'] == 25

    assert tiers['lower_guarantee']['supported_dwell_count_unique_appends'] == 26
    assert tiers['lower_guarantee']['continuous_non_precision_support_count_unique_appends'] == 25
    assert tiers['near_optimal']['supported_dwell_count_unique_appends'] == 12
    assert tiers['near_optimal']['continuous_non_precision_support_count_unique_appends'] == 11
    assert tiers['near_exact']['supported_dwell_count_unique_appends'] == 1
    assert tiers['near_exact']['continuous_non_precision_support_count_unique_appends'] == 0

    first = upgrades[('lower_guarantee', 'near_optimal')]
    assert first['removed_live_support_suffix_or_component'] == '[19, 32]'
    assert first['destroys_all_continuous_non_precision_support'] is False
    second = upgrades[('near_optimal', 'near_exact')]
    assert second['removed_live_support_suffix_or_component'] == '[8, 18]'
    assert second['destroys_all_continuous_non_precision_support'] is True
    direct = upgrades[('lower_guarantee', 'near_exact')]
    assert direct['removed_live_support_suffix_or_component'] == '[8, 32]'

    print('uncertainty dwell-freedom tariff report preserves the live-support collapse economics and keeps exact 0.95 as the last non-fragile support tier')


if __name__ == '__main__':
    main()
