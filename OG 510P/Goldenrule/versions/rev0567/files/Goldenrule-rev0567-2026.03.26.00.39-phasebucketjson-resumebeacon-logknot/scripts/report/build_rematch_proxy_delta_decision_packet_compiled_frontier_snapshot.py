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
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compiled_frontier_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compiled_frontier_snapshot_20260307.md'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _random_weight_packets(packet, count: int = 1024) -> list[dict[str, object]]:
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


def _compile_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    random_weight_packets = _random_weight_packets(packet)
    known_fingerprints = [packet.packet_semantic_fingerprint(row['packet']) for row in deterministic_packets]

    deterministic_mode_counts = Counter(row['packet']['mode'] for row in deterministic_packets)
    deterministic_body_winners = Counter()
    deterministic_repeat_winners = Counter()
    deterministic_body_candidate_evals = 0
    deterministic_compiled_body_candidate_evals = 0
    deterministic_repeat_candidate_evals = 0
    deterministic_compiled_repeat_candidate_evals = 0
    deterministic_exact_matches = 0
    deterministic_repeat_exact_matches = 0

    sample_rows: list[dict[str, object]] = []
    sample_names = {
        'coordinates_0.0001_1',
        'weights_case_001',
        'weights_case_043',
        'exact_checked_cap_STS',
    }

    for row in deterministic_packets:
        standalone = row['packet']
        name = row['name']
        body_frontier = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        compiled_body = packet.packet_body_storage_compiled_frontier(standalone)
        repeat_frontier = packet.packet_repeat_storage_frontier(
            standalone,
            known_fingerprints,
            need_standalone_portability=False,
            archive_has_reference_codebook=True,
            archive_has_reference_microframe_codec=True,
            archive_has_reference_packed_codec=True,
            archive_has_reference_byteframe_codec=True,
        )
        compiled_repeat = packet.packet_repeat_storage_compiled_frontier(standalone, known_fingerprints)

        deterministic_body_winners[body_frontier['recommended_storage_form']] += 1
        deterministic_repeat_winners[repeat_frontier['recommended_storage_form']] += 1
        deterministic_body_candidate_evals += len(body_frontier['candidate_minified_bytes'])
        deterministic_compiled_body_candidate_evals += compiled_body['candidate_evaluation_count']
        deterministic_repeat_candidate_evals += len(repeat_frontier['candidate_minified_bytes'])
        deterministic_compiled_repeat_candidate_evals += compiled_repeat['candidate_evaluation_count']

        if body_frontier['recommended_storage_form'] == compiled_body['recommended_storage_form']:
            deterministic_exact_matches += 1
        if repeat_frontier['recommended_storage_form'] == compiled_repeat['recommended_storage_form']:
            deterministic_repeat_exact_matches += 1

        if name in sample_names:
            sample_rows.append(
                {
                    'name': name,
                    'mode': standalone['mode'],
                    'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
                    'body_frontier': body_frontier,
                    'compiled_body_frontier': compiled_body,
                    'repeat_frontier': repeat_frontier,
                    'compiled_repeat_frontier': compiled_repeat,
                    'packed_seed_bytes': packet.packet_minified_bytes(packet.packet_packed_seed(standalone)),
                    'byte_seed_bytes': packet.packet_minified_bytes(packet.packet_byte_seed(standalone)),
                    'byte_reference_bytes': packet.packet_minified_bytes(packet.packet_byte_reference(standalone, known_fingerprints)),
                    'zepto_write_plan': packet.packet_archive_zepto_write_plan(standalone, []),
                    'zepto_repeat_write_plan': packet.packet_archive_zepto_write_plan(standalone, known_fingerprints),
                }
            )

    random_weight_exact_matches = 0
    random_weight_packed_wins = 0
    random_weight_byte_wins = 0
    for row in random_weight_packets:
        standalone = row['packet']
        body_frontier = packet.packet_body_storage_frontier(
            standalone,
            need_standalone_portability=False,
            archive_has_core_expander=True,
            archive_has_seed_codebook=True,
            archive_has_seed_microframe_codec=True,
            archive_has_seed_packed_codec=True,
            archive_has_seed_byteframe_codec=True,
        )
        compiled_body = packet.packet_body_storage_compiled_frontier(standalone)
        if body_frontier['recommended_storage_form'] == compiled_body['recommended_storage_form']:
            random_weight_exact_matches += 1
        if compiled_body['recommended_storage_form'] == 'packed_seed':
            random_weight_packed_wins += 1
        elif compiled_body['recommended_storage_form'] == 'byte_seed':
            random_weight_byte_wins += 1

    body_eval_savings = deterministic_body_candidate_evals - deterministic_compiled_body_candidate_evals
    repeat_eval_savings = deterministic_repeat_candidate_evals - deterministic_compiled_repeat_candidate_evals

    return {
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'deterministic_mode_counts': dict(sorted(deterministic_mode_counts.items())),
        'deterministic_body_winner_counts': dict(sorted(deterministic_body_winners.items())),
        'deterministic_repeat_winner_counts': dict(sorted(deterministic_repeat_winners.items())),
        'deterministic_body_exact_match_count': deterministic_exact_matches,
        'deterministic_repeat_exact_match_count': deterministic_repeat_exact_matches,
        'deterministic_body_candidate_evaluations_full_frontier': deterministic_body_candidate_evals,
        'deterministic_body_candidate_evaluations_compiled_frontier': deterministic_compiled_body_candidate_evals,
        'deterministic_body_candidate_evaluation_savings': body_eval_savings,
        'deterministic_body_candidate_evaluation_savings_share': round(body_eval_savings / deterministic_body_candidate_evals, 6),
        'deterministic_repeat_candidate_evaluations_full_frontier': deterministic_repeat_candidate_evals,
        'deterministic_repeat_candidate_evaluations_compiled_frontier': deterministic_compiled_repeat_candidate_evals,
        'deterministic_repeat_candidate_evaluation_savings': repeat_eval_savings,
        'deterministic_repeat_candidate_evaluation_savings_share': round(repeat_eval_savings / deterministic_repeat_candidate_evals, 6),
        'random_weight_validation_count': len(random_weight_packets),
        'random_weight_exact_match_count': random_weight_exact_matches,
        'random_weight_compiled_packed_seed_wins': random_weight_packed_wins,
        'random_weight_compiled_byte_seed_wins': random_weight_byte_wins,
        'compiled_frontier_rule': {
            'first_write_any_mode': 'choose_by_exact_packed_vs_byte_byte_arithmetic',
            'repeat_write_any_mode': 'choose_by_exact_packed_vs_byte_byte_arithmetic',
        },
        'sample_packet_rows': sorted(sample_rows, key=lambda row: row['name']),
    }


