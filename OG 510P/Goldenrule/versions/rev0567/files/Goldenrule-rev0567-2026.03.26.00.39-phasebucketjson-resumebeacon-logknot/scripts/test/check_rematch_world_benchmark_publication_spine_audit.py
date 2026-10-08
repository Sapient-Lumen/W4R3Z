#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_publication_spine_audit.schema.json'
EXAMPLE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_spine_audit_receipt.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'audit_rematch_world_benchmark_publication_spine.py'


def fail(msg: str) -> int:
    print(f'publication-spine-audit: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    if not SCHEMA_PATH.exists():
        return fail(f'missing {SCHEMA_PATH.relative_to(ROOT)}')
    if not EXAMPLE_PATH.exists():
        return fail(f'missing {EXAMPLE_PATH.relative_to(ROOT)}')

    schema = load_json(SCHEMA_PATH)
    receipt = load_json(EXAMPLE_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    if not receipt['publication_spine_ready']:
        return fail('expected publication_spine_ready=true for retained example spine')
    if receipt['retained_preflight_status']['blocking_fill_slot_count'] != 0:
        return fail('expected zero blocking fill slots in retained preflight status')
    if receipt['retained_preflight_status']['forbidden_changed_path_count'] != 0:
        return fail('expected zero forbidden changed paths in retained preflight status')
    if receipt['retained_preflight_status']['allowed_decision_null_count'] != 3:
        return fail('expected three allowed decision nulls in retained preflight status')
    if not all(receipt['checks'].values()):
        return fail('expected all audit checks to pass for retained example spine')
    if receipt['retained_bytes']['durable_spine_bytes'] <= receipt['retained_bytes']['bundle_receipt_bytes']:
        return fail('durable spine should be larger than the compact bundle receipt')

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / 'audit_receipt.json'
        proc = subprocess.run(
            [sys.executable, str(TOOL_PATH), '--output', str(out_path), '--strict'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'cli strict mode failed: {proc.stderr or proc.stdout}')
        if not out_path.exists():
            return fail('expected audit receipt output to be written')
        emitted = load_json(out_path)
        if emitted != receipt:
            return fail('strict CLI output drifted from retained example audit receipt')

    print('publication-spine-audit: ok (retained publication spine now has a deterministic rebuild audit receipt)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
