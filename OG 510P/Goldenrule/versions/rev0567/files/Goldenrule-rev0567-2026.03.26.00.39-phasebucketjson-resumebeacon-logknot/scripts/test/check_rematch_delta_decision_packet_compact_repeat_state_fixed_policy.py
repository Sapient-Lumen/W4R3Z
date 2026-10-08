#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.json'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_fixed_policy_snapshot')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()

    assert report == rebuilt
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)

    horizon_metrics = packet.fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=256,
    )
    assert horizon_metrics['entry_count'] == 274
    assert horizon_metrics['page_count'] == 18
    assert horizon_metrics['tail_entry_count'] == 2
    assert horizon_metrics['route_block_bitmap_len'] == 3
    assert len(horizon_metrics['append_rows']) == 257
    assert horizon_metrics['append_rows'][0]['rows']['paged_catalog_with_route_blocks'] == {
        'compact_state_bytes': 12891,
        'average_repeat_lookup_bytes': 1101.153285,
    }
    assert horizon_metrics['append_rows'][111]['rows']['paged_catalog_only']['compact_state_bytes'] == 16536

    focal_plan = packet.recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=0.18,
    )
    assert focal_plan['dynamic_total_objective'] == 4828958.842777
    assert focal_plan['dynamic_state_counts'] == {
        'paged_catalog_only': 33,
        'paged_catalog_with_filters': 96,
        'paged_catalog_with_route_blocks': 128,
    }
    assert focal_plan['dynamic_transition_count'] == 12
    assert focal_plan['best_fixed_state_kind'] == 'paged_catalog_with_route_blocks'
    assert focal_plan['best_fixed_total_objective'] == 4840091.073825
    assert focal_plan['best_fixed_regret_vs_dynamic'] == 11132.231048
    assert focal_plan['best_fixed_regret_per_append_state'] == 43.316074
    assert focal_plan['best_fixed_regret_share_of_dynamic_objective'] == 0.002305
    assert focal_plan['transition_penalty_break_even_per_switch_bytes'] == 927.685921

    fixed_rows = {row['state_kind']: row for row in focal_plan['fixed_rows']}
    assert fixed_rows['paged_catalog_only']['regret_vs_dynamic'] == 22369.741612
    assert fixed_rows['paged_catalog_with_filters']['regret_vs_dynamic'] == 15419.768937
    assert fixed_rows['paged_catalog_with_route_blocks']['exact_dynamic_match'] is False

    reference_budget_rows = {row['expected_repeat_lookups']: row for row in report['reference_budget_rows']}
    assert reference_budget_rows[0.1] == {
        'expected_repeat_lookups': 0.1,
        'dynamic_transition_count': 0,
        'dynamic_state_counts': {
            'paged_catalog_only': 257,
            'paged_catalog_with_filters': 0,
            'paged_catalog_with_route_blocks': 0,
        },
        'best_fixed_state_kind': 'paged_catalog_only',
        'best_fixed_regret_vs_dynamic': 0.0,
        'transition_penalty_break_even_per_switch_bytes': None,
        'exact_dynamic_match': True,
    }
    assert reference_budget_rows[0.2]['best_fixed_state_kind'] == 'paged_catalog_with_route_blocks'
    assert reference_budget_rows[0.2]['dynamic_transition_count'] == 4
    assert reference_budget_rows[0.2]['best_fixed_regret_vs_dynamic'] == 9417.3428
    assert reference_budget_rows[0.2]['transition_penalty_break_even_per_switch_bytes'] == 2354.3357
    assert reference_budget_rows[0.5]['dynamic_transition_count'] == 1
    assert reference_budget_rows[0.5]['best_fixed_regret_vs_dynamic'] == 744.469481
    assert reference_budget_rows[0.7]['exact_dynamic_match'] is True
    assert reference_budget_rows[0.7]['best_fixed_state_kind'] == 'paged_catalog_with_route_blocks'

    findings = report['headline_findings']
    assert findings['focal_dynamic_transition_count'] == 12
    assert findings['focal_best_fixed_state_kind'] == 'paged_catalog_with_route_blocks'
    assert findings['focal_transition_penalty_break_even_per_switch_bytes'] == 927.685921
    assert findings['first_exact_route_block_budget'] == 0.7

    print('compact repeat-state fixed-policy snapshot is internally consistent')


if __name__ == '__main__':
    main()
