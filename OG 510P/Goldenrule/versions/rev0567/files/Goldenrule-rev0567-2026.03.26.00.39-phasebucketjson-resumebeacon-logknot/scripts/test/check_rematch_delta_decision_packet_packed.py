#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_packed_snapshot_20260307.json'


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
    assert findings['default_first_write_storage_form_with_packed_codec'] == 'packed_seed'
    assert findings['fallback_first_write_storage_form_without_packed_codec'] == 'micro_seed'
    assert findings['default_repeat_storage_form_with_packed_codec'] == 'packed_reference'
    assert findings['fallback_repeat_storage_form_without_packed_codec'] == 'micro_reference'

    sample_rows = {row['name']: row for row in report['sample_packet_rows']}
    expected = {
        'oracle_coordinates_sms': packet.packet_from_coordinates('0.0001', '1'),
        'oracle_weights_smm': packet.packet_from_weights(
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
        'robustness_adaptive_cap_sensitive': packet.packet_from_robustness_adaptive(10, 'S', 'M'),
        'exact_checked_cap_path_tie20': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
    }
    known_fingerprints = [packet.packet_semantic_fingerprint(standalone) for standalone in expected.values()]

    for name, standalone in expected.items():
        row = sample_rows[name]
        packed_seed = packet.packet_packed_seed(standalone)
        micro_seed = packet.packet_micro_seed(standalone)
        packed_reference = packet.packet_packed_reference(standalone, known_fingerprints)
        micro_reference = packet.packet_micro_reference(standalone, known_fingerprints)
        atto_first = packet.packet_archive_atto_write_plan(standalone, [])
        atto_repeat = packet.packet_archive_atto_write_plan(standalone, known_fingerprints)

        assert row['standalone_packet'] == standalone
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(standalone)
        assert row['micro_seed_packet'] == micro_seed
        assert row['packed_seed_packet'] == packed_seed
        assert row['micro_reference_packet'] == micro_reference
        assert row['packed_reference_packet'] == packed_reference
        assert packet.expand_packed_seed_packet(packed_seed) == standalone
        assert packet.expand_packed_seed_packet(packed_seed, archive_local=True) == row['archive_local_packet']
        assert packet.expand_packet(packed_seed) == standalone
        assert packet.expand_packed_reference_packet(packed_reference) == packet.expand_micro_reference_packet(micro_reference)
        assert packet.resolve_archive_any_reference(packed_reference, known_fingerprints) == row['semantic_fingerprint']
        assert row['micro_seed_bytes'] == packet.packet_minified_bytes(micro_seed)
        assert row['packed_seed_bytes'] == packet.packet_minified_bytes(packed_seed)
        assert row['micro_reference_bytes'] == packet.packet_minified_bytes(micro_reference)
        assert row['packed_reference_bytes'] == packet.packet_minified_bytes(packed_reference)
        assert row['micro_seed_to_packed_seed_bytes_saved'] == row['micro_seed_bytes'] - row['packed_seed_bytes']
        assert row['micro_reference_to_packed_reference_bytes_saved'] == (
            row['micro_reference_bytes'] - row['packed_reference_bytes']
        )
        assert row['atto_first_write_plan'] == atto_first
        assert row['atto_repeat_write_plan'] == atto_repeat
        assert atto_first['recommended_write_kind'] == 'packed_seed_body'
        assert atto_repeat['recommended_write_kind'] == 'packed_reference'
        assert row['micro_seed_to_packed_seed_bytes_saved'] > 0
        assert row['micro_reference_to_packed_reference_bytes_saved'] > 0

    assert findings['best_micro_seed_to_packed_seed_savings_example'] in sample_rows
    assert findings['best_micro_seed_to_packed_seed_bytes_saved'] == max(
        row['micro_seed_to_packed_seed_bytes_saved'] for row in sample_rows.values()
    )
    assert findings['best_micro_reference_to_packed_reference_savings_example'] in sample_rows
    extra_cases = {
        'robustness_fixed': packet.packet_from_robustness_fixed('S', 'M'),
        'strict_adaptive': packet.packet_from_strict_adaptive('M', 'S'),
    }
    extra_known = known_fingerprints + [packet.packet_semantic_fingerprint(case) for case in extra_cases.values()]
    for case in extra_cases.values():
        packed_seed = packet.packet_packed_seed(case)
        packed_reference = packet.packet_packed_reference(case, extra_known)
        assert packet.expand_packed_seed_packet(packed_seed) == case
        assert packet.resolve_archive_any_reference(packed_reference, extra_known) == packet.packet_semantic_fingerprint(case)
        assert packet.packet_minified_bytes(packed_seed) < packet.packet_minified_bytes(packet.packet_micro_seed(case))
        assert packet.packet_minified_bytes(packed_reference) < packet.packet_minified_bytes(
            packet.packet_micro_reference(case, extra_known)
        )

    print('decision-packet-packed: ok')


if __name__ == '__main__':
    main()
