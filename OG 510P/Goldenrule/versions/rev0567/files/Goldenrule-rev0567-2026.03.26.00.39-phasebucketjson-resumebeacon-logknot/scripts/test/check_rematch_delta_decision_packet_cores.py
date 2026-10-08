#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_core_snapshot_20260307.json'


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
    assert findings['semantic_core_kind'] == packet.SEMANTIC_CORE_KIND
    assert findings['semantic_core_contract_version'] == packet.SEMANTIC_CORE_CONTRACT_VERSION
    assert findings['default_machine_storage_form'] == 'semantic_core'
    assert findings['default_human_readable_storage_form'] == 'archive_local'
    assert findings['portable_storage_form'] == 'standalone'

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

    for name, (standalone, archive_local) in expected.items():
        row = sample_rows[name]
        semantic_core = packet.packet_semantic_core(standalone)
        compact_first_write = packet.packet_archive_compact_write_plan(standalone, [])
        compact_repeat_write = packet.packet_archive_compact_write_plan(semantic_core, [packet.packet_semantic_fingerprint(standalone)])
        human_first_write = packet.packet_archive_compact_write_plan(standalone, [], need_human_readable_packet=True)

        assert row['standalone_packet'] == standalone
        assert row['archive_local_packet'] == archive_local
        assert row['semantic_core_packet'] == semantic_core
        assert row['semantic_fingerprint'] == packet.packet_semantic_fingerprint(semantic_core)
        assert packet.expand_semantic_core_packet(semantic_core) == standalone
        assert packet.expand_semantic_core_packet(semantic_core, archive_local=True) == archive_local
        assert packet.expand_packet(semantic_core) == standalone
        assert row['standalone_bytes'] == packet.packet_minified_bytes(standalone)
        assert row['archive_local_bytes'] == packet.packet_minified_bytes(archive_local)
        assert row['semantic_core_bytes'] == packet.packet_minified_bytes(semantic_core)
        assert row['reference_bytes'] == packet.packet_minified_bytes(packet.packet_reference(standalone))
        assert row['archive_local_to_core_bytes_saved'] == row['archive_local_bytes'] - row['semantic_core_bytes']
        assert row['standalone_to_core_bytes_saved'] == row['standalone_bytes'] - row['semantic_core_bytes']
        assert row['archive_local_to_core_bytes_saved'] > 0
        assert row['compact_first_write_plan'] == compact_first_write
        assert row['compact_repeat_write_plan'] == compact_repeat_write
        assert row['human_readable_first_write_plan'] == human_first_write
        assert compact_first_write['recommended_write_kind'] == 'semantic_core_body'
        assert compact_repeat_write['recommended_write_kind'] == 'reference'
        assert human_first_write['recommended_write_kind'] == 'archive_local_body'

    assert findings['best_archive_local_to_core_savings_example'] in sample_rows
    assert findings['best_archive_local_to_core_bytes_saved'] == max(
        row['archive_local_to_core_bytes_saved'] for row in sample_rows.values()
    )

    print('decision-packet-cores: ok')


if __name__ == '__main__':
    main()
