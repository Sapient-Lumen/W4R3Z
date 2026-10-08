#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_coded_reference_snapshot_20260307.json'


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
    assert findings['coded_reference_kind'] == packet.CODED_REFERENCE_KIND
    assert findings['default_repeat_storage_form_with_codebook'] == 'coded_reference'
    assert findings['fallback_repeat_storage_form_without_codebook'] == 'archive_local_reference'

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
        portable_reference = packet.packet_reference(standalone)
        archive_local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        coded_reference = packet.packet_coded_reference(standalone, known_fingerprints)
        pico_first = packet.packet_archive_pico_write_plan(standalone, [])
        pico_repeat = packet.packet_archive_pico_write_plan(standalone, known_fingerprints)

        assert row['standalone_packet'] == standalone
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(standalone)
        assert row['portable_reference_packet'] == portable_reference
        assert row['archive_local_reference_packet'] == archive_local_reference
        assert row['coded_reference_packet'] == coded_reference
        assert packet.expand_coded_reference_packet(coded_reference) == archive_local_reference
        assert packet.resolve_archive_any_reference(coded_reference, known_fingerprints) == row['semantic_fingerprint']
        assert row['portable_reference_bytes'] == packet.packet_minified_bytes(portable_reference)
        assert row['archive_local_reference_bytes'] == packet.packet_minified_bytes(archive_local_reference)
        assert row['coded_reference_bytes'] == packet.packet_minified_bytes(coded_reference)
        assert row['archive_local_reference_to_coded_reference_bytes_saved'] == (
            row['archive_local_reference_bytes'] - row['coded_reference_bytes']
        )
        assert row['portable_reference_to_coded_reference_bytes_saved'] == (
            row['portable_reference_bytes'] - row['coded_reference_bytes']
        )
        assert row['pico_first_write_plan'] == pico_first
        assert row['pico_repeat_write_plan'] == pico_repeat
        assert pico_first['recommended_write_kind'] == 'coded_seed_body'
        assert pico_repeat['recommended_write_kind'] == 'coded_reference'
        assert row['archive_local_reference_to_coded_reference_bytes_saved'] > 0

    assert findings['best_archive_local_reference_to_coded_reference_savings_example'] in sample_rows
    assert findings['best_archive_local_reference_to_coded_reference_bytes_saved'] == max(
        row['archive_local_reference_to_coded_reference_bytes_saved'] for row in sample_rows.values()
    )
    assert findings['best_portable_reference_to_coded_reference_savings_example'] in sample_rows
    assert findings['best_portable_reference_to_coded_reference_bytes_saved'] == max(
        row['portable_reference_to_coded_reference_bytes_saved'] for row in sample_rows.values()
    )

    print('decision-packet-coded-references: ok')


if __name__ == '__main__':
    main()
