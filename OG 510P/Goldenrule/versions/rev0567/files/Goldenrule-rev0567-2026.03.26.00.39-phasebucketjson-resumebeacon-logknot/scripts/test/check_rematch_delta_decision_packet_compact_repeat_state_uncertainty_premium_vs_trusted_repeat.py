#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    baseline = report['trusted_repeat_baseline']
    tiers = {row['tier']: row for row in report['uncertainty_tier_rows']}
    comparisons = {row['to_tier']: row for row in report['comparison_rows']}

    assert baseline['selected_transition_count'] == 4
    assert baseline['transition_checkpoints_unique_appends'] == [56, 111, 159, 239]
    assert baseline['transition_checkpoint_count'] == 4
    assert baseline['preserved_gain_share_of_full_dynamic_savings'] == 0.968419

    assert tiers['lower_guarantee']['exact_hard_cap'] == 3
    assert tiers['lower_guarantee']['union_transition_checkpoints_unique_appends'] == [47, 56, 111, 143, 159]
    assert tiers['near_optimal']['exact_hard_cap'] == 5
    assert tiers['near_optimal']['union_transition_checkpoints_unique_appends'] == [24, 47, 63, 111, 143, 159, 230, 239]
    assert tiers['near_exact']['exact_hard_cap'] == 11
    assert tiers['near_exact']['union_transition_checkpoints_unique_appends'] == [9, 15, 24, 31, 38, 47, 54, 63, 111, 143, 159, 230, 239, 255]

    assert comparisons['lower_guarantee']['hard_cap_delta'] == -1
    assert comparisons['lower_guarantee']['net_checkpoint_count_delta'] == 1
    assert comparisons['lower_guarantee']['checkpoints_added_unique_appends'] == [47, 143]
    assert comparisons['lower_guarantee']['checkpoints_dropped_unique_appends'] == [239]
    assert comparisons['lower_guarantee']['focal_gain_share_delta_at_0_18_repeats'] == -0.097937

    assert comparisons['near_optimal']['hard_cap_delta'] == 1
    assert comparisons['near_optimal']['net_checkpoint_count_delta'] == 4
    assert comparisons['near_optimal']['checkpoints_added_unique_appends'] == [24, 47, 63, 143, 230]
    assert comparisons['near_optimal']['checkpoints_dropped_unique_appends'] == [56]
    assert comparisons['near_optimal']['focal_gain_share_delta_at_0_18_repeats'] == 0.012062

    assert comparisons['near_exact']['hard_cap_delta'] == 7
    assert comparisons['near_exact']['net_checkpoint_count_delta'] == 10
    assert comparisons['near_exact']['checkpoints_added_unique_appends'] == [9, 15, 24, 31, 38, 47, 54, 63, 143, 230, 255]
    assert comparisons['near_exact']['checkpoints_dropped_unique_appends'] == [56]
    assert comparisons['near_exact']['focal_gain_share_delta_at_0_18_repeats'] == 0.031403

    assert findings['uncertainty_is_not_a_monotone_transition_tax'] is True
    assert findings['near_optimal_is_smallest_upgrade_that_adds_band_robustness_without_losing_focal_gain'] is True

    print('uncertainty premium vs trusted repeat stays exact: 0.95 costs +1 cap and net +4 checkpoints, while 0.85 is cheaper on cap but loses focal preservation')


if __name__ == '__main__':
    main()
