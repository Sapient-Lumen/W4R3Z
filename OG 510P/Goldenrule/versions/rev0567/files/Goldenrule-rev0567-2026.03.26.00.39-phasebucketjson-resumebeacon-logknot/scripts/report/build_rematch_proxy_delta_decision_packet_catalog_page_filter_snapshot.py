#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.md'


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



def _sample_row(packet, rows: list[dict[str, object]], pages: list[str], page_filters: list[str], page_bytes: list[int], filter_bytes: list[int], index: int) -> dict[str, object]:
    row = rows[index]
    standalone = row['packet']
    fingerprint = packet.packet_semantic_fingerprint(standalone)
    lookup_bytes, false_positive_pages, slot = _lookup_bytes(packet, fingerprint, pages, page_filters, page_bytes, filter_bytes)
    assert slot is not None
    return {
        'index': index,
        'name': row['name'],
        'mode': standalone['mode'],
        'semantic_fingerprint': fingerprint,
        'catalog_slot': slot,
        'page_index': slot // packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        'lookup_bytes_with_filters': lookup_bytes,
        'false_positive_pages_before_hit': false_positive_pages,
        'page_native_plan_core': _plan_core(packet.packet_archive_yocto_write_plan_from_pages(standalone, pages)),
        'filtered_page_plan_core': _plan_core(packet.packet_archive_yocto_write_plan_from_pages_with_filters(standalone, pages, page_filters)),
    }



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(known_fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    page_filters = packet.fingerprint_catalog_page_filters(pages)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]
    filter_bytes = [packet.packet_minified_bytes(page_filter) for page_filter in page_filters]

    exact_match_count = 0
    repeat_kind_distribution: Counter[str] = Counter()
    false_positive_distribution: Counter[int] = Counter()
    total_filtered_lookup_bytes = 0
    total_page_lookup_bytes = 0
    for row in deterministic_packets:
        standalone = row['packet']
        page_plan = packet.packet_archive_yocto_write_plan_from_pages(standalone, pages)
        filtered_plan = packet.packet_archive_yocto_write_plan_from_pages_with_filters(standalone, pages, page_filters)
        if _plan_core(page_plan) == _plan_core(filtered_plan):
            exact_match_count += 1
        repeat_kind_distribution[filtered_plan['recommended_write_kind']] += 1
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        lookup_bytes, false_positive_pages, slot = _lookup_bytes(packet, fingerprint, pages, page_filters, page_bytes, filter_bytes)
        assert slot is not None
        total_filtered_lookup_bytes += lookup_bytes
        total_page_lookup_bytes += sum(page_bytes[: slot // packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE + 1])
        false_positive_distribution[false_positive_pages] += 1

    average_filtered_lookup_bytes = total_filtered_lookup_bytes / len(deterministic_packets)
    average_page_lookup_bytes = total_page_lookup_bytes / len(deterministic_packets)
    full_string_catalog_bytes = packet.packet_minified_bytes(packet.ordered_fingerprint_catalog(known_fingerprints))
    full_paged_catalog_bytes = packet.packet_minified_bytes(pages)
    full_page_filter_bytes = packet.packet_minified_bytes(page_filters)
    full_compact_state_bytes = full_paged_catalog_bytes + full_page_filter_bytes

    sample_rows = [
        _sample_row(packet, deterministic_packets, pages, page_filters, page_bytes, filter_bytes, index)
        for index in [0, 63, 64, 127, 128, 255, 256, len(deterministic_packets) - 1]
    ]

    novel_packet = packet.packet_from_coordinates('0.125', '0.375')
    novel_lookup_bytes, novel_false_positive_pages, novel_slot = _lookup_bytes(
        packet,
        packet.packet_semantic_fingerprint(novel_packet),
        pages,
        page_filters,
        page_bytes,
        filter_bytes,
    )
    assert novel_slot is None
    appended_filters = packet.append_fingerprint_catalog_page_filters(page_filters, packet.packet_semantic_fingerprint(novel_packet))
    appended_pages = packet.append_fingerprint_catalog_pages(pages, packet.packet_semantic_fingerprint(novel_packet))

    return {
        'focus': 'Keep repeat lookup and repeat planning in the compact paged-catalog state, but add tiny page-local digest-byte filters so the writer rarely has to scan non-matching raw-digest pages at all.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'headline_findings': {
            'main_rule': 'when the archive already preserves append-only fingerprint pages, it should keep aligned page filters beside them and use those filters to skip impossible pages before decoding raw digests for repeat detection.',
            'page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
            'page_count': len(pages),
            'page_bytes': page_bytes,
            'page_filter_bytes': filter_bytes,
            'full_string_catalog_bytes': full_string_catalog_bytes,
            'full_paged_catalog_bytes': full_paged_catalog_bytes,
            'full_page_filter_bytes': full_page_filter_bytes,
            'full_compact_state_bytes': full_compact_state_bytes,
            'exact_repeat_plan_core_matches': exact_match_count,
            'repeat_kind_distribution': dict(sorted(repeat_kind_distribution.items())),
            'false_positive_page_distribution': dict(sorted(false_positive_distribution.items())),
            'average_repeat_lookup_bytes_with_filters': round(average_filtered_lookup_bytes, 6),
            'average_repeat_lookup_bytes_without_filters': round(average_page_lookup_bytes, 6),
            'average_bytes_avoided_vs_page_native_scan': round(average_page_lookup_bytes - average_filtered_lookup_bytes, 6),
            'average_bytes_avoided_share_vs_page_native_scan': round((average_page_lookup_bytes - average_filtered_lookup_bytes) / average_page_lookup_bytes, 6),
            'average_bytes_avoided_vs_string_catalog': round(full_string_catalog_bytes - average_filtered_lookup_bytes, 6),
            'average_bytes_avoided_share_vs_string_catalog': round((full_string_catalog_bytes - average_filtered_lookup_bytes) / full_string_catalog_bytes, 6),
            'average_bytes_avoided_vs_full_paged_catalog': round(full_paged_catalog_bytes - average_filtered_lookup_bytes, 6),
            'average_bytes_avoided_share_vs_full_paged_catalog': round((full_paged_catalog_bytes - average_filtered_lookup_bytes) / full_paged_catalog_bytes, 6),
        },
        'sample_rows': sample_rows,
        'novel_first_write_example': {
            'packet': novel_packet,
            'lookup_bytes_with_filters': novel_lookup_bytes,
            'false_positive_pages_before_miss': novel_false_positive_pages,
            'filtered_page_plan': packet.packet_archive_yocto_write_plan_from_pages_with_filters(novel_packet, pages, page_filters),
            'page_native_plan': packet.packet_archive_yocto_write_plan_from_pages(novel_packet, pages),
        },
        'append_locality_example': {
            'tail_page_bytes_before': packet.packet_minified_bytes(pages[-1]),
            'tail_page_bytes_after': packet.packet_minified_bytes(appended_pages[-1]),
            'tail_filter_bytes_before': packet.packet_minified_bytes(page_filters[-1]),
            'tail_filter_bytes_after': packet.packet_minified_bytes(appended_filters[-1]),
            'appended_filter_matches_rebuild': appended_filters == packet.fingerprint_catalog_page_filters(appended_pages),
        },
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Catalog-Page-Filter Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- page size: `{findings['page_size']}` across `{findings['page_count']}` pages with page bytes `{json.dumps(findings['page_bytes'])}`.",
        f"- aligned page-filter bytes: `{json.dumps(findings['page_filter_bytes'])}` with total filter-list bytes `{findings['full_page_filter_bytes']}` and full compact-state bytes `{findings['full_compact_state_bytes']}`.",
        f"- full ordered string catalog bytes: `{findings['full_string_catalog_bytes']}`.",
        f"- full paged digest catalog bytes: `{findings['full_paged_catalog_bytes']}`.",
        f"- exact core-field match between page-native planning and filter-aided page-native planning: `{findings['exact_repeat_plan_core_matches']}` / `{report['deterministic_frontier_packet_count']}` repeats.",
        f"- repeat kind distribution under filter-aided planning: `{json.dumps(findings['repeat_kind_distribution'], sort_keys=True)}`.",
        f"- false-positive page distribution before the true hit: `{json.dumps(findings['false_positive_page_distribution'], sort_keys=True)}`.",
        f"- average repeat lookup bytes with filters: `{findings['average_repeat_lookup_bytes_with_filters']}`.",
        f"- average repeat lookup bytes without filters: `{findings['average_repeat_lookup_bytes_without_filters']}`.",
        f"- average bytes avoided vs page-native scan: `{findings['average_bytes_avoided_vs_page_native_scan']}` (`{findings['average_bytes_avoided_share_vs_page_native_scan']}` share).",
        f"- average bytes avoided vs rebuilding the full ordered string catalog: `{findings['average_bytes_avoided_vs_string_catalog']}` (`{findings['average_bytes_avoided_share_vs_string_catalog']}` share).",
        f"- average bytes avoided vs scanning the full paged catalog list: `{findings['average_bytes_avoided_vs_full_paged_catalog']}` (`{findings['average_bytes_avoided_share_vs_full_paged_catalog']}` share).",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative repeat plans',
    ]
    for row in report['sample_rows']:
        lines.append(
            f"- index `{row['index']}` / `{row['name']}` (`{row['mode']}`): slot `{row['catalog_slot']}` on page `{row['page_index']}` after touching `{row['lookup_bytes_with_filters']}` bytes with `{row['false_positive_pages_before_hit']}` false-positive pages; page-native and filtered planners agree on `{row['filtered_page_plan_core']['recommended_write_kind']}` with reference `{row['filtered_page_plan_core']['reference']}`."
        )
    lines.extend(
        [
            '',
            '## Novel first-write check',
            f"- packet `{json.dumps(report['novel_first_write_example']['packet'], sort_keys=True)}` stays a non-repeat after touching `{report['novel_first_write_example']['lookup_bytes_with_filters']}` bytes with `{report['novel_first_write_example']['false_positive_pages_before_miss']}` false-positive pages, and the filtered planner matches the page-native planner exactly: `{json.dumps(report['novel_first_write_example']['filtered_page_plan'], sort_keys=True)}`.",
            '',
            '## Append-locality check',
            f"- tail page bytes: `{report['append_locality_example']['tail_page_bytes_before']}` -> `{report['append_locality_example']['tail_page_bytes_after']}`.",
            f"- tail filter bytes: `{report['append_locality_example']['tail_filter_bytes_before']}` -> `{report['append_locality_example']['tail_filter_bytes_after']}`.",
            f"- append helper matches full rebuild: `{report['append_locality_example']['appended_filter_matches_rebuild']}`.",
            '',
            '## Sources',
            '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
            '- `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`',
        ]
    )
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
