#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff_snapshot_20260308.json'
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
    rows = {row['target_dwell_region']: row for row in report['commitment_rows']}
    witnesses = {row['example_label']: row['oracle_result'] for row in report['witness_examples']}
    oracle = _load_oracle_module()

    assert findings['neutral_exact_default_region'] == '[8, 18]'
    assert findings['neutral_exact_default_tier'] == 'near_optimal'
    assert findings['singleton_precision_commitment_requires_extra_cap_for_small_extra_floor'] is True
    assert findings['singleton_precision_commitment_hard_cap_delta_vs_neutral'] == 6
    assert findings['singleton_precision_commitment_pre_amortization_checkpoint_delta_vs_neutral'] == 6
    assert findings['singleton_precision_commitment_floor_gain_vs_neutral'] == 0.019341
    assert findings['singleton_precision_commitment_slack_delta_vs_neutral'] == -5
    assert findings['relaxed_suffix_commitment_floor_loss_vs_neutral'] == 0.109999
    assert findings['relaxed_suffix_commitment_hard_cap_savings_vs_neutral'] == 2
    assert findings['relaxed_suffix_commitment_pre_amortization_checkpoint_savings_vs_neutral'] == 3
    assert findings['relaxed_suffix_commitment_extra_budget_cannot_upgrade_floor'] is True
    assert findings['master_calendar_amortization_does_not_remove_dwell_commitment_cap_and_fragility_effects'] is True

    assert rows['{2}']['classification'] == 'avoidable_precision_commitment_when_floor_leq_0_980481'
    assert rows['{2}']['hard_cap_delta_vs_baseline'] == 6
    assert rows['{2}']['pre_amortization_checkpoint_delta_vs_baseline'] == 6
    assert rows['{2}']['post_amortization_checkpoint_delta_vs_baseline'] == 0
    assert rows['{2}']['minimum_anchor_slack_delta_vs_baseline'] == -5
    assert rows['{2}']['exact_dwell_band_width_delta_vs_baseline'] == -10
    assert rows['{2}']['actual_certified_gain_share_floor_delta_vs_baseline'] == 0.019341

    assert rows['[8, 18]']['classification'] == 'neutral_exact_default_zone'
    assert rows['[8, 18]']['selected_exact_tier'] == 'near_optimal'
    assert rows['[8, 18]']['exact_hard_cap'] == 5
    assert rows['[8, 18]']['pre_amortization_checkpoint_count'] == 8
    assert rows['[8, 18]']['post_amortized_checkpoint_count'] == 17
    assert rows['[8, 18]']['minimum_anchor_slack_unique_appends'] == 5
    assert rows['[8, 18]']['exact_dwell_band_width_unique_appends'] == 11

    assert rows['[19, 32]']['classification'] == 'relaxed_only_commitment_with_budget_tolerance_subsidy'
    assert rows['[19, 32]']['hard_cap_delta_vs_baseline'] == -2
    assert rows['[19, 32]']['pre_amortization_checkpoint_delta_vs_baseline'] == -3
    assert rows['[19, 32]']['post_amortization_checkpoint_delta_vs_baseline'] == 0
    assert rows['[19, 32]']['minimum_anchor_slack_delta_vs_baseline'] == 1
    assert rows['[19, 32]']['exact_dwell_band_width_delta_vs_baseline'] == 3
    assert rows['[19, 32]']['actual_certified_gain_share_floor_delta_vs_baseline'] == -0.109999

    assert witnesses['dwell_2_forces_avoidable_precision_premium_at_floor_0_96']['status'] == 'exact_tier_available'
    assert witnesses['dwell_2_forces_avoidable_precision_premium_at_floor_0_96']['strongest_feasible_tier'] == 'near_exact'
    assert witnesses['same_floor_in_neutral_zone_needs_only_near_optimal_budget']['status'] == 'exact_tier_available'
    assert witnesses['same_floor_in_neutral_zone_needs_only_near_optimal_budget']['strongest_feasible_tier'] == 'near_optimal'
    assert witnesses['relaxed_suffix_stays_relaxed_even_with_large_budget']['status'] == 'exact_tier_available'
    assert witnesses['relaxed_suffix_stays_relaxed_even_with_large_budget']['strongest_feasible_tier'] == 'lower_guarantee'

    direct = oracle.classify_request(
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=25,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=14,
    )
    assert direct['strongest_feasible_tier'] == 'lower_guarantee'

    print('uncertainty dwell-commitment tariff stays exact: the 8 through 18 band remains the neutral zone, singleton precision stays expensive, and the relaxed suffix stays relaxed even with extra budget')


if __name__ == '__main__':
    main()
