#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.md'


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
            'why': 'the archive should not keep seven explicit zeros and eight field names when the declared profile only turns on the hazard axis.',
        },
        {
            'name': 'mixed_tradeoff_profile',
            'weights': {
                'w_width': '2',
                'w_buffer': '0.5',
                'w_knife': '0',
                'w_delta': '0',
                'w_material': '1',
                'w_undecided': '0',
                'w_ties': '0',
                'w_hazard': '0.2',
            },
            'why': 'a mixed declaration matters because future inheritors will often keep only a few nonzero priorities rather than one-hot axes or fully dense vectors.',
        },
        {
            'name': 'dense_all_ones',
            'weights': {
                'w_width': '1',
                'w_buffer': '1',
                'w_knife': '1',
                'w_delta': '1',
                'w_material': '1',
                'w_undecided': '1',
                'w_ties': '1',
                'w_hazard': '1',
            },
            'why': 'even dense declarations still benefit because the fixed local order removes repeated JSON key names entirely.',
        },
    ]
    for row in rows:
        standalone = packet.packet_from_weights(row['weights'])
        archive_local = packet.packet_from_weights(row['weights'], archive_local=True)
        legacy_packed = [packet.PACKED_MODE_TAGS['oracle_weights'], standalone['evidence']['weights']]
        packed = [packet.PACKED_MODE_TAGS['oracle_weights'], *packet.pack_weight_vector(row['weights'])]
        row.update(
            {
                'standalone_packet': standalone,
                'archive_local_packet': archive_local,
                'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
                'legacy_packed_seed_packet': legacy_packed,
                'packed_seed_packet': packed,
                'micro_seed_packet': packet.packet_micro_seed(standalone),
                'legacy_packed_seed_bytes': packet.packet_minified_bytes(legacy_packed),
                'packed_seed_bytes': packet.packet_minified_bytes(packed),
                'micro_seed_bytes': packet.packet_minified_bytes(packet.packet_micro_seed(standalone)),
                'legacy_to_packed_bytes_saved': packet.packet_minified_bytes(legacy_packed)
                - packet.packet_minified_bytes(packed),
                'micro_to_packed_bytes_saved': packet.packet_minified_bytes(packet.packet_micro_seed(standalone))
                - packet.packet_minified_bytes(packed),
            }
        )
    return rows


def _build_summary() -> dict[str, object]:
    packet = _load_packet_module()
    rows = _sample_rows(packet)
    for row in rows:
        if packet.expand_packed_weight_vector(row['packed_seed_packet'][1:]) != row['standalone_packet']['evidence']['weights']:
            raise SystemExit(f"packed weight vector round-trip mismatch for {row['name']}")
        if packet.expand_packed_seed_packet(row['packed_seed_packet']) != row['standalone_packet']:
            raise SystemExit(f"packed seed expansion mismatch for {row['name']}")
        if packet.expand_packed_seed_packet(row['packed_seed_packet'], archive_local=True) != row['archive_local_packet']:
            raise SystemExit(f"archive-local packed seed expansion mismatch for {row['name']}")
        if row['legacy_to_packed_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive legacy-to-packed savings for {row['name']}")
        if row['micro_to_packed_bytes_saved'] <= 0:
            raise SystemExit(f"expected positive micro-to-packed savings for {row['name']}")

    best_legacy = max(rows, key=lambda row: row['legacy_to_packed_bytes_saved'])
    best_micro = max(rows, key=lambda row: row['micro_to_packed_bytes_saved'])
    return {
        'focus': 'Compress oracle-weight decision packets by replacing the keyful packed weight mapping with a fixed-order nonzero vector behind one bitmask.',
        'method_note': 'Loaded the executable decision-packet module, built representative oracle-weight packets, measured the legacy packed dict payload against the new bitmask+ordered-values payload, and verified exact expansion back to standalone and archive-local packets.',
        'headline_findings': {
            'packet_script': str(PACKET_PATH.relative_to(ROOT)),
            'best_legacy_to_packed_savings_example': best_legacy['name'],
            'best_legacy_to_packed_bytes_saved': best_legacy['legacy_to_packed_bytes_saved'],
            'best_micro_to_packed_savings_example': best_micro['name'],
            'best_micro_to_packed_bytes_saved': best_micro['micro_to_packed_bytes_saved'],
            'main_rule': 'when the archive stores oracle-weight packets as packed seeds, it should encode the fixed family10 weight order once in the codec and store only the nonzero values plus a bitmask',
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
        '# Rematch-Proxy Decision Packet Weight-Vector Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{findings['packet_script']}`.",
        f"- best legacy-packed to new-packed saving: `{findings['best_legacy_to_packed_bytes_saved']}` bytes on `{findings['best_legacy_to_packed_savings_example']}`.",
        f"- best micro-seed to new-packed saving: `{findings['best_micro_to_packed_bytes_saved']}` bytes on `{findings['best_micro_to_packed_savings_example']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Representative weight-vector savings',
    ]
    for row in summary['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` -> legacy packed seed `{row['legacy_packed_seed_bytes']}` bytes, new packed seed `{row['packed_seed_bytes']}` bytes, micro seed `{row['micro_seed_bytes']}` bytes; moving from the old keyful packed form to the new vector saves `{row['legacy_to_packed_bytes_saved']}` bytes and the micro-to-packed total saving is `{row['micro_to_packed_bytes_saved']}` bytes. {row['why']}"
        )
    lines.extend([
        '',
        '## Why this matters',
        '- the earlier packed codec already removed string mode tags and collapsed finite route/signature payloads, but `oracle_weights` was still carrying a full JSON object with eight repeated field names.',
        '- the family10 weight order is fixed, so the archive can store a bitmask plus ordered nonzero values and recover the full mapping exactly at read time.',
        '- this keeps `packed_seed` as the same storage tier while making weight-mode first writes materially smaller in practice.',
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
