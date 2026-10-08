#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_profile_snapshot_20260307.json'


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
    assert findings['archive_local_packet_kind'] == packet.ARCHIVE_LOCAL_PACKET_KIND
    assert findings['standalone_packet_kind'] == packet.PACKET_KIND
    assert findings['archive_local_profile_ref'] == packet.ARCHIVE_LOCAL_PROFILE_REF
    assert findings['default_in_archive_storage_form'] == 'archive_local'
    assert findings['portable_storage_form'] == 'standalone'
    assert findings['shared_profile_replaces_repeated_fields'] == [
        'contract_version',
        'checked_caps',
        'oracle_script',
        'decision_oracle_snapshot',
        'question_targeted_probe_snapshot',
    ]

    assert report['profile_registry'] == packet.archive_local_profile_registry()

    sample_rows = {row['name']: row for row in report['sample_packet_rows']}
    expected_standalone = {
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
        'strict_adaptive_sms': packet.packet_from_strict_adaptive('S', 'M'),
        'exact_checked_cap_path_tie20': packet.packet_from_exact_checked_cap_path('S', 'T', 'S'),
    }
    expected_archive_local = {
        'oracle_coordinates_sms': packet.packet_from_coordinates('0.0001', '1', archive_local=True),
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
            },
            archive_local=True,
        ),
        'strict_adaptive_sms': packet.packet_from_strict_adaptive('S', 'M', archive_local=True),
        'exact_checked_cap_path_tie20': packet.packet_from_exact_checked_cap_path('S', 'T', 'S', archive_local=True),
    }

    for name, standalone in expected_standalone.items():
        archive_local = expected_archive_local[name]
        row = sample_rows[name]
        assert row['standalone_packet'] == standalone
        assert row['archive_local_packet'] == archive_local
        assert packet.expand_archive_local_packet(archive_local) == standalone
        assert row['standalone_bytes'] == packet.packet_minified_bytes(standalone)
        assert row['archive_local_bytes'] == packet.packet_minified_bytes(archive_local)
        assert row['bytes_saved'] == row['standalone_bytes'] - row['archive_local_bytes']
        assert row['bytes_saved'] > 0
        assert row['fraction_saved'] > 0

    assert sample_rows['strict_adaptive_sms']['standalone_packet']['result']['checked_cap_signature'] == 'SMS'
    tie20 = sample_rows['exact_checked_cap_path_tie20']['standalone_packet']
    assert tie20['result']['closure_label'] == 'TIE_tau20'
    assert tie20['result']['strict_path_class'] is None

    local_storage = packet.packet_storage_decision(need_standalone_portability=False)
    portable_storage = packet.packet_storage_decision(need_standalone_portability=True)
    assert local_storage == {
        'recommended_storage_form': 'archive_local',
        'why': 'archive-local packets replace repeated provenance with a shared profile reference and are smaller for long-lived in-archive storage',
    }
    assert portable_storage == {
        'recommended_storage_form': 'standalone',
        'why': 'standalone packets repeat provenance so they can travel outside the archive without an external profile registry',
    }

    print('decision-packet-profiles: ok')


if __name__ == '__main__':
    main()
