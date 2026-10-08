#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot.py'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = _load_module(BUILDER_PATH, 'uncertainty_cap_guardrails_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()

    assert report == rebuilt

    findings = report['headline_findings']
    assert findings['current_operating_modes_rewrite_budget_ceiling'] == 4
    assert findings['current_uncertainty_robust_default_minimum_dwell_unique_appends'] == 9
    assert findings['current_uncertainty_robust_default_transition_range'] == {
        'minimum_selected_transition_count': 2,
        'maximum_selected_transition_count': 5,
    }
    assert findings['near_exact_certified_band_wide_hard_cap'] == 11
    assert findings['near_optimal_certified_band_wide_hard_cap'] == 5
    assert findings['near_optimal_cap_safe_overlap_start_unique_appends'] == 8
    assert findings['near_optimal_cap_safe_overlap_end_unique_appends'] == 18
    assert findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends'] == 13
    assert findings['near_optimal_four_transition_no_go'] is True
    assert findings['lower_guarantee_conservative_band_wide_cap'] == 4
    assert findings['lower_guarantee_cap_status'] == 'planning_inference'
    assert findings['lower_guarantee_planning_anchor_minimum_dwell_unique_appends'] == 25

    rows = {row['minimum_gain_share_of_full_dynamic_savings']: row for row in report['guardrail_rows']}
    assert set(rows) == {0.99, 0.95, 0.85}
    assert rows[0.99]['certified_focal_lower_bound_on_hard_cap'] == 11
    assert rows[0.99]['certified_band_wide_feasible_hard_cap'] == 11
    assert rows[0.99]['band_wide_cap_safe_anchor_minimum_dwell_unique_appends'] == 2
    assert rows[0.95]['certified_focal_lower_bound_on_hard_cap'] == 5
    assert rows[0.95]['certified_band_wide_feasible_hard_cap'] == 5
    assert rows[0.95]['cap_safe_overlap_start_unique_appends'] == 8
    assert rows[0.95]['cap_safe_overlap_end_unique_appends'] == 18
    assert rows[0.95]['cap_safe_anchor_minimum_dwell_unique_appends'] == 13
    assert 'hard cap of 4 is impossible' in rows[0.95]['note']
    assert rows[0.85]['certified_focal_lower_bound_on_hard_cap'] == 3
    assert rows[0.85]['certified_band_wide_feasible_hard_cap'] == 4
    assert rows[0.85]['band_wide_hard_cap_status'] == 'planning_inference'
    assert rows[0.85]['cap_safe_overlap_start_unique_appends'] == 19
    assert rows[0.85]['cap_safe_overlap_end_unique_appends'] == 32
    assert rows[0.85]['cap_safe_anchor_minimum_dwell_unique_appends'] == 25

    print('compact repeat-state uncertainty-cap guardrails snapshot is internally consistent')


if __name__ == '__main__':
    main()
