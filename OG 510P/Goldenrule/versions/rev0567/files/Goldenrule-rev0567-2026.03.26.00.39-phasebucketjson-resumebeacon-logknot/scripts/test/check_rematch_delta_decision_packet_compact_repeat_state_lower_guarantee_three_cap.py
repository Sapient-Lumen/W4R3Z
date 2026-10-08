#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.json'
UNCERTAINTY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
GUARDRAIL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    uncertainty = _load(UNCERTAINTY_REPORT)
    guardrail = _load(GUARDRAIL_REPORT)

    findings = report['headline_findings']
    lane_rows = {row['expected_repeat_lookups']: row for row in report['promoted_lane_rows']}
    cap_rows = {row['candidate_hard_cap']: row for row in report['cap_feasibility_rows']}

    assert findings['target_minimum_gain_share_of_full_dynamic_savings'] == 0.85
    assert findings['promoted_exact_band_wide_hard_cap'] == 3
    assert findings['promoted_exact_band_start_unique_appends'] == 19
    assert findings['promoted_exact_band_end_unique_appends'] == 32
    assert findings['promoted_exact_band_width_unique_appends'] == 14
    assert findings['promoted_exact_anchor_minimum_dwell_unique_appends'] == 25
    assert findings['promoted_exact_anchor_margin_unique_appends'] == 6
    assert findings['anchor_worst_case_gain_share_of_full_dynamic_savings'] == 0.870482
    assert findings['anchor_transition_range'] == {
        'minimum_selected_transition_count': 0,
        'maximum_selected_transition_count': 3,
    }
    assert findings['anchor_union_transition_checkpoints_unique_appends'] == [47, 56, 111, 143, 159]
    assert findings['anchor_union_transition_checkpoint_count'] == 5
    assert findings['four_cap_expands_feasible_band'] is False
    assert findings['prior_guardrail_status'] == 'planning_inference'
    assert findings['prior_guardrail_cap'] == 4

    assert cap_rows[0]['is_feasible'] is False
    assert cap_rows[1]['is_feasible'] is False
    assert cap_rows[2]['is_feasible'] is False
    assert cap_rows[2]['infeasibility_witness']['expected_repeat_lookups'] == 0.18
    assert cap_rows[2]['infeasibility_witness']['best_gain_share_of_full_dynamic_savings_under_cap'] == 0.510201
    assert cap_rows[2]['infeasibility_witness']['best_minimum_dwell_unique_appends_under_cap'] == 49
    assert cap_rows[3]['feasible_dwell_bands'] == [{
        'band_start_unique_appends': 19,
        'band_end_unique_appends': 32,
        'band_width_unique_appends': 14,
    }]
    assert cap_rows[4]['feasible_dwell_bands'] == cap_rows[3]['feasible_dwell_bands']
    assert cap_rows[5]['feasible_dwell_bands'] == [{
        'band_start_unique_appends': 8,
        'band_end_unique_appends': 32,
        'band_width_unique_appends': 25,
    }]

    assert lane_rows[0.15]['selected_transition_count'] == 0
    assert lane_rows[0.15]['gain_share_of_full_dynamic_savings'] == 0.99768
    assert lane_rows[0.15]['transition_boundaries_unique_appends'] == []
    assert lane_rows[0.18]['selected_transition_count'] == 3
    assert lane_rows[0.18]['gain_share_of_full_dynamic_savings'] == 0.870482
    assert lane_rows[0.18]['transition_boundaries_unique_appends'] == [56, 111, 159]
    assert lane_rows[0.25]['selected_transition_count'] == 3
    assert lane_rows[0.25]['gain_share_of_full_dynamic_savings'] == 0.95778
    assert lane_rows[0.25]['transition_boundaries_unique_appends'] == [47, 111, 143]

    uncertainty_row = next(
        row for row in uncertainty['uncertainty_rows']
        if row['minimum_gain_share_of_full_dynamic_savings'] == 0.85
    )
    assert uncertainty_row['minimum_dwell_overlap_start_unique_appends'] == 1
    assert uncertainty_row['minimum_dwell_overlap_end_unique_appends'] == 32

    guardrail_row = next(
        row for row in guardrail['guardrail_rows']
        if row['minimum_gain_share_of_full_dynamic_savings'] == 0.85
    )
    assert guardrail_row['band_wide_hard_cap_status'] == 'planning_inference'
    assert guardrail_row['certified_band_wide_feasible_hard_cap'] == 4
    assert guardrail_row['cap_safe_overlap_start_unique_appends'] == 19
    assert guardrail_row['cap_safe_overlap_end_unique_appends'] == 32
    assert guardrail_row['cap_safe_anchor_minimum_dwell_unique_appends'] == 25

    print('lower-guarantee three-cap report is consistent with the saved uncertainty frontier and supersedes the old planning inference')


if __name__ == '__main__':
    main()
