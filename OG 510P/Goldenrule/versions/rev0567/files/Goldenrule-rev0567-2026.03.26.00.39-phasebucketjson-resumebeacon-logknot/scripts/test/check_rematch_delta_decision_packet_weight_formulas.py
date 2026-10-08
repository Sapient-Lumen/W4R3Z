#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
REPORT_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_weight_formula_snapshot.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_formula_snapshot_20260307.json'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    report_builder = _load_module(REPORT_BUILDER_PATH, 'weight_formula_snapshot')
    report = json.loads(REPORT_PATH.read_text())

    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    deterministic_weight_packets = [row for row in deterministic_packets if row['packet']['mode'] == 'oracle_weights']
    random_weight_packets = report_builder._random_weight_packets(packet)

    assert report['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert report['deterministic_frontier_packet_count'] == len(deterministic_packets) == 274
    assert report['deterministic_weight_packet_count'] == len(deterministic_weight_packets) == 189
    assert report['deterministic_formula_exact_count'] == 189
    assert report['deterministic_winner_counts'] == {'packed_seed': 24, 'byte_seed': 165}
    assert report['deterministic_tie_count'] == 18
    assert report['random_weight_validation_count'] == len(random_weight_packets) == 4096
    assert report['random_formula_exact_count'] == 4096
    assert report['random_winner_counts'] == {'packed_seed': 34, 'byte_seed': 4062}
    assert report['headline_findings']['old_first_write_seed_materializations'] == 463
    assert report['headline_findings']['new_first_write_seed_materializations'] == 274
    assert report['headline_findings']['first_write_seed_materializations_saved'] == 189
    assert report['headline_findings']['first_write_seed_materialization_savings_share'] == 0.408207

    for row in deterministic_weight_packets:
        standalone = row['packet']
        choice = packet.oracle_weight_seed_storage_choice(standalone)
        packed_seed = packet.packet_packed_seed(standalone)
        byte_seed = packet.packet_byte_seed(standalone)
        actual = {
            'packed_seed': packet.packet_minified_bytes(packed_seed),
            'byte_seed': packet.packet_minified_bytes(byte_seed),
        }
        assert choice['candidate_minified_bytes'] == actual
        compiled = packet.packet_body_storage_compiled_frontier(standalone)
        assert compiled['recommended_storage_form'] == choice['recommended_storage_form']
        expected_write_kind = 'packed_seed_body' if choice['recommended_storage_form'] == 'packed_seed' else 'byte_seed_body'
        assert packet.packet_archive_zepto_write_plan(standalone, [])['recommended_write_kind'] == expected_write_kind

    for row in random_weight_packets:
        standalone = row['packet']
        choice = packet.oracle_weight_seed_storage_choice(standalone)
        packed_seed = packet.packet_packed_seed(standalone)
        byte_seed = packet.packet_byte_seed(standalone)
        actual = {
            'packed_seed': packet.packet_minified_bytes(packed_seed),
            'byte_seed': packet.packet_minified_bytes(byte_seed),
        }
        assert choice['candidate_minified_bytes'] == actual
        compiled = packet.packet_body_storage_compiled_frontier(standalone)
        assert compiled['recommended_storage_form'] == choice['recommended_storage_form']

    sample_rows = {row['name']: row for row in report['sample_weight_rows']}
    packed = sample_rows['weights_case_001']
    assert packed['recommended_storage_form'] == 'packed_seed'
    assert packed['analytic_candidate_minified_bytes'] == {'packed_seed': 7, 'byte_seed': 8}
    assert packed['actual_candidate_minified_bytes'] == {'packed_seed': 7, 'byte_seed': 8}
    assert packed['zepto_write_plan']['recommended_write_kind'] == 'packed_seed_body'

    tie = sample_rows['weights_case_025']
    assert tie['recommended_storage_form'] == 'byte_seed'
    assert tie['tied_storage_forms'] == ['byte_seed', 'packed_seed']
    assert tie['analytic_candidate_minified_bytes'] == {'packed_seed': 8, 'byte_seed': 8}
    assert tie['zepto_write_plan']['recommended_write_kind'] == 'byte_seed_body'

    byte = sample_rows['weights_case_043']
    assert byte['recommended_storage_form'] == 'byte_seed'
    assert byte['analytic_candidate_minified_bytes'] == {'packed_seed': 9, 'byte_seed': 8}
    assert byte['zepto_write_plan']['recommended_write_kind'] == 'byte_seed_body'

    grouped = sample_rows['weights_case_049']
    assert grouped['payload_shape'] == 'grouped_atom_masks'
    assert grouped['recommended_storage_form'] == 'byte_seed'
    assert grouped['analytic_candidate_minified_bytes'] == {'packed_seed': 12, 'byte_seed': 9}

    print('decision-packet-weight-formulas: ok')


if __name__ == '__main__':
    main()
