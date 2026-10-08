#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_growth_snapshot_20260307.json'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_growth_snapshot')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()

    assert report == rebuilt
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)

    assert packet.project_fingerprint_catalog_compact_repeat_state(pages, unique_append_count=0) == {
        'unique_append_count': 0,
        'entry_count': 274,
        'page_count': 18,
        'tail_entry_count': 2,
        'route_block_bitmap_len': 3,
        'rows': {
            'paged_catalog_only': {'kind': 'paged_catalog_only', 'compact_state_bytes': 11770, 'extra_sidecar_state_bytes': 0},
            'paged_catalog_with_filters': {'kind': 'paged_catalog_with_filters', 'compact_state_bytes': 12653, 'extra_sidecar_state_bytes': 883},
            'paged_catalog_with_route_blocks': {'kind': 'paged_catalog_with_route_blocks', 'compact_state_bytes': 12891, 'extra_sidecar_state_bytes': 1121},
        },
    }
    assert packet.project_fingerprint_catalog_compact_repeat_state(pages, unique_append_count=79)['rows']['paged_catalog_with_route_blocks']['compact_state_bytes'] == 16283
    assert packet.project_fingerprint_catalog_compact_repeat_state(pages, unique_append_count=79)['rows']['paged_catalog_with_filters']['compact_state_bytes'] == 16290
    assert packet.project_fingerprint_catalog_compact_repeat_state(pages, unique_append_count=111)['rows']['paged_catalog_with_route_blocks']['extra_sidecar_state_bytes'] == 1457

    growth = packet.fingerprint_catalog_compact_repeat_state_growth_events(pages, max_unique_appends=256)
    assert growth['entry_count'] == 274
    assert growth['page_count'] == 18
    assert growth['tail_entry_count'] == 2
    assert growth['route_block_bitmap_len'] == 3
    assert len(growth['event_rows']) == 16

    first_flip = next(row for row in growth['event_rows'] if 'filter_route_state_order_flip' in row['event_kinds'])
    assert first_flip['unique_append_count'] == 79
    assert first_flip['page_count'] == 23
    assert first_flip['filter_minus_route_compact_state_bytes'] == 7

    first_cliff = next(row for row in growth['event_rows'] if 'route_block_bitmap_cliff' in row['event_kinds'])
    assert first_cliff['unique_append_count'] == 111
    assert first_cliff['route_blocks_extra_sidecar_state_bytes'] == 1457
    assert first_cliff['filter_minus_route_compact_state_bytes'] == -231

    findings = report['headline_findings']
    assert findings['first_page_birth_unique_appends'] == 15
    assert findings['first_page_birth_filter_sidecar_delta_bytes'] == 49
    assert findings['first_route_state_flip_unique_appends'] == 79
    assert findings['first_route_bitmap_cliff_unique_appends'] == 111
    assert findings['route_blocks_state_cheaper_interval_before_first_cliff'] == {
        'start_unique_appends': 79,
        'end_unique_appends': 110,
    }
    assert findings['second_route_state_flip_unique_appends'] == 191
    assert findings['second_route_bitmap_cliff_unique_appends'] == 239

    print('compact repeat-state growth snapshot is internally consistent')


if __name__ == '__main__':
    main()
