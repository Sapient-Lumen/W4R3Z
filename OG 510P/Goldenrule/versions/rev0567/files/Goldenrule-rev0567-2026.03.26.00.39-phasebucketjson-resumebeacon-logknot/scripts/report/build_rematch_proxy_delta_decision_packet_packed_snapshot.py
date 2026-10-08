#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_packed_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_packed_snapshot_20260307.md'


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
            'why': 'the declaration-first coordinate case now also benefits from the shared scalar atom codebook, so the archive no longer repeats common decimal strings like `0.0001` and `1` inside the packed tier.',
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
            'why': 'the declaration-first weight packet now exercises both the keyless weight vector and the shared scalar atom codebook, so the packed tier avoids repeated axis names, explicit zeroes, and common quoted decimal strings.',
        },
        {
            'name': 'robustness_adaptive_cap_sensitive',
            'standalone_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
            'archive_local_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M', archive_local=True),
            'why': 'adaptive-route packets benefit the most because the route string collapses to a tiny finite route code once the archive keeps the local packed codec.',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'the exact tie-cap path matters because it is the expensive diagnostic branch we still want to preserve with the smallest durable archive body.',
        },
    ]
    known_fingerprints = [packet.packet_semantic_fingerprint(row['standalone_packet']) for row in rows]
    for row in rows:
        standalone = row['standalone_packet']
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        micro_seed = packet.packet_micro_seed(standalone)
        packed_seed = packet.packet_packed_seed(standalone)
        micro_reference = packet.packet_micro_reference(standalone, known_fingerprints)
        packed_reference = packet.packet_packed_reference(standalone, known_fingerprints)
        atto_first = packet.packet_archive_atto_write_plan(standalone, [])
        atto_repeat = packet.packet_archive_atto_write_plan(standalone, known_fingerprints)
        row.update(
            {
                'semantic_fingerprint': fingerprint,
                'micro_seed_packet': micro_seed,
                'packed_seed_packet': packed_seed,
                'micro_reference_packet': micro_reference,
                'packed_reference_packet': packed_reference,
                'micro_seed_bytes': packet.packet_minified_bytes(micro_seed),
                'packed_seed_bytes': packet.packet_minified_bytes(packed_seed),
                'micro_reference_bytes': packet.packet_minified_bytes(micro_reference),
                'packed_reference_bytes': packet.packet_minified_bytes(packed_reference),
                'micro_seed_to_packed_seed_bytes_saved': packet.packet_minified_bytes(micro_seed)
                - packet.packet_minified_bytes(packed_seed),
                'micro_reference_to_packed_reference_bytes_saved': packet.packet_minified_bytes(micro_reference)
                - packet.packet_minified_bytes(packed_reference),
                'micro_seed_then_micro_reference_bytes': packet.packet_minified_bytes(micro_seed)
                + packet.packet_minified_bytes(micro_reference),
                'packed_seed_then_packed_reference_bytes': packet.packet_minified_bytes(packed_seed)
                + packet.packet_minified_bytes(packed_reference),
                'atto_first_write_plan': atto_first,
                'atto_repeat_write_plan': atto_repeat,
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if packet.expand_packed_seed_packet(row['packed_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"packed-seed standalone expansion mismatch for {row['name']}")
        if packet.expand_packed_seed_packet(row['packed_seed_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"packed-seed archive-local expansion mismatch for {row['name']}")
        if packet.expand_packet(row['packed_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"expand_packet packed-seed mismatch for {row['name']}")
        if packet.expand_packed_reference_packet(row['packed_reference_packet']) != packet.expand_micro_reference_packet(row['micro_reference_packet']):
            raise SystemExit(f"packed-reference expansion mismatch for {row['name']}")
        if packet.resolve_archive_any_reference(row['packed_reference_packet'], [row['semantic_fingerprint']]) != row['semantic_fingerprint']:
            raise SystemExit(f"packed-reference resolution mismatch for {row['name']}")
        if row['micro_seed_to_packed_seed_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive micro-seed to packed-seed savings for {row['name']}")
        if row['micro_reference_to_packed_reference_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive micro-reference to packed-reference savings for {row['name']}")
        if row['atto_first_write_plan']['recommended_write_kind'] != 'packed_seed_body':
            raise SystemExit(f"expected packed_seed_body first write for {row['name']}")
        if row['atto_repeat_write_plan']['recommended_write_kind'] != 'packed_reference':
            raise SystemExit(f"expected packed_reference repeat write for {row['name']}")

    best_seed = max(rows, key=lambda row: row['micro_seed_to_packed_seed_bytes_saved'])
    best_reference = max(rows, key=lambda row: row['micro_reference_to_packed_reference_bytes_saved'])
    seed_default = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=True,
        archive_has_seed_packed_codec=True,
    )
    seed_fallback = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=True,
        archive_has_seed_packed_codec=False,
    )
    repeat_default = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=True,
        archive_has_reference_microframe_codec=True,
        archive_has_reference_packed_codec=True,
    )
    repeat_fallback = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=True,
        archive_has_reference_microframe_codec=True,
        archive_has_reference_packed_codec=False,
    )

    return {
        'focus': 'Shrink both first-write and repeat-write rematch decision artifacts below tagged microframes by numerically tagging modes, collapsing finite probe payloads to tiny codes, encoding weight declarations as ordered nonzero vectors, atomizing repeated decimal scalars, and base64url-packing even-length local prefixes.',
        'method_note': 'Loaded the executable decision-packet module, converted representative packets into tagged microframes and then into packed seeds/references, verified exact expansion and resolution, and measured minified byte savings for both first writes and repeats, including the keyless packed weight vector and the new shared scalar atom codebook.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'default_first_write_storage_form_with_packed_codec': seed_default['recommended_storage_form'],
            'fallback_first_write_storage_form_without_packed_codec': seed_fallback['recommended_storage_form'],
            'default_repeat_storage_form_with_packed_codec': repeat_default['recommended_storage_form'],
            'fallback_repeat_storage_form_without_packed_codec': repeat_fallback['recommended_storage_form'],
            'best_micro_seed_to_packed_seed_savings_example': best_seed['name'],
            'best_micro_seed_to_packed_seed_bytes_saved': best_seed['micro_seed_to_packed_seed_bytes_saved'],
            'best_micro_reference_to_packed_reference_savings_example': best_reference['name'],
            'best_micro_reference_to_packed_reference_bytes_saved': best_reference['micro_reference_to_packed_reference_bytes_saved'],
            'main_rule': 'when the archive preserves the packed codec, first writes should store packed seeds and repeats should store packed references, leaving tagged microframes as the clearer fallback tier',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_microframe_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Packed Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- default first-write storage form with the packed codec: `{findings['default_first_write_storage_form_with_packed_codec']}`.",
        f"- fallback first-write storage form without the packed codec: `{findings['fallback_first_write_storage_form_without_packed_codec']}`.",
        f"- default repeat storage form with the packed codec: `{findings['default_repeat_storage_form_with_packed_codec']}`.",
        f"- fallback repeat storage form without the packed codec: `{findings['fallback_repeat_storage_form_without_packed_codec']}`.",
        f"- best measured micro-seed to packed-seed saving: `{findings['best_micro_seed_to_packed_seed_bytes_saved']}` bytes on `{findings['best_micro_seed_to_packed_seed_savings_example']}`.",
        f"- best measured micro-reference to packed-reference saving: `{findings['best_micro_reference_to_packed_reference_bytes_saved']}` bytes on `{findings['best_micro_reference_to_packed_reference_savings_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative packed savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> micro seed `{row['micro_seed_bytes']}` bytes, packed seed `{row['packed_seed_bytes']}` bytes, micro reference `{row['micro_reference_bytes']}` bytes, packed reference `{row['packed_reference_bytes']}` bytes; switching both writes to packed forms saves `{row['micro_seed_to_packed_seed_bytes_saved']}` bytes on the first write and `{row['micro_reference_to_packed_reference_bytes_saved']}` bytes on the repeat, dropping the two-write total from `{row['micro_seed_then_micro_reference_bytes']}` to `{row['packed_seed_then_packed_reference_bytes']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- tagged microframes already removed object-key overhead, but they still carried string mode tags, repeated common decimal strings, string route/signature payloads, and a hex repeat prefix, while the weight mode also repeated eight JSON field names and explicit zero values.',
        '- once the archive commits to a slightly richer local codec, finite probe payloads can collapse to tiny integers, repeated decimal scalars can collapse to shared atom tags, weight declarations can collapse to a fixed-order nonzero vector behind one bitmask, and the repeat prefix can collapse from 12 hex characters to 8 base64url characters while staying exactly resolvable.',
        '- tagged microframes still matter as the clearer fallback tier when operators want a more transparent local representation during debugging or manual inspection.',
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
