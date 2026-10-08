#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_coded_seed_snapshot_20260307.json'


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
    assert findings['coded_seed_kind'] == packet.CODED_SEED_KIND
    assert findings['coded_seed_profile_ref'] == packet.CODED_SEED_PROFILE_REF
    assert findings['coded_seed_mode_codes'] == packet.CODED_SEED_MODE_CODES
    assert findings['default_machine_storage_form_with_codebook'] == 'coded_seed'
    assert findings['fallback_machine_storage_form_without_codebook'] == 'semantic_core'

    sample_rows = {row['name']: row for row in report['sample_packet_rows']}
    expected = {
        'oracle_coordinates_sms': (
            packet.packet_from_coordinates('0.0001', '1'),
            packet.packet_from_coordinates('0.0001', '1', archive_local=True),
        ),
        'oracle_weights_smm': (
            packet.packet_from_weights(
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
            packet.packet_from_weights(
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
        ),
        'robustness_adaptive_cap_sensitive': (
            packet.packet_from_robustness_adaptive(10, 'S', 'M'),
            packet.packet_from_robustness_adaptive(10, 'S', 'M', archive_local=True),
        ),
        'exact_checked_cap_path_tie20': (
            packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
        ),
    }
    known_fingerprints = [packet.packet_semantic_fingerprint(standalone) for standalone, _ in expected.values()]

    for name, (standalone, archive_local) in expected.items():
        row = sample_rows[name]
        semantic_core = packet.packet_semantic_core(standalone)
        coded_seed = packet.packet_coded_seed(standalone)
        local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        first_write = packet.packet_archive_nano_write_plan(standalone, [])
        repeat_write = packet.packet_archive_nano_write_plan(standalone, known_fingerprints)

        assert row['standalone_packet'] == standalone
        assert row['archive_local_packet'] == archive_local
        assert row['semantic_core_packet'] == semantic_core
        assert row['coded_seed_packet'] == coded_seed
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(standalone)
        assert packet.expand_coded_seed_packet(coded_seed) == standalone
        assert packet.expand_coded_seed_packet(coded_seed, archive_local=True) == archive_local
        assert packet.expand_packet(coded_seed) == standalone
        assert row['standalone_bytes'] == packet.packet_minified_bytes(standalone)
        assert row['archive_local_bytes'] == packet.packet_minified_bytes(archive_local)
        assert row['semantic_core_bytes'] == packet.packet_minified_bytes(semantic_core)
        assert row['coded_seed_bytes'] == packet.packet_minified_bytes(coded_seed)
        assert row['archive_local_reference_packet'] == local_reference
        assert row['archive_local_reference_bytes'] == packet.packet_minified_bytes(local_reference)
        assert row['semantic_core_to_coded_seed_bytes_saved'] == row['semantic_core_bytes'] - row['coded_seed_bytes']
        assert row['archive_local_to_coded_seed_bytes_saved'] == row['archive_local_bytes'] - row['coded_seed_bytes']
        assert row['coded_seed_then_reference_bytes'] == row['coded_seed_bytes'] + row['archive_local_reference_bytes']
        assert row['semantic_core_then_reference_bytes'] == row['semantic_core_bytes'] + row['archive_local_reference_bytes']
        assert row['nano_first_write_plan'] == first_write
        assert row['nano_repeat_write_plan'] == repeat_write
        assert first_write['recommended_write_kind'] == 'coded_seed_body'
        assert repeat_write['recommended_write_kind'] == 'archive_local_reference'
        assert row['semantic_core_to_coded_seed_bytes_saved'] > 0

    assert findings['best_semantic_core_to_coded_seed_savings_example'] in sample_rows
    assert findings['best_semantic_core_to_coded_seed_bytes_saved'] == max(
        row['semantic_core_to_coded_seed_bytes_saved'] for row in sample_rows.values()
    )
    assert findings['best_archive_local_to_coded_seed_savings_example'] in sample_rows
    assert findings['best_archive_local_to_coded_seed_bytes_saved'] == max(
        row['archive_local_to_coded_seed_bytes_saved'] for row in sample_rows.values()
    )

    print('decision-packet-coded-seeds: ok')


if __name__ == '__main__':
    main()
