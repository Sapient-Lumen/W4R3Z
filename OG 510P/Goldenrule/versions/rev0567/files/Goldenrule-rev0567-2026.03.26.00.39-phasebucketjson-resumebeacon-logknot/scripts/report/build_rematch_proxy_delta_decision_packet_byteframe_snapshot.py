#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_byteframe_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_byteframe_snapshot_20260307.md'


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
            'why': 'coordinate packets still had to pay JSON list punctuation in the packed tier; byteframes keep the same atomized scalar payload while removing that wrapper.',
        },
        {
            'name': 'oracle_weights_hazard_only',
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
            'why': 'one-hot weight declarations now avoid both repeated JSON keys and the leftover packed-list wrapper, so the byteframe keeps only a few raw bytes before base64url encoding.',
        },
        {
            'name': 'oracle_weights_dense_all_ones',
            'standalone_packet': packet.packet_from_weights({key: '1' for key in packet.WEIGHT_KEYS}),
            'archive_local_packet': packet.packet_from_weights({key: '1' for key in packet.WEIGHT_KEYS}, archive_local=True),
            'why': 'dense repeated-value weights already benefited from grouped atom masks; byteframes then remove the remaining list punctuation and decimal integer text around that grouped payload.',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'the exact checked-cap tie path matters because it is the expensive full-path branch we still want to preserve in the smallest durable first-write body.',
        },
    ]
    known_fingerprints = [packet.packet_semantic_fingerprint(row['standalone_packet']) for row in rows]
    for row in rows:
        standalone = row['standalone_packet']
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        packed_seed = packet.packet_packed_seed(standalone)
        byte_seed = packet.packet_byte_seed(standalone)
        packed_reference = packet.packet_packed_reference(standalone, known_fingerprints)
        byte_reference = packet.packet_byte_reference(standalone, known_fingerprints)
        atto_first = packet.packet_archive_atto_write_plan(standalone, [])
        atto_repeat = packet.packet_archive_atto_write_plan(standalone, known_fingerprints)
        zepto_first = packet.packet_archive_zepto_write_plan(standalone, [])
        zepto_repeat = packet.packet_archive_zepto_write_plan(standalone, known_fingerprints)
        row.update(
            {
                'semantic_fingerprint': fingerprint,
                'packed_seed_packet': packed_seed,
                'byte_seed_packet': byte_seed,
                'packed_reference_packet': packed_reference,
                'byte_reference_packet': byte_reference,
                'packed_seed_bytes': packet.packet_minified_bytes(packed_seed),
                'byte_seed_bytes': packet.packet_minified_bytes(byte_seed),
                'packed_reference_bytes': packet.packet_minified_bytes(packed_reference),
                'byte_reference_bytes': packet.packet_minified_bytes(byte_reference),
                'packed_seed_to_byte_seed_bytes_saved': packet.packet_minified_bytes(packed_seed)
                - packet.packet_minified_bytes(byte_seed),
                'packed_reference_to_byte_reference_bytes_saved': packet.packet_minified_bytes(packed_reference)
                - packet.packet_minified_bytes(byte_reference),
                'packed_seed_then_packed_reference_bytes': packet.packet_minified_bytes(packed_seed)
                + packet.packet_minified_bytes(packed_reference),
                'byte_seed_then_byte_reference_bytes': packet.packet_minified_bytes(byte_seed)
                + packet.packet_minified_bytes(byte_reference),
                'atto_first_write_plan': atto_first,
                'atto_repeat_write_plan': atto_repeat,
                'zepto_first_write_plan': zepto_first,
                'zepto_repeat_write_plan': zepto_repeat,
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if packet.expand_byte_seed_packet(row['byte_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"byte-seed standalone expansion mismatch for {row['name']}")
        if packet.expand_byte_seed_packet(row['byte_seed_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"byte-seed archive-local expansion mismatch for {row['name']}")
        if packet.expand_packet(row['byte_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"expand_packet byte-seed mismatch for {row['name']}")
        if packet.expand_byte_reference_packet(row['byte_reference_packet']) != packet.expand_packed_reference_packet(row['packed_reference_packet']):
            raise SystemExit(f"byte-reference expansion mismatch for {row['name']}")
        if packet.resolve_archive_any_reference(row['byte_reference_packet'], [row['semantic_fingerprint']]) != row['semantic_fingerprint']:
            raise SystemExit(f"byte-reference resolution mismatch for {row['name']}")
        if row['packed_seed_to_byte_seed_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive packed-seed to byte-seed savings for {row['name']}")
        if row['packed_reference_to_byte_reference_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive packed-reference to byte-reference savings for {row['name']}")
        if row['zepto_first_write_plan']['recommended_write_kind'] != 'byte_seed_body':
            raise SystemExit(f"expected byte_seed_body first write for {row['name']}")
        if row['zepto_repeat_write_plan']['recommended_write_kind'] != 'byte_reference':
            raise SystemExit(f"expected byte_reference repeat write for {row['name']}")

    best_seed = max(rows, key=lambda row: row['packed_seed_to_byte_seed_bytes_saved'])
    best_reference = max(rows, key=lambda row: row['packed_reference_to_byte_reference_bytes_saved'])
    seed_default = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=True,
        archive_has_seed_packed_codec=True,
        archive_has_seed_byteframe_codec=True,
    )
    seed_fallback = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=True,
        archive_has_seed_packed_codec=True,
        archive_has_seed_byteframe_codec=False,
    )
    repeat_default = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=True,
        archive_has_reference_microframe_codec=True,
        archive_has_reference_packed_codec=True,
        archive_has_reference_byteframe_codec=True,
    )
    repeat_fallback = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=True,
        archive_has_reference_microframe_codec=True,
        archive_has_reference_packed_codec=True,
        archive_has_reference_byteframe_codec=False,
    )

    return {
        'focus': 'Shrink first-write and repeat-write rematch decision artifacts below numeric packed arrays by serializing the same packed payloads as raw byteframes in base64url strings, removing JSON list punctuation and decimal integer wrapper text without changing the semantic codec.',
        'method_note': 'Loaded the executable decision-packet module, converted representative packets into packed seeds/references and then into base64url byteframes, verified exact expansion and reference resolution, and measured minified byte savings for first writes and repeats while keeping the underlying packed semantic payload unchanged.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'default_first_write_storage_form_with_byteframe_codec': seed_default['recommended_storage_form'],
            'fallback_first_write_storage_form_without_byteframe_codec': seed_fallback['recommended_storage_form'],
            'default_repeat_storage_form_with_byteframe_codec': repeat_default['recommended_storage_form'],
            'fallback_repeat_storage_form_without_byteframe_codec': repeat_fallback['recommended_storage_form'],
            'best_packed_seed_to_byte_seed_bytes_saved': best_seed['packed_seed_to_byte_seed_bytes_saved'],
            'best_packed_seed_to_byte_seed_savings_example': best_seed['name'],
            'best_packed_reference_to_byte_reference_bytes_saved': best_reference['packed_reference_to_byte_reference_bytes_saved'],
            'best_packed_reference_to_byte_reference_savings_example': best_reference['name'],
            'main_rule': 'when the archive preserves the byteframe codec, first writes should store byte seeds and repeats should store byte references, leaving numeric packed arrays as the clearer fallback tier',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_packed_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Byteframe Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- default first-write storage form with the byteframe codec: `{findings['default_first_write_storage_form_with_byteframe_codec']}`.",
        f"- fallback first-write storage form without the byteframe codec: `{findings['fallback_first_write_storage_form_without_byteframe_codec']}`.",
        f"- default repeat storage form with the byteframe codec: `{findings['default_repeat_storage_form_with_byteframe_codec']}`.",
        f"- fallback repeat storage form without the byteframe codec: `{findings['fallback_repeat_storage_form_without_byteframe_codec']}`.",
        f"- best measured packed-seed to byte-seed saving: `{findings['best_packed_seed_to_byte_seed_bytes_saved']}` bytes on `{findings['best_packed_seed_to_byte_seed_savings_example']}`.",
        f"- best measured packed-reference to byte-reference saving: `{findings['best_packed_reference_to_byte_reference_bytes_saved']}` bytes on `{findings['best_packed_reference_to_byte_reference_savings_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative byteframe savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> packed seed `{row['packed_seed_bytes']}` bytes, byte seed `{row['byte_seed_bytes']}` bytes, packed reference `{row['packed_reference_bytes']}` bytes, byte reference `{row['byte_reference_bytes']}` bytes; switching both writes to byteframes saves `{row['packed_seed_to_byte_seed_bytes_saved']}` bytes on the first write and `{row['packed_reference_to_byte_reference_bytes_saved']}` bytes on the repeat, dropping the two-write total from `{row['packed_seed_then_packed_reference_bytes']}` to `{row['byte_seed_then_byte_reference_bytes']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- after packed nanoframes, the remaining overhead in many archive-local writes was no longer semantic content; it was JSON structure, especially list brackets, commas, and decimal integer text around already-compressed payload bytes.',
        '- byteframes keep the same packed semantic payloads but serialize them as raw bytes behind one base64url string, so the archive can remove that wrapper overhead without giving up exact rehydration back to packed arrays, microframes, archive-local packets, or standalone packets.',
        '- numeric packed arrays still matter as the clearer fallback tier when operators want the most inspectable local representation during debugging or manual inspection.',
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
