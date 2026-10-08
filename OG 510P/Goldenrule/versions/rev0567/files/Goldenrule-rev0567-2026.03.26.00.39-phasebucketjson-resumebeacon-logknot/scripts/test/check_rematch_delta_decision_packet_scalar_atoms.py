#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_scalar_atom_snapshot_20260307.json'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_report() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    packet = _load_packet_module()
    report = _load_report()
    findings = report['headline_findings']
    assert findings['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert findings['scalar_atom_codebook'] == packet.PACKED_SCALAR_ATOM_CODES

    expected = {
        'oracle_coordinates_sms': packet.packet_from_coordinates('0.0001', '1'),
        'hazard_only_axis': packet.packet_from_weights(
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
        'mixed_tradeoff_profile': packet.packet_from_weights(
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
        'dense_all_ones': packet.packet_from_weights({key: '1' for key in packet.WEIGHT_KEYS}),
    }

    rows = {row['name']: row for row in report['sample_packet_rows']}
    for name, standalone in expected.items():
        row = rows[name]
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

        assert row['standalone_packet'] == standalone
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(standalone)
        assert row['legacy_packed_seed_packet'] == legacy_packed
        assert row['packed_seed_packet'] == packed
        assert packet.expand_packed_seed_packet(legacy_packed) == standalone
        assert packet.expand_packed_seed_packet(packed) == standalone
        assert packet.expand_packed_seed_packet(packed, archive_local=True) == row['archive_local_packet']
        assert row['legacy_packed_seed_bytes'] == packet.packet_minified_bytes(legacy_packed)
        assert row['packed_seed_bytes'] == packet.packet_minified_bytes(packed)
        assert row['legacy_to_packed_bytes_saved'] == row['legacy_packed_seed_bytes'] - row['packed_seed_bytes']
        assert row['legacy_to_packed_bytes_saved'] > 0

    assert findings['best_legacy_to_packed_savings_example'] in rows
    assert findings['best_legacy_to_packed_bytes_saved'] == max(
        row['legacy_to_packed_bytes_saved'] for row in rows.values()
    )

    print('decision-packet-scalar-atoms: ok')


if __name__ == '__main__':
    main()
