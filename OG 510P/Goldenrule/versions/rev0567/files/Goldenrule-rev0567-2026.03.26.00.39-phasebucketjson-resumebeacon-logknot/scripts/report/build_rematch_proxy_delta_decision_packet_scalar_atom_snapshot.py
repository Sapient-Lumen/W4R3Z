#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_scalar_atom_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_scalar_atom_snapshot_20260307.md'


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
            'why': 'the coordinate case shows that once the archive already knows common decimal atoms, even a direct `(B,H)` witness can stop paying quoted scalar strings for familiar values like `0.0001` and `1`.',
        },
        {
            'name': 'hazard_only_axis',
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
            'why': 'the one-hot hazard profile isolates the `"1" -> 0` atom collapse on top of the earlier bitmask vector shrink.',
        },
        {
            'name': 'mixed_tradeoff_profile',
            'standalone_packet': packet.packet_from_weights(
                {
                    'w_width': '2',
                    'w_buffer': '0.5',
                    'w_knife': '0',
                    'w_delta': '0',
                    'w_material': '1',
                    'w_undecided': '0',
                    'w_ties': '0',
                    'w_hazard': '0.2',
                }
            ),
            'archive_local_packet': packet.packet_from_weights(
                {
                    'w_width': '2',
                    'w_buffer': '0.5',
                    'w_knife': '0',
                    'w_delta': '0',
                    'w_material': '1',
                    'w_undecided': '0',
                    'w_ties': '0',
                    'w_hazard': '0.2',
                },
                archive_local=True,
            ),
            'why': 'mixed sparse declarations matter because future implementors will often reuse a small handful of human-entered decimals such as `2`, `0.5`, `1`, and `0.2`.',
        },
        {
            'name': 'dense_all_ones',
            'standalone_packet': packet.packet_from_weights({key: '1' for key in packet.WEIGHT_KEYS}),
            'archive_local_packet': packet.packet_from_weights(
                {key: '1' for key in packet.WEIGHT_KEYS},
                archive_local=True,
            ),
            'why': 'even dense declarations benefit because the repeated all-ones payload turns into one bitmask plus a run of tiny atom integers.',
        },
    ]
    for row in rows:
        standalone = row['standalone_packet']
        if standalone['mode'] == 'oracle_weights':
            legacy_packed = [
                packet.PACKED_MODE_TAGS['oracle_weights'],
                *packet.pack_weight_vector(standalone['evidence']['weights'], atomize_scalars=False),
            ]
            packed = [
                packet.PACKED_MODE_TAGS['oracle_weights'],
                *packet.pack_weight_vector(standalone['evidence']['weights']),
            ]
        else:
            legacy_packed = packet.packet_packed_seed(standalone, atomize_scalars=False)
            packed = packet.packet_packed_seed(standalone)
        row.update(
            {
                'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
                'legacy_packed_seed_packet': legacy_packed,
                'packed_seed_packet': packed,
                'legacy_packed_seed_bytes': packet.packet_minified_bytes(legacy_packed),
                'packed_seed_bytes': packet.packet_minified_bytes(packed),
                'legacy_to_packed_bytes_saved': packet.packet_minified_bytes(legacy_packed)
                - packet.packet_minified_bytes(packed),
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)
    for row in rows:
        if packet.expand_packed_seed_packet(row['legacy_packed_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"legacy packed-seed expansion mismatch for {row['name']}")
        if packet.expand_packed_seed_packet(row['packed_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"packed-seed expansion mismatch for {row['name']}")
        if packet.expand_packed_seed_packet(row['packed_seed_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"archive-local packed-seed expansion mismatch for {row['name']}")
        if row['legacy_to_packed_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive atom savings for {row['name']}")

    best_row = max(rows, key=lambda row: row['legacy_to_packed_bytes_saved'])
    return {
        'focus': 'Shrink packed first-write bodies further by replacing repeated canonical decimal strings with a tiny shared scalar atom codebook inside the archive-local packed codec.',
        'method_note': 'Loaded the executable decision-packet module, built representative coordinate and weight packets, compared the previous packed-seed form against the new scalar-atom packed-seed form, and verified exact standalone and archive-local rehydration.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'best_legacy_to_packed_savings_example': best_row['name'],
            'best_legacy_to_packed_bytes_saved': best_row['legacy_to_packed_bytes_saved'],
            'scalar_atom_codebook': packet.PACKED_SCALAR_ATOM_CODES,
            'main_rule': 'when a packed seed would otherwise repeat one of the archive\'s common canonical decimal strings, it should store the shared scalar atom code instead of the quoted decimal text',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_packed_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Scalar-Atom Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- best previous-packed to scalar-atom packed saving: `{findings['best_legacy_to_packed_bytes_saved']}` bytes on `{findings['best_legacy_to_packed_savings_example']}`.",
        f"- scalar atom codebook: `{findings['scalar_atom_codebook']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative scalar-atom savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> previous packed seed `{row['legacy_packed_seed_bytes']}` bytes, scalar-atom packed seed `{row['packed_seed_bytes']}` bytes; the shared decimal atom codebook saves `{row['legacy_to_packed_bytes_saved']}` bytes while preserving exact expansion. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- after the packed-nanoframe and weight-vector passes, many of the remaining bytes were no longer structural; they were just repeated quoted decimal lexemes such as `"1"`, `"0.5"`, `"2"`, `"0.2"`, and `"0.0001"`.',
        '- those lexemes recur often enough in the family10 archive that a tiny shared scalar codebook is cheaper than spelling them out inside every new packed seed.',
        '- the codec remains exact because expansion maps each atom code back to the same canonical decimal string before rebuilding the standalone or archive-local packet.',
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
