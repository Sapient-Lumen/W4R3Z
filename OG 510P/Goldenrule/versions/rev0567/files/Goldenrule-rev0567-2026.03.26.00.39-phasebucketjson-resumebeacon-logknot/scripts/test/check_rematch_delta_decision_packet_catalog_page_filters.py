#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.json'


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


def _lookup_bytes(packet, fingerprint: str, pages: list[str], page_filters: list[str], page_bytes: list[int], filter_bytes: list[int]) -> tuple[int, int, int | None]:
    target_digest = packet._fingerprint_digest_bytes(fingerprint)
    value = target_digest[0]
    slot_base = 0
    bytes_touched = 0
    false_positive_pages = 0
    for page_index, (page, page_filter) in enumerate(zip(pages, page_filters)):
        bytes_touched += filter_bytes[page_index]
        entry_count, mask = packet._decode_fingerprint_catalog_page_filter_payload(page_filter)
        if not mask[value >> 3] & (1 << (value & 7)):
            slot_base += entry_count
            continue
        bytes_touched += page_bytes[page_index]
        payload, payload_entry_count = packet._decode_fingerprint_catalog_page_payload(page)
        assert payload_entry_count == entry_count
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return bytes_touched, false_positive_pages, slot_base + entry_index
        false_positive_pages += 1
        slot_base += entry_count
    return bytes_touched, false_positive_pages, None


