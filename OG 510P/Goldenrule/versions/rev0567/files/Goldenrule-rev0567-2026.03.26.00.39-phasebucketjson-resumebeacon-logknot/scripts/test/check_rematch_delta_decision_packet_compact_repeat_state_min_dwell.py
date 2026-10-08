#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_min_dwell_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()
    assert report == rebuilt

    packet_text = PACKET_PATH.read_text()
    assert 'def fingerprint_catalog_compact_repeat_state_min_dwell_frontier_from_metrics(' in packet_text
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_min_dwell_from_metrics(' in packet_text

    findings = report['headline_findings']
    assert findings['entry_count'] == 274
    assert findings['page_count'] == 18
    assert findings['frontier_regime_count'] == 7
    assert findings['dynamic_transition_count'] == 12
    assert findings['min_dwell_two_suppresses_one_step_cliffs_transition_count'] == 11
    assert findings['min_dwell_eight_transition_count'] == 5
    assert findings['min_dwell_eight_regret_vs_unbounded_dynamic'] == 217.295277
    assert findings['min_dwell_eight_gain_share_of_full_dynamic_savings'] == 0.980481
    assert findings['min_dwell_nineteen_transition_count'] == 3
    assert findings['min_dwell_nineteen_gain_share_of_full_dynamic_savings'] == 0.870482
    assert findings['min_dwell_forty_nine_transition_count'] == 1
    assert findings['min_dwell_forty_nine_gain_share_of_full_dynamic_savings'] == 0.510201
    assert findings['route_blocks_only_threshold_minimum_dwell_unique_appends'] == 57
    assert findings['practical_default_minimum_dwell_unique_appends'] == 8

    frontier_rows = {row['minimum_dwell_start_unique_appends']: row for row in report['frontier_rows']}
    assert frontier_rows[1]['selected_transition_count'] == 12
    assert frontier_rows[2]['minimum_dwell_end_unique_appends'] == 6
    assert frontier_rows[7]['selected_transition_count'] == 9
    assert frontier_rows[8]['interval_summary'] == 'pages 0–23; filters 24–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256'
    assert frontier_rows[19]['selected_transition_count'] == 3
    assert frontier_rows[49]['cumulative_gain_vs_fixed_route_blocks'] == 5679.676082
    assert frontier_rows[57]['selected_transition_count'] == 0
    assert frontier_rows[57]['minimum_dwell_end_unique_appends'] == 257

    reference_rows = {row['minimum_dwell_unique_appends']: row for row in report['reference_rows']}
    assert reference_rows[1]['selected_transition_count'] == 12
    assert reference_rows[2]['selected_transition_count'] == 11
    assert reference_rows[8] == {
        'minimum_dwell_unique_appends': 8,
        'effective_minimum_dwell_unique_appends': 8,
        'selected_transition_count': 5,
        'minimum_interval_dwell_unique_appends': 18,
        'cumulative_objective_without_transition_penalty': 4829176.138064,
        'regret_vs_unbounded_dynamic': 217.295277,
        'recommended_state_counts': {
            'paged_catalog_only': 24,
            'paged_catalog_with_filters': 115,
            'paged_catalog_with_route_blocks': 118,
        },
        'interval_summary': 'pages 0–23; filters 24–62; route-blocks 63–110; filters 111–158; route-blocks 159–238; filters 239–256',
    }
    assert reference_rows[57]['selected_transition_count'] == 0
    assert reference_rows[256]['selected_transition_count'] == 0

    print('compact repeat-state minimum-dwell snapshot is internally consistent')


if __name__ == '__main__':
    main()
