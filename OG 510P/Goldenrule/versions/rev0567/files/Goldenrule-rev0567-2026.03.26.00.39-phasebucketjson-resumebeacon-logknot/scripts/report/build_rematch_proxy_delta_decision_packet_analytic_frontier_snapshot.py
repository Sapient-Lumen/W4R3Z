#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_analytic_frontier_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_analytic_frontier_snapshot_20260307.md'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _random_weight_packets(packet, count: int = 2048) -> list[dict[str, object]]:
    rng = random.Random(0)
    scalar_choices = ['0', '1', '0.5', '2', '0.2', '0.0001', '0.000000', '3.14', '10', '11', '123', '0.333333333', '100000', '0.0000001']
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    while len(rows) < count:
        weights = {key: rng.choice(scalar_choices) for key in packet.WEIGHT_KEYS}
        standalone = packet.packet_from_weights(weights)
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        rows.append({'name': f'random_weights_{len(rows)+1:04d}', 'packet': standalone})
    return rows


def _random_coordinate_packets(packet, count: int = 128) -> list[dict[str, object]]:
    rng = random.Random(1)
    scalar_choices = ['1', '0.5', '2', '0.2', '0.0001', '0.000000', '3.14', '10', '11', '123', '0.333333333', '100000', '0.0000001']
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    while len(rows) < count:
        standalone = packet.packet_from_coordinates(rng.choice(scalar_choices), rng.choice(scalar_choices))
        fingerprint = packet.packet_semantic_fingerprint(standalone)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        rows.append({'name': f'random_coordinates_{len(rows)+1:04d}', 'packet': standalone})
    return rows


def _synthetic_known_fingerprints(packet, fingerprint: str, *, prefix_len: int) -> list[str]:
    normalized = packet._normalize_fingerprint(fingerprint)
    if prefix_len < packet.MIN_REFERENCE_PREFIX_HEX_LEN or prefix_len > 64 or prefix_len % 2 != 0:
        raise ValueError(f'prefix_len must be an even integer in [{packet.MIN_REFERENCE_PREFIX_HEX_LEN},64], got {prefix_len}')
    shared = normalized[:prefix_len - 1]
    diverging = '0' if normalized[prefix_len - 1] != '0' else '1'
    collider_hex = shared + diverging + ('0' * (64 - prefix_len))
    if collider_hex == normalized:
        collider_hex = shared + ('1' if diverging == '0' else '0') + ('f' * (64 - prefix_len))
    known = [f'sha256:{normalized}', f'sha256:{collider_hex}']
    required = packet.minimal_unique_reference_prefix_hex_len(fingerprint, known)
    assert required == prefix_len, (prefix_len, required, fingerprint, known)
    return known


