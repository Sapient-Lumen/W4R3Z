#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_switch_penalty_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()
    assert report == rebuilt

    packet_text = PACKET_PATH.read_text()
    assert 'def fingerprint_catalog_compact_repeat_state_switch_penalty_frontier_from_metrics(' in packet_text
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_penalty_from_metrics(' in packet_text

    findings = report['headline_findings']
    assert findings['entry_count'] == 274
    assert findings['page_count'] == 18
    assert findings['frontier_regime_count'] == 9
    assert findings['micro_churn_ceiling_bytes'] == 45.40069
    assert findings['focal_transition_count'] == 4
    assert findings['focal_advantage_vs_fixed_route_blocks_bytes'] == 7069.915895
    assert findings['fixed_route_blocks_only_after_transition_penalty_bytes'] == 5679.676082

    frontier_rows = {row['transition_count']: row for row in report['frontier_rows']}
    assert frontier_rows[12]['transition_penalty_end_bytes'] == 1.979429
    assert frontier_rows[5]['transition_penalty_start_bytes'] == 45.40069
    assert frontier_rows[4]['transition_penalty_end_bytes'] == 1090.254986
    assert frontier_rows[1]['transition_penalty_start_bytes'] == 2005.364255
    assert frontier_rows[0]['state_counts'] == {
        'paged_catalog_only': 0,
        'paged_catalog_with_filters': 0,
        'paged_catalog_with_route_blocks': 257,
    }

    reference_rows = {row['transition_penalty_per_switch_bytes']: row for row in report['reference_transition_penalty_rows']}
    assert reference_rows[50.0]['transition_count'] == 5
    assert reference_rows[200.0]['transition_count'] == 4
    assert reference_rows[927.685921] == {
        'transition_penalty_per_switch_bytes': 927.685921,
        'transition_count': 4,
        'state_counts': {
            'paged_catalog_only': 56,
            'paged_catalog_with_filters': 66,
            'paged_catalog_with_route_blocks': 135,
        },
        'cumulative_objective_with_transition_penalty': 4833021.15793,
        'active_transition_penalty_start_bytes': 134.276182,
        'active_transition_penalty_end_bytes': 1090.254986,
        'summary': 'robust mid-cost regime: stay bare until append 56, then route blocks, filters at the first cliff, route blocks, filters',
    }
    assert reference_rows[6000.0]['transition_count'] == 0

    print('compact repeat-state switch-penalty snapshot is internally consistent')


if __name__ == '__main__':
    main()
