#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_microframe_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_microframe_snapshot_20260307.md'


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
            'why': 'the declaration-first coordinate case isolates the object-key overhead most cleanly because the underlying semantic payload is only two short scalars.',
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
            'why': 'even the heavier declaration-first weight packet still benefits from stripping object keys off the outer wrapper once the archive commits to positional decoding.',
        },
        {
            'name': 'robustness_adaptive_cap_sensitive',
            'standalone_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
            'archive_local_packet': packet.packet_from_robustness_adaptive(10, 'S', 'M', archive_local=True),
            'why': 'adaptive route packets are a good stress test for future note-taking because many later sessions may need to refer back to the same short route string.',
        },
        {
            'name': 'exact_checked_cap_path_tie20',
            'standalone_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            'archive_local_packet': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
            'why': 'the tie-cap escalation case matters because it is the expensive diagnosis we most want to preserve with the smallest possible in-archive wrappers.',
        },
    ]
    known_fingerprints = [packet.packet_semantic_fingerprint(row['standalone_packet']) for row in rows]
    for row in rows:
        standalone = row['standalone_packet']
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        coded_seed = packet.packet_coded_seed(standalone)
        micro_seed = packet.packet_micro_seed(standalone)
        coded_reference = packet.packet_coded_reference(standalone, known_fingerprints)
        micro_reference = packet.packet_micro_reference(standalone, known_fingerprints)
        archive_local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        femto_first = packet.packet_archive_femto_write_plan(standalone, [])
        femto_repeat = packet.packet_archive_femto_write_plan(standalone, known_fingerprints)
        row.update(
            {
                'semantic_fingerprint': fingerprint,
                'coded_seed_packet': coded_seed,
                'micro_seed_packet': micro_seed,
                'coded_reference_packet': coded_reference,
                'micro_reference_packet': micro_reference,
                'archive_local_reference_packet': archive_local_reference,
                'coded_seed_bytes': packet.packet_minified_bytes(coded_seed),
                'micro_seed_bytes': packet.packet_minified_bytes(micro_seed),
                'coded_reference_bytes': packet.packet_minified_bytes(coded_reference),
                'micro_reference_bytes': packet.packet_minified_bytes(micro_reference),
                'archive_local_reference_bytes': packet.packet_minified_bytes(archive_local_reference),
                'coded_seed_to_micro_seed_bytes_saved': packet.packet_minified_bytes(coded_seed)
                - packet.packet_minified_bytes(micro_seed),
                'coded_reference_to_micro_reference_bytes_saved': packet.packet_minified_bytes(coded_reference)
                - packet.packet_minified_bytes(micro_reference),
                'archive_local_reference_to_micro_reference_bytes_saved': packet.packet_minified_bytes(archive_local_reference)
                - packet.packet_minified_bytes(micro_reference),
                'coded_seed_then_coded_reference_bytes': packet.packet_minified_bytes(coded_seed)
                + packet.packet_minified_bytes(coded_reference),
                'micro_seed_then_micro_reference_bytes': packet.packet_minified_bytes(micro_seed)
                + packet.packet_minified_bytes(micro_reference),
                'femto_first_write_plan': femto_first,
                'femto_repeat_write_plan': femto_repeat,
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)

    for row in rows:
        if packet.expand_micro_seed_packet(row['micro_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"micro-seed standalone expansion mismatch for {row['name']}")
        if packet.expand_micro_seed_packet(row['micro_seed_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"micro-seed archive-local expansion mismatch for {row['name']}")
        if packet.expand_packet(row['micro_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"expand_packet micro-seed mismatch for {row['name']}")
        if packet.expand_micro_reference_packet(row['micro_reference_packet']) != row['archive_local_reference_packet']:
            raise SystemExit(f"micro-reference expansion mismatch for {row['name']}")
        if packet.resolve_archive_any_reference(row['micro_reference_packet'], [row['semantic_fingerprint']]) != row['semantic_fingerprint']:
            raise SystemExit(f"micro-reference resolution mismatch for {row['name']}")
        if row['coded_seed_to_micro_seed_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive coded-seed to micro-seed savings for {row['name']}")
        if row['coded_reference_to_micro_reference_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive coded-reference to micro-reference savings for {row['name']}")
        if row['femto_first_write_plan']['recommended_write_kind'] != 'micro_seed_body':
            raise SystemExit(f"expected micro_seed_body first write for {row['name']}")
        if row['femto_repeat_write_plan']['recommended_write_kind'] != 'micro_reference':
            raise SystemExit(f"expected micro_reference repeat write for {row['name']}")

    best_seed = max(rows, key=lambda row: row['coded_seed_to_micro_seed_bytes_saved'])
    best_reference = max(rows, key=lambda row: row['coded_reference_to_micro_reference_bytes_saved'])
    seed_default = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=True,
    )
    seed_fallback = packet.packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=False,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=False,
    )
    repeat_default = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=True,
        archive_has_reference_microframe_codec=True,
    )
    repeat_fallback = packet.packet_repeat_storage_decision(
        need_standalone_portability=False,
        archive_has_reference_codebook=True,
        archive_has_reference_microframe_codec=False,
    )

    return {
        'focus': 'Shrink both first-write and repeat-write rematch decision artifacts below object-wrapped coded packets by using tiny tagged microframes (JSON arrays) inside the archive.',
        'method_note': 'Loaded the executable decision-packet module, converted representative packets into coded seeds/references and then into tagged microframe seeds/references, verified exact expansion and resolution, and measured minified byte savings for both first writes and repeats.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'microframe_reference_tag': packet.MICROFRAME_REFERENCE_TAG,
            'default_first_write_storage_form_with_microframe_codec': seed_default['recommended_storage_form'],
            'fallback_first_write_storage_form_without_microframe_codec': seed_fallback['recommended_storage_form'],
            'default_repeat_storage_form_with_microframe_codec': repeat_default['recommended_storage_form'],
            'fallback_repeat_storage_form_without_microframe_codec': repeat_fallback['recommended_storage_form'],
            'best_coded_seed_to_micro_seed_savings_example': best_seed['name'],
            'best_coded_seed_to_micro_seed_bytes_saved': best_seed['coded_seed_to_micro_seed_bytes_saved'],
            'best_coded_reference_to_micro_reference_savings_example': best_reference['name'],
            'best_coded_reference_to_micro_reference_bytes_saved': best_reference['coded_reference_to_micro_reference_bytes_saved'],
            'main_rule': 'when the archive preserves the local microframe codec, first writes should store micro seeds and repeats should store micro references, leaving object-wrapped coded packets as the clearer fallback tier',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_coded_reference_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Microframe Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- microframe reference tag: `{findings['microframe_reference_tag']}`.",
        f"- default first-write storage form with the microframe codec: `{findings['default_first_write_storage_form_with_microframe_codec']}`.",
        f"- fallback first-write storage form without the microframe codec: `{findings['fallback_first_write_storage_form_without_microframe_codec']}`.",
        f"- default repeat storage form with the microframe codec: `{findings['default_repeat_storage_form_with_microframe_codec']}`.",
        f"- fallback repeat storage form without the microframe codec: `{findings['fallback_repeat_storage_form_without_microframe_codec']}`.",
        f"- best measured coded-seed to micro-seed saving: `{findings['best_coded_seed_to_micro_seed_bytes_saved']}` bytes on `{findings['best_coded_seed_to_micro_seed_savings_example']}`.",
        f"- best measured coded-reference to micro-reference saving: `{findings['best_coded_reference_to_micro_reference_bytes_saved']}` bytes on `{findings['best_coded_reference_to_micro_reference_savings_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative microframe savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> coded seed `{row['coded_seed_bytes']}` bytes, micro seed `{row['micro_seed_bytes']}` bytes, coded reference `{row['coded_reference_bytes']}` bytes, micro reference `{row['micro_reference_bytes']}` bytes; switching both writes to microframes saves `{row['coded_seed_to_micro_seed_bytes_saved']}` bytes on the first write and `{row['coded_reference_to_micro_reference_bytes_saved']}` bytes on the repeat, dropping the two-write total from `{row['coded_seed_then_coded_reference_bytes']}` to `{row['micro_seed_then_micro_reference_bytes']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- coded seeds and coded references already solved repeated semantics, but they still paid JSON object-key overhead on every write.',
        '- once the archive commits to a tiny positional decoder, the durable artifact can be a tagged array rather than an object wrapper without losing exact reconstructability.',
        '- object-wrapped coded packets still matter as the clearer fallback tier when operators want more explicit field labels during debugging or manual inspection.',
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
