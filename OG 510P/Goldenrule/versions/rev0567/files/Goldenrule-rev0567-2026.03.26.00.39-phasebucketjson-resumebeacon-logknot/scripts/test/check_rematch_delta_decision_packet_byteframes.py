#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_byteframe_snapshot_20260307.json'


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
    assert findings['default_first_write_storage_form_with_byteframe_codec'] == 'byte_seed'
    assert findings['fallback_first_write_storage_form_without_byteframe_codec'] == 'packed_seed'
    assert findings['default_repeat_storage_form_with_byteframe_codec'] == 'byte_reference'
    assert findings['fallback_repeat_storage_form_without_byteframe_codec'] == 'packed_reference'

    sample_rows = {row['name']: row for row in report['sample_packet_rows']}
    expected = {
        'oracle_coordinates_sms': packet.packet_from_coordinates('0.0001', '1'),
        'oracle_weights_hazard_only': packet.packet_from_weights(
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
        'oracle_weights_dense_all_ones': packet.packet_from_weights({key: '1' for key in packet.WEIGHT_KEYS}),
        'exact_checked_cap_path_tie20': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
    }
    known_fingerprints = [packet.packet_semantic_fingerprint(standalone) for standalone in expected.values()]

    for name, standalone in expected.items():
        row = sample_rows[name]
        packed_seed = packet.packet_packed_seed(standalone)
        byte_seed = packet.packet_byte_seed(standalone)
        packed_reference = packet.packet_packed_reference(standalone, known_fingerprints)
        byte_reference = packet.packet_byte_reference(standalone, known_fingerprints)
        zepto_first = packet.packet_archive_zepto_write_plan(standalone, [])
        zepto_repeat = packet.packet_archive_zepto_write_plan(standalone, known_fingerprints)

        assert row['standalone_packet'] == standalone
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(standalone)
        assert row['packed_seed_packet'] == packed_seed
        assert row['byte_seed_packet'] == byte_seed
        assert row['packed_reference_packet'] == packed_reference
        assert row['byte_reference_packet'] == byte_reference
        assert packet.expand_byte_seed_packet(byte_seed) == standalone
        assert packet.expand_byte_seed_packet(byte_seed, archive_local=True) == row['archive_local_packet']
        assert packet.expand_packet(byte_seed) == standalone
        assert packet.expand_byte_reference_packet(byte_reference) == packet.expand_packed_reference_packet(packed_reference)
        assert packet.resolve_archive_any_reference(byte_reference, known_fingerprints) == row['semantic_fingerprint']
        assert row['packed_seed_bytes'] == packet.packet_minified_bytes(packed_seed)
        assert row['byte_seed_bytes'] == packet.packet_minified_bytes(byte_seed)
        assert row['packed_reference_bytes'] == packet.packet_minified_bytes(packed_reference)
        assert row['byte_reference_bytes'] == packet.packet_minified_bytes(byte_reference)
        assert row['packed_seed_to_byte_seed_bytes_saved'] == row['packed_seed_bytes'] - row['byte_seed_bytes']
        assert row['packed_reference_to_byte_reference_bytes_saved'] == row['packed_reference_bytes'] - row['byte_reference_bytes']
        assert row['zepto_first_write_plan'] == zepto_first
        assert row['zepto_repeat_write_plan'] == zepto_repeat
        assert zepto_first['recommended_write_kind'] == 'byte_seed_body'
        assert zepto_repeat['recommended_write_kind'] == 'byte_reference'
        assert row['packed_seed_to_byte_seed_bytes_saved'] > 0
        assert row['packed_reference_to_byte_reference_bytes_saved'] > 0

    assert findings['best_packed_seed_to_byte_seed_savings_example'] in sample_rows
    assert findings['best_packed_seed_to_byte_seed_bytes_saved'] == max(
        row['packed_seed_to_byte_seed_bytes_saved'] for row in sample_rows.values()
    )
    assert findings['best_packed_reference_to_byte_reference_savings_example'] in sample_rows
    assert findings['best_packed_reference_to_byte_reference_bytes_saved'] == max(
        row['packed_reference_to_byte_reference_bytes_saved'] for row in sample_rows.values()
    )

    extra_cases = {
        'robustness_fixed': packet.packet_from_robustness_fixed('S', 'M'),
        'robustness_adaptive': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
        'strict_adaptive': packet.packet_from_strict_adaptive('M', 'S'),
        'non_atom_coordinate': packet.packet_from_coordinates('0.3333', '1'),
    }
    extra_known = known_fingerprints + [packet.packet_semantic_fingerprint(case) for case in extra_cases.values()]
    for case in extra_cases.values():
        byte_seed = packet.packet_byte_seed(case)
        byte_reference = packet.packet_byte_reference(case, extra_known)
        assert packet.expand_byte_seed_packet(byte_seed) == case
        assert packet.resolve_archive_any_reference(byte_reference, extra_known) == packet.packet_semantic_fingerprint(case)
        assert packet.packet_minified_bytes(byte_seed) <= packet.packet_minified_bytes(packet.packet_packed_seed(case))
        assert packet.packet_minified_bytes(byte_reference) < packet.packet_minified_bytes(
            packet.packet_packed_reference(case, extra_known)
        )

    print('decision-packet-byteframes: ok')


if __name__ == '__main__':
    main()
