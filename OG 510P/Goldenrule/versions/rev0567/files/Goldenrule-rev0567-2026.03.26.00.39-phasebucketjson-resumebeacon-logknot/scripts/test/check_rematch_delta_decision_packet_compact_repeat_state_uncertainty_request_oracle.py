#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    examples = {row['example_label']: row['oracle_result'] for row in report['oracle_examples']}
    oracle = _load_oracle_module()

    assert findings['oracle_script'] == 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'
    assert findings['evaluation_order'][0] == 'required_gain_share_floor'
    assert findings['evaluation_order'][1] == 'target_dwell_against_floor_conditioned_live_support'
    assert findings['exact_floor_cliffs'] == [0.870482, 0.980481, 0.999822]
    assert findings['widest_live_support_below_first_floor_cliff'] == '{2} ∪ [8, 32]'
    assert findings['continuous_non_precision_support_after_first_floor_cliff'] == '[8, 18]'
    assert findings['singleton_precision_support_after_second_floor_cliff'] == '{2}'
    assert findings['strongest_future_proof_non_fragile_default'] == 'near_optimal'
    assert findings['mode_specific_checkpoint_thresholds_before_amortization'] == {
        'lower_guarantee': 5,
        'near_optimal': 8,
        'near_exact': 14,
    }
    assert findings['post_amortized_master_calendar_size'] == 17

    assert examples['strong_non_fragile_default']['status'] == 'exact_tier_available'
    assert examples['strong_non_fragile_default']['strongest_feasible_tier'] == 'near_optimal'
    assert examples['strong_non_fragile_default']['blocking_summary'] == 'none'

    assert examples['high_floor_positive_slack_conflict']['status'] == 'no_current_exact_tier'
    assert examples['high_floor_positive_slack_conflict']['blocking_summary'] == 'high_floor_positive_slack_conflict'
    assert examples['high_floor_positive_slack_conflict']['recommended_repair_family'] == 'lower_required_floor_to_0.980481_or_drop_slack_to_zero'

    assert examples['floor_pruned_relaxed_suffix']['status'] == 'no_current_exact_tier'
    assert examples['floor_pruned_relaxed_suffix']['blocking_summary'] == 'target_dwell_pruned_by_required_floor'
    assert examples['floor_pruned_relaxed_suffix']['nearest_live_support_repair_for_target_dwell'] == 18

    assert examples['cap_underflow_on_relaxed_request']['status'] == 'no_current_exact_tier'
    assert examples['cap_underflow_on_relaxed_request']['blocking_summary'] == 'hard_cap_underflow'
    assert examples['cap_underflow_on_relaxed_request']['recommended_repair_family'] == 'raise_cap_budget_or_lower_required_floor'

    direct = oracle.classify_request(
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=3,
        minimum_anchor_slack_unique_appends=6,
        minimum_band_width_unique_appends=14,
        target_dwell_unique_appends=25,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=5,
    )
    assert direct['status'] == 'exact_tier_available'
    assert direct['strongest_feasible_tier'] == 'lower_guarantee'
    assert direct['eligible_tiers_by_floor'] == ['near_exact', 'near_optimal', 'lower_guarantee']

    precision = oracle.classify_request(
        required_gain_share_floor='0.999',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=2,
        master_calendar_pre_registered=True,
    )
    assert precision['status'] == 'exact_tier_available'
    assert precision['strongest_feasible_tier'] == 'near_exact'
    assert precision['floor_conditioned_live_support_components'] == [{'start_unique_appends': 2, 'end_unique_appends': 2}]

    print('uncertainty request oracle stays executable: exact request bundles now route to strongest feasible tier or explicit tier deficits')


if __name__ == '__main__':
    main()
