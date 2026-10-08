#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_write_snapshot_20260307.json'


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


def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text())

    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(known_fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]

    exact_match_count = 0
    total_scan_bytes = 0
    for index, row in enumerate(deterministic_packets):
        standalone = row['packet']
        ordered_plan = packet.packet_archive_yocto_write_plan(standalone, known_fingerprints)
        page_native_plan = packet.packet_archive_yocto_write_plan_from_pages(standalone, pages)
        if _plan_core(ordered_plan) == _plan_core(page_native_plan):
            exact_match_count += 1
        slot = packet.find_fingerprint_catalog_slot_from_pages(
            packet.packet_semantic_fingerprint(standalone),
            pages,
            page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        )
        assert slot == index
        page_index = slot // packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE
        total_scan_bytes += sum(page_bytes[: page_index + 1])

    average_scan_bytes = total_scan_bytes / len(deterministic_packets)

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(deterministic_packets) == 274
    assert report['headline_findings']['page_size'] == packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE == 16
    assert report['headline_findings']['page_count'] == 18
    assert report['headline_findings']['page_bytes'] == [686] * 17 + [89]
    assert report['headline_findings']['full_string_catalog_bytes'] == 20277
    assert report['headline_findings']['full_paged_catalog_bytes'] == 11770
    assert report['headline_findings']['exact_repeat_plan_core_matches'] == exact_match_count == 274
    assert report['headline_findings']['repeat_kind_distribution'] == {'short_catalog_reference': 274}
    assert report['headline_findings']['average_repeat_lookup_scan_bytes'] == 6214.708029
    assert report['headline_findings']['average_bytes_avoided_vs_string_catalog'] == 14062.291971
    assert report['headline_findings']['average_bytes_avoided_share_vs_string_catalog'] == 0.693509
    assert report['headline_findings']['average_bytes_avoided_vs_full_paged_catalog'] == 5555.291971
    assert report['headline_findings']['average_bytes_avoided_share_vs_full_paged_catalog'] == 0.471987
    assert round(average_scan_bytes, 6) == report['headline_findings']['average_repeat_lookup_scan_bytes']

    for slot in [0, 63, 64, 127, 128, 255, 256, 273]:
        assert packet.find_fingerprint_catalog_slot_from_pages(known_fingerprints[slot], pages) == slot

    novel_packet = packet.packet_from_coordinates('0.125', '0.375')
    assert packet.find_fingerprint_catalog_slot_from_pages(packet.packet_semantic_fingerprint(novel_packet), pages) is None
    assert packet.packet_archive_yocto_write_plan_from_pages(novel_packet, pages) == packet.packet_archive_zepto_write_plan(novel_packet, set(known_fingerprints))

    try:
        packet.packet_archive_yocto_write_plan_from_pages(deterministic_packets[0]['packet'], 'not-pages')
    except packet.PacketError:
        pass
    else:
        raise AssertionError('non-list page catalogs must be rejected')

    try:
        packet.find_fingerprint_catalog_slot_from_pages(known_fingerprints[0], [packet._base64url_encode_bytes(bytes([packet.FINGERPRINT_CATALOG_PAGE_TAG, 0]))])
    except packet.PacketError:
        pass
    else:
        raise AssertionError('truncated catalog pages must be rejected during direct repeat lookup')

    sample_rows = {row['index']: row for row in report['sample_rows']}
    assert sample_rows[0]['page_scan_bytes'] == 686
    assert sample_rows[64]['page_scan_bytes'] == 3430
    assert sample_rows[128]['page_scan_bytes'] == 6174
    assert sample_rows[256]['page_scan_bytes'] == 11662
    assert sample_rows[273]['page_native_plan_core']['reference'] == 'gRE'

    print('decision-packet-catalog-page-writes: ok')


if __name__ == '__main__':
    main()
