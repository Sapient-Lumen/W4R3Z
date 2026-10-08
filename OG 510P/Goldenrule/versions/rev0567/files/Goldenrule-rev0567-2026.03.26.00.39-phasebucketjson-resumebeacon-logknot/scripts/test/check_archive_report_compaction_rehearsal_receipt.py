#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'archive_report_compaction_rehearsal_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_rehearsal_receipt.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_archive_report_compaction_rehearsal_receipt.py'
PACKAGE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
MANIFEST = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_manifest_receipt.json'


def fail(msg: str) -> int:
    print(f'archive-report-compaction-rehearsal-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCHEMA, EXAMPLE, TOOL, PACKAGE, MANIFEST]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    schema = load_json(SCHEMA)
    if schema.get('title') != 'Archive Report Compaction Rehearsal Receipt':
        return fail('schema title mismatch')
    receipt = load_json(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)
    proc = subprocess.run([sys.executable, str(TOOL), '--strict'], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    live = load_json(EXAMPLE)
    if receipt != live:
        return fail('example receipt should match the current live tool output exactly')
    if receipt['status_counts'] != {'passed_check_count': 11, 'total_check_count': 11, 'ready_to_cite': True}:
        return fail('unexpected status counts')
    if receipt['package_receipt_path'] != 'examples/snapshots/rematch_world_benchmark_package_receipt.json':
        return fail('expected package receipt path to point at the standing package receipt example')
    if receipt['compaction_manifest_receipt_path'] != 'examples/snapshots/archive_report_compaction_manifest_receipt.json':
        return fail('expected manifest receipt path to point at the standing compaction manifest example')
    metrics = receipt['summary_metrics']
    frontier = receipt['projected_next_frontier']
    manifest = load_json(MANIFEST)
    if metrics['trimmed_family_count'] != len(manifest['trim_manifest']):
        return fail('trimmed family count should match the standing manifest receipt')
    if metrics['trimmed_file_count'] != sum(int(row['exact_report_file_count']) for row in manifest['trim_manifest']):
        return fail('trimmed file count should match the standing manifest receipt')
    if metrics['trimmed_raw_bytes'] != int(manifest['summary_metrics']['manifest_raw_bytes']):
        return fail('trimmed bytes should match the standing manifest receipt exactly')
    if metrics['projected_frontier_family_count'] != len(frontier):
        return fail('projected frontier family count should match the projected frontier table length')
    if metrics['projected_frontier_gap_count'] != sum(1 for row in frontier if row['projected_compaction_readiness'] == 'handle_gap'):
        return fail('projected frontier gap count should match the projected frontier table')
    print('archive-report-compaction-rehearsal-receipt: ok '
          f'({len(frontier)} projected next-frontier rows rebuild-match the current manifest rehearsal)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
