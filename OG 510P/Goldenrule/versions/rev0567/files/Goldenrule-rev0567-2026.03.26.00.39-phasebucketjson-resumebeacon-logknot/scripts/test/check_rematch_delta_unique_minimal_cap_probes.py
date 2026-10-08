#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report['headline_findings']
    assert findings['stability_anchor'] == 'TTTMMMMUU'
    assert findings['material_anchor'] == 'TTTMMMMMU'
    assert findings['strict_trajectory_class_count_when_w_hazard_gt_0'] == 4
    assert findings['universally_required_boundary_thresholds_in_order'] == [
        '-0.000463764',
        '0.000033068',
        '0.000313597',
    ]
    assert findings['universal_separation_rule_for_adjacent_open_classes'] == (
        'to distinguish two adjacent strict rho classes for every rho in both classes using only strict winner symbols, some probe threshold must equal their shared boundary exactly'
    )
    assert findings['unique_minimal_sufficient_probe_caps_when_using_strict_winner_symbols'] == [10, 20, 10000]
    assert findings['why_the_probe_set_is_unique'] == (
        'each of the three adjacent class boundaries requires an exact threshold witness, and the only caps realizing tau(10), tau(10000), and tau(20) exactly are 10, 10000, and 20 respectively'
    )

    rows = report['boundary_necessity_rows']
    assert [row['adjacent_class_pair'] for row in rows] == [
        ['material_all_checked_caps', 'low_cap_stability_then_material'],
        ['low_cap_stability_then_material', 'stability_then_mid_cap_material_then_tail_stability'],
        ['stability_then_mid_cap_material_then_tail_stability', 'stability_all_checked_caps'],
    ]
    assert [row['required_exact_threshold_name'] for row in rows] == ['tau(10)', 'tau(10000)', 'tau(20)']
    assert [row['caps_realizing_required_threshold_exactly'] for row in rows] == [[10], [10000], [20]]

    witnesses = report['supporting_threshold_witnesses']
    assert witnesses == {
        'tau_at_cap_10': -0.000464,
        'tau_at_cap_20': 0.000314,
        'tau_at_cap_10000': 0.000033,
        'caps_realizing_tau_at_cap_10_exactly': [10],
        'caps_realizing_tau_at_cap_20_exactly': [20],
        'caps_realizing_tau_at_cap_10000_exactly': [10000],
    }

    print('ok: rematch delta unique minimal cap probes snapshot')


if __name__ == '__main__':
    main()
