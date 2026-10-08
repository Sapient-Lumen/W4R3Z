#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_oracle_snapshot_20260306.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_oracle.py'


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    report = _load_json(REPORT_PATH)
    oracle = _load_oracle_module()

    assert report['focus'] == (
        'Turn the family10 projective decision cone into a small executable oracle so inheritors can classify directly from declared weights or direct (B,H) coordinates instead of re-deriving the handoff rules from multiple reports.'
    )
    findings = report['headline_findings']
    assert findings['oracle_script'] == 'scripts/analysis/rematch_proxy_delta_decision_oracle.py'
    assert findings['accepted_input_modes'] == ['projective_coordinates', 'weights']
    assert findings['projective_coordinate_mode_requires'] == ['B', 'H']
    assert findings['weight_mode_requires'] == [
        'w_width', 'w_buffer', 'w_knife', 'w_delta', 'w_material', 'w_undecided', 'w_ties', 'w_hazard'
    ]
    assert findings['zero_probe_when_weights_declared'] is True
    assert findings['black_box_probes_are_fallback_only'] is True
    assert findings['checked_caps'] == [10, 20, 10000]
    assert findings['exact_thresholds'] == [
        {'boundary_name': 'tau(10)', 'cap': 10, 'value': '-0.000463764'},
        {'boundary_name': 'tau(10000)', 'cap': 10000, 'value': '0.000033068'},
        {'boundary_name': 'tau(20)', 'cap': 20, 'value': '0.000313597'},
    ]
    assert findings['baseline_nonhazard_surplus_expression'] == (
        '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties'
    )
    assert findings['closure_labels_supported'] == ['MMM', 'SMM', 'SMS', 'SSS', 'TIE_tau10', 'TIE_tau10000', 'TIE_tau20', 'TIE_origin']
    assert findings['most_compact_handoff_rule'] == (
        'run the oracle directly when declared weights or direct (B,H) coordinates are available; only route to probe contracts when the final choice must be diagnosed from winner symbols alone'
    )

    direct_rows = report['sample_projective_coordinate_invocations']
    assert [row['example_label'] for row in direct_rows] == [
        'robust_material_from_zero_hazard_axis',
        'single_reversal_from_positive_hazard_cone',
        'double_reversal_from_positive_hazard_cone',
        'tie_at_cap_20_boundary_ray',
    ]
    for row in direct_rows:
        rerun = oracle.classify_from_direct_coordinates(row['input']['B'], row['input']['H'])
        assert rerun == row['oracle_result']
        assert rerun['closure_label'] == row['expected_closure_label']

    weight_row = report['sample_weight_invocation']
    rerun_weight = oracle.classify_from_weights(weight_row['input'])
    assert rerun_weight == weight_row['oracle_result']
    assert rerun_weight['baseline_nonhazard_surplus'] == '0.000000'
    assert rerun_weight['closure_label'] == 'SMM'
    assert rerun_weight['declared_weights']['w_hazard'] == '1'

    tie10 = oracle.classify_from_direct_coordinates('-0.000463764', '1')
    assert tie10['closure_label'] == 'TIE_tau10'
    assert tie10['checked_cap_outcomes'] == [
        {'cap': 10, 'outcome': 'tie', 'winner': None},
        {'cap': 20, 'outcome': 'strict_winner', 'winner': 'TTTMMMMMU'},
        {'cap': 10000, 'outcome': 'strict_winner', 'winner': 'TTTMMMMMU'},
    ]

    origin = oracle.classify_from_direct_coordinates('0', '0')
    assert origin['closure_label'] == 'TIE_origin'
    assert origin['checked_cap_outcomes'] == [
        {'cap': 10, 'outcome': 'tie', 'winner': None},
        {'cap': 20, 'outcome': 'tie', 'winner': None},
        {'cap': 10000, 'outcome': 'tie', 'winner': None},
    ]

    print('decision-oracle: ok')


if __name__ == '__main__':
    main()
