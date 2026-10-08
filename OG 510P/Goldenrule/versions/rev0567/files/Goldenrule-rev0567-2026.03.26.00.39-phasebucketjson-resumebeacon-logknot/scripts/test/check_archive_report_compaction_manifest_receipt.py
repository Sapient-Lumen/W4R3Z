#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'archive_report_compaction_manifest_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_manifest_receipt.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_archive_report_compaction_manifest_receipt.py'
PACKAGE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
CANDIDATE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_candidate_receipt.json'


def fail(msg: str) -> int:
    print(f'archive-report-compaction-manifest-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCHEMA, EXAMPLE, TOOL, PACKAGE_RECEIPT, CANDIDATE_RECEIPT]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    schema = load_json(SCHEMA)
    if schema.get('title') != 'Archive Report Compaction Manifest Receipt':
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
    if receipt['status_counts'] != {'passed_check_count': 9, 'total_check_count': 9, 'ready_to_cite': True}:
        return fail('unexpected status counts')
    if receipt['package_receipt_path'] != 'examples/snapshots/rematch_world_benchmark_package_receipt.json':
        return fail('expected package receipt path to point at the standing package receipt example')
    if receipt['compaction_candidate_receipt_path'] != 'examples/snapshots/archive_report_compaction_candidate_receipt.json':
        return fail('expected candidate receipt path to point at the standing compaction candidate receipt example')
    rows = receipt['trim_manifest']
    metrics = receipt['summary_metrics']
    if metrics['manifest_family_count'] != len(rows):
        return fail('manifest family count should match the manifest table length')
    if metrics['manifest_file_count'] != sum(int(row['exact_report_file_count']) for row in rows):
        return fail('manifest file count should match the manifest table exactly')
    if metrics['manifest_raw_bytes'] != sum(int(row['raw_bytes']) for row in rows):
        return fail('manifest bytes should match the manifest table exactly')
    if metrics['manifest_rows_using_semantic_alias_count'] != sum(1 for row in rows if row['semantic_alias_used']):
        return fail('semantic-alias-backed manifest count should match the manifest table')
    print('archive-report-compaction-manifest-receipt: ok '
          f'({len(rows)} exact-file trim rows rebuild-match the current citation-backed compaction frontier)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
