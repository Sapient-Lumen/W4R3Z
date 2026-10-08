#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'rematch_world_benchmark_frozen_handoff_audit_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_frozen_handoff_audit_receipt.json'
TOOL = ROOT / 'scripts' / 'tools' / 'audit_rematch_world_benchmark_frozen_handoffs.py'
EXPECTED_ROWS = [
    ('canonicalization_planner_contract', 'examples/snapshots/rematch_world_benchmark_canonicalization_handoff.json'),
    ('winner_triage_handoff', 'examples/snapshots/rematch_world_benchmark_winner_triage_handoff.json'),
    ('delta_shortlist_handoff', 'examples/snapshots/rematch_world_benchmark_delta_shortlist_handoff.json'),
    ('paired_ranking_interpretation_handoff', 'examples/snapshots/rematch_world_benchmark_paired_ranking_interpretation_handoff.json'),
    ('matching_state_interpretation_handoff', 'examples/snapshots/rematch_world_benchmark_matching_state_interpretation_handoff.json'),
    ('turnover_tempo_interpretation_handoff', 'examples/snapshots/rematch_world_benchmark_turnover_tempo_interpretation_handoff.json'),
    ('world_semantics_interpretation_handoff', 'examples/snapshots/rematch_world_benchmark_world_semantics_interpretation_handoff.json'),
    ('compact_decision_bundle', 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json'),
]


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-frozen-handoff-audit: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCHEMA, EXAMPLE, TOOL]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    schema = load_json(SCHEMA)
    if schema.get('title') != 'Rematch World Benchmark Frozen Handoff Audit Receipt':
        return fail('schema title mismatch')

    receipt = load_json(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    proc = subprocess.run([sys.executable, str(TOOL), '--strict'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    live_receipt = json.loads(proc.stdout)

    if receipt != live_receipt:
        return fail('example receipt should match the current live tool output exactly')
    if receipt['rebuilt_seed_matches_standing_seed'] is not True:
        return fail('standing seed should rebuild-match exactly')
    if receipt['status_counts'] != {
        'audited_section_count': 8,
        'exact_match_count': 8,
        'mismatch_count': 0,
        'cited_source_path_count': 8,
    }:
        return fail('unexpected status counts')

    rows = [(row['section_path'], row['source_path']) for row in receipt['audited_sections']]
    if rows != EXPECTED_ROWS:
        return fail('audited sections mismatch')
    if any(row['exact_match'] is not True for row in receipt['audited_sections']):
        return fail('all audited sections should exact-match their source')
    if receipt['archive_posture']['prefer_citation_over_recopy'] is not True:
        return fail('archive posture should prefer citation over recopy')

    print('rematch-world-benchmark-frozen-handoff-audit: ok (8 audited sections, standing seed rebuild-matches current copied handoffs)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
