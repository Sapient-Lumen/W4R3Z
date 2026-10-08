#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'rematch_world_benchmark_package_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_package_receipt.py'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-package-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCHEMA, EXAMPLE, TOOL]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    schema = load_json(SCHEMA)
    if schema.get('title') != 'Rematch World Benchmark Package Receipt':
        return fail('schema title mismatch')

    receipt = load_json(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    proc = subprocess.run([sys.executable, str(TOOL), '--strict'], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    live_receipt = load_json(EXAMPLE)
    if receipt != live_receipt:
        return fail('example receipt should match the current live tool output exactly')
    if receipt['status_counts'] != {'package_ready': True, 'passed_check_count': 7, 'total_check_count': 7}:
        return fail('unexpected status counts')
    if receipt['policy_checks'] != {
        'publication_chain_ready': True,
        'post_prune_zip_ready': True,
        'compiled_artifact_digest_consistent': True,
        'pdf_free_tree': True,
        'scratch_tree_empty': True,
        'scratch_manifest_clear': True,
        'pycache_free_tree': True,
    }:
        return fail('unexpected policy checks')
    if receipt['measurement_scope']['excluded_output_path'] != 'examples/snapshots/rematch_world_benchmark_package_receipt.json':
        return fail('expected self-excluded output path to point at the standing package receipt example')
    if receipt['retention_hygiene']['pdf_file_count'] != 0:
        return fail('package receipt should confirm the tree is pdf-free')
    if receipt['retention_hygiene']['examples_scratch_file_count'] != 0:
        return fail('package receipt should confirm examples/scratch is empty')
    if receipt['report_growth_surface']['path'] != 'artifacts/reports':
        return fail('expected report growth surface path to be artifacts/reports')
    if receipt['archive_posture']['prefer_citation_over_recopy'] is not True:
        return fail('archive posture should prefer citation over recopy')

    print('rematch-world-benchmark-package-receipt: ok (package boundary stays chain-consistent, pdf-free, scratch-free, and size-profiled before the next zip)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
