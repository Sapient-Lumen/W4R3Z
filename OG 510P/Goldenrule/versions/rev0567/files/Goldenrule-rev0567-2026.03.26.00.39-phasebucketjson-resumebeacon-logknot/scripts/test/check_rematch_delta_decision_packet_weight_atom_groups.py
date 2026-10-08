#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_atom_group_snapshot_20260307.json'


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
    assert findings['grouped_weight_format_tag'] == packet.PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG

    expected_weights = {
        'hazard_only_axis': {
            'w_width': '0',
            'w_buffer': '0',
            'w_knife': '0',
            'w_delta': '0',
            'w_material': '0',
            'w_undecided': '0',
            'w_ties': '0',
            'w_hazard': '1',
        },
        'dense_all_ones': {key: '1' for key in packet.WEIGHT_KEYS},
        'two_atom_blocks': {
            'w_width': '1',
            'w_buffer': '1',
            'w_knife': '1',
            'w_delta': '1',
            'w_material': '0.5',
            'w_undecided': '0.5',
            'w_ties': '0.5',
            'w_hazard': '0.5',
        },
    }

    rows = {row['name']: row for row in report['sample_packet_rows']}
    grouped_rows = []
    for name, weights in expected_weights.items():
        row = rows[name]
        standalone = packet.packet_from_weights(weights)
        archive_local = packet.packet_from_weights(weights, archive_local=True)
        scalar_atom_vector = [
            packet.PACKED_MODE_TAGS['oracle_weights'],
            *packet.pack_weight_vector(weights),
        ]
        grouped_best = packet.packet_packed_seed(standalone)

        assert row['standalone_packet'] == standalone
        assert row['archive_local_packet'] == archive_local
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(standalone)
        assert row['scalar_atom_vector_packet'] == scalar_atom_vector
        assert row['grouped_best_packet'] == grouped_best
        assert packet.expand_packed_seed_packet(scalar_atom_vector) == standalone
        assert packet.expand_packed_seed_packet(grouped_best) == standalone
        assert packet.expand_packed_seed_packet(grouped_best, archive_local=True) == archive_local
        assert row['scalar_atom_vector_bytes'] == packet.packet_minified_bytes(scalar_atom_vector)
        assert row['grouped_best_bytes'] == packet.packet_minified_bytes(grouped_best)
        assert row['scalar_vector_to_grouped_bytes_saved'] == (
            row['scalar_atom_vector_bytes'] - row['grouped_best_bytes']
        )
        assert row['grouped_best_bytes'] <= row['scalar_atom_vector_bytes']
        if row['grouped_best_uses_atom_masks']:
            grouped_rows.append(name)
            assert grouped_best[1] == packet.PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG
        else:
            assert grouped_best == scalar_atom_vector

    assert findings['grouped_rows'] == grouped_rows
    assert findings['best_scalar_vector_to_grouped_savings_example'] in rows
    assert findings['best_scalar_vector_to_grouped_bytes_saved'] == max(
        row['scalar_vector_to_grouped_bytes_saved'] for row in rows.values()
    )
    assert findings['best_scalar_vector_to_grouped_bytes_saved'] > 0

    print('decision-packet-weight-atom-groups: ok')


if __name__ == '__main__':
    main()
