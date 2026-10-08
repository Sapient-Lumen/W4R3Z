#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.md'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sample_rows(packet):
    rows = [
        {
            'name': 'oracle_coordinates_sms',
            'standalone_packet': packet.packet_from_coordinates('0.0001', '1'),
            'archive_local_packet': packet.packet_from_coordinates('0.0001', '1', archive_local=True),
            'why': 'the same declaration-first decision can arrive in either storage form, so this is the cleanest duplicate-by-semantics example',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'even the justified escalation case should deduplicate across repeats rather than paying for another full body',
        },
    ]
    for row in rows:
        standalone = row['standalone_packet']
        archive_local = row['archive_local_packet']
        standalone_fingerprint = packet.packet_semantic_fingerprint(standalone)
        archive_local_fingerprint = packet.packet_semantic_fingerprint(archive_local)
        reference = packet.packet_reference(standalone)
        first_write = packet.packet_archive_write_plan(standalone, [])
        repeat_write = packet.packet_archive_write_plan(archive_local, [standalone_fingerprint])
        row['standalone_bytes'] = packet.packet_minified_bytes(standalone)
        row['archive_local_bytes'] = packet.packet_minified_bytes(archive_local)
        row['standalone_fingerprint'] = standalone_fingerprint
        row['archive_local_fingerprint'] = archive_local_fingerprint
        row['reference_packet'] = reference
        row['reference_bytes'] = packet.packet_minified_bytes(reference)
        row['body_then_reference_bytes'] = row['archive_local_bytes'] + row['reference_bytes']
        row['two_archive_local_bodies_bytes'] = row['archive_local_bytes'] * 2
        row['duplicate_bytes_saved'] = row['archive_local_bytes'] - row['reference_bytes']
        row['first_write_plan'] = first_write
        row['repeat_write_plan'] = repeat_write
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if row['standalone_fingerprint'] != row['archive_local_fingerprint']:
            raise SystemExit(f"fingerprint mismatch across storage forms for {row['name']}")
        if packet.expand_packet(row['archive_local_packet']) != row['standalone_packet']:
            raise SystemExit(f"expansion mismatch for {row['name']}")
        if row['duplicate_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive duplicate-byte savings for {row['name']}")
        if row['first_write_plan']['recommended_write_kind'] != 'archive_local_body':
            raise SystemExit(f"expected archive_local_body first write for {row['name']}")
        if row['repeat_write_plan']['recommended_write_kind'] != 'reference':
            raise SystemExit(f"expected reference repeat write for {row['name']}")

    best = max(rows, key=lambda row: row['duplicate_bytes_saved'])

    return {
        'focus': 'Deduplicate rematch decision packets by semantic fingerprint so standalone and archive-local variants of the same decision collapse to one stored body plus lightweight references.',
        'method_note': 'Loaded the executable decision-packet module, generated representative standalone and archive-local packets for the same decisions, verified semantic fingerprints match across storage forms, and measured the byte savings of writing a reference instead of another packet body.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'packet_kind': packet.PACKET_KIND,
            'archive_local_packet_kind': packet.ARCHIVE_LOCAL_PACKET_KIND,
            'packet_reference_kind': packet.PACKET_REFERENCE_KIND,
            'fingerprint_algorithm': 'sha256 over canonical expanded standalone packet JSON',
            'same_decision_same_fingerprint_across_storage_forms': True,
            'default_first_write_kind': 'archive_local_body',
            'default_repeat_write_kind': 'reference',
            'best_duplicate_savings_example': best['name'],
            'best_duplicate_bytes_saved': best['duplicate_bytes_saved'],
            'main_rule': 'store one archive-local packet body per semantic fingerprint, then store only reference packets for later repeats of the same decision',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_profile_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Fingerprint Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- packet reference kind: `{findings['packet_reference_kind']}`.",
        f"- fingerprint algorithm: `{findings['fingerprint_algorithm']}`.",
        f"- default first write kind: `{findings['default_first_write_kind']}`.",
        f"- default repeat write kind: `{findings['default_repeat_write_kind']}`.",
        f"- best duplicate-byte savings example: `{findings['best_duplicate_savings_example']}` saves `{findings['best_duplicate_bytes_saved']}` bytes on the repeat write.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative duplicate handling',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> standalone `{row['standalone_bytes']}` bytes, archive-local `{row['archive_local_bytes']}` bytes, reference `{row['reference_bytes']}` bytes; same fingerprint `{row['standalone_fingerprint']}` across forms; storing a repeat as a reference instead of another archive-local body saves `{row['duplicate_bytes_saved']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- packet minimization alone is not enough once the archive accumulates multiple sessions; the same decision can reappear in different storage forms or be regenerated later.',
        '- a semantic fingerprint lets the archive treat those as the same evidence object, keep one archive-local body, and replace later repeats with a tiny reference packet.',
        '',
        '## Sources',
    ])
    for src in summary['sources']:
        lines.append(f'- `{src}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()
