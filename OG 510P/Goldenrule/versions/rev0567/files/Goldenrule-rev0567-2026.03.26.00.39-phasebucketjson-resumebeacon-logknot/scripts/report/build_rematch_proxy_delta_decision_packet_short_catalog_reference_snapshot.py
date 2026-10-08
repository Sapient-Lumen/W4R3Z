#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_short_catalog_reference_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_short_catalog_reference_snapshot_20260307.md'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _row(packet, index: int, row: dict[str, object], known_fingerprints: list[str]) -> dict[str, object]:
    standalone = row['packet']
    fingerprint = packet.packet_semantic_fingerprint(standalone)
    byte_reference = packet.packet_byte_reference(standalone, known_fingerprints)
    catalog_reference = packet.packet_catalog_reference(standalone, known_fingerprints)
    short_catalog_reference = packet.packet_short_catalog_reference(standalone, known_fingerprints)
    return {
        'slot': index,
        'name': row['name'],
        'mode': standalone['mode'],
        'semantic_fingerprint': fingerprint,
        'byte_reference_packet': byte_reference,
        'catalog_reference_packet': catalog_reference,
        'short_catalog_reference_packet': short_catalog_reference,
        'byte_reference_bytes': packet.packet_minified_bytes(byte_reference),
        'catalog_reference_bytes': packet.packet_minified_bytes(catalog_reference),
        'short_catalog_reference_bytes': packet.packet_minified_bytes(short_catalog_reference),
        'bytes_saved_vs_byte_reference': packet.packet_minified_bytes(byte_reference) - packet.packet_minified_bytes(short_catalog_reference),
        'bytes_saved_vs_catalog_reference': packet.packet_minified_bytes(catalog_reference) - packet.packet_minified_bytes(short_catalog_reference),
        'resolved_fingerprint': packet.resolve_archive_any_reference(short_catalog_reference, known_fingerprints),
        'yocto_repeat_write_plan': packet.packet_archive_yocto_write_plan(standalone, known_fingerprints),
        'set_fallback_repeat_write_plan': packet.packet_archive_yocto_write_plan(standalone, set(known_fingerprints)),
    }


def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]

    rows = [_row(packet, index, row, known_fingerprints) for index, row in enumerate(deterministic_packets)]
    short_length_distribution = Counter(row['short_catalog_reference_bytes'] for row in rows)
    catalog_length_distribution = Counter(row['catalog_reference_bytes'] for row in rows)
    byte_length_distribution = Counter(row['byte_reference_bytes'] for row in rows)
    total_byte_bytes = sum(row['byte_reference_bytes'] for row in rows)
    total_catalog_bytes = sum(row['catalog_reference_bytes'] for row in rows)
    total_short_bytes = sum(row['short_catalog_reference_bytes'] for row in rows)

    sample_indices = [0, 42, 127, 128, len(rows) - 1]
    sample_rows = [rows[index] for index in sample_indices]

    return {
        'focus': 'Shrink repeat writes below uvarint catalog-slot references by packing the common under-16384 append-only slot range into one 14-bit short token.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(rows),
        'headline_findings': {
            'main_rule': 'when the archive preserves an append-only ordered semantic-fingerprint catalog and the slot fits under 16384, repeats should store a short_catalog_reference; otherwise fall back to catalog_reference, and if only an unordered fingerprint set is available, fall back to byte_reference.',
            'byte_reference_total_bytes': total_byte_bytes,
            'catalog_reference_total_bytes': total_catalog_bytes,
            'short_catalog_reference_total_bytes': total_short_bytes,
            'repeat_bytes_saved_vs_byte_reference': total_byte_bytes - total_short_bytes,
            'repeat_byte_savings_share_vs_byte_reference': round((total_byte_bytes - total_short_bytes) / total_byte_bytes, 6),
            'repeat_bytes_saved_vs_catalog_reference': total_catalog_bytes - total_short_bytes,
            'repeat_byte_savings_share_vs_catalog_reference': round((total_catalog_bytes - total_short_bytes) / total_catalog_bytes, 6),
            'average_short_catalog_reference_bytes': round(total_short_bytes / len(rows), 6),
            'short_catalog_reference_length_distribution': dict(sorted(short_length_distribution.items())),
            'catalog_reference_length_distribution': dict(sorted(catalog_length_distribution.items())),
            'byte_reference_length_distribution': dict(sorted(byte_length_distribution.items())),
            'short_catalog_reference_max_slot': packet.SHORT_CATALOG_REFERENCE_MAX_SLOT,
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
        '# Rematch-Proxy Decision Packet Short-Catalog-Reference Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- byte-reference total repeat bytes: `{findings['byte_reference_total_bytes']}`.",
        f"- catalog-reference total repeat bytes: `{findings['catalog_reference_total_bytes']}`.",
        f"- short-catalog-reference total repeat bytes: `{findings['short_catalog_reference_total_bytes']}`.",
        f"- repeat bytes saved vs byte-reference: `{findings['repeat_bytes_saved_vs_byte_reference']}` (`{findings['repeat_byte_savings_share_vs_byte_reference']}` share).",
        f"- repeat bytes saved vs catalog-reference: `{findings['repeat_bytes_saved_vs_catalog_reference']}` (`{findings['repeat_byte_savings_share_vs_catalog_reference']}` share).",
        f"- average short-catalog-reference bytes: `{findings['average_short_catalog_reference_bytes']}`.",
        f"- short-catalog-reference length distribution: `{json.dumps(findings['short_catalog_reference_length_distribution'], sort_keys=True)}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative catalog slots',
    ]
    for row in report['sample_rows']:
        lines.append(
            f"- slot `{row['slot']}` / `{row['name']}` (`{row['mode']}`): short `{row['short_catalog_reference_packet']}` at `{row['short_catalog_reference_bytes']}` bytes vs catalog `{row['catalog_reference_packet']}` at `{row['catalog_reference_bytes']}` and byte-reference `{row['byte_reference_packet']}` at `{row['byte_reference_bytes']}`, saving `{row['bytes_saved_vs_catalog_reference']}` vs catalog and `{row['bytes_saved_vs_byte_reference']}` vs byte-reference; yocto repeat kind `{row['yocto_repeat_write_plan']['recommended_write_kind']}`, unordered-set fallback `{row['set_fallback_repeat_write_plan']['recommended_write_kind']}`."
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
