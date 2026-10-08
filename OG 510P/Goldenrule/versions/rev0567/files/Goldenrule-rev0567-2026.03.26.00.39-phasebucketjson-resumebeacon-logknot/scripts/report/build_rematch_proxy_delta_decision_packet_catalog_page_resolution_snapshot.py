#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_resolution_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_resolution_snapshot_20260307.md'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sample_row(packet, slot: int, known_fingerprints: list[str], pages: list[str]) -> dict[str, object]:
    ordered = packet.ordered_fingerprint_catalog(known_fingerprints)
    fingerprint = ordered[slot]
    page_size = packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE
    page_index = slot // page_size
    entry_index = slot % page_size
    short_reference = packet._base64url_encode_bytes(
        bytes([packet.SHORT_CATALOG_REFERENCE_PREFIX | (slot >> 8), slot & 0xFF])
    )
    catalog_reference = packet._base64url_encode_bytes(bytes([packet.CATALOG_REFERENCE_TAG]) + packet._encode_uvarint(slot))
    return {
        'slot': slot,
        'page_index': page_index,
        'entry_index': entry_index,
        'semantic_fingerprint': fingerprint,
        'short_catalog_reference_packet': short_reference,
        'catalog_reference_packet': catalog_reference,
        'page_bytes': packet.packet_minified_bytes(pages[page_index]),
        'resolved_from_pages_via_short_reference': packet.resolve_archive_any_catalog_reference_from_pages(
            short_reference,
            pages,
            page_size=page_size,
        ),
        'resolved_from_pages_via_catalog_reference': packet.resolve_archive_any_catalog_reference_from_pages(
            catalog_reference,
            pages,
            page_size=page_size,
        ),
        'resolved_from_ordered_catalog': ordered[slot],
    }



def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    ordered = packet.ordered_fingerprint_catalog(known_fingerprints)
    page_size = packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE
    pages = packet.fingerprint_catalog_pages(ordered, page_size=page_size)
    page_bytes = [packet.packet_minified_bytes(page) for page in pages]
    page_entry_counts = [packet.fingerprint_catalog_page_entry_count(page) for page in pages]
    weighted_touched_bytes = sum(count * page_bytes[index] for index, count in enumerate(page_entry_counts))
    average_touched_page_bytes = weighted_touched_bytes / len(ordered)
    full_string_catalog_bytes = packet.packet_minified_bytes(ordered)
    full_paged_catalog_bytes = packet.packet_minified_bytes(pages)

    sample_slots = [0, 63, 64, 127, 128, 255, 256, len(ordered) - 1]
    sample_rows = [_sample_row(packet, slot, ordered, pages) for slot in sample_slots]

    return {
        'focus': 'Resolve append-only catalog-slot repeat references directly from paged raw-digest catalog state so the archive does not have to rehydrate a full ordered sha256-string list just to map a slot back to its semantic fingerprint.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(ordered),
        'headline_findings': {
            'main_rule': 'when the archive already stores append-only raw-digest catalog pages, catalog-slot repeat references should resolve straight from those pages; do not first rebuild a full ordered sha256-string catalog unless you actually need the human-readable list.',
            'page_size': page_size,
            'page_count': len(pages),
            'page_bytes': page_bytes,
            'page_entry_counts': page_entry_counts,
            'string_catalog_bytes': full_string_catalog_bytes,
            'paged_catalog_bytes': full_paged_catalog_bytes,
            'average_resolution_touched_page_bytes': round(average_touched_page_bytes, 6),
            'max_resolution_touched_page_bytes': max(page_bytes),
            'tail_resolution_touched_page_bytes': page_bytes[-1],
            'average_bytes_avoided_vs_string_catalog': round(full_string_catalog_bytes - average_touched_page_bytes, 6),
            'average_bytes_avoided_share_vs_string_catalog': round((full_string_catalog_bytes - average_touched_page_bytes) / full_string_catalog_bytes, 6),
            'average_bytes_avoided_vs_full_paged_catalog': round(full_paged_catalog_bytes - average_touched_page_bytes, 6),
            'average_bytes_avoided_share_vs_full_paged_catalog': round((full_paged_catalog_bytes - average_touched_page_bytes) / full_paged_catalog_bytes, 6),
        },
        'sample_rows': sample_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }



def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Catalog-Page-Resolution Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- page size: `{findings['page_size']}` across `{findings['page_count']}` pages.",
        f"- page bytes: `{json.dumps(findings['page_bytes'])}` with entry counts `{json.dumps(findings['page_entry_counts'])}`.",
        f"- full ordered string catalog bytes: `{findings['string_catalog_bytes']}`.",
        f"- full paged digest catalog bytes: `{findings['paged_catalog_bytes']}`.",
        f"- average page bytes touched by direct slot resolution: `{findings['average_resolution_touched_page_bytes']}`.",
        f"- average bytes avoided vs rebuilding the full string catalog: `{findings['average_bytes_avoided_vs_string_catalog']}` (`{findings['average_bytes_avoided_share_vs_string_catalog']}` share).",
        f"- average bytes avoided vs scanning the whole paged catalog: `{findings['average_bytes_avoided_vs_full_paged_catalog']}` (`{findings['average_bytes_avoided_share_vs_full_paged_catalog']}` share).",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative slot lookups',
    ]
    for row in report['sample_rows']:
        lines.append(
            f"- slot `{row['slot']}` resolves from page `{row['page_index']}` / entry `{row['entry_index']}` by touching a `{row['page_bytes']}`-byte page: short ref `{row['short_catalog_reference_packet']}` and generic catalog ref `{row['catalog_reference_packet']}` both resolve to `{row['semantic_fingerprint']}` directly from pages."
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
