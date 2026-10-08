#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_preference_halfspace_snapshot_20260306.json'
EXPECTED_STABILITY = 'TTTMMMMUU'
EXPECTED_MATERIAL = 'TTTMMMMMU'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report.get('headline_findings', {})
    assert findings.get('representative_corner_count') == 8
    assert findings.get('unique_preference_halfspace_pattern_count') == 2
    assert findings.get('material_anchor') == EXPECTED_MATERIAL
    assert findings.get('stability_anchor') == EXPECTED_STABILITY

    invariant = findings.get('invariant_nonhazard_tradeoff_coefficients', {})
    assert invariant.get('width_gain_coefficient') == 0.00027
    assert invariant.get('anchor_buffer_gain_coefficient') == 0.00013
    assert invariant.get('knife_edge_separation_gain_coefficient') == 0.000122
    assert invariant.get('anchor_delta_cost_coefficient') == 0.00142
    assert invariant.get('material_leader_loss_coefficient') == 1
    assert invariant.get('additional_undecided_coefficient') == 1
    assert invariant.get('additional_anchor_tie_coefficient') == 1

    assert findings.get('hazard_clearance_gain_for_stability_at_cap_10') == 0.000464
    assert findings.get('hazard_clearance_gain_for_stability_at_cap_10000') == -0.000033
    assert findings.get('hazard_sensitivity_strip_width_per_unit_w_hazard') == 0.000497

    patterns = report.get('halfspace_patterns', [])
    assert len(patterns) == 2
    by_cap = {pattern['additional_budget_cap']: pattern for pattern in patterns}
    assert sorted(by_cap) == [10, 10000]
    assert by_cap[10]['representative_corner_count'] == 4
    assert by_cap[10000]['representative_corner_count'] == 4
    assert by_cap[10]['left_side_gains']['hazard_clearance_gain_coefficient'] == 0.000464
    assert by_cap[10000]['left_side_gains']['hazard_clearance_gain_coefficient'] == -0.000033
    assert by_cap[10]['right_side_costs'] == by_cap[10000]['right_side_costs']

    coefficient_rows = report.get('coefficient_rows', [])
    assert len(coefficient_rows) == 8
    for row in coefficient_rows:
        left = row['stability_wins_iff']['left_side_gains']
        right = row['stability_wins_iff']['right_side_costs']
        assert left['width_gain_coefficient'] == 0.00027
        assert left['anchor_buffer_gain_coefficient'] == 0.00013
        assert left['knife_edge_separation_gain_coefficient'] == 0.000122
        assert right['anchor_delta_cost_coefficient'] == 0.00142
        assert right['material_leader_loss_coefficient'] == 1
        assert right['additional_undecided_coefficient'] == 1
        assert right['additional_anchor_tie_coefficient'] == 1
        assert row['material_anchor'] == EXPECTED_MATERIAL
        assert row['stability_anchor'] == EXPECTED_STABILITY

    print('ok: rematch delta preference half-space snapshot')


if __name__ == '__main__':
    main()
