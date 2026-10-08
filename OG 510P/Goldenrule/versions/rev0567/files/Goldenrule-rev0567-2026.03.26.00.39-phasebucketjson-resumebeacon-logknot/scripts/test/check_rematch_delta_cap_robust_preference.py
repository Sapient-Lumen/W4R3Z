#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_cap_robust_preference_snapshot_20260306.json'
EXPECTED_STABILITY = 'TTTMMMMUU'
EXPECTED_MATERIAL = 'TTTMMMMMU'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report.get('headline_findings', {})
    assert findings.get('stability_anchor') == EXPECTED_STABILITY
    assert findings.get('material_anchor') == EXPECTED_MATERIAL

    policy_box = findings.get('policy_box_under_test', {})
    assert policy_box.get('budget_family') == [10, 20, 50, 100]
    assert policy_box.get('minimum_additional_budget_cap_inclusive') == 10
    assert policy_box.get('maximum_additional_budget_cap_checked') == 10000
    assert policy_box.get('representative_face_count_checked_per_cap') == 4

    assert findings.get('largest_hazard_gain_for_stability') == 0.000464
    assert findings.get('cap_with_largest_hazard_gain_for_stability') == 10
    assert findings.get('smallest_hazard_gain_for_stability') == -0.000313
    assert findings.get('cap_with_smallest_hazard_gain_for_stability') == 20
    assert findings.get('true_cap_sensitive_ambiguity_strip_width_per_unit_w_hazard') == 0.000777
    assert findings.get('endpoint_only_ambiguity_strip_width_per_unit_w_hazard') == 0.000497
    assert findings.get('additional_width_missed_by_endpoint_only_check_per_unit_w_hazard') == 0.00028
    assert findings.get('relative_widening_over_endpoint_only_check') == 0.56338

    assert findings.get('baseline_nonhazard_surplus_expression') == (
        '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties'
    )
    assert findings.get('stability_anchor_cap_robust_if') == (
        '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties > 0.000313*w_hazard'
    )
    assert findings.get('material_anchor_cap_robust_if') == (
        '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties < -0.000464*w_hazard'
    )
    assert findings.get('cap_sensitive_if') == (
        '-0.000464*w_hazard <= 0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties <= 0.000313*w_hazard'
    )
    assert findings.get('tail_false_stability_safety_band_if_using_only_cap_10000') == (
        '0.000033*w_hazard < 0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties <= 0.000313*w_hazard'
    )
    assert findings.get('low_cap_false_material_safety_band_if_using_only_cap_10000') == (
        '-0.000464*w_hazard <= 0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties < -0.000033*w_hazard'
    )

    extrema = report.get('extremal_cap_rows', {})
    largest = extrema.get('largest_hazard_gain_for_stability_row', {})
    smallest = extrema.get('smallest_hazard_gain_for_stability_row', {})
    assert largest.get('additional_budget_cap') == 10
    assert largest.get('hazard_gain_for_stability') == 0.000464
    assert largest.get('material_anchor_binding_hazard_panel') == {'extortion': 80, 'delay': 2}
    assert largest.get('stability_anchor_binding_hazard_panel') == {'extortion': 50, 'delay': 2}
    assert smallest.get('additional_budget_cap') == 20
    assert smallest.get('hazard_gain_for_stability') == -0.000313
    assert smallest.get('material_anchor_binding_hazard_panel') == {'extortion': 20, 'delay': 0}
    assert smallest.get('stability_anchor_binding_hazard_panel') == {'extortion': 50, 'delay': 2}

    regions = report.get('robustness_regions', [])
    assert [row['region_label'] for row in regions] == [
        'cap_robust_material',
        'cap_sensitive_ambiguity_strip',
        'cap_robust_stability',
    ]
    assert regions[0]['winner'] == EXPECTED_MATERIAL
    assert regions[1]['winner'] == 'depends_on_declared_additional_budget_cap'
    assert regions[2]['winner'] == EXPECTED_STABILITY
    assert regions[1]['strip_width_per_unit_w_hazard'] == 0.000777

    print('ok: rematch delta cap-robust preference snapshot')


if __name__ == '__main__':
    main()