def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text())

    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(known_fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    page_filters = packet.fingerprint_catalog_page_filters(pages)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]
    filter_bytes = [packet.packet_minified_bytes(page_filter) for page_filter in page_filters]

    exact_match_count = 0
    total_filtered_lookup_bytes = 0
    total_page_lookup_bytes = 0
    false_positive_distribution: dict[int, int] = {}
    for index, row in enumerate(deterministic_packets):
        standalone = row['packet']
        page_plan = packet.packet_archive_yocto_write_plan_from_pages(standalone, pages)
        filtered_plan = packet.packet_archive_yocto_write_plan_from_pages_with_filters(standalone, pages, page_filters)
        if _plan_core(page_plan) == _plan_core(filtered_plan):
            exact_match_count += 1
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        lookup_bytes, false_positive_pages, slot = _lookup_bytes(packet, fingerprint, pages, page_filters, page_bytes, filter_bytes)
        assert slot == index
        total_filtered_lookup_bytes += lookup_bytes
        total_page_lookup_bytes += sum(page_bytes[: slot // packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE + 1])
        false_positive_distribution[false_positive_pages] = false_positive_distribution.get(false_positive_pages, 0) + 1

    average_filtered_lookup_bytes = total_filtered_lookup_bytes / len(deterministic_packets)
    average_page_lookup_bytes = total_page_lookup_bytes / len(deterministic_packets)

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(deterministic_packets) == 274
    assert report['headline_findings']['page_size'] == packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE == 16
    assert report['headline_findings']['page_count'] == 18
    assert report['headline_findings']['page_bytes'] == [686] * 17 + [89]
    assert report['headline_findings']['page_filter_bytes'] == [48] * 18
    assert report['headline_findings']['full_string_catalog_bytes'] == 20277
    assert report['headline_findings']['full_paged_catalog_bytes'] == 11770
    assert report['headline_findings']['full_page_filter_bytes'] == 883
    assert report['headline_findings']['full_compact_state_bytes'] == 12653
    assert report['headline_findings']['exact_repeat_plan_core_matches'] == exact_match_count == 274
    assert report['headline_findings']['repeat_kind_distribution'] == {'short_catalog_reference': 274}
    assert report['headline_findings']['false_positive_page_distribution'] == {'0': 170, '1': 75, '2': 23, '3': 5, '4': 1}
    assert report['headline_findings']['average_repeat_lookup_bytes_with_filters'] == 1467.306569
    assert report['headline_findings']['average_repeat_lookup_bytes_without_filters'] == 6214.708029
    assert report['headline_findings']['average_bytes_avoided_vs_page_native_scan'] == 4747.40146
    assert report['headline_findings']['average_bytes_avoided_share_vs_page_native_scan'] == 0.763898
    assert report['headline_findings']['average_bytes_avoided_vs_string_catalog'] == 18809.693431
    assert report['headline_findings']['average_bytes_avoided_share_vs_string_catalog'] == 0.927637
    assert report['headline_findings']['average_bytes_avoided_vs_full_paged_catalog'] == 10302.693431
    assert report['headline_findings']['average_bytes_avoided_share_vs_full_paged_catalog'] == 0.875335
    assert round(average_filtered_lookup_bytes, 6) == report['headline_findings']['average_repeat_lookup_bytes_with_filters']
    assert round(average_page_lookup_bytes, 6) == report['headline_findings']['average_repeat_lookup_bytes_without_filters']
    assert false_positive_distribution == {0: 170, 1: 75, 2: 23, 3: 5, 4: 1}

    for slot in [0, 63, 64, 127, 128, 255, 256, 273]:
        assert packet.find_fingerprint_catalog_slot_from_pages_with_filters(known_fingerprints[slot], pages, page_filters) == slot
        assert packet.packet_archive_yocto_write_plan_from_pages_with_filters(deterministic_packets[slot]['packet'], pages, page_filters)['reference'] == packet.packet_short_catalog_reference_from_slot(slot)

    novel_packet = packet.packet_from_coordinates('0.125', '0.375')
    novel_fingerprint = packet.packet_semantic_fingerprint(novel_packet)
    assert packet.find_fingerprint_catalog_slot_from_pages_with_filters(novel_fingerprint, pages, page_filters) is None
    assert packet.packet_archive_yocto_write_plan_from_pages_with_filters(novel_packet, pages, page_filters) == packet.packet_archive_yocto_write_plan_from_pages(novel_packet, pages)

    appended_filters = packet.append_fingerprint_catalog_page_filters(page_filters, novel_fingerprint)
    appended_pages = packet.append_fingerprint_catalog_pages(pages, novel_fingerprint)
    assert appended_filters == packet.fingerprint_catalog_page_filters(appended_pages)
    assert packet.packet_minified_bytes(page_filters[-1]) == 48
    assert packet.packet_minified_bytes(appended_filters[-1]) == 48

    try:
        packet.find_fingerprint_catalog_slot_from_pages_with_filters(known_fingerprints[0], pages, 'not-filters')
    except packet.PacketError:
        pass
    else:
        raise AssertionError('non-list page-filter catalogs must be rejected')

    try:
        packet.find_fingerprint_catalog_slot_from_pages_with_filters(known_fingerprints[0], pages, page_filters[:-1])
    except packet.PacketError:
        pass
    else:
        raise AssertionError('misaligned page-filter catalogs must be rejected')

    try:
        packet.fingerprint_catalog_page_filter_might_contain(known_fingerprints[0], packet._base64url_encode_bytes(bytes([packet.FINGERPRINT_CATALOG_PAGE_FILTER_TAG, 1, 0])))
    except packet.PacketError:
        pass
    else:
        raise AssertionError('truncated page filters must be rejected')

    sample_rows = {row['index']: row for row in report['sample_rows']}
    assert sample_rows[0]['lookup_bytes_with_filters'] == 734
    assert sample_rows[64]['lookup_bytes_with_filters'] == 926
    assert sample_rows[128]['lookup_bytes_with_filters'] == 1118
    assert sample_rows[256]['lookup_bytes_with_filters'] == 2188
    assert sample_rows[256]['false_positive_pages_before_hit'] == 1
    assert sample_rows[273]['filtered_page_plan_core']['reference'] == 'gRE'

    print('decision-packet-catalog-page-filters: ok')


if __name__ == '__main__':
    main()
