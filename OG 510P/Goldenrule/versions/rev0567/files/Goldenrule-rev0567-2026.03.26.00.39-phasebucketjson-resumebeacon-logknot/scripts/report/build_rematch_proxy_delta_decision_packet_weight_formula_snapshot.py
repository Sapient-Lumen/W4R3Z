#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet.py'
FRONTIER_BUILDER_PATH = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_decision_packet_frontier_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_formula_snapshot_20260307.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_weight_formula_snapshot_20260307.md'


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _random_weight_packets(packet, count: int = 4096) -> list[dict[str, object]]:
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


def _sample_row(packet, row: dict[str, object]) -> dict[str, object]:
    standalone = row['packet']
    choice = packet.oracle_weight_seed_storage_choice(standalone)
    packed_seed = packet.packet_packed_seed(standalone)
    byte_seed = packet.packet_byte_seed(standalone)
    actual_packed_bytes = packet.packet_minified_bytes(packed_seed)
    actual_byte_bytes = packet.packet_minified_bytes(byte_seed)
    return {
        'name': row['name'],
        'semantic_fingerprint': packet.packet_semantic_fingerprint(standalone),
        'weights': standalone['evidence']['weights'],
        'payload_shape': choice['payload_shape'],
        'group_count': choice['group_count'],
        'active_axis_count': choice['active_axis_count'],
        'tied_storage_forms': choice['tied_storage_forms'],
        'recommended_storage_form': choice['recommended_storage_form'],
        'analytic_candidate_minified_bytes': choice['candidate_minified_bytes'],
        'actual_candidate_minified_bytes': {
            'packed_seed': actual_packed_bytes,
            'byte_seed': actual_byte_bytes,
        },
        'packed_seed_packet': packed_seed,
        'byte_seed_packet': byte_seed,
        'zepto_write_plan': packet.packet_archive_zepto_write_plan(standalone, []),
    }


def _build_summary() -> dict[str, object]:
    packet = _load_module(PACKET_PATH, 'rematch_proxy_delta_decision_packet')
    frontier_builder = _load_module(FRONTIER_BUILDER_PATH, 'frontier_snapshot')
    deterministic_packets = frontier_builder._frontier_test_packets(packet)
    deterministic_weight_packets = [row for row in deterministic_packets if row['packet']['mode'] == 'oracle_weights']
    random_weight_packets = _random_weight_packets(packet)

    deterministic_exact_count = 0
    deterministic_packed_wins = 0
    deterministic_byte_wins = 0
    deterministic_ties = 0
    for row in deterministic_weight_packets:
        standalone = row['packet']
        choice = packet.oracle_weight_seed_storage_choice(standalone)
        packed_bytes = packet.packet_minified_bytes(packet.packet_packed_seed(standalone))
        byte_bytes = packet.packet_minified_bytes(packet.packet_byte_seed(standalone))
        if choice['candidate_minified_bytes'] == {'packed_seed': packed_bytes, 'byte_seed': byte_bytes}:
            deterministic_exact_count += 1
        if choice['recommended_storage_form'] == 'packed_seed':
            deterministic_packed_wins += 1
        else:
            deterministic_byte_wins += 1
        if len(choice['tied_storage_forms']) > 1:
            deterministic_ties += 1

    random_exact_count = 0
    random_packed_wins = 0
    random_byte_wins = 0
    for row in random_weight_packets:
        standalone = row['packet']
        choice = packet.oracle_weight_seed_storage_choice(standalone)
        packed_bytes = packet.packet_minified_bytes(packet.packet_packed_seed(standalone))
        byte_bytes = packet.packet_minified_bytes(packet.packet_byte_seed(standalone))
        if choice['candidate_minified_bytes'] == {'packed_seed': packed_bytes, 'byte_seed': byte_bytes}:
            random_exact_count += 1
        if choice['recommended_storage_form'] == 'packed_seed':
            random_packed_wins += 1
        else:
            random_byte_wins += 1

    sample_names = ['weights_case_001', 'weights_case_025', 'weights_case_043', 'weights_case_049']
    sample_rows = [_sample_row(packet, next(row for row in deterministic_weight_packets if row['name'] == name)) for name in sample_names]

    old_first_write_seed_materializations = len(deterministic_packets) + len(deterministic_weight_packets)
    new_first_write_seed_materializations = len(deterministic_packets)
    materialization_savings = old_first_write_seed_materializations - new_first_write_seed_materializations

    return {
        'focus': 'Replace the last live measured first-write branch for oracle_weights with exact payload-byte formulas, so the writer can choose between packed_seed and byte_seed without materializing both candidates.',
        'packet_script': str(PACKET_PATH.relative_to(ROOT)),
        'deterministic_frontier_packet_count': len(deterministic_packets),
        'deterministic_weight_packet_count': len(deterministic_weight_packets),
        'deterministic_formula_exact_count': deterministic_exact_count,
        'deterministic_winner_counts': {
            'packed_seed': deterministic_packed_wins,
            'byte_seed': deterministic_byte_wins,
        },
        'deterministic_tie_count': deterministic_ties,
        'random_weight_validation_count': len(random_weight_packets),
        'random_formula_exact_count': random_exact_count,
        'random_winner_counts': {
            'packed_seed': random_packed_wins,
            'byte_seed': random_byte_wins,
        },
        'headline_findings': {
            'main_rule': 'for oracle_weights first writes, compute the packed_seed and byte_seed minified-byte counts from the packed payload shape itself, then materialize only the winner; repeats still go straight to byte_reference and non-weight first writes still go straight to byte_seed.',
            'deterministic_weight_winners': {'packed_seed': deterministic_packed_wins, 'byte_seed': deterministic_byte_wins},
            'deterministic_tie_count': deterministic_ties,
            'random_weight_winners': {'packed_seed': random_packed_wins, 'byte_seed': random_byte_wins},
            'old_first_write_seed_materializations': old_first_write_seed_materializations,
            'new_first_write_seed_materializations': new_first_write_seed_materializations,
            'first_write_seed_materializations_saved': materialization_savings,
            'first_write_seed_materialization_savings_share': round(materialization_savings / old_first_write_seed_materializations, 6),
        },
        'sample_weight_rows': sample_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'sources': [
            str(PACKET_PATH.relative_to(ROOT)),
            str(FRONTIER_BUILDER_PATH.relative_to(ROOT)),
        ],
    }


