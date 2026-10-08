#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.md'


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
            'why': 'the declaration-first coordinate case shows the purest gain from moving archive-local mode and contract strings into the shared codebook.',
        },
        {
            'name': 'oracle_weights_smm',
            'standalone_packet': packet.packet_from_weights(
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
            'archive_local_packet': packet.packet_from_weights(
                {
                    'w_width': '0',
                    'w_buffer': '0',
                    'w_knife': '0',
                    'w_delta': '0',
                    'w_material': '0',
                    'w_undecided': '0',
                    'w_ties': '0',
                    'w_hazard': '1',
                },
                archive_local=True,
            ),
            'why': 'even when the evidence payload itself is large, the archive can still stop repeating the long semantic-core wrapper on every first write.',
        },
        {
            'name': 'robustness_adaptive_cap_sensitive',
            'standalone_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
            'archive_local_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M', archive_local=True),
            'why': 'adaptive black-box routes are especially codebook-friendly because the long-lived body is just one short route string plus a mode code.',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'the exact-path escalation case shows that even justified heavier diagnoses can collapse to a tiny archive-local seed without losing reproducibility.',
        },
    ]
    known_fingerprints = [packet.packet_semantic_fingerprint(row['standalone_packet']) for row in rows]
    for row in rows:
        standalone = row['standalone_packet']
        archive_local = row['archive_local_packet']
        semantic_core = packet.packet_semantic_core(standalone)
        coded_seed = packet.packet_coded_seed(standalone)
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        first_write = packet.packet_archive_nano_write_plan(standalone, [])
        repeat_write = packet.packet_archive_nano_write_plan(standalone, known_fingerprints)
        local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        row.update(
            {
                'semantic_core_packet': semantic_core,
                'coded_seed_packet': coded_seed,
                'semantic_fingerprint': fingerprint,
                'standalone_bytes': packet.packet_minified_bytes(standalone),
                'archive_local_bytes': packet.packet_minified_bytes(archive_local),
                'semantic_core_bytes': packet.packet_minified_bytes(semantic_core),
                'coded_seed_bytes': packet.packet_minified_bytes(coded_seed),
                'archive_local_reference_packet': local_reference,
                'archive_local_reference_bytes': packet.packet_minified_bytes(local_reference),
                'semantic_core_to_coded_seed_bytes_saved': packet.packet_minified_bytes(semantic_core)
                - packet.packet_minified_bytes(coded_seed),
                'archive_local_to_coded_seed_bytes_saved': packet.packet_minified_bytes(archive_local)
                - packet.packet_minified_bytes(coded_seed),
                'coded_seed_then_reference_bytes': packet.packet_minified_bytes(coded_seed)
                + packet.packet_minified_bytes(local_reference),
                'semantic_core_then_reference_bytes': packet.packet_minified_bytes(semantic_core)
                + packet.packet_minified_bytes(local_reference),
                'nano_first_write_plan': first_write,
                'nano_repeat_write_plan': repeat_write,
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if packet.expand_coded_seed_packet(row['coded_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"coded-seed standalone expansion mismatch for {row['name']}")
        if packet.expand_coded_seed_packet(row['coded_seed_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"coded-seed archive-local expansion mismatch for {row['name']}")
        if packet.expand_packet(row['coded_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"expand_packet coded-seed mismatch for {row['name']}")
        if row['semantic_core_to_coded_seed_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive semantic-core to coded-seed savings for {row['name']}")
        if row['nano_first_write_plan']['recommended_write_kind'] != 'coded_seed_body':
            raise SystemExit(f"expected coded_seed_body first write for {row['name']}")
        if row['nano_repeat_write_plan']['recommended_write_kind'] != 'archive_local_reference':
            raise SystemExit(f"expected archive_local_reference repeat write for {row['name']}")

    best_core_savings = max(rows, key=lambda row: row['semantic_core_to_coded_seed_bytes_saved'])
    best_archive_savings = max(rows, key=lambda row: row['archive_local_to_coded_seed_bytes_saved'])
    codebook_default = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
    )
    fallback_machine_default = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=False,
    )

    return {
        'focus': 'Shrink first-write rematch decision bodies below semantic cores by replacing repeated mode and contract strings with a shared archive-local seed codebook.',
        'method_note': 'Loaded the executable decision-packet module, converted representative packets into archive-local coded seeds, verified lossless expansion back to both standalone and archive-local packet forms, and measured minified byte savings relative to semantic cores and archive-local packet bodies.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'coded_seed_kind': packet.CODED_SEED_KIND,
            'coded_seed_profile_ref': packet.CODED_SEED_PROFILE_REF,
            'coded_seed_mode_codes': packet.CODED_SEED_MODE_CODES,
            'default_machine_storage_form_with_codebook': codebook_default['recommended_storage_form'],
            'fallback_machine_storage_form_without_codebook': fallback_machine_default['recommended_storage_form'],
            'best_semantic_core_to_coded_seed_savings_example': best_core_savings['name'],
            'best_semantic_core_to_coded_seed_bytes_saved': best_core_savings['semantic_core_to_coded_seed_bytes_saved'],
            'best_archive_local_to_coded_seed_savings_example': best_archive_savings['name'],
            'best_archive_local_to_coded_seed_bytes_saved': best_archive_savings['archive_local_to_coded_seed_bytes_saved'],
            'main_rule': 'when the archive preserves the local seed codebook, first writes should keep one coded seed per fingerprint and reserve semantic cores for the more self-describing fallback tier',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_core_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Coded-Seed Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- coded seed kind: `{findings['coded_seed_kind']}`.",
        f"- coded seed profile ref: `{findings['coded_seed_profile_ref']}`.",
        f"- coded seed mode codes: `{findings['coded_seed_mode_codes']}`.",
        f"- default machine-oriented in-archive storage form when the codebook is available: `{findings['default_machine_storage_form_with_codebook']}`.",
        f"- fallback machine-oriented storage form without the codebook: `{findings['fallback_machine_storage_form_without_codebook']}`.",
        f"- best measured semantic-core to coded-seed saving: `{findings['best_semantic_core_to_coded_seed_bytes_saved']}` bytes on `{findings['best_semantic_core_to_coded_seed_savings_example']}`.",
        f"- best measured archive-local to coded-seed saving: `{findings['best_archive_local_to_coded_seed_bytes_saved']}` bytes on `{findings['best_archive_local_to_coded_seed_savings_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative first-write savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> archive-local `{row['archive_local_bytes']}` bytes, semantic core `{row['semantic_core_bytes']}` bytes, coded seed `{row['coded_seed_bytes']}` bytes, repeat prefix reference `{row['archive_local_reference_bytes']}` bytes; switching the first durable body from semantic core to coded seed saves `{row['semantic_core_to_coded_seed_bytes_saved']}` bytes and the two-write total drops from `{row['semantic_core_then_reference_bytes']}` to `{row['coded_seed_then_reference_bytes']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- semantic cores removed deterministic result fields, but they still repeated a long packet-kind string, a long contract string, and verbose mode names on every new body.',
        '- inside this archive, those repeated wrapper strings can move into a shared codebook because the executable expander is already part of the durable environment.',
        '- semantic cores still matter as the more self-describing fallback tier when the archive wants a less compressed but easier-to-inspect machine seed.',
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
