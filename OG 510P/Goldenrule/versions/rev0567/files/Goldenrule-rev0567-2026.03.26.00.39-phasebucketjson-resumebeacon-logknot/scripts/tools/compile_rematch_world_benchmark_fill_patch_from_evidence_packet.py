#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
PACKET_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_evidence_packet.schema.json'
PATCH_SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_fill_patch.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def build_fill_patch(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        'artifact_state': 'filled_benchmark',
        'benchmark_id': packet['benchmark_id'],
        'decision_contract_path': packet['decision_contract_path'],
        'matching_state_contract': {
            'comparability_note': packet['matching_observations']['comparability_note'],
            'matched_state_fields': list(packet['matching_observations']['matched_state_fields']),
            'matching_efficiency_model': packet['matching_observations']['matching_efficiency_model'],
            'rematch_delay_rounds': packet['matching_observations']['rematch_delay_rounds'],
            'search_state_fields': list(packet['matching_observations']['search_state_fields']),
        },
        'occupancy_accounting_contract': {
            'policy_rows': list(packet['occupancy_policy_rows']),
        },
        'paired_ranking_views_contract': {
            'leaderboard_rows': list(packet['leaderboard_rows']),
        },
        'patch_intent': 'fill only the mutable seed surface, then compile back to one retained benchmark artifact',
        'patch_version': '2026-03-16.rematch_world_benchmark_fill_patch.v1',
        'seed_artifact_path': 'examples/snapshots/rematch_world_benchmark_seed.json',
        'turnover_tempo_contract': {
            'policy_rows': list(packet['turnover_policy_rows']),
        },
        'world_semantics_contract': dict(packet['world_semantics_observations']),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Compile a tiny rematch-world evidence packet into the standard fill patch.')
    parser.add_argument('packet', nargs='?', default=str(DEFAULT_PACKET), help='Path to the rematch-world evidence packet JSON.')
    parser.add_argument('--output', help='Write the compiled fill patch to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the compiled fill patch.')
    args = parser.parse_args()

    packet_path = Path(args.packet)
    packet = load_json(packet_path)
    packet_schema = load_json(PACKET_SCHEMA_PATH)
    patch_schema = load_json(PATCH_SCHEMA_PATH)

    jsonschema.Draft202012Validator.check_schema(packet_schema)
    jsonschema.Draft202012Validator.check_schema(patch_schema)
    jsonschema.validate(packet, packet_schema)

    patch = build_fill_patch(packet)
    jsonschema.validate(patch, patch_schema)

    summary = {
        'packet_path': packet_path.resolve().relative_to(ROOT).as_posix() if packet_path.resolve().is_relative_to(ROOT) else str(packet_path),
        'packet_bytes': len(json.dumps(packet, indent=2, sort_keys=True).encode('utf-8')) + 1,
        'patch_bytes': len(json.dumps(patch, indent=2, sort_keys=True).encode('utf-8')) + 1,
        'compiled_policy_row_count': len(patch['occupancy_accounting_contract']['policy_rows']),
        'compiled_turnover_row_count': len(patch['turnover_tempo_contract']['policy_rows']),
        'compiled_leaderboard_row_count': len(patch['paired_ranking_views_contract']['leaderboard_rows']),
    }

    if args.summary_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(patch, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(
            'rematch-world-benchmark-evidence-packet: '
            f'wrote {output_path} ({summary["compiled_policy_row_count"]} occupancy rows, '
            f'{summary["compiled_turnover_row_count"]} turnover rows, '
            f'{summary["compiled_leaderboard_row_count"]} leaderboard rows)'
        )
        return 0

    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
