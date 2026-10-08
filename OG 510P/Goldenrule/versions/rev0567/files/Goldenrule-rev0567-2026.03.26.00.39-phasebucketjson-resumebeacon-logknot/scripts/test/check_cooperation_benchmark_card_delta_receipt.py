#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'cooperation_benchmark_card.py'
CARD_SCHEMA = ROOT / 'schemas' / 'cooperation_benchmark_card.schema.json'
DELTA_SCHEMA = ROOT / 'schemas' / 'cooperation_benchmark_card_delta_receipt.schema.json'
EXAMPLE_OLD = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.json'
EXAMPLE_NEW = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example_v2.json'
EXAMPLE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.delta_receipt.json'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-delta-receipt: {msg}', file=sys.stderr)
    return 1



def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)



def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))



def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



def main() -> int:
    card_schema = load_json(CARD_SCHEMA)
    delta_schema = load_json(DELTA_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(card_schema)
    jsonschema.Draft202012Validator.check_schema(delta_schema)
    jsonschema.validate(load_json(EXAMPLE_OLD), card_schema)
    jsonschema.validate(load_json(EXAMPLE_NEW), card_schema)

    snapshot = load_json(EXAMPLE_RECEIPT)
    jsonschema.validate(snapshot, delta_schema)
    expected_pairs = {
        'old_card_path': EXAMPLE_OLD,
        'new_card_path': EXAMPLE_NEW,
        'delta_tool_path': TOOL,
    }
    for field, path in expected_pairs.items():
        if snapshot.get(field) != path.relative_to(ROOT).as_posix():
            return fail(f'{field} mismatch in example delta receipt')
    hash_pairs = {
        'old_card_sha256': EXAMPLE_OLD,
        'new_card_sha256': EXAMPLE_NEW,
        'delta_tool_sha256': TOOL,
    }
    for field, path in hash_pairs.items():
        if snapshot.get(field) != sha256_file(path):
            return fail(f'{field} does not match current file contents for {path.relative_to(ROOT)}')
    expected_claim_surface = {
        'evaluated_subject.evaluated_subject_provenance',
        'evaluated_subject.evaluation_window_snapshot_date',
        'evaluated_subject.update_drift_posture',
    }
    if set(snapshot.get('claim_surface_changed_field_paths', [])) != expected_claim_surface:
        return fail('example delta receipt should isolate the evaluated-subject claim-surface changes')
    if snapshot.get('claim_surface_changed') is not True:
        return fail('expected example delta receipt to mark claim_surface_changed=true')

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        receipt = tmpdir / 'card.delta_receipt.json'
        proc = run(
            'python3', str(TOOL), 'compare', str(EXAMPLE_OLD), str(EXAMPLE_NEW),
            '--receipt-output', str(receipt),
        )
        if proc.returncode != 0:
            return fail(f'compare command failed: {proc.stderr.strip()}')
        live = load_json(receipt)
        jsonschema.validate(live, delta_schema)
        if live != snapshot:
            return fail('live delta receipt drift detected against canonical example snapshot')
        if 'claim-surface=' not in proc.stdout:
            return fail('expected compare output to summarize claim-surface versus metadata-only changes')

    print('cooperation-benchmark-card-delta-receipt: ok')
    print(f'cooperation-benchmark-card-delta-receipt: validated {EXAMPLE_RECEIPT.relative_to(ROOT)} and live compare output')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
