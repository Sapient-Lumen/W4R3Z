#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_min_dwell_repeat_uncertainty_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()
    assert report == rebuilt
    packet_text = PACKET_PATH.read_text()
    assert 'def _compact_repeat_state_preserved_gain_share(' in packet_text
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_under_repeat_uncertainty_from_metrics(' in packet_text
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_under_repeat_uncertainty(' in packet_text
    findings = report['headline_findings']
    assert findings['entry_count'] == 274
    assert findings['page_count'] == 18
    assert findings['route_block_bitmap_len'] == 3
    assert findings['ninety_nine_percent_overlap_end_unique_appends'] == 2
    assert findings['ninety_five_percent_anchor_minimum_dwell_unique_appends'] == 9
    assert findings['ninety_five_percent_anchor_margin_unique_appends'] == 8
    assert findings['ninety_five_percent_worst_case_gain_share_of_full_dynamic_savings'] == 0.980481
    assert findings['ninety_five_percent_minimum_selected_transition_count'] == 2
    assert findings['ninety_five_percent_maximum_selected_transition_count'] == 5
    assert findings['eighty_five_percent_anchor_minimum_dwell_unique_appends'] == 16
    assert findings['eighty_five_percent_anchor_margin_unique_appends'] == 15
    assert findings['eighty_five_percent_minimum_selected_transition_count'] == 0
    assert findings['eighty_five_percent_maximum_selected_transition_count'] == 5
    uncertainty_rows = {row['minimum_gain_share_of_full_dynamic_savings']: row for row in report['uncertainty_rows']}
    assert uncertainty_rows[0.99]['anchor_minimum_dwell_unique_appends'] == 1
    assert uncertainty_rows[0.95]['anchor_minimum_dwell_unique_appends'] == 9
    assert uncertainty_rows[0.85]['anchor_minimum_dwell_unique_appends'] == 16
    assert uncertainty_rows[0.95]['anchor_rows'][1]['interval_summary'].startswith('pages 0–23; filters 24–62')
    assert uncertainty_rows[0.85]['anchor_rows'][0]['interval_summary'] == 'pages 0–256'
    print('compact repeat-state repeat-uncertainty dwell anchors are internally consistent')


if __name__ == '__main__':
    main()
