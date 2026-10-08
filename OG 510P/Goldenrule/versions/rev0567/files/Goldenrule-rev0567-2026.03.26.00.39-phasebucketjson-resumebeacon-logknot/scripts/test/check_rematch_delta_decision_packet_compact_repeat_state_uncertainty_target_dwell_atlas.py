#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.json'
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
    rows = {row['region_label']: row for row in report['atlas_rows']}
    witnesses = {row['example_label']: row['oracle_result'] for row in report['witness_examples']}
    oracle = _load_oracle_module()

    assert findings['strongest_actual_certified_gain_share_floor_by_live_dwell_region'] == {
        '{2}': 0.999822,
        '[8, 18]': 0.980481,
        '[19, 32]': 0.870482,
    }
    assert findings['cheapest_exact_tier_by_live_dwell_region'] == {
        '{2}': 'near_exact',
        '[8, 18]': 'near_optimal',
        '[19, 32]': 'lower_guarantee',
    }
    assert findings['exact_hard_cap_by_live_dwell_region'] == {
        '{2}': 11,
        '[8, 18]': 5,
        '[19, 32]': 3,
    }
    assert findings['mode_specific_checkpoint_count_by_live_dwell_region'] == {
        '{2}': 14,
        '[8, 18]': 8,
        '[19, 32]': 5,
    }
    assert findings['internal_exact_gap_interval_unique_appends'] == [3, 7]
    assert findings['precision_singleton_forces_high_cap_even_at_low_floor'] is True
    assert findings['relaxed_suffix_cannot_be_upgraded_by_extra_budget'] is True
    assert findings['continuous_non_precision_exact_menu'] == [8, 32]

    assert rows['<2']['menu_status'] == 'no_current_exact_tier'
    assert rows['<2']['blocking_summary'] == 'target_dwell_below_current_exact_menu'
    assert rows['<2']['nearest_live_support_repair_unique_appends'] == 2

    assert rows['{2}']['menu_status'] == 'exact_tier_available'
    assert rows['{2}']['cheapest_exact_tier_available_at_target_dwell'] == 'near_exact'
    assert rows['{2}']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'] == 0.999822
    assert rows['{2}']['exact_hard_cap'] == 11
    assert rows['{2}']['mode_specific_checkpoint_count'] == 14

    assert rows['[3, 7]']['menu_status'] == 'no_current_exact_tier'
    assert rows['[3, 7]']['blocking_summary'] == 'target_dwell_inside_internal_exact_gap'
    assert rows['[3, 7]']['nearest_live_support_repair_unique_appends'] == 2

    assert rows['[8, 18]']['menu_status'] == 'exact_tier_available'
    assert rows['[8, 18]']['cheapest_exact_tier_available_at_target_dwell'] == 'near_optimal'
    assert rows['[8, 18]']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'] == 0.980481
    assert rows['[8, 18]']['exact_hard_cap'] == 5
    assert rows['[8, 18]']['mode_specific_checkpoint_count'] == 8

    assert rows['[19, 32]']['menu_status'] == 'exact_tier_available'
    assert rows['[19, 32]']['cheapest_exact_tier_available_at_target_dwell'] == 'lower_guarantee'
    assert rows['[19, 32]']['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'] == 0.870482
    assert rows['[19, 32]']['exact_hard_cap'] == 3
    assert rows['[19, 32]']['mode_specific_checkpoint_count'] == 5

    assert rows['>32']['menu_status'] == 'no_current_exact_tier'
    assert rows['>32']['blocking_summary'] == 'target_dwell_above_current_exact_menu'
    assert rows['>32']['nearest_live_support_repair_unique_appends'] == 32

    assert witnesses['precision_singleton_still_requires_precision_budget']['status'] == 'no_current_exact_tier'
    assert witnesses['precision_singleton_still_requires_precision_budget']['blocking_summary'] == 'hard_cap_underflow'
    assert witnesses['high_floor_band_resolves_cleanly_inside_8_through_18']['status'] == 'exact_tier_available'
    assert witnesses['high_floor_band_resolves_cleanly_inside_8_through_18']['strongest_feasible_tier'] == 'near_optimal'
    assert witnesses['relaxed_suffix_is_pruned_once_floor_exceeds_0_870482']['status'] == 'no_current_exact_tier'
    assert witnesses['relaxed_suffix_is_pruned_once_floor_exceeds_0_870482']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'

    direct = oracle.classify_request(
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=20,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=25,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=20,
    )
    assert direct['status'] == 'exact_tier_available'
    assert direct['strongest_feasible_tier'] == 'lower_guarantee'

    precision = oracle.classify_request(
        required_gain_share_floor='0.999',
        max_hard_cap_budget_inclusive=10,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=2,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=20,
    )
    assert precision['status'] == 'no_current_exact_tier'
    assert precision['blocking_summary'] == 'hard_cap_underflow'

    print('uncertainty target-dwell atlas stays exact: fixed dwell now maps directly to surviving exact tier or exact menu gap')


if __name__ == '__main__':
    main()
