#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_catalog_reference_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report = json.loads(REPORT_PATH.read_text())

    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(deterministic_packets) == 274
    assert report['headline_findings']['byte_reference_total_bytes'] == 3288
    assert report['headline_findings']['catalog_reference_total_bytes'] == 1516
    assert report['headline_findings']['repeat_bytes_saved'] == 1772
    assert report['headline_findings']['repeat_byte_savings_share'] == 0.538929
    assert report['headline_findings']['average_byte_reference_bytes'] == 12.0
    assert report['headline_findings']['average_catalog_reference_bytes'] == 5.532847
    assert report['headline_findings']['catalog_reference_length_distribution'] == {'5': 128, '6': 146}
    assert report['headline_findings']['byte_reference_length_distribution'] == {'12': 274}

    for index, row in enumerate(deterministic_packets):
        standalone = row['packet']
        fingerprint = known_fingerprints[index]
        catalog_reference = packet.packet_catalog_reference(standalone, known_fingerprints)
        assert packet.resolve_archive_any_reference(catalog_reference, known_fingerprints) == fingerprint
        expanded = packet.expand_catalog_reference_packet(catalog_reference)
        assert expanded == {'packet_kind': packet.ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND, 'slot': index}
        yocto = packet.packet_archive_yocto_write_plan(standalone, known_fingerprints)
        assert yocto['recommended_write_kind'] == 'short_catalog_reference'
        assert yocto['catalog_slot'] == index
        assert yocto['reference'] == packet.packet_short_catalog_reference(standalone, known_fingerprints)
        fallback = packet.packet_archive_yocto_write_plan(standalone, set(known_fingerprints))
        assert fallback['recommended_write_kind'] == 'byte_reference'

    sample_rows = {row['slot']: row for row in report['sample_rows']}
    assert sample_rows[0]['catalog_reference_bytes'] == 5
    assert sample_rows[0]['yocto_repeat_write_plan']['recommended_write_kind'] == 'short_catalog_reference'
    assert sample_rows[0]['set_fallback_repeat_write_plan']['recommended_write_kind'] == 'byte_reference'
    assert sample_rows[127]['catalog_reference_bytes'] == 5
    assert sample_rows[128]['catalog_reference_bytes'] == 6
    assert sample_rows[273]['catalog_reference_bytes'] == 6

    try:
        packet.packet_catalog_reference(deterministic_packets[0]['packet'], set(known_fingerprints))
    except packet.PacketError:
        pass
    else:
        raise AssertionError('unordered sets must not be accepted for catalog-slot references')

    print('decision-packet-catalog-references: ok')


if __name__ == '__main__':
    main()
