#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_frontier_snapshot_20260307.json'


def _load_packet_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_packet', PACKET_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_report() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def _weight_samples(packet) -> list[dict[str, str]]:
    samples: list[dict[str, str]] = []
    for key in packet.WEIGHT_KEYS:
        for value in ['1', '0.5', '2', '0.2', '0.0001', '3.14']:
            weights = {name: '0' for name in packet.WEIGHT_KEYS}
            weights[key] = value
            samples.append(weights)
    for value in ['1', '0.5', '2', '0.2', '0.0001', '3.14']:
        samples.append({key: value for key in packet.WEIGHT_KEYS})
    for split in range(1, len(packet.WEIGHT_KEYS)):
        samples.append(
            {
                key: ('1' if index < split else '0.5')
                for index, key in enumerate(packet.WEIGHT_KEYS)
            }
        )
    rng = random.Random(0)
    scalar_choices = ['0', '1', '0.5', '2', '0.2', '0.0001', '3.14']
    for _ in range(128):
        samples.append({key: rng.choice(scalar_choices) for key in packet.WEIGHT_KEYS})
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for weights in samples:
        signature = tuple(weights[key] for key in packet.WEIGHT_KEYS)
        if signature in seen:
            continue
        seen.add(signature)
        unique.append(weights)
    return unique


def _frontier_test_packets(packet) -> list[dict[str, object]]:
    packets: list[dict[str, object]] = []
    scalar_values = ['0', '1', '0.5', '2', '0.2', '0.0001', '0.000000', '3.14']
    for B in scalar_values:
        for H in scalar_values:
            packets.append({'name': f'coordinates_{B}_{H}', 'packet': packet.packet_from_coordinates(B, H)})
    for signature in ['MM', 'SM', 'SS']:
        packets.append({'name': f'robustness_fixed_{signature}', 'packet': packet.packet_from_robustness_fixed(*signature)})
    for args in [(10, 'M', None), (10, 'S', 'M'), (10, 'S', 'S'), (20, 'S', None), (20, 'M', 'M'), (20, 'M', 'S')]:
        label = 'adaptive_' + '_'.join('none' if value is None else str(value) for value in args)
        packets.append({'name': label, 'packet': packet.packet_from_robustness_adaptive(*args)})
    for args in [('M', 'M'), ('M', 'S'), ('S', 'M'), ('S', 'S')]:
        packets.append({'name': 'strict_' + ''.join(args), 'packet': packet.packet_from_strict_adaptive(*args)})
    for signature in ['MMM', 'SMM', 'SMS', 'SSS', 'TMM', 'SMT', 'STS', 'TTT']:
        packets.append({'name': f'exact_checked_cap_{signature}', 'packet': packet.packet_from_exact_checked_cap_path(*signature)})
    for index, weights in enumerate(_weight_samples(packet), start=1):
        packets.append({'name': f'weights_case_{index:03d}', 'packet': packet.packet_from_weights(weights)})
    unique: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in packets:
        fingerprint = packet.packet_semantic_fingerprint(row['packet'])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        unique.append(row)
    return unique


