#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_atom_group_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_atom_group_snapshot_20260307.md'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sample_rows(packet):
    rows = [
        {
            'name': 'hazard_only_axis',
            'weights': {
                'w_width': '0',
                'w_buffer': '0',
                'w_knife': '0',
                'w_delta': '0',
                'w_material': '0',
                'w_undecided': '0',
                'w_ties': '0',
                'w_hazard': '1',
            },
            'why': 'one-hot declarations should stay on the existing sparse vector fallback because there is only one repeated atom and nothing to group.',
        },
        {
            'name': 'dense_all_ones',
            'weights': {key: '1' for key in packet.WEIGHT_KEYS},
            'why': 'uniform dense declarations should collapse from one atom code per active axis to one shared mask plus one shared atom.',
        },
        {
            'name': 'two_atom_blocks',
            'weights': {
                'w_width': '1',
                'w_buffer': '1',
                'w_knife': '1',
                'w_delta': '1',
                'w_material': '0.5',
                'w_undecided': '0.5',
                'w_ties': '0.5',
                'w_hazard': '0.5',
            },
            'why': 'human-authored starting profiles often repeat a small number of scalar atoms across several axes; one mask per atom is cheaper than re-listing the same atom on every axis.',
        },
    ]
    for row in rows:
        standalone = packet.packet_from_weights(row['weights'])
        archive_local = packet.packet_from_weights(row['weights'], archive_local=True)
        scalar_atom_vector = [
            packet.PACKED_MODE_TAGS['oracle_weights'],
            *packet.pack_weight_vector(row['weights']),
        ]
        grouped_best = packet.packet_packed_seed(standalone)
        row.update(
            {
                'standalone_packet': standalone,
                'archive_local_packet': archive_local,
                'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
                'scalar_atom_vector_packet': scalar_atom_vector,
                'grouped_best_packet': grouped_best,
                'scalar_atom_vector_bytes': packet.packet_minified_bytes(scalar_atom_vector),
                'grouped_best_bytes': packet.packet_minified_bytes(grouped_best),
                'scalar_vector_to_grouped_bytes_saved': packet.packet_minified_bytes(scalar_atom_vector)
                - packet.packet_minified_bytes(grouped_best),
                'grouped_best_uses_atom_masks': grouped_best[1] == packet.PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG,
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)
    for row in rows:
        if packet.expand_packed_seed_packet(row['scalar_atom_vector_packet']) != row['standalone_packet']:
            raise SystemExit(f"scalar-atom vector expansion mismatch for {row['name']}")
        if packet.expand_packed_seed_packet(row['grouped_best_packet']) != row['standalone_packet']:
            raise SystemExit(f"grouped packed-seed expansion mismatch for {row['name']}")
        if packet.expand_packed_seed_packet(row['grouped_best_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"archive-local grouped packed-seed expansion mismatch for {row['name']}")
        if row['grouped_best_bytes'] > row['scalar_atom_vector_bytes']:
            raise SystemExit(f"expected grouped-best form to never exceed scalar-atom vector bytes for {row['name']}")

    best_row = max(rows, key=lambda row: row['scalar_vector_to_grouped_bytes_saved'])
    grouped_rows = [row for row in rows if row['grouped_best_uses_atom_masks']]
    return {
        'focus': 'Shrink repeated-value oracle-weight packed seeds by grouping equal scalar atoms behind axis masks instead of re-emitting the same atom once per active axis.',
        'method_note': 'Loaded the executable decision-packet module, compared the scalar-atom sparse vector against the new grouped-atom best form on representative oracle-weight packets, and verified exact standalone and archive-local rehydration.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'best_scalar_vector_to_grouped_savings_example': best_row['name'],
            'best_scalar_vector_to_grouped_bytes_saved': best_row['scalar_vector_to_grouped_bytes_saved'],
            'grouped_weight_format_tag': packet.PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG,
            'grouped_rows': [row['name'] for row in grouped_rows],
            'main_rule': 'when an oracle-weight packed seed repeats the same scalar atom across multiple active axes, the archive should store one axis mask per repeated atom and fall back to the sparse ordered-value vector otherwise',
        },
        'sample_packet_rows': rows,
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            'artifacts/reports/rematch_proxy_delta_decision_packet_scalar_atom_snapshot_20260307.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.json',
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Decision Packet Weight-Atom Group Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- best scalar-atom-vector to grouped-best saving: `{findings['best_scalar_vector_to_grouped_bytes_saved']}` bytes on `{findings['best_scalar_vector_to_grouped_savings_example']}`.",
        f"- grouped atom-mask format tag: `{findings['grouped_weight_format_tag']}`.",
        f"- grouped form selected on: `{findings['grouped_rows']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative grouped-weight savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> scalar-atom sparse vector `{row['scalar_atom_vector_bytes']}` bytes, grouped-best packed seed `{row['grouped_best_bytes']}` bytes; grouping repeated atoms saves `{row['scalar_vector_to_grouped_bytes_saved']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- the scalar-atom pass removed quoted decimal text, but dense or repeated-value weight declarations were still paying one atom code per active axis.',
        '- when several active axes share the same scalar atom, one bitmask per atom is cheaper than re-listing the atom in fixed-order vector position for each axis.',
        '- the codec remains exact because each grouped atom mask expands back into the same full eight-axis weight map before rebuilding the archive-local or standalone packet.',
        '- the archive should therefore choose the smaller of two oracle-weight packed forms: the sparse ordered-value vector or the grouped atom-mask form.',
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
