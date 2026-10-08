#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.json'


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
    assert findings['portable_reference_kind'] == packet.PACKET_REFERENCE_KIND
    assert findings['archive_local_reference_kind'] == packet.ARCHIVE_LOCAL_REFERENCE_KIND
    assert findings['min_reference_prefix_hex_len'] == packet.MIN_REFERENCE_PREFIX_HEX_LEN
    assert findings['default_first_write_kind'] == 'semantic_core_body'
    assert findings['default_repeat_write_kind_inside_archive'] == 'archive_local_reference'
    assert findings['portable_repeat_write_kind'] == 'reference'

    sample_rows = {row['name']: row for row in report['sample_packet_rows']}
    packets = {
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
    known_fingerprints = [packet.packet_semantic_fingerprint(obj) for obj in packets.values()]

    for name, standalone in packets.items():
        row = sample_rows[name]
        semantic_core = packet.packet_semantic_core(standalone)
        portable_reference = packet.packet_reference(standalone)
        archive_local_reference = packet.packet_archive_local_reference(standalone, known_fingerprints)
        portable_repeat = packet.packet_archive_compact_write_plan(standalone, known_fingerprints)
        ultracompact_repeat = packet.packet_archive_ultracompact_write_plan(standalone, known_fingerprints)
        first_write = packet.packet_archive_ultracompact_write_plan(standalone, [])
        fingerprint = packet.packet_semantic_fingerprint(standalone)

        assert row['semantic_fingerprint'] == fingerprint
        assert row['semantic_core_packet'] == semantic_core
        assert row['semantic_core_bytes'] == packet.packet_minified_bytes(semantic_core)
        assert row['portable_reference_packet'] == portable_reference
        assert row['portable_reference_bytes'] == packet.packet_minified_bytes(portable_reference)
        assert row['archive_local_reference_packet'] == archive_local_reference
        assert row['archive_local_reference_bytes'] == packet.packet_minified_bytes(archive_local_reference)
        assert row['prefix_hex_len'] == packet.minimal_unique_reference_prefix_hex_len(fingerprint, known_fingerprints)
        assert row['resolved_fingerprint'] == packet.resolve_archive_local_reference(archive_local_reference, known_fingerprints)
        assert row['repeat_reference_bytes_saved'] == row['portable_reference_bytes'] - row['archive_local_reference_bytes']
        assert row['semantic_core_then_portable_reference_bytes'] == row['semantic_core_bytes'] + row['portable_reference_bytes']
        assert row['semantic_core_then_archive_local_reference_bytes'] == row['semantic_core_bytes'] + row['archive_local_reference_bytes']
        assert row['portable_repeat_write_plan'] == portable_repeat
        assert row['ultracompact_repeat_write_plan'] == ultracompact_repeat
        assert row['ultracompact_first_write_plan'] == first_write
        assert portable_repeat['recommended_write_kind'] == 'reference'
        assert ultracompact_repeat['recommended_write_kind'] == 'archive_local_reference'
        assert first_write['recommended_write_kind'] == 'semantic_core_body'
        assert row['repeat_reference_bytes_saved'] > 0

    assert findings['best_repeat_reference_savings_example'] in sample_rows
    assert findings['best_repeat_reference_bytes_saved'] == max(
        row['repeat_reference_bytes_saved'] for row in sample_rows.values()
    )
    assert findings['longest_required_prefix_example'] in sample_rows
    assert findings['longest_required_prefix_hex_len'] == max(row['prefix_hex_len'] for row in sample_rows.values())

    print('decision-packet-prefix-references: ok')


if __name__ == '__main__':
    main()
