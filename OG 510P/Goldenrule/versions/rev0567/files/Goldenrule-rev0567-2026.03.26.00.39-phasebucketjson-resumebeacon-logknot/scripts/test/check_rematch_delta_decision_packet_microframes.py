#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_microframe_snapshot_20260307.json'


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
    assert findings['microframe_reference_tag'] == packet.MICROFRAME_REFERENCE_TAG
    assert findings['default_first_write_storage_form_with_microframe_codec'] == 'micro_seed'
    assert findings['fallback_first_write_storage_form_without_microframe_codec'] == 'coded_seed'
    assert findings['default_repeat_storage_form_with_microframe_codec'] == 'micro_reference'
    assert findings['fallback_repeat_storage_form_without_microframe_codec'] == 'coded_reference'

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
        micro_seed = packet.packet_micro_seed(standalone)
        coded_seed = packet.packet_coded_seed(standalone)
        micro_reference = packet.packet_micro_reference(standalone, known_fingerprints)
        coded_reference = packet.packet_coded_reference(standalone, known_fingerprints)
        archive_local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        femto_first = packet.packet_archive_femto_write_plan(standalone, [])
        femto_repeat = packet.packet_archive_femto_write_plan(standalone, known_fingerprints)

        assert row['standalone_packet'] == standalone
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(standalone)
        assert row['coded_seed_packet'] == coded_seed
        assert row['micro_seed_packet'] == micro_seed
        assert row['coded_reference_packet'] == coded_reference
        assert row['micro_reference_packet'] == micro_reference
        assert row['archive_local_reference_packet'] == archive_local_reference
        assert packet.expand_micro_seed_packet(micro_seed) == standalone
        assert packet.expand_micro_seed_packet(micro_seed, archive_local=True) == row['archive_local_packet']
        assert packet.expand_packet(micro_seed) == standalone
        assert packet.expand_micro_reference_packet(micro_reference) == archive_local_reference
        assert packet.resolve_archive_any_reference(micro_reference, known_fingerprints) == row['semantic_fingerprint']
        assert row['coded_seed_bytes'] == packet.packet_minified_bytes(coded_seed)
        assert row['micro_seed_bytes'] == packet.packet_minified_bytes(micro_seed)
        assert row['coded_reference_bytes'] == packet.packet_minified_bytes(coded_reference)
        assert row['micro_reference_bytes'] == packet.packet_minified_bytes(micro_reference)
        assert row['archive_local_reference_bytes'] == packet.packet_minified_bytes(archive_local_reference)
        assert row['coded_seed_to_micro_seed_bytes_saved'] == row['coded_seed_bytes'] - row['micro_seed_bytes']
        assert row['coded_reference_to_micro_reference_bytes_saved'] == (
            row['coded_reference_bytes'] - row['micro_reference_bytes']
        )
        assert row['archive_local_reference_to_micro_reference_bytes_saved'] == (
            row['archive_local_reference_bytes'] - row['micro_reference_bytes']
        )
        assert row['femto_first_write_plan'] == femto_first
        assert row['femto_repeat_write_plan'] == femto_repeat
        assert femto_first['recommended_write_kind'] == 'micro_seed_body'
        assert femto_repeat['recommended_write_kind'] == 'micro_reference'
        assert row['coded_seed_to_micro_seed_bytes_saved'] > 0
        assert row['coded_reference_to_micro_reference_bytes_saved'] > 0

    assert findings['best_coded_seed_to_micro_seed_savings_example'] in sample_rows
    assert findings['best_coded_seed_to_micro_seed_bytes_saved'] == max(
        row['coded_seed_to_micro_seed_bytes_saved'] for row in sample_rows.values()
    )
    assert findings['best_coded_reference_to_micro_reference_savings_example'] in sample_rows
    assert findings['best_coded_reference_to_micro_reference_bytes_saved'] == max(
        row['coded_reference_to_micro_reference_bytes_saved'] for row in sample_rows.values()
    )

    print('decision-packet-microframes: ok')


if __name__ == '__main__':
    main()
