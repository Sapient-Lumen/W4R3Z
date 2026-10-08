#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_delta_shortlist_handoff.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_delta_shortlist_handoff.schema.json'
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_delta_shortlist_handoff.py'
SNAPSHOT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_delta_shortlist_handoff_snapshot_20260317.json'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-delta-shortlist-handoff: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [HANDOFF_PATH, SCHEMA_PATH, PUBLISHABILITY_PATH, DECISION_PATH, TOOL_PATH, SNAPSHOT_JSON]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    handoff = load_json(HANDOFF_PATH)
    schema = load_json(SCHEMA_PATH)
    publishability = load_json(PUBLISHABILITY_PATH)
    snapshot = load_json(SNAPSHOT_JSON)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(handoff, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid schema: {exc.message}')

    proc = subprocess.run(
        [sys.executable, str(TOOL_PATH), '--summary-json'],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    summary = json.loads(proc.stdout)

    strict_profile = next(row for row in publishability['guardrail_profiles'] if row['profile_name'] == 'family4_width0p0010_hazard1000_sub0p01')
    if len(handoff['primary_shortlist_rows']) != strict_profile['candidate_count']:
        return fail('handoff should preserve strict shortlist candidate count exactly')
    if handoff['declared_budget_family_caps'] != strict_profile['candidate_rows'][0]['covered_budget_caps']:
        return fail('handoff should preserve declared budget-family caps from the strict shortlist')
    if handoff['publishability_report_sha256'] != summary['publishability_report_sha256']:
        return fail('handoff digest should match tool summary output')
    if snapshot['primary_shortlist_count'] != len(handoff['primary_shortlist_rows']):
        return fail('snapshot should report shortlist count exactly')
    anchors = [row['shared_core_anchor_delta'] for row in handoff['primary_shortlist_rows']]
    if anchors != summary['primary_anchor_deltas']:
        return fail('summary anchor deltas should match the handoff rows exactly')

    print('rematch-world-benchmark-delta-shortlist-handoff: ok (benchmark seed can carry a compact publishable-delta shortlist copied from the strict proxy guardrail profile)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
