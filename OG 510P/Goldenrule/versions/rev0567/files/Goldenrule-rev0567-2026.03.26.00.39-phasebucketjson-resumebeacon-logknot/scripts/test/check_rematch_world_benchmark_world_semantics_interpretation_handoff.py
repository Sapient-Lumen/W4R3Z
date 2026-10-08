#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_world_semantics_interpretation_handoff.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_world_semantics_interpretation_handoff.schema.json'
PUBLICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_world_publication_contract_snapshot_20260316.json'
ROLE_NOTE_PATH = ROOT / 'docs' / 'LIBRARY' / 'topics' / 'rematch_role_assignment_is_a_first_class_contract.md'
INHERITOR_BRIEF_PATH = ROOT / 'docs' / 'LIBRARY' / 'topics' / 'golden_rule_inheritor_brief.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_world_semantics_interpretation_handoff.py'
SNAPSHOT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_semantics_interpretation_handoff_snapshot_20260317.json'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-world-semantics-interpretation-handoff: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: object) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def main() -> int:
    for path in [HANDOFF_PATH, SCHEMA_PATH, PUBLICATION_PATH, ROLE_NOTE_PATH, INHERITOR_BRIEF_PATH, TOOL_PATH, SNAPSHOT_JSON]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    handoff = load_json(HANDOFF_PATH)
    schema = load_json(SCHEMA_PATH)
    publication = load_json(PUBLICATION_PATH)
    snapshot = load_json(SNAPSHOT_JSON)
    role_note = ROLE_NOTE_PATH.read_text(encoding='utf-8')
    inheritor_brief = INHERITOR_BRIEF_PATH.read_text(encoding='utf-8')
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)
    proc = subprocess.run([sys.executable, str(TOOL_PATH), '--summary-json'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    summary = json.loads(proc.stdout)

    sq12 = next((row for row in publication['question_rows'] if row['question_id'] == 'SQ-012'), None)
    if sq12 is None:
        return fail('publication contract snapshot should contain SQ-012')
    if handoff['publication_contract_report_sha256'] != sha256_json(publication):
        return fail('handoff should preserve publication contract snapshot digest exactly')
    if handoff['role_assignment_note_sha256'] != sha256_text(role_note):
        return fail('handoff should preserve role-assignment note digest exactly')
    if handoff['inheritor_brief_sha256'] != sha256_text(inheritor_brief):
        return fail('handoff should preserve inheritor brief digest exactly')
    if handoff['disclosure_boundary_summary']['minimal_world_semantics_fields'] != sq12['minimal_fields']:
        return fail('handoff should preserve SQ-012 minimal world semantics fields exactly')
    if handoff['world_semantics_contract_guidance']['required_world_section_fields'] != sq12['section_publication_fields']:
        return fail('handoff should preserve SQ-012 section publication fields exactly')
    if not handoff['role_semantics_interpretation']['role_swapped_companion_required_when_asymmetry_is_in_play']:
        return fail('handoff should require role-swapped companions when asymmetry is in play')
    if summary['required_world_section_field_count'] != len(sq12['section_publication_fields']):
        return fail('tool summary should report world semantics field count exactly')
    if snapshot['minimal_world_semantics_field_count'] != len(sq12['minimal_fields']):
        return fail('snapshot should report minimal world-semantics field count exactly')
    print('rematch-world-benchmark-world-semantics-interpretation-handoff: ok (benchmark seed can carry a compact SQ-012 role/state-carry interpretation copied from the standing publication contract and topic notes)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
