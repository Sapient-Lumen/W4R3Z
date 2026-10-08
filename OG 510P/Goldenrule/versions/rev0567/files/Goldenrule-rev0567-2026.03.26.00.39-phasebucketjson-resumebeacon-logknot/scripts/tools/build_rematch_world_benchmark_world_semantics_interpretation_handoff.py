#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.json'
ROLE_NOTE_PATH = ROOT / 'docs' / 'LIBRARY' / 'topics' / 'rematch_role_assignment_is_a_first_class_contract.md'
INHERITOR_BRIEF_PATH = ROOT / 'docs' / 'LIBRARY' / 'topics' / 'golden_rule_inheritor_brief.md'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_world_semantics_interpretation_handoff.schema.json'
LINKED_QUESTION_IDS = ['SQ-012']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _question_row(publication_report: dict[str, Any]) -> dict[str, Any]:
    for row in publication_report['question_rows']:
        if row['question_id'] == 'SQ-012':
            return row
    raise KeyError('SQ-012 question row not found in publication contract snapshot')


def build_handoff(publication_report: dict[str, Any], role_note_text: str, inheritor_brief_text: str) -> dict[str, Any]:
    question_row = _question_row(publication_report)
    return {
        'contract_kind': 'rematch_world_benchmark_world_semantics_interpretation_handoff',
        'contract_version': '2026-03-17.rematch_world_benchmark_world_semantics_interpretation_handoff.v1',
        'planner_origin': 'copy the current SQ-012 world-semantics interpretation into the benchmark seed until native rematch worlds can emit explicit role-assignment and state-carry semantics directly',
        'publication_contract_report_path': 'artifacts/reports/rematch_world_publication_contract_snapshot_20260316.json',
        'publication_contract_report_sha256': sha256_json(publication_report),
        'role_assignment_note_path': 'docs/LIBRARY/topics/rematch_role_assignment_is_a_first_class_contract.md',
        'role_assignment_note_sha256': sha256_text(role_note_text),
        'inheritor_brief_path': 'docs/LIBRARY/topics/golden_rule_inheritor_brief.md',
        'inheritor_brief_sha256': sha256_text(inheritor_brief_text),
        'linked_question_ids': list(LINKED_QUESTION_IDS),
        'disclosure_boundary_summary': {
            'question_summary': question_row['question_summary'],
            'linked_assumption_summary': question_row['linked_assumption_summary'],
            'minimal_world_semantics_fields': list(question_row['minimal_fields']),
            'section_publication_fields': list(question_row['section_publication_fields']),
            'question_exit_gap': question_row['question_exit_gap'],
        },
        'role_semantics_interpretation': {
            'fixed_role_benchmark_required': True,
            'role_swapped_companion_required_when_asymmetry_is_in_play': True,
            'state_carry_disclosure_required': True,
            'seat_assignment_confound_warning': 'A policy can look fair in one seat and exploitative in the other, so seat assignment must be disclosed as world semantics rather than treated as an invisible engine default.',
            'conservative_handoff_posture': [
                'keep one explicit fixed-role benchmark',
                'keep one explicit role-swapped companion benchmark',
                'treat claims that change materially across those two runs as provisional rather than general',
            ],
        },
        'world_semantics_contract_guidance': {
            'required_world_section_fields': list(question_row['section_publication_fields']),
            'comparability_rule': 'Do not compare rematch-world results across worlds unless role assignment, asymmetry trigger, carry, reset, and role-swapped companion policies are all disclosed in the world semantics section.',
            'asymmetry_trigger_rule': 'Declare when role-swapped companion runs become mandatory instead of leaving seat symmetry implicit once asymmetric strategies or asymmetric environments are admitted.',
            'state_carry_rule': 'Declare which rematch-relevant state persists across partnership continuations and when new partners reset partnership-local memory so seat effects and carry effects are not conflated.',
            'provisional_claim_rule': question_row['linked_assumption_summary'],
        },
        'upgrade_requirement': 'Replace this copied world-semantics interpretation handoff with a native world-owned role/state-carry semantics section once endogenous rematch benchmarks emit explicit role policy, carry/reset policy, and companion-run triggers directly from real runs.',
        'size_discipline_note': 'Carry only the asymmetry trigger rule, the fixed-role versus swapped-role posture, and the required disclosure fields inside the benchmark seed; keep wider literature synthesis in the cited topic notes rather than copying it forward.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the compact world-semantics interpretation handoff section to copy into the rematch-world benchmark seed.')
    parser.add_argument('--publication-report', default=str(PUBLICATION_PATH), help='Path to the rematch-world publication contract snapshot JSON.')
    parser.add_argument('--role-note', default=str(ROLE_NOTE_PATH), help='Path to the role-assignment topic note.')
    parser.add_argument('--inheritor-brief', default=str(INHERITOR_BRIEF_PATH), help='Path to the inheritor brief topic note.')
    parser.add_argument('--output', help='Write the handoff JSON to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full handoff JSON.')
    args = parser.parse_args()

    def resolve(raw: str) -> Path:
        p = Path(raw)
        return p.resolve() if p.is_absolute() else (ROOT / p).resolve()

    publication_report = load_json(resolve(args.publication_report))
    role_note_text = resolve(args.role_note).read_text(encoding='utf-8')
    inheritor_brief_text = resolve(args.inheritor_brief).read_text(encoding='utf-8')
    handoff = build_handoff(publication_report, role_note_text, inheritor_brief_text)
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)

    if args.summary_json:
        summary = {
            'publication_contract_report_sha256': handoff['publication_contract_report_sha256'],
            'role_assignment_note_sha256': handoff['role_assignment_note_sha256'],
            'inheritor_brief_sha256': handoff['inheritor_brief_sha256'],
            'required_world_section_field_count': len(handoff['world_semantics_contract_guidance']['required_world_section_fields']),
            'role_swapped_companion_required_when_asymmetry_is_in_play': handoff['role_semantics_interpretation']['role_swapped_companion_required_when_asymmetry_is_in_play'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(handoff, indent=2, sort_keys=True) + '\n'
    if args.output:
        out = resolve(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding='utf-8')
        print(f'rematch-world-benchmark-world-semantics-interpretation-handoff: wrote {out.relative_to(ROOT).as_posix()}')
        return 0
    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
