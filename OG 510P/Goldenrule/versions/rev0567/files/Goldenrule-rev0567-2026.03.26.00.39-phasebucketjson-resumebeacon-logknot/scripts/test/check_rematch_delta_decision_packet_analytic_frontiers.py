#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
ANALYTIC_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_analytic_frontier_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_analytic_frontier_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    analytic_builder = _load_module(ANALYTIC_BUILDER_PATH, 'analytic_snapshot')
    report = json.loads(REPORT_PATH.read_text())

    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]
    random_weight_packets = analytic_builder._random_weight_packets(packet)
    random_coordinate_packets = analytic_builder._random_coordinate_packets(packet)

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(deterministic_packets)
    assert report['deterministic_first_write_exact_match_count'] == len(deterministic_packets)
    assert report['deterministic_repeat_exact_match_count'] == len(deterministic_packets)
    assert report['deterministic_first_write_winner_counts'] == {'byte_seed': 250, 'packed_seed': 24}
    assert report['deterministic_repeat_winner_counts'] == {'byte_reference': 274}
    assert report['deterministic_full_frontier_first_write_candidate_evaluations'] == len(deterministic_packets) * 6
    assert report['deterministic_exact_first_write_candidate_evaluations'] == len(deterministic_packets)
    assert report['deterministic_full_frontier_repeat_candidate_evaluations'] == len(deterministic_packets) * 6
    assert report['deterministic_exact_repeat_candidate_evaluations'] == len(deterministic_packets)
    assert report['random_weight_validation_count'] == len(random_weight_packets)
    assert report['random_coordinate_validation_count'] == len(random_coordinate_packets)
    assert report['random_weight_exact_match_count'] == len(random_weight_packets)
    assert report['random_coordinate_exact_match_count'] == len(random_coordinate_packets)
    assert report['synthetic_repeat_prefix_validation_count'] == 27
    assert report['synthetic_repeat_prefix_exact_match_count'] == 27

    for row in deterministic_packets:
        standalone = row['packet']
        measured_first = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        exact_first = packet.packet_seed_storage_exact_choice(standalone)
        assert measured_first['recommended_storage_form'] == exact_first['recommended_storage_form']
        assert exact_first['candidate_storage_forms'] == ['packed_seed', 'byte_seed']
        packed_seed = packet.packet_packed_seed(standalone)
        assert packet._packed_seed_minified_bytes_exact(packed_seed) == packet.packet_minified_bytes(packed_seed)
        assert packet._byte_seed_minified_bytes_exact_from_packed_seed(packed_seed) == packet.packet_minified_bytes(packet.packet_byte_seed(standalone))

        measured_repeat = packet.packet_repeat_storage_frontier(
            standalone,
            known_fingerprints,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        exact_repeat = packet.packet_repeat_storage_exact_choice(standalone, known_fingerprints)
        assert measured_repeat['recommended_storage_form'] == exact_repeat['recommended_storage_form'] == 'byte_reference'
        assert exact_repeat['candidate_storage_forms'] == ['packed_reference', 'byte_reference']
        assert packet.packet_archive_zepto_write_plan(standalone, known_fingerprints)['recommended_write_kind'] == 'byte_reference'

    for row in random_weight_packets[:256]:
        standalone = row['packet']
        measured_first = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        exact_first = packet.packet_seed_storage_exact_choice(standalone)
        assert measured_first['recommended_storage_form'] == exact_first['recommended_storage_form']

    for row in random_coordinate_packets[:256]:
        standalone = row['packet']
        measured_first = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        exact_first = packet.packet_seed_storage_exact_choice(standalone)
        assert measured_first['recommended_storage_form'] == exact_first['recommended_storage_form']

    target = next(row for row in deterministic_packets if row['name'] == 'coordinates_0.0001_1')['packet']
    for prefix_len in range(packet.MIN_REFERENCE_PREFIX_HEX_LEN, 65, 2):
        synthetic_known = analytic_builder._synthetic_known_fingerprints(packet, packet.packet_semantic_fingerprint(target), prefix_len=prefix_len)
        measured_repeat = packet.packet_repeat_storage_frontier(
            target,
            synthetic_known,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        exact_repeat = packet.packet_repeat_storage_exact_choice(target, synthetic_known)
        assert measured_repeat['recommended_storage_form'] == exact_repeat['recommended_storage_form'] == 'byte_reference'
        assert exact_repeat['prefix_hex_len'] == prefix_len

    sample_rows = {row['name']: row for row in report['sample_rows']}
    width = sample_rows['weights_case_001']
    assert width['exact_first_choice']['recommended_storage_form'] == 'packed_seed'
    assert width['exact_first_choice']['candidate_minified_bytes'] == {'byte_seed': 8, 'packed_seed': 7}
    assert width['zepto_first_write_plan']['recommended_write_kind'] == 'packed_seed_body'

    hazard = sample_rows['weights_case_043']
    assert hazard['exact_first_choice']['recommended_storage_form'] == 'byte_seed'
    assert hazard['exact_first_choice']['candidate_minified_bytes'] == {'byte_seed': 8, 'packed_seed': 9}

    coordinates = sample_rows['coordinates_0.0001_1']
    assert coordinates['exact_first_choice']['recommended_storage_form'] == 'byte_seed'
    assert coordinates['exact_first_choice']['candidate_minified_bytes'] == {'byte_seed': 6, 'packed_seed': 7}

    tie20 = sample_rows['exact_checked_cap_STS']
    assert tie20['exact_repeat_choice']['recommended_storage_form'] == 'byte_reference'
    assert tie20['zepto_repeat_write_plan']['recommended_write_kind'] == 'byte_reference'

    prefix_rows = {row['prefix_len']: row for row in report['repeat_prefix_rows']}
    assert prefix_rows[12]['exact_choice']['candidate_minified_bytes'] == {'byte_reference': 12, 'packed_reference': 14}
    assert prefix_rows[64]['exact_choice']['candidate_minified_bytes']['byte_reference'] < prefix_rows[64]['exact_choice']['candidate_minified_bytes']['packed_reference']

    print('decision-packet-analytic-frontiers: ok')


if __name__ == '__main__':
    main()
