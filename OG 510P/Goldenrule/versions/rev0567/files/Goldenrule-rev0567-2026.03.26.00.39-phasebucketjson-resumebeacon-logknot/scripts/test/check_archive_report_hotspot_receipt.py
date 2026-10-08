#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'archive_report_hotspot_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'archive_report_hotspot_receipt.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_archive_report_hotspot_receipt.py'
PACKAGE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'


def fail(msg: str) -> int:
    print(f'archive-report-hotspot-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCHEMA, EXAMPLE, TOOL, PACKAGE_RECEIPT]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    schema = load_json(SCHEMA)
    if schema.get('title') != 'Archive Report Hotspot Receipt':
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
    if receipt['status_counts'] != {'passed_check_count': 4, 'total_check_count': 4, 'ready_to_cite': True}:
        return fail('unexpected status counts')
    if any(value is not True for value in receipt['policy_checks'].values()):
        return fail('all hotspot policy checks should pass')
    if receipt['measurement_scope']['excluded_output_path'] != 'examples/snapshots/archive_report_hotspot_receipt.json':
        return fail('expected self-excluded output path to point at the standing hotspot receipt example')
    if receipt['report_bucket_totals']['path'] != 'artifacts/reports':
        return fail('expected report bucket path to be artifacts/reports')
    if receipt['package_receipt_path'] != 'examples/snapshots/rematch_world_benchmark_package_receipt.json':
        return fail('expected package receipt path to point at the standing package receipt example')

    families = receipt['largest_report_families']
    files = receipt['largest_report_files']
    targets = receipt['priority_compaction_targets']
    raw_bytes = receipt['report_bucket_totals']['raw_bytes']
    family_names = {row['family'] for row in families}

    if raw_bytes == 0:
        if families != [] or files != [] or targets != []:
            return fail('expected empty hotspot tables when the measured report frontier is empty')
    else:
        if not families or not files:
            return fail('expected non-empty hotspot tables when the measured report frontier is non-empty')
        if any(row['family'] not in family_names for row in targets):
            return fail('priority compaction targets should name current hotspot families')

    print(
        'archive-report-hotspot-receipt: ok '
        f'({len(families)} hotspot families over {raw_bytes} raw bytes stay aligned with the standing package receipt)'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
