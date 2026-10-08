#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_gap_retirement_rubric_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_gap_retirement_rubric.schema.json'
DECISION_CONTRACT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
EXPECTED_QUESTIONS = [f'SQ-0{i}' for i in range(17, 27)]
SECTION_EXPECTED = {
    'delay_contract': ['SQ-017', 'SQ-018'],
    'winner_contract': ['SQ-019', 'SQ-020', 'SQ-021'],
    'delta_contract': ['SQ-022', 'SQ-023', 'SQ-024', 'SQ-025', 'SQ-026'],
}


def fail(msg: str) -> int:
    print(f'rematch-gap-retirement-rubric: {msg}', file=sys.stderr)
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
    contract = load_json(DECISION_CONTRACT_PATH)

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
        return fail('question_rows must list SQ-017 through SQ-026 in order')

    if report['status_counts']['schema_specified_and_validator_enforced'] != len(EXPECTED_QUESTIONS):
        return fail('expected all questions to be schema-specified and validator-enforced')
    if report['status_counts']['proxy_emitted'] != len(EXPECTED_QUESTIONS):
        return fail('expected all questions to be proxy-emitted')
    if report['status_counts']['world_benchmark_pending'] != len(EXPECTED_QUESTIONS):
        return fail('expected all questions to remain world-benchmark pending')

    contract_rows = {row['question_id']: row for row in contract['question_coverage']}
    for row in report['question_rows']:
        if not row['schema_specified'] or not row['validator_enforced'] or not row['proxy_emitted']:
            return fail(f"{row['question_id']}: expected schema_specified, validator_enforced, and proxy_emitted")
        if row['world_benchmark_emitted']:
            return fail(f"{row['question_id']}: world benchmark should still be pending in current archive")
        contract_row = contract_rows[row['question_id']]
        if row['minimal_fields'] != contract_row['minimal_fields']:
            return fail(f"{row['question_id']}: minimal_fields drift from decision contract")
        if row['source_reports'] != contract_row['source_reports']:
            return fail(f"{row['question_id']}: source_reports drift from decision contract")

    seen_sections = {}
    for section in report['section_status']:
        sec = section['contract_section']
        seen_sections[sec] = section['question_ids']
        if section['question_ids'] != SECTION_EXPECTED[sec]:
            return fail(f'{sec}: unexpected question_ids')
        if section['question_count'] != len(SECTION_EXPECTED[sec]):
            return fail(f'{sec}: question_count mismatch')
        if section['world_benchmark_emitted']:
            return fail(f'{sec}: world benchmark should still be pending')
    if set(seen_sections) != set(SECTION_EXPECTED):
        return fail('section_status must cover delay_contract, winner_contract, and delta_contract')

    size = report['archive_size_reason']
    if size['component_report_total_bytes'] != contract['component_report_total_bytes']:
        return fail('component_report_total_bytes mismatch with decision contract')
    if size['bundle_json_bytes'] != contract['bundle_json_bytes']:
        return fail('bundle_json_bytes mismatch with decision contract')
    if size['bundle_vs_components_raw_byte_ratio'] != contract['bundle_vs_components_raw_byte_ratio']:
        return fail('bundle_vs_components_raw_byte_ratio mismatch with decision contract')

    if 'world benchmark emission' not in report['recommended_next_move']:
        return fail('recommended_next_move should point to world benchmark emission')

    print(
        'rematch-gap-retirement-rubric: ok '
        f"({len(question_ids)} questions, {report['status_counts']['world_benchmark_pending']} still need world emission)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
