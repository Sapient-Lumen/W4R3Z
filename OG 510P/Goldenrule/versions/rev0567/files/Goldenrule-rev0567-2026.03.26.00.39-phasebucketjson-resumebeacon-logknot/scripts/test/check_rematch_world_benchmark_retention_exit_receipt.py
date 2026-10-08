#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_retention_exit_receipt.schema.json'
EXAMPLE_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_retention_exit_receipt.py'


def fail(msg: str) -> int:
    print(f'retention-exit-receipt: {msg}', file=sys.stderr)
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

    if len(receipt['durable_retained_objects']) != 6:
        return fail('expected six durable retained publication objects')
    if len(receipt['exit_ready_transient_objects']) != 4:
        return fail('expected four exit-ready transient objects (one patch + three scratch sources)')
    if receipt['exit_conditions']['retention_exit_ready']:
        if not all(row['exit_ready'] for row in receipt['exit_ready_transient_objects']):
            return fail('expected all transient objects to be exit-ready when the retained example is pre-prune ready')
    else:
        if receipt['exit_conditions']['scratch_hashes_match_receipt_now']:
            return fail('already-pruned retained example should mark scratch_hashes_match_receipt_now false')
        if any(row['exit_ready'] for row in receipt['exit_ready_transient_objects']):
            return fail('already-pruned retained example should mark transient rows non-exit-ready')
    if receipt['retained_byte_totals']['transient_exit_bytes'] <= 0:
        return fail('expected positive transient exit bytes')
    if receipt['retained_byte_totals']['retained_publication_set_bytes'] <= receipt['retained_byte_totals']['transient_exit_bytes']:
        return fail('expected retained publication set to outweigh transient exit bytes')

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / 'retention_exit_receipt.json'
        proc = subprocess.run(
            [sys.executable, str(TOOL_PATH), '--output', str(out_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'cli emit mode failed: {proc.stderr or proc.stdout}')
        if not out_path.exists():
            return fail('expected retention-exit receipt output to be written')
        emitted = load_json(out_path)
        jsonschema.validate(emitted, schema)
        if emitted == receipt:
            pass
        else:
            if emitted['durable_retained_objects'] != receipt['durable_retained_objects']:
                return fail('post-prune live receipt should preserve the durable retained publication set exactly')
            if len(emitted['exit_ready_transient_objects']) != len(receipt['exit_ready_transient_objects']):
                return fail('post-prune live receipt should preserve the transient object list shape')
            if emitted['exit_conditions']['scratch_hashes_match_receipt_now']:
                return fail('post-prune live receipt should mark scratch_hashes_match_receipt_now false after cleanup')
            if emitted['exit_conditions']['retention_exit_ready']:
                return fail('post-prune live receipt should not remain retention-exit-ready once scratch has already left the tree')
            if any(row['exit_ready'] for row in emitted['exit_ready_transient_objects']):
                return fail('post-prune live receipt should mark transient rows non-exit-ready because cleanup already occurred')

    print('retention-exit-receipt: ok (the retained example validates in either pre-prune or already-pruned form, and the live tool tolerates both states)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
