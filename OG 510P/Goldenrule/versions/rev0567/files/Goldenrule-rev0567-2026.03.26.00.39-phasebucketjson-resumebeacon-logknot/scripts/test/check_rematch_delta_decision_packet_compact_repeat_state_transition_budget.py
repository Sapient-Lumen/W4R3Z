#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_transition_budget_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()
    assert report == rebuilt

    packet_text = PACKET_PATH.read_text()
    assert 'def fingerprint_catalog_compact_repeat_state_transition_budget_frontier_from_metrics(' in packet_text
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_budget_from_metrics(' in packet_text

    findings = report['headline_findings']
    assert findings['entry_count'] == 274
    assert findings['page_count'] == 18
    assert findings['dynamic_transition_count'] == 12
    assert findings['first_switch_gain_vs_fixed_route_blocks_bytes'] == 5679.676082
    assert findings['third_switch_gain_vs_second_budget_bytes'] == 2920.473524
    assert findings['first_four_switch_gain_share_of_full_dynamic_savings'] == 0.968419
    assert findings['fifth_switch_gain_bytes'] == 134.276182
    assert findings['sixth_switch_gain_bytes'] == 1.979428
    assert findings['practical_transition_budget_ceiling'] == 4

    frontier_rows = {row['budget_start_transition_count']: row for row in report['frontier_rows']}
    assert frontier_rows[0]['selected_transition_count'] == 0
    assert frontier_rows[1]['interval_summary'] == 'pages 0–55; route-blocks 56–256'
    assert frontier_rows[3]['objective_improvement_vs_previous_budget'] == 2920.473524
    assert frontier_rows[4]['gain_share_of_full_dynamic_savings'] == 0.968419
    assert frontier_rows[12]['budget_end_transition_count'] == 256
    assert frontier_rows[12]['regret_vs_unbounded_dynamic'] == 0.0

    reference_rows = {row['max_transition_count']: row for row in report['reference_budget_rows']}
    assert reference_rows[0]['selected_transition_count'] == 0
    assert reference_rows[1]['selected_transition_count'] == 1
    assert reference_rows[4] == {
        'max_transition_count': 4,
        'effective_max_transition_count': 4,
        'selected_transition_count': 4,
        'cumulative_objective_without_transition_penalty': 4829310.414246,
        'regret_vs_unbounded_dynamic': 351.571459,
        'objective_improvement_vs_previous_budget': 1090.254986,
        'recommended_state_counts': {
            'paged_catalog_only': 56,
            'paged_catalog_with_filters': 66,
            'paged_catalog_with_route_blocks': 135,
        },
        'interval_summary': 'pages 0–55; route-blocks 56–110; filters 111–158; route-blocks 159–238; filters 239–256',
    }
    assert reference_rows[256]['selected_transition_count'] == 12
    assert reference_rows[256]['regret_vs_unbounded_dynamic'] == 0.0

    print('compact repeat-state transition-budget snapshot is internally consistent')


if __name__ == '__main__':
    main()
