#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_fingerprint_snapshot_20260307.json'


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
    assert findings['packet_kind'] == packet.PACKET_KIND
    assert findings['archive_local_packet_kind'] == packet.ARCHIVE_LOCAL_PACKET_KIND
    assert findings['packet_reference_kind'] == packet.PACKET_REFERENCE_KIND
    assert findings['fingerprint_algorithm'] == 'sha256 over canonical expanded standalone packet JSON'
    assert findings['same_decision_same_fingerprint_across_storage_forms'] is True
    assert findings['default_first_write_kind'] == 'archive_local_body'
    assert findings['default_repeat_write_kind'] == 'reference'

    sample_rows = {row['name']: row for row in report['sample_packet_rows']}
    expected = {
        'oracle_coordinates_sms': (
            packet.packet_from_coordinates('0.0001', '1'),
            packet.packet_from_coordinates('0.0001', '1', archive_local=True),
        ),
        'exact_checked_cap_path_tie20': (
            packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
            packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
        ),
    }

    for name, (standalone, archive_local) in expected.items():
        row = sample_rows[name]
        standalone_fingerprint = packet.packet_semantic_fingerprint(standalone)
        archive_local_fingerprint = packet.packet_semantic_fingerprint(archive_local)
        reference = packet.packet_reference(standalone)
        first_write = packet.packet_archive_write_plan(standalone, [])
        repeat_write = packet.packet_archive_write_plan(archive_local, [standalone_fingerprint])

        assert row['standalone_packet'] == standalone
        assert row['archive_local_packet'] == archive_local
        assert row['standalone_fingerprint'] == standalone_fingerprint
        assert row['archive_local_fingerprint'] == archive_local_fingerprint
        assert standalone_fingerprint == archive_local_fingerprint
        assert row['reference_packet'] == reference
        assert row['standalone_bytes'] == packet.packet_minified_bytes(standalone)
        assert row['archive_local_bytes'] == packet.packet_minified_bytes(archive_local)
        assert row['reference_bytes'] == packet.packet_minified_bytes(reference)
        assert row['body_then_reference_bytes'] == row['archive_local_bytes'] + row['reference_bytes']
        assert row['two_archive_local_bodies_bytes'] == row['archive_local_bytes'] * 2
        assert row['duplicate_bytes_saved'] == row['archive_local_bytes'] - row['reference_bytes']
        assert row['duplicate_bytes_saved'] > 0
        assert row['first_write_plan'] == first_write
        assert row['repeat_write_plan'] == repeat_write
        assert packet.expand_packet(archive_local) == standalone

    assert findings['best_duplicate_savings_example'] in sample_rows
    assert findings['best_duplicate_bytes_saved'] == max(row['duplicate_bytes_saved'] for row in sample_rows.values())

    print('decision-packet-fingerprints: ok')


if __name__ == '__main__':
    main()
