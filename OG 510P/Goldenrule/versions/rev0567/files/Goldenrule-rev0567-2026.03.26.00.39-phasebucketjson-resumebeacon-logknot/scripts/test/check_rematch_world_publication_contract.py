#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_publication_contract.schema.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
EXPECTED_QUESTIONS = [f'SQ-0{i}' for i in range(12, 27)]
SECTION_EXPECTED = {
    'world_semantics_contract': ['SQ-012'],
    'matching_state_contract': ['SQ-013'],
    'occupancy_accounting_contract': ['SQ-014'],
    'turnover_tempo_contract': ['SQ-015'],
    'paired_ranking_views_contract': ['SQ-016'],
    'compact_decision_bundle': [f'SQ-0{i}' for i in range(17, 27)],
}


def fail(msg: str) -> int:
    print(f'rematch-world-publication-contract: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    if not REPORT_PATH.exists():
        return fail(f'missing {REPORT_PATH.relative_to(ROOT)}')
    if not SCHEMA_PATH.exists():
        return fail(f'missing {SCHEMA_PATH.relative_to(ROOT)}')
    if not DECISION_CONTRACT_PATH.exists():
        return fail(f'missing {DECISION_CONTRACT_PATH.relative_to(ROOT)}')

    report = load_json(REPORT_PATH)
    schema = load_json(SCHEMA_PATH)
    decision = load_json(DECISION_CONTRACT_PATH)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(report, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid schema: {exc.message}')

    if report.get('gap_id') != 'SG-003':
        return fail('unexpected gap_id')

    question_ids = [row['question_id'] for row in report['question_rows']]
    if question_ids != EXPECTED_QUESTIONS:
        return fail('question_rows must list SQ-012 through SQ-026 in order')

    counts = report['status_counts']
    if counts['schema_specified_and_validator_enforced'] != len(EXPECTED_QUESTIONS):
        return fail('expected all questions to be schema-specified and validator-enforced')
    if counts['world_benchmark_pending'] != len(EXPECTED_QUESTIONS):
        return fail('expected all questions to remain world-benchmark pending')
    if counts['newly_schema_specified_world_questions'] != 5:
        return fail('expected five newly schema-specified world questions')
    if counts['decision_bundle_questions'] != 10:
        return fail('expected ten compact decision bundle questions')

    decision_rows = {row['question_id']: row for row in decision['question_coverage']}
    for row in report['question_rows']:
        if not row['schema_specified'] or not row['validator_enforced']:
            return fail(f"{row['question_id']}: expected schema_specified and validator_enforced")
        if row['world_benchmark_emitted']:
            return fail(f"{row['question_id']}: world benchmark should still be pending")
        if row['contract_section'] == 'compact_decision_bundle':
            decision_row = decision_rows[row['question_id']]
            if row['minimal_fields'] != decision_row['minimal_fields']:
                return fail(f"{row['question_id']}: minimal_fields drift from decision contract")
            if row['source_artifacts'] != decision_row['source_reports']:
                return fail(f"{row['question_id']}: source_artifacts drift from decision contract")
        else:
            if len(row['source_artifacts']) < 1:
                return fail(f"{row['question_id']}: expected at least one source artifact")

    seen_sections = {}
    for row in report['section_rows']:
        sec = row['contract_section']
        seen_sections[sec] = row['question_ids']
        if row['question_ids'] != SECTION_EXPECTED[sec]:
            return fail(f'{sec}: unexpected question_ids')
        if row['question_count'] != len(SECTION_EXPECTED[sec]):
            return fail(f'{sec}: question_count mismatch')
        if row['world_benchmark_emitted']:
            return fail(f'{sec}: world benchmark should still be pending')
        if sec == 'compact_decision_bundle':
            if row.get('decision_contract_path') != 'artifacts/reports/rematch_decision_contract_snapshot_20260316.json':
                return fail('compact_decision_bundle should reference the standing decision contract')
    if set(seen_sections) != set(SECTION_EXPECTED):
        return fail('section_rows must cover the six publication sections exactly once')

    shape = report['publication_contract_shape']
    if shape['benchmark_kind'] != 'endogenous_rematch_world_publication_contract':
        return fail('unexpected benchmark_kind')
    if shape['required_sections'] != list(SECTION_EXPECTED):
        return fail('required_sections must match the six publication sections in order')
    if shape['resolves_question_count'] != len(EXPECTED_QUESTIONS):
        return fail('resolves_question_count mismatch')

    if 'one retained JSON artifact' not in report['recommended_next_move']:
        return fail('recommended_next_move should point to one retained JSON artifact emission')

    print(
        'rematch-world-publication-contract: ok '
        f"({len(EXPECTED_QUESTIONS)} questions, {len(SECTION_EXPECTED)} sections, world emission still pending)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
