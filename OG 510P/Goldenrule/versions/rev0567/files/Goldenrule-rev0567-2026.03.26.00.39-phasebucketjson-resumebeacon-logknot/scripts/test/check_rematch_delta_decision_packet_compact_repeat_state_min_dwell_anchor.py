#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.json'
MIN_DWELL_REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_min_dwell_anchor_snapshot')
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()
    assert report == rebuilt

    packet_text = PACKET_PATH.read_text()
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(' in packet_text
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_metrics(' in packet_text
    assert 'def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor(' in packet_text

    min_dwell_report = json.loads(MIN_DWELL_REPORT_PATH.read_text())
    frontier = {'frontier_rows': min_dwell_report['frontier_rows']}

    ninety_nine = packet.recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(
        frontier,
        minimum_gain_share_of_full_dynamic_savings=0.99,
    )
    assert ninety_nine['anchor_minimum_dwell_unique_appends'] == 4
    assert ninety_nine['anchor_margin_unique_appends'] == 2
    assert ninety_nine['minimum_dwell_start_unique_appends'] == 2
    assert ninety_nine['minimum_dwell_end_unique_appends'] == 6
    assert ninety_nine['selected_transition_count'] == 11
    assert ninety_nine['gain_share_of_full_dynamic_savings'] == 0.999822

    ninety_five = packet.recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(
        frontier,
        minimum_gain_share_of_full_dynamic_savings=0.95,
    )
    assert ninety_five['anchor_minimum_dwell_unique_appends'] == 13
    assert ninety_five['anchor_margin_unique_appends'] == 5
    assert ninety_five['minimum_dwell_start_unique_appends'] == 8
    assert ninety_five['minimum_dwell_end_unique_appends'] == 18
    assert ninety_five['selected_transition_count'] == 5
    assert ninety_five['gain_share_of_full_dynamic_savings'] == 0.980481
    assert ninety_five['regret_vs_unbounded_dynamic'] == 217.295277

    eighty_five = packet.recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(
        frontier,
        minimum_gain_share_of_full_dynamic_savings=0.85,
    )
    assert eighty_five['anchor_minimum_dwell_unique_appends'] == 33
    assert eighty_five['anchor_margin_unique_appends'] == 14
    assert eighty_five['minimum_dwell_start_unique_appends'] == 19
    assert eighty_five['minimum_dwell_end_unique_appends'] == 48
    assert eighty_five['selected_transition_count'] == 3
    assert eighty_five['gain_share_of_full_dynamic_savings'] == 0.870482

    zero = packet.recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(
        frontier,
        minimum_gain_share_of_full_dynamic_savings=0.0,
    )
    assert zero['anchor_minimum_dwell_unique_appends'] == 157
    assert zero['anchor_margin_unique_appends'] == 100
    assert zero['minimum_dwell_start_unique_appends'] == 57
    assert zero['minimum_dwell_end_unique_appends'] == 257
    assert zero['selected_transition_count'] == 0
    assert zero['gain_share_of_full_dynamic_savings'] == 0.0

    findings = report['headline_findings']
    assert findings['frontier_regime_count'] == 7
    assert findings['ninety_nine_percent_anchor_minimum_dwell_unique_appends'] == 4
    assert findings['ninety_five_percent_anchor_minimum_dwell_unique_appends'] == 13
    assert findings['ninety_five_percent_anchor_margin_unique_appends'] == 5
    assert findings['ninety_five_percent_anchor_transition_count'] == 5
    assert findings['eighty_five_percent_anchor_minimum_dwell_unique_appends'] == 33
    assert findings['eighty_five_percent_anchor_transition_count'] == 3
    assert findings['zero_percent_anchor_minimum_dwell_unique_appends'] == 157
    assert findings['zero_percent_anchor_margin_unique_appends'] == 100

    print('compact repeat-state minimum-dwell anchors are internally consistent')


if __name__ == '__main__':
    main()