def main() -> None:
    packet = _load_packet_module()
    report = _load_report()
    findings = report['headline_findings']

    packets = _frontier_test_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in packets]
    body_winner_counts: dict[str, int] = {}
    repeat_winner_counts: dict[str, int] = {}
    override_rows = []
    repeat_override_rows = []
    max_override = None
    for row in packets:
        standalone = row['packet']
        frontier = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        repeat_frontier = packet.packet_repeat_storage_frontier(
            standalone,
            known_fingerprints,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        body_winner_counts[frontier['recommended_storage_form']] = body_winner_counts.get(frontier['recommended_storage_form'], 0) + 1
        repeat_winner_counts[repeat_frontier['recommended_storage_form']] = repeat_winner_counts.get(repeat_frontier['recommended_storage_form'], 0) + 1
        if frontier['recommended_storage_form'] != frontier['default_storage_form']:
            payload = {
                'name': row['name'],
                'mode': standalone['mode'],
                'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
                'recommended_storage_form': frontier['recommended_storage_form'],
                'default_storage_form': frontier['default_storage_form'],
                'bytes_saved_vs_default': frontier['bytes_saved_vs_default'],
                'candidate_minified_bytes': frontier['candidate_minified_bytes'],
            }
            override_rows.append(payload)
            if max_override is None or payload['bytes_saved_vs_default'] > max_override['bytes_saved_vs_default']:
                max_override = payload
        if repeat_frontier['recommended_storage_form'] != repeat_frontier['default_storage_form']:
            repeat_override_rows.append(
                {
                    'name': row['name'],
                    'mode': standalone['mode'],
                    'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
                    'recommended_storage_form': repeat_frontier['recommended_storage_form'],
                    'default_storage_form': repeat_frontier['default_storage_form'],
                    'bytes_saved_vs_default': repeat_frontier['bytes_saved_vs_default'],
                    'candidate_minified_bytes': repeat_frontier['candidate_minified_bytes'],
                }
            )

    assert findings['packet_script'] == str(PACKET_PATH.relative_to(ROOT))
    assert findings['tested_packet_count'] == len(packets)
    assert findings['coarse_default_first_write_storage_form_with_byteframe_codec'] == 'byte_seed'
    assert findings['measured_first_write_winner_counts'] == body_winner_counts
    assert findings['packets_where_measured_frontier_overrides_coarse_default'] == len(override_rows)
    assert findings['modes_with_measured_overrides'] == sorted({row['mode'] for row in override_rows})
    assert findings['largest_bytes_saved_vs_coarse_default'] == max_override['bytes_saved_vs_default']
    assert findings['largest_savings_example'] == max_override['name']
    assert findings['coarse_default_repeat_storage_form_with_byteframe_codec'] == 'byte_reference'
    assert findings['measured_repeat_winner_counts'] == repeat_winner_counts
    assert findings['repeat_frontier_override_count'] == len(repeat_override_rows)
    assert findings['repeat_frontier_override_count'] == 0
    assert 'oracle_weights' in findings['modes_with_measured_overrides']

    rows = {row['name']: row for row in report['sample_packet_rows']}
    exception = rows['oracle_weights_width_one_exception']
    exception_packet = packet.packet_from_weights(
        {
            'w_width': '1',
            'w_buffer': '0',
            'w_knife': '0',
            'w_delta': '0',
            'w_material': '0',
            'w_undecided': '0',
            'w_ties': '0',
            'w_hazard': '0',
        }
    )
    assert exception['standalone_packet'] == exception_packet
    assert exception['body_frontier']['recommended_storage_form'] == 'packed_seed'
    assert exception['body_frontier']['default_storage_form'] == 'byte_seed'
    assert exception['packed_seed_bytes'] == 7
    assert exception['byte_seed_bytes'] == 8
    assert exception['zepto_first_write_plan']['recommended_write_kind'] == 'packed_seed_body'
    assert exception['zepto_first_write_plan']['body'] == packet.packet_packed_seed(exception_packet)

    byteframe_win_names = [
        'oracle_weights_hazard_one_byteframe_win',
        'oracle_coordinates_sms_byteframe_win',
        'exact_checked_cap_path_tie20_byteframe_win',
    ]
    known_samples = [row['semantic_fingerprint'] for row in report['sample_packet_rows']]
    for name in byteframe_win_names:
        row = rows[name]
        assert row['body_frontier']['recommended_storage_form'] == 'byte_seed'
        assert row['repeat_frontier']['recommended_storage_form'] == 'byte_reference'
        assert row['byte_seed_bytes'] < row['packed_seed_bytes']
        assert row['byte_reference_bytes'] < row['packed_reference_bytes']
        assert packet.expand_byte_seed_packet(row['byte_seed_packet']) == row['standalone_packet']
        assert packet.resolve_archive_any_reference(row['byte_reference_packet'], known_samples) == row['semantic_fingerprint']
        assert row['zepto_first_write_plan']['recommended_write_kind'] == 'byte_seed_body'
        assert row['zepto_repeat_write_plan']['recommended_write_kind'] == 'byte_reference'

    assert report['frontier_override_examples']
    first_override = report['frontier_override_examples'][0]
    assert first_override['recommended_storage_form'] == 'packed_seed'
    assert first_override['default_storage_form'] == 'byte_seed'
    assert first_override['bytes_saved_vs_default'] == 1
    assert report['repeat_frontier_override_examples'] == []

    print('decision-packet-frontiers: ok')


if __name__ == '__main__':
    main()
