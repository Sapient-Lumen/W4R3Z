#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_size_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_size_snapshot_20260307.md'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


def _candidate_row(packet, fingerprints: list[str], page_size: int) -> dict[str, object]:
    pages = packet.fingerprint_catalog_pages(fingerprints, page_size=page_size)
    page_filters = packet.fingerprint_catalog_page_filters(pages)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]
    filter_bytes = [packet.packet_minified_bytes(page_filter) for page_filter in page_filters]

    total_filtered_lookup_bytes = 0
    total_page_lookup_bytes = 0
    total_false_positive_pages = 0
    for fingerprint in fingerprints:
        lookup_bytes, false_positive_pages, slot = _lookup_bytes(packet, fingerprint, pages, page_filters, page_bytes, filter_bytes)
        assert slot is not None
        total_filtered_lookup_bytes += lookup_bytes
        total_page_lookup_bytes += sum(page_bytes[: slot // page_size + 1])
        total_false_positive_pages += false_positive_pages

    average_filtered_lookup_bytes = total_filtered_lookup_bytes / len(fingerprints)
    average_page_lookup_bytes = total_page_lookup_bytes / len(fingerprints)
    paged_catalog_bytes = packet.packet_minified_bytes(pages)
    filter_list_bytes = packet.packet_minified_bytes(page_filters)
    full_compact_state_bytes = paged_catalog_bytes + filter_list_bytes
    return {
        'page_size': page_size,
        'page_count': len(pages),
        'page_bytes': page_bytes,
        'page_filter_bytes': filter_bytes,
        'paged_catalog_bytes': paged_catalog_bytes,
        'filter_list_bytes': filter_list_bytes,
        'full_compact_state_bytes': full_compact_state_bytes,
        'average_repeat_lookup_bytes_with_filters': round(average_filtered_lookup_bytes, 6),
        'average_repeat_lookup_bytes_without_filters': round(average_page_lookup_bytes, 6),
        'average_false_positive_pages_before_hit': round(total_false_positive_pages / len(fingerprints), 6),
        'combined_state_plus_lookup_objective': round(full_compact_state_bytes + average_filtered_lookup_bytes, 6),
    }


def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    candidate_rows = [
        _candidate_row(packet, fingerprints, page_size)
        for page_size in packet.FILTERED_FINGERPRINT_CATALOG_PAGE_SIZE_CANDIDATES
    ]
    rows_by_size = {row['page_size']: row for row in candidate_rows}
    best_lookup_row = min(candidate_rows, key=lambda row: (row['average_repeat_lookup_bytes_with_filters'], row['full_compact_state_bytes'], row['page_size']))
    best_power_of_two_objective_row = min(candidate_rows, key=lambda row: (row['combined_state_plus_lookup_objective'], row['average_repeat_lookup_bytes_with_filters'], row['page_size']))
    default_row = rows_by_size[packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE]
    legacy_row = rows_by_size[64]

    return {
        'focus': 'Stop treating 64-entry fingerprint pages as inherited law now that repeat reads and repeat writes both run inside the filtered compact catalog. Choose the filtered page size by measured lookup/state tradeoff instead.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'headline_findings': {
            'page_size_candidates': list(packet.FILTERED_FINGERPRINT_CATALOG_PAGE_SIZE_CANDIDATES),
            'default_page_size': packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
            'legacy_page_size': 64,
            'best_lookup_page_size': best_lookup_row['page_size'],
            'best_lookup_average_repeat_lookup_bytes_with_filters': best_lookup_row['average_repeat_lookup_bytes_with_filters'],
            'best_power_of_two_combined_objective_page_size': best_power_of_two_objective_row['page_size'],
            'best_power_of_two_combined_objective_value': best_power_of_two_objective_row['combined_state_plus_lookup_objective'],
            'default_full_compact_state_bytes': default_row['full_compact_state_bytes'],
            'legacy_full_compact_state_bytes': legacy_row['full_compact_state_bytes'],
            'default_average_repeat_lookup_bytes_with_filters': default_row['average_repeat_lookup_bytes_with_filters'],
            'legacy_average_repeat_lookup_bytes_with_filters': legacy_row['average_repeat_lookup_bytes_with_filters'],
            'default_minus_legacy_compact_state_bytes': default_row['full_compact_state_bytes'] - legacy_row['full_compact_state_bytes'],
            'default_lookup_bytes_saved_vs_legacy': round(legacy_row['average_repeat_lookup_bytes_with_filters'] - default_row['average_repeat_lookup_bytes_with_filters'], 6),
            'default_lookup_savings_share_vs_legacy': round((legacy_row['average_repeat_lookup_bytes_with_filters'] - default_row['average_repeat_lookup_bytes_with_filters']) / legacy_row['average_repeat_lookup_bytes_with_filters'], 6),
            'main_rule': 'when the archive keeps filtered paged digest catalogs, prefer 16-entry pages as the default clean power-of-two shape: they preserve nearly all of the tiny-page lookup gain while avoiding the state blowup of 8-entry pages and decisively beat the older 64-entry default on the measured lookup/state frontier.',
        },
        'candidate_rows': candidate_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }


def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Catalog-Page-Size Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- measured power-of-two page-size candidates: `{json.dumps(findings['page_size_candidates'])}`.",
        f"- best raw filtered-lookup page size in this candidate set: `{findings['best_lookup_page_size']}` with average filtered repeat lookup `{findings['best_lookup_average_repeat_lookup_bytes_with_filters']}` bytes.",
        f"- best combined `full_compact_state_bytes + average_repeat_lookup_bytes_with_filters` objective in this candidate set: page size `{findings['best_power_of_two_combined_objective_page_size']}` at `{findings['best_power_of_two_combined_objective_value']}`.",
        f"- new default filtered page size: `{findings['default_page_size']}`; legacy filtered page size: `{findings['legacy_page_size']}`.",
        f"- default compact state bytes: `{findings['default_full_compact_state_bytes']}` vs legacy `{findings['legacy_full_compact_state_bytes']}` (delta `{findings['default_minus_legacy_compact_state_bytes']}`).",
        f"- default average filtered repeat lookup: `{findings['default_average_repeat_lookup_bytes_with_filters']}` vs legacy `{findings['legacy_average_repeat_lookup_bytes_with_filters']}`, saving `{findings['default_lookup_bytes_saved_vs_legacy']}` bytes on average (`{findings['default_lookup_savings_share_vs_legacy']}` share).",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Candidate table',
    ]
    for row in report['candidate_rows']:
        lines.append(
            f"- page size `{row['page_size']}`: `{row['page_count']}` pages, compact state `{row['full_compact_state_bytes']}` bytes, avg filtered repeat lookup `{row['average_repeat_lookup_bytes_with_filters']}`, avg page-native repeat lookup `{row['average_repeat_lookup_bytes_without_filters']}`, avg false-positive pages `{row['average_false_positive_pages_before_hit']}`, combined objective `{row['combined_state_plus_lookup_objective']}`."
        )
    lines.extend(
        [
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
