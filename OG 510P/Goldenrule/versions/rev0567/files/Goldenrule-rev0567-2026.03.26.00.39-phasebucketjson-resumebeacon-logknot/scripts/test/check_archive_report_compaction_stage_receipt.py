#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'archive_report_compaction_stage_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_stage_receipt.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_archive_report_compaction_stage_receipt.py'
MANIFEST = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_manifest_receipt.json'
REHEARSAL = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_rehearsal_receipt.json'


def fail(msg: str) -> int:
    print(f'archive-report-compaction-stage-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCHEMA, EXAMPLE, TOOL, MANIFEST, REHEARSAL]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    schema = load_json(SCHEMA)
    if schema.get('title') != 'Archive Report Compaction Stage Receipt':
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
    if receipt['status_counts'] != {'passed_check_count': 15, 'total_check_count': 15, 'ready_to_cite': True}:
        return fail('unexpected status counts')
    if receipt['compaction_manifest_receipt_path'] != 'examples/snapshots/archive_report_compaction_manifest_receipt.json':
        return fail('expected manifest receipt path to point at the standing compaction manifest example')
    if receipt['compaction_rehearsal_receipt_path'] != 'examples/snapshots/archive_report_compaction_rehearsal_receipt.json':
        return fail('expected rehearsal receipt path to point at the standing compaction rehearsal example')
    rows = receipt['stage_manifest']
    metrics = receipt['summary_metrics']
    if metrics['stage_family_count'] != len(rows):
        return fail('stage family count should match the stage manifest length')
    if metrics['stage_file_count'] != sum(int(row['exact_report_file_count']) for row in rows):
        return fail('stage file count should match the stage manifest exactly')
    if metrics['stage_raw_bytes'] != sum(int(row['raw_bytes']) for row in rows):
        return fail('stage bytes should match the stage manifest exactly')
    if any((ROOT / path).exists() for row in rows for path in row['stage_paths']):
        return fail('stage paths should remain absent on the package-ready tree')
    print('archive-report-compaction-stage-receipt: ok '
          f'({len(rows)} reversible stage rows rebuild-match the current manifest and rehearsal pair)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
