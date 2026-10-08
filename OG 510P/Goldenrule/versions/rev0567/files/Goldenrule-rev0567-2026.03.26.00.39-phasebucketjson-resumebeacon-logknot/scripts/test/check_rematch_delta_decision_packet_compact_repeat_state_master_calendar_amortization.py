#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    rows = {row['mode']: row for row in report['mode_rows']}

    assert findings['full_master_audit_checkpoint_count'] == 17
    assert findings['full_master_audit_checkpoints_unique_appends'] == [9, 15, 24, 31, 38, 47, 54, 56, 63, 79, 111, 143, 159, 191, 230, 239, 255]
    assert findings['structural_only_checkpoints_unique_appends'] == [79, 191]
    assert findings['all_current_modes_become_calendar_free_to_switch_once_full_master_is_pre_registered'] is True
    assert findings['near_exact_is_cheapest_future_proof_starting_point'] is True

    assert rows['trusted_repeat_rewrite_budgeted']['mode_specific_checkpoint_count'] == 4
    assert rows['trusted_repeat_rewrite_budgeted']['additional_dates_needed_to_pre_register_full_master_calendar'] == 13
    assert rows['trusted_repeat_rewrite_budgeted']['master_calendar_dates_not_already_in_mode_specific_calendar'] == [9, 15, 24, 31, 38, 47, 54, 63, 79, 143, 191, 230, 255]
    assert rows['trusted_repeat_rewrite_budgeted']['master_calendar_coverage_share'] == 0.235294

    assert rows['lower_guarantee']['mode_specific_checkpoint_count'] == 5
    assert rows['lower_guarantee']['additional_dates_needed_to_pre_register_full_master_calendar'] == 12
    assert rows['lower_guarantee']['master_calendar_dates_not_already_in_mode_specific_calendar'] == [9, 15, 24, 31, 38, 54, 63, 79, 191, 230, 239, 255]
    assert rows['lower_guarantee']['master_calendar_coverage_share'] == 0.294118

    assert rows['near_optimal']['mode_specific_checkpoint_count'] == 8
    assert rows['near_optimal']['additional_dates_needed_to_pre_register_full_master_calendar'] == 9
    assert rows['near_optimal']['master_calendar_dates_not_already_in_mode_specific_calendar'] == [9, 15, 31, 38, 54, 56, 79, 191, 255]
    assert rows['near_optimal']['master_calendar_coverage_share'] == 0.470588

    assert rows['near_exact']['mode_specific_checkpoint_count'] == 14
    assert rows['near_exact']['additional_dates_needed_to_pre_register_full_master_calendar'] == 3
    assert rows['near_exact']['master_calendar_dates_not_already_in_mode_specific_calendar'] == [56, 79, 191]
    assert rows['near_exact']['master_calendar_coverage_share'] == 0.823529

    for row in rows.values():
        assert row['switching_inside_master_calendar_requires_new_dates'] == 0

    print('master calendar amortization stays exact: pre-registering the 17-point calendar makes all current mode switches calendar-free, and near-exact starts only three dates short of full coverage')


if __name__ == '__main__':
    main()
