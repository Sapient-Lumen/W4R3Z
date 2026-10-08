#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compiled_frontier_snapshot_20260307.json'


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
    packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in packets]

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(packets)
    assert report['deterministic_body_winner_counts'] == {'byte_seed': 250, 'packed_seed': 24}
    assert report['deterministic_repeat_winner_counts'] == {'byte_reference': 274}
    assert report['deterministic_body_exact_match_count'] == len(packets)
    assert report['deterministic_repeat_exact_match_count'] == len(packets)
    assert report['deterministic_body_candidate_evaluations_full_frontier'] == len(packets) * 6
    assert report['deterministic_body_candidate_evaluations_compiled_frontier'] == len(packets)
    assert report['deterministic_body_candidate_evaluation_savings'] == 1370
    assert report['deterministic_repeat_candidate_evaluations_full_frontier'] == len(packets) * 6
    assert report['deterministic_repeat_candidate_evaluations_compiled_frontier'] == len(packets)
    assert report['deterministic_repeat_candidate_evaluation_savings'] == 1370
    assert report['random_weight_validation_count'] == 1024
    assert report['random_weight_exact_match_count'] == 1024

    for row in packets:
        standalone = row['packet']
        measured_body = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        compiled_body = packet.packet_body_storage_compiled_frontier(standalone)
        assert measured_body['recommended_storage_form'] == compiled_body['recommended_storage_form']

        measured_repeat = packet.packet_repeat_storage_frontier(
            standalone,
            known_fingerprints,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        compiled_repeat = packet.packet_repeat_storage_compiled_frontier(standalone, known_fingerprints)
        assert measured_repeat['recommended_storage_form'] == compiled_repeat['recommended_storage_form'] == 'byte_reference'
        assert packet.packet_archive_zepto_write_plan(standalone, known_fingerprints)['recommended_write_kind'] == 'byte_reference'

    rows = {row['name']: row for row in report['sample_packet_rows']}
    width = rows['weights_case_001']
    assert width['compiled_body_frontier']['recommended_storage_form'] == 'packed_seed'
    assert width['packed_seed_bytes'] == 7
    assert width['byte_seed_bytes'] == 8
    assert width['zepto_write_plan']['recommended_write_kind'] == 'packed_seed_body'

    hazard = rows['weights_case_043']
    assert hazard['compiled_body_frontier']['recommended_storage_form'] == 'byte_seed'
    assert hazard['byte_seed_bytes'] < hazard['packed_seed_bytes']
    assert hazard['zepto_write_plan']['recommended_write_kind'] == 'byte_seed_body'

    coordinates = rows['coordinates_0.0001_1']
    assert coordinates['mode'] == 'oracle_coordinates'
    assert coordinates['compiled_body_frontier']['candidate_storage_forms'] == ['packed_seed', 'byte_seed']
    assert coordinates['zepto_write_plan']['recommended_write_kind'] == 'byte_seed_body'

    tie20 = rows['exact_checked_cap_STS']
    assert tie20['mode'] == 'probe_exact_checked_cap_path'
    assert tie20['compiled_repeat_frontier']['recommended_storage_form'] == 'byte_reference'
    assert tie20['zepto_repeat_write_plan']['recommended_write_kind'] == 'byte_reference'

    print('decision-packet-compiled-frontiers: ok')


if __name__ == '__main__':
    main()
