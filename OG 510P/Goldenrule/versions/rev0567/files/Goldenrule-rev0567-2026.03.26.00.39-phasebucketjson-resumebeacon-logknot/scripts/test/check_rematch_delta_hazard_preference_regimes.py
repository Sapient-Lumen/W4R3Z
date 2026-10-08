#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_preference_regime_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report.get('headline_findings', {})
    assert findings.get('representative_face_count_checked_per_cap') == 4
    assert findings.get('hazard_preference_regime_count') == 3
    assert findings.get('largest_cap_where_hazard_clearance_still_favors_stability') == 14
    assert findings.get('smallest_cap_where_hazard_clearance_favors_material') == 15
    assert findings.get('material_anchor_binding_hazard_panel_switch_cap') == 20
    assert findings.get('positive_hazard_gain_for_stability_at_full_shortlist_threshold') == 0.000464
    assert findings.get('positive_hazard_gain_for_stability_just_before_sign_flip') == 0.000064
    assert findings.get('negative_hazard_gain_for_stability_at_first_material_favoring_cap') == -0.000017
    assert findings.get('negative_hazard_gain_for_stability_at_binding_panel_switch_cap') == -0.000313
    assert findings.get('negative_hazard_gain_for_stability_at_cap_10000') == -0.000033
    assert findings.get('asymptotic_hazard_gain_for_stability_after_binding_panel_switch') == -0.000018

    regimes = report.get('regime_rows', [])
    assert len(regimes) == 3

    first, second, third = regimes
    assert (first['cap_start_inclusive'], first['cap_end_inclusive']) == (10, 14)
    assert first['hazard_gain_sign'] == 'positive_for_stability'
    assert first['material_anchor_binding_hazard_panel']['extortion'] == 80
    assert first['material_anchor_binding_hazard_panel']['delay'] == 2
    assert first['stability_anchor_binding_hazard_panel']['extortion'] == 50
    assert first['stability_anchor_binding_hazard_panel']['delay'] == 2

    assert (second['cap_start_inclusive'], second['cap_end_inclusive']) == (15, 19)
    assert second['hazard_gain_sign'] == 'negative_for_material'
    assert second['material_anchor_binding_hazard_panel'] == first['material_anchor_binding_hazard_panel']
    assert second['stability_anchor_binding_hazard_panel'] == first['stability_anchor_binding_hazard_panel']

    assert (third['cap_start_inclusive'], third['cap_end_inclusive']) == (20, 10000)
    assert third['hazard_gain_sign'] == 'negative_for_material'
    assert third['material_anchor_binding_hazard_panel']['extortion'] == 20
    assert third['material_anchor_binding_hazard_panel']['delay'] == 0
    assert third['stability_anchor_binding_hazard_panel'] == first['stability_anchor_binding_hazard_panel']

    rep_rows = report.get('representative_cap_rows', [])
    assert [row['additional_budget_cap'] for row in rep_rows] == [10, 14, 15, 19, 20, 10000]
    assert rep_rows[0]['hazard_gain_for_stability'] == 0.000464
    assert rep_rows[1]['hazard_gain_for_stability'] == 0.000064
    assert rep_rows[2]['hazard_gain_for_stability'] == -0.000017
    assert rep_rows[3]['hazard_gain_for_stability'] == -0.000294
    assert rep_rows[4]['hazard_gain_for_stability'] == -0.000313
    assert rep_rows[5]['hazard_gain_for_stability'] == -0.000033

    print('ok: rematch delta hazard preference regimes snapshot')


if __name__ == '__main__':
    main()
