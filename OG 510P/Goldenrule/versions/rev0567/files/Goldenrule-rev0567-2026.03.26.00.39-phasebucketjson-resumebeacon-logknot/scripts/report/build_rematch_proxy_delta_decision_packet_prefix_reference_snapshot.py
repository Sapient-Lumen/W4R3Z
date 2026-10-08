#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.md'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _base_rows(packet):
    return [
        {
            'name': 'oracle_coordinates_sms',
            'packet': packet.packet_from_coordinates('0.0001', '1'),
            'why': 'a repeated declaration-first decision should not keep paying for the full sha256 string once the archive already indexes the body.',
        },
        {
            'name': 'oracle_weights_smm',
            'packet': packet.packet_from_weights(
                {
                    'w_width': '0',
                    'w_buffer': '0',
                    'w_knife': '0',
                    'w_delta': '0',
                    'w_material': '0',
                    'w_undecided': '0',
                    'w_ties': '0',
                    'w_hazard': '1',
                }
            ),
            'why': 'the heavier declaration packet benefits most from already using semantic cores on first write, so its repeat pointer should be as small as possible too.',
        },
        {
            'name': 'robustness_adaptive_cap_sensitive',
            'packet': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
            'why': 'adaptive black-box routes are already compact, which makes the remaining full-fingerprint repeat reference look especially wasteful.',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'why': 'even the justified escalation case should repeat by the shortest unique archive address, not by restating the whole hash.',
        },
    ]


def _sample_rows(packet):
    rows = _base_rows(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in rows]
    for row, fingerprint in zip(rows, known_fingerprints):
        standalone = row['packet']
        semantic_core = packet.packet_semantic_core(standalone)
        portable_reference = packet.packet_reference(standalone)
        archive_local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        portable_repeat = packet.packet_archive_compact_write_plan(standalone, known_fingerprints)
        ultracompact_repeat = packet.packet_archive_ultracompact_write_plan(standalone, known_fingerprints)
        first_write = packet.packet_archive_ultracompact_write_plan(standalone, [])
        prefix_hex_len = packet.minimal_unique_reference_prefix_hex_len(fingerprint, known_fingerprints)
        row.update(
            {
                'semantic_fingerprint': fingerprint,
                'semantic_core_packet': semantic_core,
                'semantic_core_bytes': packet.packet_minified_bytes(semantic_core),
                'portable_reference_packet': portable_reference,
                'portable_reference_bytes': packet.packet_minified_bytes(portable_reference),
                'archive_local_reference_packet': archive_local_reference,
                'archive_local_reference_bytes': packet.packet_minified_bytes(archive_local_reference),
                'prefix_hex_len': prefix_hex_len,
                'resolved_fingerprint': packet.resolve_archive_local_reference(archive_local_reference, known_fingerprints),
                'repeat_reference_bytes_saved': packet.packet_minified_bytes(portable_reference)
                - packet.packet_minified_bytes(archive_local_reference),
                'semantic_core_then_portable_reference_bytes': packet.packet_minified_bytes(semantic_core)
                + packet.packet_minified_bytes(portable_reference),
                'semantic_core_then_archive_local_reference_bytes': packet.packet_minified_bytes(semantic_core)
                + packet.packet_minified_bytes(archive_local_reference),
                'portable_repeat_write_plan': portable_repeat,
                'ultracompact_repeat_write_plan': ultracompact_repeat,
                'ultracompact_first_write_plan': first_write,
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if row['portable_repeat_write_plan']['recommended_write_kind'] != 'reference':
            raise SystemExit(f"expected portable reference repeat for {row['name']}")
        if row['ultracompact_repeat_write_plan']['recommended_write_kind'] != 'archive_local_reference':
            raise SystemExit(f"expected archive-local reference repeat for {row['name']}")
        if row['ultracompact_first_write_plan']['recommended_write_kind'] != 'semantic_core_body':
            raise SystemExit(f"expected semantic-core first write for {row['name']}")
        if row['resolved_fingerprint'] != row['semantic_fingerprint']:
            raise SystemExit(f"archive-local prefix reference did not resolve for {row['name']}")
        if row['repeat_reference_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive repeat-reference savings for {row['name']}")

    best = max(rows, key=lambda row: row['repeat_reference_bytes_saved'])
    longest_prefix = max(rows, key=lambda row: row['prefix_hex_len'])

    return {
        'focus': 'Shrink duplicate rematch decision references inside the archive by replacing full semantic fingerprints with the shortest unique local prefix that resolves against the known body index.',
        'method_note': 'Loaded the executable decision-packet module, generated representative semantic decisions, built both portable full-fingerprint references and archive-local prefix references against the same known fingerprint set, verified prefix resolution, and measured repeat-write byte savings.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'portable_reference_kind': packet.PACKET_REFERENCE_KIND,
            'archive_local_reference_kind': packet.ARCHIVE_LOCAL_REFERENCE_KIND,
            'min_reference_prefix_hex_len': packet.MIN_REFERENCE_PREFIX_HEX_LEN,
            'default_first_write_kind': 'semantic_core_body',
            'default_repeat_write_kind_inside_archive': 'archive_local_reference',
            'portable_repeat_write_kind': 'reference',
            'best_repeat_reference_savings_example': best['name'],
            'best_repeat_reference_bytes_saved': best['repeat_reference_bytes_saved'],
            'longest_required_prefix_example': longest_prefix['name'],
            'longest_required_prefix_hex_len': longest_prefix['prefix_hex_len'],
            'main_rule': 'after the archive already stores a semantic body, repeat writes should use the shortest unique local fingerprint prefix instead of a full exported fingerprint string',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_core_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Prefix-Reference Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- portable reference kind: `{findings['portable_reference_kind']}`.",
        f"- archive-local reference kind: `{findings['archive_local_reference_kind']}`.",
        f"- minimum configured prefix length: `{findings['min_reference_prefix_hex_len']}` hex characters.",
        f"- default first write kind: `{findings['default_first_write_kind']}`.",
        f"- default repeat write kind inside archive: `{findings['default_repeat_write_kind_inside_archive']}`.",
        f"- best measured repeat-reference saving: `{findings['best_repeat_reference_bytes_saved']}` bytes on `{findings['best_repeat_reference_savings_example']}`.",
        f"- longest required prefix in the representative set: `{findings['longest_required_prefix_hex_len']}` hex characters on `{findings['longest_required_prefix_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative repeat handling',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> semantic core `{row['semantic_core_bytes']}` bytes, portable reference `{row['portable_reference_bytes']}` bytes, archive-local prefix reference `{row['archive_local_reference_bytes']}` bytes, unique prefix `{row['archive_local_reference_packet']['prefix']}` (`{row['prefix_hex_len']}` hex); switching the repeat write from a portable reference to the local prefix form saves `{row['repeat_reference_bytes_saved']}` bytes, and the two-write total drops from `{row['semantic_core_then_portable_reference_bytes']}` to `{row['semantic_core_then_archive_local_reference_bytes']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- semantic cores already made first writes small, but duplicate references were still paying for a full exported sha256 string even when the archive already had a content-addressed local index.',
        '- prefix-resolved local references keep export-safe full fingerprints available when packets leave the archive, while letting in-archive repeats pay only for the shortest unambiguous pointer.',
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
