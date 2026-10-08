#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.json'
BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot.py'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = _load_module(BUILDER_PATH, 'operating_modes_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()

    assert report == rebuilt

    findings = report['headline_findings']
    assert findings['default_operating_mode'] == 'uncertainty_robust_default'
    assert findings['default_anchor_minimum_dwell_unique_appends'] == 9
    assert findings['default_anchor_margin_unique_appends'] == 8
    assert findings['default_worst_case_gain_share_of_full_dynamic_savings'] == 0.980481
    assert findings['default_transition_range'] == {
        'minimum_selected_transition_count': 2,
        'maximum_selected_transition_count': 5,
    }
    assert findings['rewrite_budget_mode_transition_ceiling'] == 4
    assert findings['rewrite_budget_mode_gain_share_of_full_dynamic_savings'] == 0.968419
    assert findings['legacy_single_budget_near_optimal_anchor'] == 13
    assert findings['single_budget_practical_default_minimum_dwell_unique_appends'] == 8
    assert findings['fixed_route_blocks_switch_cost_break_even_per_transition_bytes'] == 927.685921
    assert findings['fixed_route_blocks_first_exact_repeat_budget'] == 0.7
    assert findings['full_dynamic_transition_count'] == 12

    rows = {row['mode']: row for row in report['operating_rows']}
    assert set(rows) == {
        'exact_dynamic',
        'rewrite_budgeted',
        'uncertainty_robust_default',
        'uncertainty_robust_simplicity',
        'fixed_route_blocks',
    }
    assert rows['rewrite_budgeted']['measured_preserved_gain_share_of_full_dynamic_savings'] == 0.968419
    assert rows['rewrite_budgeted']['worst_case_transition_range'] == '4-4'
    assert rows['uncertainty_robust_default']['policy_form'] == 'minimum dwell = 9'
    assert rows['uncertainty_robust_default']['measured_preserved_gain_share_of_full_dynamic_savings'] == 0.980481
    assert rows['uncertainty_robust_default']['worst_case_transition_range'] == '2-5'
    assert rows['uncertainty_robust_simplicity']['policy_form'] == 'minimum dwell = 16'
    assert rows['uncertainty_robust_simplicity']['worst_case_transition_range'] == '0-5'
    assert rows['fixed_route_blocks']['measured_preserved_gain_share_of_full_dynamic_savings'] is None
    assert rows['fixed_route_blocks']['key_measure'] == {
        'focal_regret_vs_dynamic_at_0_18_repeats': 11132.231048,
        'switch_cost_break_even_per_transition_bytes': 927.685921,
        'first_exact_route_block_budget': 0.7,
    }

    assert len(report['decision_rules']) == 5
    print('compact repeat-state operating modes snapshot is internally consistent')


if __name__ == '__main__':
    main()
