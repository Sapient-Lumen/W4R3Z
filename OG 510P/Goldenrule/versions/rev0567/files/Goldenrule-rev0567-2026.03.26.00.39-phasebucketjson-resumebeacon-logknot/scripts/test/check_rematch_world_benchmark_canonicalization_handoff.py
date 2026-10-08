#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_canonicalization_handoff.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_canonicalization_handoff.schema.json'
BRIDGE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_canonicalization_bridge_receipt.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_canonicalization_handoff.py'
SNAPSHOT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_canonicalization_handoff_snapshot_20260317.json'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-canonicalization-handoff: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [HANDOFF_PATH, SCHEMA_PATH, BRIDGE_PATH, TOOL_PATH, SNAPSHOT_JSON]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    handoff = load_json(HANDOFF_PATH)
    schema = load_json(SCHEMA_PATH)
    bridge = load_json(BRIDGE_PATH)
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

    bridge_mode_rows = bridge['planner_contract']['mode_rows']
    if len(handoff['mode_rows']) != len(bridge_mode_rows):
        return fail('handoff should preserve bridge mode count exactly')
    if handoff['zero_noise_dispatch_contract']['ordered_rule_count'] != bridge['zero_noise_classifier_contract']['ordered_rule_count']:
        return fail('handoff should preserve ordered rule count from bridge receipt')
    if handoff['bridge_receipt_sha256'] != summary['bridge_receipt_sha256']:
        return fail('handoff digest should match tool summary output')
    if snapshot['mode_count'] != len(handoff['mode_rows']):
        return fail('snapshot should report handoff mode count exactly')

    print('rematch-world-benchmark-canonicalization-handoff: ok (benchmark seed can carry a compact native planner handoff copied from the bridge receipt)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
