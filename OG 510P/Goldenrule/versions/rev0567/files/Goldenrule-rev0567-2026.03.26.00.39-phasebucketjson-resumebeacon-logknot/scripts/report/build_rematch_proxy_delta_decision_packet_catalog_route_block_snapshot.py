#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_route_block_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_route_block_snapshot_20260307.md'


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
        page = pages[page_index]
        payload, entry_count = packet._decode_fingerprint_catalog_page_payload(page)
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return bytes_touched, false_positive_pages, page_index * packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE + entry_index
        false_positive_pages += 1
    return bytes_touched, false_positive_pages, None



def _sample_row(packet, rows: list[dict[str, object]], pages: list[str], route_blocks: list[str], page_bytes: list[int], route_block_bytes: list[int], index: int) -> dict[str, object]:
    row = rows[index]
    standalone = row['packet']
    fingerprint = packet.packet_semantic_fingerprint(standalone)
    lookup_bytes, false_positive_pages, slot = _lookup_bytes(packet, fingerprint, pages, route_blocks, page_bytes, route_block_bytes)
    assert slot is not None
    return {
        'index': index,
        'name': row['name'],
        'mode': standalone['mode'],
        'semantic_fingerprint': fingerprint,
        'catalog_slot': slot,
        'page_index': slot // packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'lookup_bytes_with_route_blocks': lookup_bytes,
        'false_positive_pages_before_hit': false_positive_pages,
        'filtered_page_plan_core': _plan_core(packet.packet_archive_yocto_write_plan_from_pages_with_filters(standalone, pages, packet.fingerprint_catalog_page_filters(pages))),
        'route_block_plan_core': _plan_core(packet.packet_archive_yocto_write_plan_from_pages_with_route_blocks(standalone, pages, route_blocks)),
    }



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(known_fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    page_filters = packet.fingerprint_catalog_page_filters(pages)
    route_blocks = packet.fingerprint_catalog_page_route_blocks(pages)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]
    filter_bytes = [packet.packet_minified_bytes(page_filter) for page_filter in page_filters]
    route_block_bytes = [packet.packet_minified_bytes(route_block) for route_block in route_blocks]

    exact_match_count = 0
    repeat_kind_distribution: Counter[str] = Counter()
    false_positive_distribution: Counter[int] = Counter()
    route_block_distribution: Counter[int] = Counter()
    total_route_lookup_bytes = 0
    total_filtered_lookup_bytes = 0

    for row in deterministic_packets:
        standalone = row['packet']
        filtered_plan = packet.packet_archive_yocto_write_plan_from_pages_with_filters(standalone, pages, page_filters)
        routed_plan = packet.packet_archive_yocto_write_plan_from_pages_with_route_blocks(standalone, pages, route_blocks)
        if _plan_core(filtered_plan) == _plan_core(routed_plan):
            exact_match_count += 1
        repeat_kind_distribution[routed_plan['recommended_write_kind']] += 1
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        route_lookup_bytes, false_positive_pages, slot = _lookup_bytes(packet, fingerprint, pages, route_blocks, page_bytes, route_block_bytes)
        assert slot is not None
        filtered_lookup_bytes = 0
        value = packet._fingerprint_digest_bytes(fingerprint)[0]
        for page_index, page_filter in enumerate(page_filters):
            filtered_lookup_bytes += filter_bytes[page_index]
            entry_count, mask = packet._decode_fingerprint_catalog_page_filter_payload(page_filter)
            if not mask[value >> 3] & (1 << (value & 7)):
                continue
            filtered_lookup_bytes += page_bytes[page_index]
            page = pages[page_index]
            payload, payload_entry_count = packet._decode_fingerprint_catalog_page_payload(page)
            assert payload_entry_count == entry_count
            found = False
            for entry_index in range(entry_count):
                start = entry_index * 32
                if payload[start : start + 32] == packet._fingerprint_digest_bytes(fingerprint):
                    found = True
                    break
            if found:
                break
        total_route_lookup_bytes += route_lookup_bytes
        total_filtered_lookup_bytes += filtered_lookup_bytes
        false_positive_distribution[false_positive_pages] += 1
        route_block_distribution[packet._fingerprint_digest_bytes(fingerprint)[0] >> 4] += 1

    average_route_lookup_bytes = total_route_lookup_bytes / len(deterministic_packets)
    average_filtered_lookup_bytes = total_filtered_lookup_bytes / len(deterministic_packets)
    full_string_catalog_bytes = packet.packet_minified_bytes(packet.ordered_fingerprint_catalog(known_fingerprints))
    full_paged_catalog_bytes = packet.packet_minified_bytes(pages)
    full_page_filter_bytes = packet.packet_minified_bytes(page_filters)
    full_route_block_bytes = packet.packet_minified_bytes(route_blocks)
    full_compact_state_with_filters_bytes = full_paged_catalog_bytes + full_page_filter_bytes
    full_compact_state_with_route_blocks_bytes = full_paged_catalog_bytes + full_route_block_bytes

    sample_rows = [
        _sample_row(packet, deterministic_packets, pages, route_blocks, page_bytes, route_block_bytes, index)
        for index in [0, 63, 64, 127, 128, 255, 256, len(deterministic_packets) - 1]
    ]

    novel_packet = packet.packet_from_coordinates('0.125', '0.375')
    novel_fingerprint = packet.packet_semantic_fingerprint(novel_packet)
    novel_lookup_bytes, novel_false_positive_pages, novel_slot = _lookup_bytes(
        packet,
        novel_fingerprint,
        pages,
        route_blocks,
        page_bytes,
        route_block_bytes,
    )
    assert novel_slot is None
    appended_route_blocks = packet.append_fingerprint_catalog_page_route_blocks(route_blocks, pages, novel_fingerprint)
    appended_pages = packet.append_fingerprint_catalog_pages(pages, novel_fingerprint)
    changed_block_indices = [
        index
        for index, (before, after) in enumerate(zip(route_blocks, appended_route_blocks))
        if before != after
    ]

    return {
        'focus': 'Replace linear page-filter scans with digest-byte route blocks so repeat planning can jump straight to candidate compact pages instead of touching most filter artifacts on every lookup.',
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'headline_findings': {
            'exact_repeat_plan_core_matches': exact_match_count,
            'average_repeat_lookup_bytes_with_route_blocks': round(average_route_lookup_bytes, 6),
            'average_repeat_lookup_bytes_with_filters': round(average_filtered_lookup_bytes, 6),
            'average_bytes_avoided_vs_filter_scan': round(average_filtered_lookup_bytes - average_route_lookup_bytes, 6),
            'average_bytes_avoided_share_vs_filter_scan': round((average_filtered_lookup_bytes - average_route_lookup_bytes) / average_filtered_lookup_bytes, 6),
            'average_bytes_avoided_vs_string_catalog': round(full_string_catalog_bytes - average_route_lookup_bytes, 6),
            'average_bytes_avoided_share_vs_string_catalog': round((full_string_catalog_bytes - average_route_lookup_bytes) / full_string_catalog_bytes, 6),
            'full_compact_state_with_filters_bytes': full_compact_state_with_filters_bytes,
            'full_compact_state_with_route_blocks_bytes': full_compact_state_with_route_blocks_bytes,
            'route_block_state_bytes_delta_vs_filters': full_compact_state_with_route_blocks_bytes - full_compact_state_with_filters_bytes,
            'route_block_index_distribution': {str(key): value for key, value in sorted(route_block_distribution.items())},
            'false_positive_page_distribution': {str(key): value for key, value in sorted(false_positive_distribution.items())},
        },
        'append_locality_example': {
            'novel_fingerprint': novel_fingerprint,
            'route_block_bytes_before': packet.packet_minified_bytes(route_blocks[target_block := (packet._fingerprint_digest_bytes(novel_fingerprint)[0] >> 4)]),
            'route_block_bytes_after': packet.packet_minified_bytes(appended_route_blocks[target_block]),
            'changed_block_indices': changed_block_indices,
            'appended_route_blocks_match_rebuild': appended_route_blocks == packet.fingerprint_catalog_page_route_blocks(appended_pages),
            'tail_page_bytes_before': packet.packet_minified_bytes(pages[-1]),
            'tail_page_bytes_after': packet.packet_minified_bytes(appended_pages[-1]),
        },
        'novel_first_write_example': {
            'packet': novel_packet,
            'lookup_bytes_with_route_blocks': novel_lookup_bytes,
            'false_positive_pages_before_miss': novel_false_positive_pages,
            'route_block_plan': packet.packet_archive_yocto_write_plan_from_pages_with_route_blocks(novel_packet, pages, route_blocks),
            'filtered_plan': packet.packet_archive_yocto_write_plan_from_pages_with_filters(novel_packet, pages, page_filters),
        },
        'sample_rows': sample_rows,
        'packet_script': 'scripts/analysis/rematch_proxy_delta_decision_packet.py',
        'source_script': 'scripts/report/build_rematch_proxy_delta_decision_packet_catalog_route_block_snapshot.py',
        'sources': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_size_snapshot_20260307.json',
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Catalog Route-Block Snapshot — 2026-03-07',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Headline Findings',
        '',
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- exact repeat-plan core matches versus page-filter planning: `{findings['exact_repeat_plan_core_matches']}`.",
        f"- average repeat lookup bytes with route blocks: `{findings['average_repeat_lookup_bytes_with_route_blocks']}`.",
        f"- average repeat lookup bytes with page filters: `{findings['average_repeat_lookup_bytes_with_filters']}`.",
        f"- average bytes avoided versus filter scan: `{findings['average_bytes_avoided_vs_filter_scan']}` (`{findings['average_bytes_avoided_share_vs_filter_scan']}` share).",
        f"- compact state bytes with page filters: `{findings['full_compact_state_with_filters_bytes']}`.",
        f"- compact state bytes with route blocks: `{findings['full_compact_state_with_route_blocks_bytes']}`.",
        f"- route-block state delta versus filters: `{findings['route_block_state_bytes_delta_vs_filters']}`.",
        '',
        '## Sample Rows',
        '',
    ]
    for row in report['sample_rows']:
        lines.append(
            f"- index `{row['index']}` / `{row['name']}` (`{row['mode']}`): slot `{row['catalog_slot']}` on page `{row['page_index']}` after touching `{row['lookup_bytes_with_route_blocks']}` bytes with `{row['false_positive_pages_before_hit']}` false-positive pages; filter and route-block planners agree on `{row['route_block_plan_core']['recommended_write_kind']}` with reference `{row['route_block_plan_core']['reference']}`."
        )
    lines.extend([
        '',
        '## Append Locality Example',
        '',
        f"- novel fingerprint `{report['append_locality_example']['novel_fingerprint']}` changes route blocks `{report['append_locality_example']['changed_block_indices']}` and matches full rebuild: `{report['append_locality_example']['appended_route_blocks_match_rebuild']}`.",
        f"- changed route block bytes: `{report['append_locality_example']['route_block_bytes_before']}` -> `{report['append_locality_example']['route_block_bytes_after']}`.",
        f"- tail page bytes: `{report['append_locality_example']['tail_page_bytes_before']}` -> `{report['append_locality_example']['tail_page_bytes_after']}`.",
        '',
        '## Novel First-Write Example',
        '',
        f"- packet `{json.dumps(report['novel_first_write_example']['packet'], sort_keys=True)}` stays a first write after touching `{report['novel_first_write_example']['lookup_bytes_with_route_blocks']}` bytes with `{report['novel_first_write_example']['false_positive_pages_before_miss']}` false-positive pages, and the route-block planner matches the filtered planner exactly: `{json.dumps(report['novel_first_write_example']['route_block_plan'], sort_keys=True)}`.",
    ])
    return '\n'.join(lines)



def main() -> None:
    summary = _build_summary()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary) + '\n', encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
