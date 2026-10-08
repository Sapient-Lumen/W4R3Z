#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_resolution_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text())

    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    ordered = packet.ordered_fingerprint_catalog(known_fingerprints)
    pages = packet.fingerprint_catalog_pages(ordered, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]
    page_entry_counts = [packet.fingerprint_catalog_page_entry_count(page) for page in pages]
    average_touched_page_bytes = sum(count * page_bytes[index] for index, count in enumerate(page_entry_counts)) / len(ordered)

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(ordered) == 274
    assert report['headline_findings']['page_size'] == packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE == 16
    assert report['headline_findings']['page_count'] == 18
    assert report['headline_findings']['page_bytes'] == [686] * 17 + [89]
    assert report['headline_findings']['page_entry_counts'] == [16] * 17 + [2]
    assert report['headline_findings']['string_catalog_bytes'] == 20277
    assert report['headline_findings']['paged_catalog_bytes'] == 11770
    assert report['headline_findings']['average_resolution_touched_page_bytes'] == 681.642336
    assert report['headline_findings']['max_resolution_touched_page_bytes'] == 686
    assert report['headline_findings']['tail_resolution_touched_page_bytes'] == 89
    assert report['headline_findings']['average_bytes_avoided_vs_string_catalog'] == 19595.357664
    assert report['headline_findings']['average_bytes_avoided_share_vs_string_catalog'] == 0.966383
    assert report['headline_findings']['average_bytes_avoided_vs_full_paged_catalog'] == 11088.357664
    assert report['headline_findings']['average_bytes_avoided_share_vs_full_paged_catalog'] == 0.942086

    assert packet.fingerprint_catalog_page_entry_count(pages[0]) == 16
    assert packet.fingerprint_catalog_page_entry_count(pages[-1]) == 2
    assert round(average_touched_page_bytes, 6) == report['headline_findings']['average_resolution_touched_page_bytes']

    for slot in [0, 63, 64, 127, 128, 255, 256, 273]:
        resolved = packet.resolve_fingerprint_catalog_slot_from_pages(
            slot,
            pages,
            page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        )
        assert resolved == ordered[slot]
        short_reference = packet._base64url_encode_bytes(
            bytes([packet.SHORT_CATALOG_REFERENCE_PREFIX | (slot >> 8), slot & 0xFF])
        )
        catalog_reference = packet._base64url_encode_bytes(bytes([packet.CATALOG_REFERENCE_TAG]) + packet._encode_uvarint(slot))
        assert packet.resolve_archive_any_catalog_reference_from_pages(short_reference, pages) == ordered[slot]
        assert packet.resolve_archive_any_catalog_reference_from_pages(catalog_reference, pages) == ordered[slot]

    sample_rows = {row['slot']: row for row in report['sample_rows']}
    assert sample_rows[0]['page_index'] == 0
    assert sample_rows[63]['entry_index'] == 15
    assert sample_rows[64]['page_index'] == 4
    assert sample_rows[127]['entry_index'] == 15
    assert sample_rows[128]['page_index'] == 8
    assert sample_rows[255]['page_index'] == 15
    assert sample_rows[256]['page_index'] == 16
    assert sample_rows[273]['entry_index'] == 1
    assert sample_rows[273]['page_bytes'] == 89
    assert sample_rows[273]['resolved_from_pages_via_short_reference'] == ordered[273]
    assert sample_rows[273]['resolved_from_pages_via_catalog_reference'] == ordered[273]

    try:
        packet.resolve_fingerprint_catalog_slot_from_pages(-1, pages)
    except packet.PacketError:
        pass
    else:
        raise AssertionError('negative slots must be rejected')

    try:
        packet.resolve_fingerprint_catalog_slot_from_pages(len(ordered), pages)
    except packet.PacketError:
        pass
    else:
        raise AssertionError('out-of-range slots must be rejected')

    print('decision-packet-catalog-page-resolution: ok')


if __name__ == '__main__':
    main()
