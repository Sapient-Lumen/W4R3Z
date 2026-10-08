#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_coded_reference_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_coded_reference_snapshot_20260307.md'


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
            'why': 'the declaration-first coordinate case isolates the reference-wrapper savings cleanly because the semantic body is already minimal under the coded-seed layer.',
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
            'why': 'even when the body is heavier, every duplicate write still benefits from shrinking the repeat reference wrapper itself.',
        },
        {
            'name': 'robustness_adaptive_cap_sensitive',
            'standalone_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
            'archive_local_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M', archive_local=True),
            'why': 'adaptive route packets are the natural stress test for repeated archival notes because many future sessions may refer back to the same robustness verdict.',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'the escalated tie-cap case matters because even justified heavy diagnoses should have the lightest possible in-archive repeat pointer.',
        },
    ]
    known_fingerprints = [packet.packet_semantic_fingerprint(row['standalone_packet']) for row in rows]
    for row in rows:
        standalone = row['standalone_packet']
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        portable_reference = packet.packet_reference(standalone)
        archive_local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        coded_reference = packet.packet_coded_reference(standalone, known_fingerprints)
        coded_seed = packet.packet_coded_seed(standalone)
        nano_repeat = packet.packet_archive_nano_write_plan(standalone, known_fingerprints)
        pico_first = packet.packet_archive_pico_write_plan(standalone, [])
        pico_repeat = packet.packet_archive_pico_write_plan(standalone, known_fingerprints)
        row.update(
            {
                'semantic_fingerprint': fingerprint,
                'portable_reference_packet': portable_reference,
                'archive_local_reference_packet': archive_local_reference,
                'coded_reference_packet': coded_reference,
                'portable_reference_bytes': packet.packet_minified_bytes(portable_reference),
                'archive_local_reference_bytes': packet.packet_minified_bytes(archive_local_reference),
                'coded_reference_bytes': packet.packet_minified_bytes(coded_reference),
                'coded_seed_packet': coded_seed,
                'coded_seed_bytes': packet.packet_minified_bytes(coded_seed),
                'portable_reference_to_coded_reference_bytes_saved': packet.packet_minified_bytes(portable_reference)
                - packet.packet_minified_bytes(coded_reference),
                'archive_local_reference_to_coded_reference_bytes_saved': packet.packet_minified_bytes(archive_local_reference)
                - packet.packet_minified_bytes(coded_reference),
                'coded_seed_then_archive_local_reference_bytes': packet.packet_minified_bytes(coded_seed)
                + packet.packet_minified_bytes(archive_local_reference),
                'coded_seed_then_coded_reference_bytes': packet.packet_minified_bytes(coded_seed)
                + packet.packet_minified_bytes(coded_reference),
                'nano_repeat_write_plan': nano_repeat,
                'pico_first_write_plan': pico_first,
                'pico_repeat_write_plan': pico_repeat,
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if packet.expand_coded_reference_packet(row['coded_reference_packet']) != row['archive_local_reference_packet']:
            raise SystemExit(f"coded-reference expansion mismatch for {row['name']}")
        if packet.resolve_archive_any_reference(row['coded_reference_packet'], [row['semantic_fingerprint']]) != row['semantic_fingerprint']:
            raise SystemExit(f"coded-reference resolution mismatch for {row['name']}")
        if row['archive_local_reference_to_coded_reference_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive archive-local-reference to coded-reference savings for {row['name']}")
        if row['pico_first_write_plan']['recommended_write_kind'] != 'coded_seed_body':
            raise SystemExit(f"expected coded_seed_body first write for {row['name']}")
        if row['pico_repeat_write_plan']['recommended_write_kind'] != 'coded_reference':
            raise SystemExit(f"expected coded_reference repeat write for {row['name']}")

    best_local = max(rows, key=lambda row: row['archive_local_reference_to_coded_reference_bytes_saved'])
    best_portable = max(rows, key=lambda row: row['portable_reference_to_coded_reference_bytes_saved'])
    codebook_default = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=True,
    )
    fallback_default = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=False,
    )

    return {
        'focus': 'Shrink duplicate rematch decision writes below archive-local prefix references by moving the repeat-reference wrapper itself into a tiny local codebook.',
        'method_note': 'Loaded the executable decision-packet module, converted representative duplicate writes into portable references, archive-local prefix references, and coded references, verified exact expansion and resolution, and measured minified byte savings for repeat-write storage.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'coded_reference_kind': packet.CODED_REFERENCE_KIND,
            'default_repeat_storage_form_with_codebook': codebook_default['recommended_storage_form'],
            'fallback_repeat_storage_form_without_codebook': fallback_default['recommended_storage_form'],
            'best_archive_local_reference_to_coded_reference_savings_example': best_local['name'],
            'best_archive_local_reference_to_coded_reference_bytes_saved': best_local['archive_local_reference_to_coded_reference_bytes_saved'],
            'best_portable_reference_to_coded_reference_savings_example': best_portable['name'],
            'best_portable_reference_to_coded_reference_bytes_saved': best_portable['portable_reference_to_coded_reference_bytes_saved'],
            'main_rule': 'when the archive preserves the local reference codebook, duplicate writes should store coded references rather than larger archive-local prefix references or exported full-fingerprint references',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Coded-Reference Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- coded reference kind: `{findings['coded_reference_kind']}`.",
        f"- default in-archive repeat storage form with the reference codebook: `{findings['default_repeat_storage_form_with_codebook']}`.",
        f"- fallback repeat storage form without the reference codebook: `{findings['fallback_repeat_storage_form_without_codebook']}`.",
        f"- best measured archive-local-reference to coded-reference saving: `{findings['best_archive_local_reference_to_coded_reference_bytes_saved']}` bytes on `{findings['best_archive_local_reference_to_coded_reference_savings_example']}`.",
        f"- best measured portable-reference to coded-reference saving: `{findings['best_portable_reference_to_coded_reference_bytes_saved']}` bytes on `{findings['best_portable_reference_to_coded_reference_savings_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative repeat-write savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> portable reference `{row['portable_reference_bytes']}` bytes, archive-local prefix reference `{row['archive_local_reference_bytes']}` bytes, coded reference `{row['coded_reference_bytes']}` bytes; switching the repeat artifact from prefix reference to coded reference saves `{row['archive_local_reference_to_coded_reference_bytes_saved']}` bytes, and the two-write total drops from `{row['coded_seed_then_archive_local_reference_bytes']}` to `{row['coded_seed_then_coded_reference_bytes']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- prefix references already stopped repeating the full exported hash string, but they still kept a long JSON wrapper on every duplicate write.',
        '- once the archive already depends on local codebooks for coded seeds, there is little reason to leave repeat references self-describing and verbose.',
        '- archive-local prefix references still matter as the clearer fallback tier when operators want a more explicit local pointer without using the repeat-reference codebook.',
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