def _render_md(report: dict[str, object]) -> str:
    lines = [
        '# Rematch-Proxy Decision Packet Compiled-Frontier Snapshot (2026-03-07)',
        '',
        '## Focus',
        '- Compile the measured zepto frontier into an exact shortlist rule so future writes do not have to re-evaluate every local codec candidate.',
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packet count: `{report['deterministic_frontier_packet_count']}`.",
        f"- deterministic body winners: `{json.dumps(report['deterministic_body_winner_counts'], sort_keys=True)}`.",
        f"- deterministic repeat winners: `{json.dumps(report['deterministic_repeat_winner_counts'], sort_keys=True)}`.",
        f"- deterministic body exact matches: `{report['deterministic_body_exact_match_count']}` / `{report['deterministic_frontier_packet_count']}`.",
        f"- deterministic repeat exact matches: `{report['deterministic_repeat_exact_match_count']}` / `{report['deterministic_frontier_packet_count']}`.",
        f"- deterministic body candidate evaluations: full frontier `{report['deterministic_body_candidate_evaluations_full_frontier']}` vs compiled frontier `{report['deterministic_body_candidate_evaluations_compiled_frontier']}`, saving `{report['deterministic_body_candidate_evaluation_savings']}` (`{report['deterministic_body_candidate_evaluation_savings_share']}` share).",
        f"- deterministic repeat candidate evaluations: full frontier `{report['deterministic_repeat_candidate_evaluations_full_frontier']}` vs compiled frontier `{report['deterministic_repeat_candidate_evaluations_compiled_frontier']}`, saving `{report['deterministic_repeat_candidate_evaluation_savings']}` (`{report['deterministic_repeat_candidate_evaluation_savings_share']}` share).",
        f"- random weight validation: `{report['random_weight_exact_match_count']}` / `{report['random_weight_validation_count']}` exact matches, with compiled winners `packed_seed={report['random_weight_compiled_packed_seed_wins']}` and `byte_seed={report['random_weight_compiled_byte_seed_wins']}`.",
        '- main rule: for zepto in-archive writes, choose between `packed_seed` and `byte_seed` for every first write by exact byte arithmetic on the shared packed payload, and choose between `packed_reference` and `byte_reference` for repeats by exact byte arithmetic on the resolved even-length prefix.',
        '',
        '## Representative compiled-frontier cases',
    ]
    for row in report['sample_packet_rows']:
        lines.append(
            f"- `{row['name']}` (`{row['mode']}`) -> measured first-write `{row['body_frontier']['recommended_storage_form']}`, compiled first-write `{row['compiled_body_frontier']['recommended_storage_form']}`, measured repeat `{row['repeat_frontier']['recommended_storage_form']}`, compiled repeat `{row['compiled_repeat_frontier']['recommended_storage_form']}`; packed seed `{row['packed_seed_bytes']}` bytes, byte seed `{row['byte_seed_bytes']}` bytes, byte reference `{row['byte_reference_bytes']}` bytes."
        )
    lines.extend(
        [
            '',
            '## Sources',
            '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
            '- `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`',
            '- `artifacts/reports/rematch_proxy_delta_decision_packet_frontier_snapshot_20260307.json`',
        ]
    )
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _compile_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
