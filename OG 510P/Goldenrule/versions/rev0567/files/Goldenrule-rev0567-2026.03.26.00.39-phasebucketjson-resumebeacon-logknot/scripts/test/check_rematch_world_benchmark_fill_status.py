#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_fill_status_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_fill_status.schema.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
EXPECTED_SECTION_COUNTS = {
    'benchmark_metadata': 1,
    'world_semantics_contract': 6,
    'matching_state_contract': 3,
    'occupancy_accounting_contract': 5,
    'turnover_tempo_contract': 4,
    'paired_ranking_views_contract': 5,
}
EXPECTED_ALLOWED_NULLS = [
    'compact_decision_bundle.delay_contract.extortion_rows[0].predicted_nonnegative_delay_winner_intervals[2].end_delay',
    'compact_decision_bundle.delay_contract.extortion_rows[1].predicted_nonnegative_delay_winner_intervals[2].end_delay',
    'compact_decision_bundle.delay_contract.extortion_rows[2].predicted_nonnegative_delay_winner_intervals[2].end_delay',
]

sys.path.insert(0, str(ROOT))
from scripts.tools.rematch_world_benchmark_completion_gate import load_json, summarize_completion_status  # noqa: E402


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-fill-status: {msg}', file=sys.stderr)
    return 1


def main() -> int:
    for path in [REPORT_PATH, SCHEMA_PATH, SEED_PATH, DECISION_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    report = load_json(REPORT_PATH)
    schema = load_json(SCHEMA_PATH)
    seed = load_json(SEED_PATH)
    decision = load_json(DECISION_PATH)
    summary = summarize_completion_status(seed, decision)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(report, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid schema: {exc.message}')

    if report['completion_ready']:
        return fail('seed-derived fill-status snapshot should not yet be completion_ready')

    counts = report['status_counts']
    expected_counts = summary['status_counts']
    for key, value in expected_counts.items():
        if counts[key] != value:
            return fail(f'status_counts[{key!r}] mismatch: expected {value}, found {counts[key]}')

    if counts['blocking_slot_count'] != 24:
        return fail('expected 24 fill blockers outside compact_decision_bundle')
    if counts['template_blocker_count'] != 13:
        return fail('expected 13 template-string blockers')
    if counts['null_blocker_count'] != 11:
        return fail('expected 11 null-fill blockers')
    if counts['world_section_status_pending_count'] != 5:
        return fail('expected all five world sections to remain pending_fill in the seed')
    if counts['allowed_decision_null_count'] != 3:
        return fail('expected three allowed open-ended decision nulls')

    by_section = {row['section']: row for row in report['section_rows']}
    if set(by_section) != set(EXPECTED_SECTION_COUNTS):
        return fail('section_rows must cover benchmark metadata plus the five world sections exactly once')
    for section, expected in EXPECTED_SECTION_COUNTS.items():
        row = by_section[section]
        if row['blocking_slot_count'] != expected:
            return fail(f'{section}: expected {expected} fill blockers')
        if section == 'benchmark_metadata' and row['status_transition_required']:
            return fail('benchmark_metadata should not require a section-status transition')
        if section != 'benchmark_metadata' and not row['status_transition_required']:
            return fail(f'{section}: expected status_transition_required')

    allowed_paths = [row['path'] for row in report['allowed_decision_null_rows']]
    if allowed_paths != EXPECTED_ALLOWED_NULLS:
        return fail('allowed_decision_null_rows drift from copied open-ended delay intervals')

    if '24 remaining seed slots' not in report['recommended_next_move']:
        return fail('recommended_next_move should mention the 24 remaining seed slots explicitly')

    print('rematch-world-benchmark-fill-status: ok (24 fill blockers, 3 allowed decision nulls, 5 pending section flips)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