def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    random_weight_packets = _random_weight_packets(packet)
    random_coordinate_packets = _random_coordinate_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]

    deterministic_mode_counts = Counter(row['packet']['mode'] for row in deterministic_packets)
    deterministic_first_winners = Counter()
    deterministic_repeat_winners = Counter()
    deterministic_first_matches = 0
    deterministic_repeat_matches = 0

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
        deterministic_first_winners[exact_first['recommended_storage_form']] += 1
        if measured_first['recommended_storage_form'] == exact_first['recommended_storage_form']:
            deterministic_first_matches += 1

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
        deterministic_repeat_winners[exact_repeat['recommended_storage_form']] += 1
        if measured_repeat['recommended_storage_form'] == exact_repeat['recommended_storage_form']:
            deterministic_repeat_matches += 1

    random_weight_matches = 0
    random_weight_winners = Counter()
    for row in random_weight_packets:
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
        random_weight_winners[exact_first['recommended_storage_form']] += 1
        if measured_first['recommended_storage_form'] == exact_first['recommended_storage_form']:
            random_weight_matches += 1

    random_coordinate_matches = 0
    random_coordinate_winners = Counter()
    for row in random_coordinate_packets:
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
        random_coordinate_winners[exact_first['recommended_storage_form']] += 1
        if measured_first['recommended_storage_form'] == exact_first['recommended_storage_form']:
            random_coordinate_matches += 1

    repeat_prefix_rows: list[dict[str, object]] = []
    prefix_lengths = list(range(packet.MIN_REFERENCE_PREFIX_HEX_LEN, 65, 2))
    prefix_target = next(row for row in deterministic_packets if row['name'] == 'coordinates_0.0001_1')
    prefix_packet = prefix_target['packet']
    prefix_repeat_matches = 0
    prefix_repeat_winners = Counter()
    for prefix_len in prefix_lengths:
        synthetic_known = _synthetic_known_fingerprints(packet, packet.packet_semantic_fingerprint(prefix_packet), prefix_len=prefix_len)
        measured_repeat = packet.packet_repeat_storage_frontier(
            prefix_packet,
            synthetic_known,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        exact_repeat = packet.packet_repeat_storage_exact_choice(prefix_packet, synthetic_known)
        if measured_repeat['recommended_storage_form'] == exact_repeat['recommended_storage_form']:
            prefix_repeat_matches += 1
        prefix_repeat_winners[exact_repeat['recommended_storage_form']] += 1
        if prefix_len in {12, 14, 16, 20, 24, 32, 48, 64}:
            repeat_prefix_rows.append({
                'prefix_len': prefix_len,
                'exact_choice': exact_repeat,
                'measured_repeat_frontier': measured_repeat,
                'packed_reference_packet': packet.packet_packed_reference(prefix_packet, synthetic_known),
                'byte_reference_packet': packet.packet_byte_reference(prefix_packet, synthetic_known),
            })

    sample_names = {'coordinates_0.0001_1', 'weights_case_001', 'weights_case_043', 'exact_checked_cap_STS'}
    sample_rows: list[dict[str, object]] = []
    for row in deterministic_packets:
        if row['name'] not in sample_names:
            continue
        standalone = row['packet']
        sample_rows.append({
            'name': row['name'],
            'mode': standalone['mode'],
            'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
            'measured_first_frontier': packet.packet_body_storage_frontier(
                standalone,
                need_standalone_portability=False,
                archive_has_core_expander=True,
                archive_has_seed_codebook=True,
                archive_has_seed_microframe_codec=True,
                archive_has_seed_packed_codec=True,
                archive_has_seed_byteframe_codec=True,
            ),
            'exact_first_choice': packet.packet_seed_storage_exact_choice(standalone),
            'packed_seed_packet': packet.packet_packed_seed(standalone),
            'byte_seed_packet': packet.packet_byte_seed(standalone),
            'measured_repeat_frontier': packet.packet_repeat_storage_frontier(
                standalone,
                known_fingerprints,
                need_standalone_portability=False,
                archive_has_reference_codebook=True,
                archive_has_reference_microframe_codec=True,
                archive_has_reference_packed_codec=True,
                archive_has_reference_byteframe_codec=True,
            ),
            'exact_repeat_choice': packet.packet_repeat_storage_exact_choice(standalone, known_fingerprints),
            'packed_reference_packet': packet.packet_packed_reference(standalone, known_fingerprints),
            'byte_reference_packet': packet.packet_byte_reference(standalone, known_fingerprints),
            'zepto_first_write_plan': packet.packet_archive_zepto_write_plan(standalone, []),
            'zepto_repeat_write_plan': packet.packet_archive_zepto_write_plan(standalone, known_fingerprints),
        })

    return {
        'focus': 'replace measured frontier dependence in the live zepto writer with exact wrapper arithmetic on shared packed payloads and resolved reference prefixes',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'deterministic_mode_counts': dict(sorted(deterministic_mode_counts.items())),
        'deterministic_first_write_exact_match_count': deterministic_first_matches,
        'deterministic_repeat_exact_match_count': deterministic_repeat_matches,
        'deterministic_first_write_winner_counts': dict(sorted(deterministic_first_winners.items())),
        'deterministic_repeat_winner_counts': dict(sorted(deterministic_repeat_winners.items())),
        'deterministic_full_frontier_first_write_candidate_evaluations': len(deterministic_packets) * 6,
        'deterministic_exact_first_write_candidate_evaluations': len(deterministic_packets),
        'deterministic_full_frontier_repeat_candidate_evaluations': len(deterministic_packets) * 6,
        'deterministic_exact_repeat_candidate_evaluations': len(deterministic_packets),
        'random_weight_validation_count': len(random_weight_packets),
        'random_weight_exact_match_count': random_weight_matches,
        'random_weight_winner_counts': dict(sorted(random_weight_winners.items())),
        'random_coordinate_validation_count': len(random_coordinate_packets),
        'random_coordinate_exact_match_count': random_coordinate_matches,
        'random_coordinate_winner_counts': dict(sorted(random_coordinate_winners.items())),
        'synthetic_repeat_prefix_validation_count': len(prefix_lengths),
        'synthetic_repeat_prefix_exact_match_count': prefix_repeat_matches,
        'synthetic_repeat_prefix_winner_counts': dict(sorted(prefix_repeat_winners.items())),
        'headline_findings': {
            'main_rule': 'for first writes, choose exactly between packed_seed and byte_seed from the shared packed payload; for repeats, choose exactly between packed_reference and byte_reference from the resolved even-length prefix',
            'live_writer_dependency_removed': "the zepto writer no longer needs yesterday's measured frontier snapshot to justify today's codec choice",
            'deterministic_first_write_winners': dict(sorted(deterministic_first_winners.items())),
            'deterministic_repeat_winners': dict(sorted(deterministic_repeat_winners.items())),
            'random_coordinate_winners': dict(sorted(random_coordinate_winners.items())),
            'random_weight_winners': dict(sorted(random_weight_winners.items())),
            'synthetic_repeat_prefix_winners': dict(sorted(prefix_repeat_winners.items())),
        },
        'sample_rows': sorted(sample_rows, key=lambda row: row['name']),
        'repeat_prefix_rows': sorted(repeat_prefix_rows, key=lambda row: row['prefix_len']),
        'sources': [str(PACKET_PATH.relative_to(ROOT)), str(FRONTIER_BUILDER_PATH.relative_to(ROOT))],
    }


def _render_md(report: dict[str, object]) -> str:
    lines = [
        '# Rematch-Proxy Decision Packet Analytic-Frontier Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}.",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- deterministic first-write exact matches: `{report['deterministic_first_write_exact_match_count']}` / `{report['deterministic_frontier_packet_count']}`.",
        f"- deterministic repeat exact matches: `{report['deterministic_repeat_exact_match_count']}` / `{report['deterministic_frontier_packet_count']}`.",
        f"- deterministic first-write winners: `{json.dumps(report['deterministic_first_write_winner_counts'], sort_keys=True)}`.",
        f"- deterministic repeat winners: `{json.dumps(report['deterministic_repeat_winner_counts'], sort_keys=True)}`.",
        f"- random coordinate exact matches: `{report['random_coordinate_exact_match_count']}` / `{report['random_coordinate_validation_count']}` with winners `{json.dumps(report['random_coordinate_winner_counts'], sort_keys=True)}`.",
        f"- random weight exact matches: `{report['random_weight_exact_match_count']}` / `{report['random_weight_validation_count']}` with winners `{json.dumps(report['random_weight_winner_counts'], sort_keys=True)}`.",
        f"- synthetic repeat-prefix exact matches: `{report['synthetic_repeat_prefix_exact_match_count']}` / `{report['synthetic_repeat_prefix_validation_count']}` with winners `{json.dumps(report['synthetic_repeat_prefix_winner_counts'], sort_keys=True)}`.",
        f"- first-write candidate evaluations fall from `{report['deterministic_full_frontier_first_write_candidate_evaluations']}` under the full frontier to `{report['deterministic_exact_first_write_candidate_evaluations']}` under exact wrapper arithmetic.",
        f"- repeat candidate evaluations fall from `{report['deterministic_full_frontier_repeat_candidate_evaluations']}` under the full frontier to `{report['deterministic_exact_repeat_candidate_evaluations']}` under exact wrapper arithmetic.",
        '',
        '## Sample packet rows',
    ]
    for row in report['sample_rows']:
        lines.append(
            f"- `{row['name']}` (`{row['mode']}`): first-write exact `{row['exact_first_choice']['recommended_storage_form']}` from `{json.dumps(row['exact_first_choice']['candidate_minified_bytes'], sort_keys=True)}`; repeat exact `{row['exact_repeat_choice']['recommended_storage_form']}` from `{json.dumps(row['exact_repeat_choice']['candidate_minified_bytes'], sort_keys=True)}`; zepto writes `{row['zepto_first_write_plan']['recommended_write_kind']}` then `{row['zepto_repeat_write_plan']['recommended_write_kind']}`."
        )
    lines.extend(['', '## Synthetic repeat-prefix stress rows'])
    for row in report['repeat_prefix_rows']:
        lines.append(
            f"- prefix `{row['prefix_len']}` hex chars: exact repeat `{row['exact_choice']['recommended_storage_form']}` from `{json.dumps(row['exact_choice']['candidate_minified_bytes'], sort_keys=True)}`."
        )
    lines.extend(['', '## Sources', '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`', '- `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`'])
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
