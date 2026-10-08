#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot_20260308.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    live_rows = {row['region_label']: row for row in report['live_region_rows']}
    dead_rows = {row['region_label']: row for row in report['dead_region_rows']}
    witnesses = {row['example_label']: row['oracle_result'] for row in report['witness_examples']}
    oracle = _load_oracle_module()

    assert findings['ceiling_actual_certified_gain_share_floor_by_live_region'] == {
        '{2}': 0.999822,
        '[8, 18]': 0.980481,
        '[19, 32]': 0.870482,
    }
    assert findings['ceiling_exact_hard_cap_by_live_region'] == {
        '{2}': 11,
        '[8, 18]': 5,
        '[19, 32]': 3,
    }
    assert findings['ceiling_mode_specific_checkpoint_count_by_live_region'] == {
        '{2}': 14,
        '[8, 18]': 8,
        '[19, 32]': 5,
    }
    assert findings['all_live_regions_are_budget_ceiling_limited_without_retargeting'] is True
    assert findings['dead_regions_ignore_extra_budget_until_dwell_moves'] is True
    assert findings['stronger_floor_requires_region_jump'] == {
        '[19, 32]': '[8, 18]',
        '[8, 18]': '{2}',
        '{2}': None,
    }
    assert findings['extra_floor_available_only_by_retargeting'] == {
        '[19, 32]': 0.109999,
        '[8, 18]': 0.019341,
        '{2}': 0.0,
    }
    assert findings['post_amortization_master_calendar_changes_only_checkpoint_payment_not_region_ceiling'] is True

    assert live_rows['{2}']['extra_budget_can_raise_floor_without_changing_target_dwell'] is False
    assert live_rows['{2}']['next_region_needed_for_stronger_exact_floor'] is None
    assert live_rows['[8, 18]']['ceiling_actual_certified_gain_share_floor_of_full_dynamic_savings'] == 0.980481
    assert live_rows['[8, 18]']['next_region_needed_for_stronger_exact_floor'] == '{2}'
    assert live_rows['[8, 18]']['stronger_exact_floor_available_by_retargeting'] == 0.019341
    assert live_rows['[19, 32]']['ceiling_actual_certified_gain_share_floor_of_full_dynamic_savings'] == 0.870482
    assert live_rows['[19, 32]']['next_region_needed_for_stronger_exact_floor'] == '[8, 18]'
    assert live_rows['[19, 32]']['stronger_exact_floor_available_by_retargeting'] == 0.109999

    assert dead_rows['<2']['extra_budget_can_buy_entry_without_changing_target_dwell'] is False
    assert dead_rows['<2']['nearest_live_region_repair'] == '{2}'
    assert dead_rows['[3, 7]']['blocking_summary'] == 'target_dwell_inside_internal_exact_gap'
    assert dead_rows['[3, 7]']['nearest_live_region_repair'] == '[8, 18]'
    assert dead_rows['>32']['nearest_live_region_repair'] == '[19, 32]'

    assert witnesses['extra_budget_cannot_upgrade_8_through_18_past_its_region_ceiling']['status'] == 'no_current_exact_tier'
    assert witnesses['extra_budget_cannot_upgrade_8_through_18_past_its_region_ceiling']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert witnesses['extra_budget_cannot_upgrade_19_through_32_past_its_region_ceiling']['status'] == 'no_current_exact_tier'
    assert witnesses['extra_budget_cannot_upgrade_19_through_32_past_its_region_ceiling']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert witnesses['dead_gap_ignores_extra_budget_until_dwell_moves']['status'] == 'no_current_exact_tier'
    assert witnesses['dead_gap_ignores_extra_budget_until_dwell_moves']['blocking_summary'] == 'target_dwell_inside_internal_exact_gap'

    band = oracle.classify_request(
        required_gain_share_floor='0.99',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=13,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=14,
    )
    assert band['status'] == 'no_current_exact_tier'
    assert band['blocking_summary'] == 'target_dwell_pruned_by_required_floor'

    suffix = oracle.classify_request(
        required_gain_share_floor='0.95',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=25,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=14,
    )
    assert suffix['status'] == 'no_current_exact_tier'
    assert suffix['blocking_summary'] == 'target_dwell_pruned_by_required_floor'

    print('uncertainty fixed-dwell budget ceilings stay exact: stronger floors require dwell-region jumps, while dead regions ignore extra budget entirely')


if __name__ == '__main__':
    main()
