#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_snapshot_20260307.json'


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
    monolith = packet.fingerprint_catalog_page(ordered)

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(ordered) == 274
    assert report['headline_findings']['page_size'] == packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE == 16
    assert report['headline_findings']['string_catalog_bytes'] == 20277
    assert report['headline_findings']['monolith_catalog_page_bytes'] == 11694
    assert report['headline_findings']['paged_catalog_bytes'] == 11770
    assert report['headline_findings']['total_bytes_saved_vs_strings'] == 8507
    assert report['headline_findings']['bytes_saved_share_vs_strings'] == 0.419539
    assert report['headline_findings']['monolith_bytes_saved_vs_strings'] == 8583
    assert report['headline_findings']['monolith_saved_share_vs_strings'] == 0.423287
    assert report['headline_findings']['page_count'] == 18
    assert report['headline_findings']['page_length_distribution'] == [686] * 17 + [89]
    assert report['headline_findings']['append_tail_old_page_bytes'] == 89
    assert report['headline_findings']['append_tail_new_page_bytes'] == 132
    assert report['headline_findings']['append_tail_growth_bytes'] == 43
    assert report['headline_findings']['appended_string_catalog_bytes'] == 20351
    assert report['headline_findings']['overflow_page_count_before_append'] == 4
    assert report['headline_findings']['overflow_page_count_after_append'] == 5
    assert report['headline_findings']['overflow_new_page_bytes'] == 46

    assert packet.packet_minified_bytes(ordered) == 20277
    assert packet.packet_minified_bytes(monolith) == 11694
    assert packet.packet_minified_bytes(pages) == 11770
    assert packet.expand_fingerprint_catalog_pages(pages) == ordered
    assert packet.fingerprint_catalog_lookup_from_pages(pages)[ordered[0]] == 0
    assert packet.fingerprint_catalog_lookup_from_pages(pages)[ordered[127]] == 127
    assert packet.fingerprint_catalog_lookup_from_pages(pages)[ordered[128]] == 128
    assert packet.fingerprint_catalog_lookup_from_pages(pages)[ordered[-1]] == 273

    sample_rows = {row['page_index']: row for row in report['sample_page_rows']}
    assert sample_rows[0]['slot_range'] == [0, 15]
    assert sample_rows[0]['entry_count'] == 16
    assert sample_rows[17]['slot_range'] == [272, 273]
    assert sample_rows[17]['entry_count'] == 2
    assert sample_rows[17]['page_bytes'] == 89

    new_fingerprint = 'sha256:' + 'ab' * 32
    appended_pages = packet.append_fingerprint_catalog_pages(pages, new_fingerprint, page_size=16)
    assert len(appended_pages) == 18
    assert packet.packet_minified_bytes(appended_pages[-1]) == 132
    assert packet.expand_fingerprint_catalog_pages(appended_pages)[-1] == new_fingerprint
    assert packet.append_fingerprint_catalog_pages(appended_pages, new_fingerprint, page_size=16) == appended_pages

    full_pages = packet.fingerprint_catalog_pages(ordered[:64], page_size=16)
    overflow_appended = packet.append_fingerprint_catalog_pages(full_pages, new_fingerprint, page_size=16)
    assert len(full_pages) == 4
    assert len(overflow_appended) == 5
    assert packet.packet_minified_bytes(overflow_appended[-1]) == 46
    assert packet.expand_fingerprint_catalog_page(overflow_appended[-1]) == [new_fingerprint]

    try:
        packet.fingerprint_catalog_page([])
    except packet.PacketError:
        pass
    else:
        raise AssertionError('empty fingerprint pages must be rejected')

    try:
        packet.expand_fingerprint_catalog_page(packet._base64url_encode_bytes(bytes([packet.FINGERPRINT_CATALOG_PAGE_TAG, 0])))
    except packet.PacketError:
        pass
    else:
        raise AssertionError('truncated digest payloads must be rejected')

    print('decision-packet-catalog-pages: ok')


if __name__ == '__main__':
    main()
