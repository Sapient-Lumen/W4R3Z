#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot_20260307.json'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    builder = _load_module(REPORT_BUILDER_PATH, 'compact_repeat_state_staging_snapshot')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text())
    rebuilt = builder._build_summary()

    assert report == rebuilt
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)

    plan = packet.fingerprint_catalog_compact_repeat_state_budget_staging_plan(
        pages,
        expected_repeat_lookups=0.18,
        max_unique_appends=256,
    )
    assert plan['entry_count'] == 274
    assert plan['page_count'] == 18
    assert plan['tail_entry_count'] == 2
    assert plan['route_block_bitmap_len'] == 3
    assert plan['interval_rows'] == [
        {'start_unique_appends': 0, 'recommended_state_kind': 'paged_catalog_only', 'start_page_count': 18, 'start_tail_entry_count': 2, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 8, 'end_page_count': 18, 'end_tail_entry_count': 10, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 9, 'recommended_state_kind': 'paged_catalog_with_filters', 'start_page_count': 18, 'start_tail_entry_count': 11, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 14, 'end_page_count': 18, 'end_tail_entry_count': 16, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 15, 'recommended_state_kind': 'paged_catalog_only', 'start_page_count': 19, 'start_tail_entry_count': 1, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 23, 'end_page_count': 19, 'end_tail_entry_count': 9, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 24, 'recommended_state_kind': 'paged_catalog_with_filters', 'start_page_count': 19, 'start_tail_entry_count': 10, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 30, 'end_page_count': 19, 'end_tail_entry_count': 16, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 31, 'recommended_state_kind': 'paged_catalog_only', 'start_page_count': 20, 'start_tail_entry_count': 1, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 37, 'end_page_count': 20, 'end_tail_entry_count': 7, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 38, 'recommended_state_kind': 'paged_catalog_with_filters', 'start_page_count': 20, 'start_tail_entry_count': 8, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 46, 'end_page_count': 20, 'end_tail_entry_count': 16, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 47, 'recommended_state_kind': 'paged_catalog_only', 'start_page_count': 21, 'start_tail_entry_count': 1, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 53, 'end_page_count': 21, 'end_tail_entry_count': 7, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 54, 'recommended_state_kind': 'paged_catalog_with_filters', 'start_page_count': 21, 'start_tail_entry_count': 8, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 62, 'end_page_count': 21, 'end_tail_entry_count': 16, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 63, 'recommended_state_kind': 'paged_catalog_with_route_blocks', 'start_page_count': 22, 'start_tail_entry_count': 1, 'start_route_block_bitmap_len': 3, 'end_unique_appends': 110, 'end_page_count': 24, 'end_tail_entry_count': 16, 'end_route_block_bitmap_len': 3},
        {'start_unique_appends': 111, 'recommended_state_kind': 'paged_catalog_only', 'start_page_count': 25, 'start_tail_entry_count': 1, 'start_route_block_bitmap_len': 4, 'end_unique_appends': 111, 'end_page_count': 25, 'end_tail_entry_count': 1, 'end_route_block_bitmap_len': 4},
        {'start_unique_appends': 112, 'recommended_state_kind': 'paged_catalog_with_filters', 'start_page_count': 25, 'start_tail_entry_count': 2, 'start_route_block_bitmap_len': 4, 'end_unique_appends': 158, 'end_page_count': 27, 'end_tail_entry_count': 16, 'end_route_block_bitmap_len': 4},
        {'start_unique_appends': 159, 'recommended_state_kind': 'paged_catalog_with_route_blocks', 'start_page_count': 28, 'start_tail_entry_count': 1, 'start_route_block_bitmap_len': 4, 'end_unique_appends': 238, 'end_page_count': 32, 'end_tail_entry_count': 16, 'end_route_block_bitmap_len': 4},
        {'start_unique_appends': 239, 'recommended_state_kind': 'paged_catalog_with_filters', 'start_page_count': 33, 'start_tail_entry_count': 1, 'start_route_block_bitmap_len': 5, 'end_unique_appends': 256, 'end_page_count': 34, 'end_tail_entry_count': 2, 'end_route_block_bitmap_len': 5},
    ]
    assert len(plan['transition_rows']) == 12
    assert plan['transition_rows'][0] == {
        'unique_append_count': 9,
        'page_count': 18,
        'tail_entry_count': 11,
        'route_block_bitmap_len': 3,
        'from_state_kind': 'paged_catalog_only',
        'to_state_kind': 'paged_catalog_with_filters',
        'break_even_repeat_lookups': {
            'paged_catalog_only_to_filters': 0.179721,
            'filters_to_route_blocks': 0.62666,
            'paged_catalog_only_to_route_blocks': 0.211791,
        },
    }
    assert plan['transition_rows'][8] == {
        'unique_append_count': 111,
        'page_count': 25,
        'tail_entry_count': 1,
        'route_block_bitmap_len': 4,
        'from_state_kind': 'paged_catalog_with_route_blocks',
        'to_state_kind': 'paged_catalog_only',
        'break_even_repeat_lookups': {
            'paged_catalog_only_to_filters': 0.180291,
            'filters_to_route_blocks': 0.451561,
            'paged_catalog_only_to_route_blocks': 0.19927,
        },
    }

    findings = report['headline_findings']
    assert findings['interval_count'] == 13
    assert findings['baseline_break_even_repeat_lookups'] == {
        'paged_catalog_only_to_filters': 0.185996,
        'filters_to_route_blocks': 0.650001,
        'paged_catalog_only_to_route_blocks': 0.219221,
    }
    assert findings['first_filter_interval'] == {'start_unique_appends': 9, 'end_unique_appends': 14}
    assert findings['first_route_interval'] == {'start_unique_appends': 63, 'end_unique_appends': 110}
    assert findings['bitmap_cliff_page_reentry_interval'] == {'start_unique_appends': 111, 'end_unique_appends': 111}
    assert findings['filter_reentry_after_first_cliff'] == {'start_unique_appends': 112, 'end_unique_appends': 158}
    assert findings['second_route_interval'] == {'start_unique_appends': 159, 'end_unique_appends': 238}
    assert findings['final_filter_interval'] == {'start_unique_appends': 239, 'end_unique_appends': 256}

    threshold_rows = {row['unique_append_count']: row for row in report['threshold_rows']}
    assert threshold_rows[63]['break_even_repeat_lookups'] == {
        'paged_catalog_only_to_filters': 0.182601,
        'filters_to_route_blocks': 0.091192,
        'paged_catalog_only_to_route_blocks': 0.175991,
    }
    assert threshold_rows[63]['recommended_state_kind_at_expected_repeat_budget'] == 'paged_catalog_with_route_blocks'
    assert threshold_rows[111]['break_even_repeat_lookups'] == {
        'paged_catalog_only_to_filters': 0.180291,
        'filters_to_route_blocks': 0.451561,
        'paged_catalog_only_to_route_blocks': 0.19927,
    }
    assert threshold_rows[111]['recommended_state_kind_at_expected_repeat_budget'] == 'paged_catalog_only'
    assert threshold_rows[239]['recommended_state_kind_at_expected_repeat_budget'] == 'paged_catalog_with_filters'

    print('compact repeat-state staging snapshot is internally consistent')


if __name__ == '__main__':
    main()