def _render_md(report: dict[str, object]) -> str:
    lines = [
        '# Rematch-Proxy Decision Packet Weight-Formula Snapshot (2026-03-07)',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- packet script: `{report['packet_script']}`.",
        f"- deterministic frontier packets: `{report['deterministic_frontier_packet_count']}`, of which `{report['deterministic_weight_packet_count']}` are `oracle_weights`.",
        f"- deterministic formula exactness: `{report['deterministic_formula_exact_count']}` / `{report['deterministic_weight_packet_count']}`.",
        f"- deterministic winners: `{json.dumps(report['deterministic_winner_counts'], sort_keys=True)}` with `{report['deterministic_tie_count']}` ties resolved toward `byte_seed`.",
        f"- random weight exactness: `{report['random_formula_exact_count']}` / `{report['random_weight_validation_count']}`.",
        f"- random winners: `{json.dumps(report['random_winner_counts'], sort_keys=True)}`.",
        f"- first-write seed materializations on the deterministic frontier: old compiled rule `{report['headline_findings']['old_first_write_seed_materializations']}` vs analytic rule `{report['headline_findings']['new_first_write_seed_materializations']}`, saving `{report['headline_findings']['first_write_seed_materializations_saved']}` (`{report['headline_findings']['first_write_seed_materialization_savings_share']}` share).",
        f"- main rule: {report['headline_findings']['main_rule']}",
        '',
        '## Representative oracle-weight cases',
    ]
    for row in report['sample_weight_rows']:
        lines.append(
            f"- `{row['name']}` -> winner `{row['recommended_storage_form']}`, shape `{row['payload_shape']}`, active axes `{row['active_axis_count']}`, groups `{row['group_count']}`, analytic bytes `{json.dumps(row['analytic_candidate_minified_bytes'], sort_keys=True)}`, actual bytes `{json.dumps(row['actual_candidate_minified_bytes'], sort_keys=True)}`."
        )
    lines.extend(
        [
            '',
            '## Sources',
            '- `scripts/analysis/rematch_proxy_delta_decision_packet.py`',
            '- `scripts/report/build_rematch_proxy_delta_decision_packet_frontier_snapshot.py`',
        ]
    )
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
