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
RECEIPT_SCHEMA = ROOT / 'schemas' / 'cooperation_benchmark_card_freeze_receipt.schema.json'
EXAMPLE_JSON = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.json'
EXAMPLE_MD = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.md'
EXAMPLE_NEW = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example_v2.json'
EXAMPLE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'cooperation_benchmark_card_example.freeze_receipt.json'


def fail(msg: str) -> int:
    print(f'cooperation-benchmark-card-freeze-receipt: {msg}', file=sys.stderr)
    return 1



def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)



def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))



def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



def main() -> int:
    receipt_schema = load_json(RECEIPT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)

    snapshot = load_json(EXAMPLE_RECEIPT)
    jsonschema.validate(snapshot, receipt_schema)
    if snapshot.get('claim_ready') is not True:
        return fail('expected example freeze receipt to be claim_ready=true')
    expected_pairs = {
        'card_path': EXAMPLE_JSON,
        'rendered_markdown_path': EXAMPLE_MD,
        'card_schema_path': CARD_SCHEMA,
        'freeze_tool_path': TOOL,
    }
    for field, path in expected_pairs.items():
        if snapshot.get(field) != path.relative_to(ROOT).as_posix():
            return fail(f'{field} mismatch in example freeze receipt')
    hash_pairs = {
        'card_sha256': EXAMPLE_JSON,
        'rendered_markdown_sha256': EXAMPLE_MD,
        'card_schema_sha256': CARD_SCHEMA,
        'freeze_tool_sha256': TOOL,
    }
    for field, path in hash_pairs.items():
        if snapshot.get(field) != sha256_file(path):
            return fail(f'{field} does not match current file contents for {path.relative_to(ROOT)}')

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        rendered = tmpdir / 'card.md'
        receipt = tmpdir / 'card.freeze_receipt.json'
        proc = run(
            'python3', str(TOOL), 'freeze', str(EXAMPLE_JSON),
            '--render-output', str(rendered),
            '--receipt-output', str(receipt),
        )
        if proc.returncode != 0:
            return fail(f'freeze command failed: {proc.stderr.strip()}')
        if rendered.read_text(encoding='utf-8') != EXAMPLE_MD.read_text(encoding='utf-8'):
            return fail('freeze render output drift detected against canonical markdown example')
        live_receipt = load_json(receipt)
        jsonschema.validate(live_receipt, receipt_schema)
        if live_receipt.get('card_sha256') != sha256_file(EXAMPLE_JSON):
            return fail('freeze command produced unexpected card hash')
        if live_receipt.get('rendered_markdown_sha256') != sha256_file(rendered):
            return fail('freeze command produced unexpected render hash')
        if 'claim-ready' not in proc.stdout:
            return fail('expected freeze output to mention claim-ready status')

        guarded_render = tmpdir / 'card_v2.md'
        guarded_receipt = tmpdir / 'card_v2.freeze_receipt.json'
        guarded = run(
            'python3', str(TOOL), 'freeze', str(EXAMPLE_NEW),
            '--require-current-operational-head',
            '--render-output', str(guarded_render),
            '--receipt-output', str(guarded_receipt),
        )
        if guarded.returncode != 0:
            return fail(f'guarded freeze command failed: {guarded.stderr.strip()}')
        guarded_payload = load_json(guarded_receipt)
        guard = guarded_payload.get('lineage_guard')
        if not isinstance(guard, dict):
            return fail('expected guarded freeze receipt to retain lineage_guard')
        if guard.get('guard_kind') != 'require_unique_operational_head':
            return fail('unexpected guard_kind in guarded freeze receipt')
        stale = run(
            'python3', str(TOOL), 'freeze', str(EXAMPLE_JSON),
            '--require-current-operational-head',
            '--render-output', str(tmpdir / 'stale.md'),
            '--receipt-output', str(tmpdir / 'stale.freeze_receipt.json'),
        )
        if stale.returncode == 0:
            return fail('expected guarded freeze to fail on stale non-head card')

    print('cooperation-benchmark-card-freeze-receipt: ok')
    print(f'cooperation-benchmark-card-freeze-receipt: validated {EXAMPLE_RECEIPT.relative_to(ROOT)} and live freeze output')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
