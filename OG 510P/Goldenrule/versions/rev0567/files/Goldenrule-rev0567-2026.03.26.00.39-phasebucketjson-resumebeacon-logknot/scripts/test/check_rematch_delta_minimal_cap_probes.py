#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_minimal_cap_probe_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report['headline_findings']
    assert findings['stability_anchor'] == 'TTTMMMMUU'
    assert findings['material_anchor'] == 'TTTMMMMMU'
    assert findings['strict_trajectory_class_count_when_w_hazard_gt_0'] == 4
    assert findings['minimum_probe_count_needed_for_strict_classification'] == 3
    assert findings['why_two_probes_are_globally_insufficient'] == (
        'for any ordered threshold pair tau(a) and tau(b), only three strict winner signatures are realizable because one mixed pattern is impossible'
    )
    assert findings['minimal_sufficient_probe_caps'] == [10, 20, 10000]
    thresholds = findings['ordered_probe_thresholds']
    assert thresholds == {
        'tau_at_cap_10': -0.000464,
        'tau_at_cap_20': 0.000314,
        'tau_at_cap_10000': 0.000033,
        'strict_order': 'tau(10) < tau(10000) < tau(20)',
    }
    assert findings['probe_signature_legend'] == {'S': 'TTTMMMMUU', 'M': 'TTTMMMMMU'}
    assert findings['recommended_three_probe_decision_order'] == [20, 10, 10000]

    rows = report['strict_class_probe_signatures']
    assert [row['class_label'] for row in rows] == [
        'material_all_checked_caps',
        'low_cap_stability_then_material',
        'stability_then_mid_cap_material_then_tail_stability',
        'stability_all_checked_caps',
    ]
    assert [row['signature_on_probe_caps_10_20_10000'] for row in rows] == ['MMM', 'SMM', 'SMS', 'SSS']

    pairs = report['two_probe_insufficiency_rows']
    pair_lookup = {tuple(row['probe_caps']): row for row in pairs}
    assert pair_lookup[(10, 20)]['realized_strict_signatures'] == ['MM', 'SM', 'SS']
    assert pair_lookup[(10, 20)]['strict_signature_count'] == 3
    assert pair_lookup[(10, 10000)]['realized_strict_signatures'] == ['MM', 'SM', 'SS']
    assert pair_lookup[(10, 10000)]['strict_signature_count'] == 3
    assert pair_lookup[(20, 10000)]['realized_strict_signatures'] == ['MM', 'MS', 'SS']
    assert pair_lookup[(20, 10000)]['strict_signature_count'] == 3

    tree = report['three_probe_decision_tree']
    assert tree == [
        {'step': 1, 'probe_cap': 20, 'if_symbol_is_S': 'stability_all_checked_caps', 'if_symbol_is_M': 'go_to_step_2'},
        {'step': 2, 'probe_cap': 10, 'if_symbol_is_M': 'material_all_checked_caps', 'if_symbol_is_S': 'go_to_step_3'},
        {
            'step': 3,
            'probe_cap': 10000,
            'if_symbol_is_S': 'stability_then_mid_cap_material_then_tail_stability',
            'if_symbol_is_M': 'low_cap_stability_then_material',
        },
    ]

    print('ok: rematch delta minimal cap probes snapshot')


if __name__ == '__main__':
    main()
