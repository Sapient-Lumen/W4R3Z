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
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_evidence_receipt.schema.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_evidence_receipt.py'
SCRATCH_DIR = ROOT / 'examples' / 'scratch' / 'rematch_world_benchmark'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-evidence-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: object) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    for path in [PACKET_PATH, RECEIPT_PATH, SEED_PATH, SCHEMA_PATH, TOOL_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    packet = load_json(PACKET_PATH)
    receipt = load_json(RECEIPT_PATH)
    schema = load_json(SCHEMA_PATH)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(receipt, schema)
    except jsonschema.ValidationError as exc:
        return fail(f'receipt schema validation failed: {exc.message}')
    except jsonschema.SchemaError as exc:
        return fail(f'invalid receipt schema: {exc.message}')

    if receipt['packet_sha256'] != sha256_json(packet):
        return fail('packet_sha256 should match the canonical evidence packet digest')
    if not receipt['strict_coverage_passed']:
        return fail('example receipt should pass strict coverage')
    if receipt['missing_sections']:
        return fail('example receipt should not miss any benchmark sections')
    if receipt['scratch_source_count'] != len(receipt['scratch_sources']):
        return fail('scratch_source_count should match scratch_sources length')
    if receipt['packet_bytes'] != len(PACKET_PATH.read_bytes()):
        return fail('packet_bytes should match the stored example packet size')
    if len(PACKET_PATH.read_bytes()) + len(RECEIPT_PATH.read_bytes()) >= len(SEED_PATH.read_bytes()):
        return fail('packet plus receipt should stay smaller than the full retained seed')

    labels = {row['label'] for row in receipt['scratch_sources']}
    if labels != {'world_semantics_notes', 'policy_metrics_table', 'leaderboard_table'}:
        return fail(f'unexpected scratch source labels: {sorted(labels)}')

    with tempfile.TemporaryDirectory() as tmpdir:
        bad_out = Path(tmpdir) / 'bad_receipt.json'
        proc = subprocess.run(
            [
                sys.executable,
                str(TOOL_PATH),
                str(PACKET_PATH),
                '--scratch-source', f'world_semantics_notes={SCRATCH_DIR / "source_world_semantics.json"}',
                '--coverage', 'world_semantics_notes=world_semantics_contract',
                '--strict-coverage',
                '--output', str(bad_out),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return fail('strict coverage should fail when receipt coverage omits expected sections')

    print('rematch-world-benchmark-evidence-receipt: ok (packet-to-scratch provenance now has a retained compact receipt)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
