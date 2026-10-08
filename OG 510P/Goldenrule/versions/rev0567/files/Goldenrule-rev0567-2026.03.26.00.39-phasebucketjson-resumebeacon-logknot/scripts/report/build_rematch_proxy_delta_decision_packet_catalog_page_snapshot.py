#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_page_snapshot_20260307.md'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    ordered = packet.ordered_fingerprint_catalog(known_fingerprints)
    page_size = packet.DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE
    monolith = packet.fingerprint_catalog_page(ordered)
    pages = packet.fingerprint_catalog_pages(ordered, page_size=page_size)
    expanded = packet.expand_fingerprint_catalog_pages(pages)
    lookup = packet.fingerprint_catalog_lookup_from_pages(pages)
    new_fingerprint = 'sha256:' + 'ab' * 32
    appended_pages = packet.append_fingerprint_catalog_pages(pages, new_fingerprint, page_size=page_size)
    overflow_pages = packet.fingerprint_catalog_pages(ordered[: page_size * 4], page_size=page_size)
    overflow_appended = packet.append_fingerprint_catalog_pages(overflow_pages, new_fingerprint, page_size=page_size)

    string_catalog_bytes = packet.packet_minified_bytes(ordered)
    monolith_catalog_bytes = packet.packet_minified_bytes(monolith)
    paged_catalog_bytes = packet.packet_minified_bytes(pages)
    page_lengths = [packet.packet_minified_bytes(page) for page in pages]
    total_saved_vs_strings = string_catalog_bytes - paged_catalog_bytes
    monolith_saved_vs_strings = string_catalog_bytes - monolith_catalog_bytes
    append_tail_old_page_bytes = packet.packet_minified_bytes(pages[-1])
    append_tail_new_page_bytes = packet.packet_minified_bytes(appended_pages[-1])
    append_tail_growth_bytes = append_tail_new_page_bytes - append_tail_old_page_bytes
    appended_string_catalog_bytes = packet.packet_minified_bytes(ordered + [new_fingerprint])
    overflow_new_page_bytes = packet.packet_minified_bytes(overflow_appended[-1])

    sample_page_rows = []
    start = 0
    for page_index, page in enumerate(pages):
        page_entries = packet.expand_fingerprint_catalog_page(page)
        end = start + len(page_entries) - 1
        sample_page_rows.append(
            {
                'page_index': page_index,
                'slot_range': [start, end],
                'entry_count': len(page_entries),
                'page_bytes': packet.packet_minified_bytes(page),
                'first_fingerprint': page_entries[0],
                'last_fingerprint': page_entries[-1],
            }
        )
        start = end + 1

    return {
        'focus': 'Store the append-only semantic-fingerprint catalog as paged raw-digest blocks so catalog-slot repeat references stay cheap without dragging along a bulky string catalog.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(ordered),
        'headline_findings': {
            'main_rule': 'when the archive uses catalog-slot repeats, it should keep the append-only fingerprint catalog as paged raw-digest blocks; rehydrate full sha256 strings only for export, debugging, or external interchange.',
            'page_size': page_size,
            'string_catalog_bytes': string_catalog_bytes,
            'monolith_catalog_page_bytes': monolith_catalog_bytes,
            'paged_catalog_bytes': paged_catalog_bytes,
            'total_bytes_saved_vs_strings': total_saved_vs_strings,
            'bytes_saved_share_vs_strings': round(total_saved_vs_strings / string_catalog_bytes, 6),
            'monolith_bytes_saved_vs_strings': monolith_saved_vs_strings,
            'monolith_saved_share_vs_strings': round(monolith_saved_vs_strings / string_catalog_bytes, 6),
            'page_count': len(pages),
            'page_length_distribution': page_lengths,
            'append_tail_old_page_bytes': append_tail_old_page_bytes,
            'append_tail_new_page_bytes': append_tail_new_page_bytes,
            'append_tail_growth_bytes': append_tail_growth_bytes,
            'appended_string_catalog_bytes': appended_string_catalog_bytes,
            'overflow_page_count_before_append': len(overflow_pages),
            'overflow_page_count_after_append': len(overflow_appended),
            'overflow_new_page_bytes': overflow_new_page_bytes,
        },
        'sample_page_rows': sample_page_rows,
        'lookup_checks': {
            'slot_0': lookup[ordered[0]],
            'slot_127': lookup[ordered[127]],
            'slot_128': lookup[ordered[128]],
            'slot_last': lookup[ordered[-1]],
            'roundtrip_ok': expanded == ordered,
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
        '# Rematch-Proxy Decision Packet Catalog-Page Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- default page size: `{findings['page_size']}`.",
        f"- string catalog bytes: `{findings['string_catalog_bytes']}`.",
        f"- monolith raw-digest page bytes: `{findings['monolith_catalog_page_bytes']}`.",
        f"- paged raw-digest catalog bytes: `{findings['paged_catalog_bytes']}`.",
        f"- paged savings vs strings: `{findings['total_bytes_saved_vs_strings']}` (`{findings['bytes_saved_share_vs_strings']}` share).",
        f"- monolith savings vs strings: `{findings['monolith_bytes_saved_vs_strings']}` (`{findings['monolith_saved_share_vs_strings']}` share).",
        f"- page count: `{findings['page_count']}` with per-page byte lengths `{json.dumps(findings['page_length_distribution'])}`.",
        f"- append to the current 18-entry tail page changes only one page artifact: `{findings['append_tail_old_page_bytes']}` -> `{findings['append_tail_new_page_bytes']}` bytes (`+{findings['append_tail_growth_bytes']}`), instead of rewriting a `{findings['appended_string_catalog_bytes']}`-byte string catalog.",
        f"- if the tail page is already full, append creates one new `{findings['overflow_new_page_bytes']}`-byte page and page count goes `{findings['overflow_page_count_before_append']}` -> `{findings['overflow_page_count_after_append']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative pages',
    ]
    for row in report['sample_page_rows']:
        lines.append(
            f"- page `{row['page_index']}` covers slots `{row['slot_range'][0]}`-`{row['slot_range'][1]}` with `{row['entry_count']}` digests at `{row['page_bytes']}` bytes; first `{row['first_fingerprint']}`, last `{row['last_fingerprint']}`."
        )
    lines.extend(
        [
            '',
            '## Lookup checks',
            f"- slot 0: `{report['lookup_checks']['slot_0']}`.",
            f"- slot 127: `{report['lookup_checks']['slot_127']}`.",
            f"- slot 128: `{report['lookup_checks']['slot_128']}`.",
            f"- slot last: `{report['lookup_checks']['slot_last']}`.",
            f"- round-trip exact: `{report['lookup_checks']['roundtrip_ok']}`.",
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
