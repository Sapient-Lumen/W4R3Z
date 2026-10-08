#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_route_block_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def _plan_core(plan: dict[str, object]) -> dict[str, object]:
    core: dict[str, object] = {
        'recommended_write_kind': plan['recommended_write_kind'],
        'semantic_fingerprint': plan['semantic_fingerprint'],
    }
    if 'catalog_slot' in plan:
        core['catalog_slot'] = plan['catalog_slot']
    if 'reference' in plan:
        core['reference'] = plan['reference']
    if 'body' in plan:
        core['body'] = plan['body']
    return core



def _lookup_bytes(packet, fingerprint: str, pages: list[str], route_blocks: list[str], page_bytes: list[int], route_block_bytes: list[int]) -> tuple[int, int, int | None]:
    target_digest = packet._fingerprint_digest_bytes(fingerprint)
    block_index = target_digest[0] >> 4
    bytes_touched = route_block_bytes[block_index]
    candidate_pages = packet.fingerprint_catalog_route_block_candidate_pages(
        fingerprint,
        route_blocks,
        page_count=len(pages),
    )
    false_positive_pages = 0
    for page_index in candidate_pages:
        bytes_touched += page_bytes[page_index]
        payload, entry_count = packet._decode_fingerprint_catalog_page_payload(pages[page_index])
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return bytes_touched, false_positive_pages, page_index * packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE + entry_index
        false_positive_pages += 1
    return bytes_touched, false_positive_pages, None



def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(known_fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    page_filters = packet.fingerprint_catalog_page_filters(pages)
    route_blocks = packet.fingerprint_catalog_page_route_blocks(pages)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]
    route_block_bytes = [packet.packet_minified_bytes(route_block) for route_block in route_blocks]

    exact_match_count = 0
    total_route_lookup_bytes = 0
    total_filtered_lookup_bytes = 0
    false_positive_distribution: dict[str, int] = {}
    route_block_index_distribution: dict[str, int] = {}

    for row in deterministic_packets:
        standalone = row['packet']
        filtered_plan = packet.packet_archive_yocto_write_plan_from_pages_with_filters(standalone, pages, page_filters)
        routed_plan = packet.packet_archive_yocto_write_plan_from_pages_with_route_blocks(standalone, pages, route_blocks)
        if _plan_core(filtered_plan) == _plan_core(routed_plan):
            exact_match_count += 1
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        lookup_bytes, false_positive_pages, slot = _lookup_bytes(packet, fingerprint, pages, route_blocks, page_bytes, route_block_bytes)
        assert slot is not None
        total_route_lookup_bytes += lookup_bytes
        value = packet._fingerprint_digest_bytes(fingerprint)[0]
        route_block_index_distribution[str(value >> 4)] = route_block_index_distribution.get(str(value >> 4), 0) + 1
        false_positive_distribution[str(false_positive_pages)] = false_positive_distribution.get(str(false_positive_pages), 0) + 1

        filtered_lookup_bytes = 0
        for page_index, page_filter in enumerate(page_filters):
            filtered_lookup_bytes += packet.packet_minified_bytes(page_filter)
            entry_count, mask = packet._decode_fingerprint_catalog_page_filter_payload(page_filter)
            if not mask[value >> 3] & (1 << (value & 7)):
                continue
            filtered_lookup_bytes += page_bytes[page_index]
            payload, payload_entry_count = packet._decode_fingerprint_catalog_page_payload(pages[page_index])
            assert payload_entry_count == entry_count
            found = False
            for entry_index in range(entry_count):
                start = entry_index * 32
                if payload[start : start + 32] == packet._fingerprint_digest_bytes(fingerprint):
                    found = True
                    break
            if found:
                break
        total_filtered_lookup_bytes += filtered_lookup_bytes

    average_route_lookup_bytes = total_route_lookup_bytes / len(deterministic_packets)
    average_filtered_lookup_bytes = total_filtered_lookup_bytes / len(deterministic_packets)
    full_compact_state_with_filters_bytes = packet.packet_minified_bytes(pages) + packet.packet_minified_bytes(page_filters)
    full_compact_state_with_route_blocks_bytes = packet.packet_minified_bytes(pages) + packet.packet_minified_bytes(route_blocks)

    assert report['deterministic_frontier_packet_count'] == 274
    assert report['headline_findings']['exact_repeat_plan_core_matches'] == 274
    assert round(average_route_lookup_bytes, 6) == report['headline_findings']['average_repeat_lookup_bytes_with_route_blocks']
    assert round(average_filtered_lookup_bytes, 6) == report['headline_findings']['average_repeat_lookup_bytes_with_filters']
    assert report['headline_findings']['full_compact_state_with_filters_bytes'] == full_compact_state_with_filters_bytes
    assert report['headline_findings']['full_compact_state_with_route_blocks_bytes'] == full_compact_state_with_route_blocks_bytes
    assert report['headline_findings']['route_block_state_bytes_delta_vs_filters'] == full_compact_state_with_route_blocks_bytes - full_compact_state_with_filters_bytes
    assert report['headline_findings']['route_block_index_distribution'] == route_block_index_distribution
    assert report['headline_findings']['false_positive_page_distribution'] == false_positive_distribution

    novel_packet = packet.packet_from_coordinates('0.125', '0.375')
    novel_fingerprint = packet.packet_semantic_fingerprint(novel_packet)
    appended_route_blocks = packet.append_fingerprint_catalog_page_route_blocks(route_blocks, pages, novel_fingerprint)
    appended_pages = packet.append_fingerprint_catalog_pages(pages, novel_fingerprint)
    changed_block_indices = [
        index
        for index, (before, after) in enumerate(zip(route_blocks, appended_route_blocks))
        if before != after
    ]
    append_example = report['append_locality_example']
    target_block = packet._fingerprint_digest_bytes(novel_fingerprint)[0] >> 4
    assert append_example['novel_fingerprint'] == novel_fingerprint
    assert append_example['changed_block_indices'] == changed_block_indices
    assert append_example['appended_route_blocks_match_rebuild'] is True
    assert append_example['route_block_bytes_before'] == packet.packet_minified_bytes(route_blocks[target_block])
    assert append_example['route_block_bytes_after'] == packet.packet_minified_bytes(appended_route_blocks[target_block])
    assert append_example['tail_page_bytes_before'] == packet.packet_minified_bytes(pages[-1])
    assert append_example['tail_page_bytes_after'] == packet.packet_minified_bytes(appended_pages[-1])

    sample_rows = {row['index']: row for row in report['sample_rows']}
    assert sample_rows[0]['lookup_bytes_with_route_blocks'] >= packet.packet_minified_bytes(route_blocks[0])
    assert sample_rows[256]['route_block_plan_core']['recommended_write_kind'] == 'short_catalog_reference'

    print('catalog route-block snapshot is internally consistent')


if __name__ == '__main__':
    main()
