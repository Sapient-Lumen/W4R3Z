#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    shifts = {(row['from_tier'], row['to_tier']): row for row in report['tolerance_shift_rows']}

    assert findings['near_exact_is_single_point_precision_mode'] is True
    assert findings['near_optimal_is_true_tolerance_band'] is True
    assert findings['lower_guarantee_is_widest_certified_band'] is True
    assert findings['exact_dwell_band_widths_by_descending_guarantee'] == [1, 11, 14]
    assert findings['minimum_anchor_slacks_by_descending_guarantee'] == [0, 5, 6]
    assert findings['near_optimal_to_near_exact_band_width_delta_unique_appends'] == -10
    assert findings['near_optimal_to_near_exact_minimum_anchor_slack_delta_unique_appends'] == -5
    assert findings['lower_to_near_optimal_band_width_delta_unique_appends'] == -3
    assert findings['lower_to_near_optimal_minimum_anchor_slack_delta_unique_appends'] == -1

    assert tiers['near_exact']['anchor_left_slack_unique_appends'] == 0
    assert tiers['near_exact']['anchor_right_slack_unique_appends'] == 0
    assert tiers['near_exact']['retuning_error_budget_unique_appends'] == 0
    assert tiers['near_optimal']['anchor_left_slack_unique_appends'] == 5
    assert tiers['near_optimal']['anchor_right_slack_unique_appends'] == 5
    assert tiers['near_optimal']['retuning_error_budget_unique_appends'] == 10
    assert tiers['lower_guarantee']['anchor_left_slack_unique_appends'] == 6
    assert tiers['lower_guarantee']['anchor_right_slack_unique_appends'] == 7
    assert tiers['lower_guarantee']['retuning_error_budget_unique_appends'] == 13

    lower_to_near_optimal = shifts[('lower_guarantee', 'near_optimal')]
    assert lower_to_near_optimal['hard_cap_delta'] == 2
    assert lower_to_near_optimal['checkpoint_count_delta'] == 3
    assert lower_to_near_optimal['dwell_band_width_delta_unique_appends'] == -3
    assert lower_to_near_optimal['retuning_error_budget_delta_unique_appends'] == -3
    assert lower_to_near_optimal['minimum_anchor_slack_delta_unique_appends'] == -1
    assert lower_to_near_optimal['anchor_shift_unique_appends'] == -12

    near_optimal_to_near_exact = shifts[('near_optimal', 'near_exact')]
    assert near_optimal_to_near_exact['hard_cap_delta'] == 6
    assert near_optimal_to_near_exact['checkpoint_count_delta'] == 6
    assert near_optimal_to_near_exact['dwell_band_width_delta_unique_appends'] == -10
    assert near_optimal_to_near_exact['retuning_error_budget_delta_unique_appends'] == -10
    assert near_optimal_to_near_exact['minimum_anchor_slack_delta_unique_appends'] == -5
    assert near_optimal_to_near_exact['anchor_shift_unique_appends'] == -11

    lower_to_near_exact = shifts[('lower_guarantee', 'near_exact')]
    assert lower_to_near_exact['hard_cap_delta'] == 8
    assert lower_to_near_exact['checkpoint_count_delta'] == 9
    assert lower_to_near_exact['dwell_band_width_delta_unique_appends'] == -13
    assert lower_to_near_exact['retuning_error_budget_delta_unique_appends'] == -13
    assert lower_to_near_exact['minimum_anchor_slack_delta_unique_appends'] == -6
    assert lower_to_near_exact['anchor_shift_unique_appends'] == -23

    print('uncertainty dwell-tolerance staircase report keeps the exact tier widths and makes the 0.99 lane a deliberate precision mode')


if __name__ == '__main__':
    main()
