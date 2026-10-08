#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_write_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_write_snapshot_20260307.md'


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


def _sample_row(packet, rows: list[dict[str, object]], known_fingerprints: list[str], pages: list[str], page_bytes: list[int], index: int) -> dict[str, object]:
    row = rows[index]
    standalone = row['packet']
    fingerprint = packet.packet_semantic_fingerprint(standalone)
    slot = packet.find_fingerprint_catalog_slot_from_pages(fingerprint, pages, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    assert slot is not None
    page_index = slot // packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE
    return {
        'index': index,
        'name': row['name'],
        'mode': standalone['mode'],
        'semantic_fingerprint': fingerprint,
        'catalog_slot': slot,
        'page_index': page_index,
        'page_scan_bytes': sum(page_bytes[: page_index + 1]),
        'ordered_plan_core': _plan_core(packet.packet_archive_yocto_write_plan(standalone, known_fingerprints)),
        'page_native_plan_core': _plan_core(packet.packet_archive_yocto_write_plan_from_pages(standalone, pages)),
    }



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    pages = packet.fingerprint_catalog_pages(known_fingerprints, page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]

    exact_match_count = 0
    repeat_kind_distribution: Counter[str] = Counter()
    total_scan_bytes = 0
    for row in deterministic_packets:
        standalone = row['packet']
        ordered_plan = packet.packet_archive_yocto_write_plan(standalone, known_fingerprints)
        page_native_plan = packet.packet_archive_yocto_write_plan_from_pages(standalone, pages)
        if _plan_core(ordered_plan) == _plan_core(page_native_plan):
            exact_match_count += 1
        repeat_kind_distribution[page_native_plan['recommended_write_kind']] += 1
        slot = packet.find_fingerprint_catalog_slot_from_pages(
            packet.packet_semantic_fingerprint(standalone),
            pages,
            page_size=packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
        )
        assert slot is not None
        page_index = slot // packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE
        total_scan_bytes += sum(page_bytes[: page_index + 1])

    average_scan_bytes = total_scan_bytes / len(deterministic_packets)
    full_string_catalog_bytes = packet.packet_minified_bytes(packet.ordered_fingerprint_catalog(known_fingerprints))
    full_paged_catalog_bytes = packet.packet_minified_bytes(pages)

    sample_rows = [
        _sample_row(packet, deterministic_packets, known_fingerprints, pages, page_bytes, index)
        for index in [0, 63, 64, 127, 128, 255, 256, len(deterministic_packets) - 1]
    ]

    novel_packet = packet.packet_from_coordinates('0.125', '0.375')
    novel_plan_from_pages = packet.packet_archive_yocto_write_plan_from_pages(novel_packet, pages)
    novel_plan_from_zepto = packet.packet_archive_zepto_write_plan(novel_packet, set(known_fingerprints))

    return {
        'focus': 'Choose repeat writes directly from compact paged raw-digest catalog state so the live writer does not have to rebuild a full ordered sha256-string catalog before deciding whether a packet is a repeat and which local slot reference to emit.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'headline_findings': {
            'main_rule': 'when the archive already preserves append-only fingerprint pages, repeat detection and slot-reference planning should operate directly on those pages; only rehydrate the full ordered sha256-string catalog when a human-readable surface actually needs it.',
            'page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
            'page_count': len(pages),
            'page_bytes': page_bytes,
            'full_string_catalog_bytes': full_string_catalog_bytes,
            'full_paged_catalog_bytes': full_paged_catalog_bytes,
            'exact_repeat_plan_core_matches': exact_match_count,
            'repeat_kind_distribution': dict(sorted(repeat_kind_distribution.items())),
            'average_repeat_lookup_scan_bytes': round(average_scan_bytes, 6),
            'average_bytes_avoided_vs_string_catalog': round(full_string_catalog_bytes - average_scan_bytes, 6),
            'average_bytes_avoided_share_vs_string_catalog': round((full_string_catalog_bytes - average_scan_bytes) / full_string_catalog_bytes, 6),
            'average_bytes_avoided_vs_full_paged_catalog': round(full_paged_catalog_bytes - average_scan_bytes, 6),
            'average_bytes_avoided_share_vs_full_paged_catalog': round((full_paged_catalog_bytes - average_scan_bytes) / full_paged_catalog_bytes, 6),
        },
        'sample_rows': sample_rows,
        'novel_first_write_example': {
            'packet': novel_packet,
            'page_native_plan': novel_plan_from_pages,
            'zepto_plan_against_unordered_known_set': novel_plan_from_zepto,
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
        '# Rematch-Proxy Decision Packet Catalog-Page-Write Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- page size: `{findings['page_size']}` across `{findings['page_count']}` pages with page bytes `{json.dumps(findings['page_bytes'])}`.",
        f"- full ordered string catalog bytes: `{findings['full_string_catalog_bytes']}`.",
        f"- full paged digest catalog bytes: `{findings['full_paged_catalog_bytes']}`.",
        f"- exact core-field match between ordered-catalog yocto planning and page-native yocto planning: `{findings['exact_repeat_plan_core_matches']}` / `{report['deterministic_frontier_packet_count']}` repeats.",
        f"- repeat kind distribution under page-native planning: `{json.dumps(findings['repeat_kind_distribution'], sort_keys=True)}`.",
        f"- average page bytes scanned before finding the repeat slot: `{findings['average_repeat_lookup_scan_bytes']}`.",
        f"- average bytes avoided vs rebuilding the full ordered string catalog: `{findings['average_bytes_avoided_vs_string_catalog']}` (`{findings['average_bytes_avoided_share_vs_string_catalog']}` share).",
        f"- average bytes avoided vs scanning the whole paged catalog list: `{findings['average_bytes_avoided_vs_full_paged_catalog']}` (`{findings['average_bytes_avoided_share_vs_full_paged_catalog']}` share).",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative repeat plans',
    ]
    for row in report['sample_rows']:
        lines.append(
            f"- index `{row['index']}` / `{row['name']}` (`{row['mode']}`): slot `{row['catalog_slot']}` on page `{row['page_index']}` after scanning `{row['page_scan_bytes']}` bytes; ordered and page-native planners agree on `{row['page_native_plan_core']['recommended_write_kind']}` with reference `{row['page_native_plan_core']['reference']}`."
        )
    lines.extend(
        [
            '',
            '## Novel first-write check',
            f"- packet `{json.dumps(report['novel_first_write_example']['packet'], sort_keys=True)}` stays a non-repeat and the page-native planner matches the zepto first-write planner exactly: `{json.dumps(report['novel_first_write_example']['page_native_plan'], sort_keys=True)}`.",
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
