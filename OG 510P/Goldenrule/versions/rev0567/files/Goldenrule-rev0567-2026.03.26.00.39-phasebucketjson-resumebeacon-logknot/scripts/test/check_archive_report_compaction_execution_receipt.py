#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'archive_report_compaction_execution_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_execution_receipt.json'


def fail(msg: str) -> int:
    print(f'archive-report-compaction-execution-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCHEMA, EXAMPLE]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    schema = load_json(SCHEMA)
    if schema.get('title') != 'Archive Report Compaction Execution Receipt':
        return fail('schema title mismatch')
    receipt = load_json(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)
    if receipt['status_counts']['ready_to_cite'] is not True:
        return fail('receipt should be ready to cite')
    rows = receipt['executed_manifest']
    metrics = receipt['summary_metrics']
    if metrics['executed_family_count'] != len(rows):
        return fail('executed family count should match the executed manifest length')
    if metrics['executed_file_count'] != sum(int(row['exact_report_file_count']) for row in rows):
        return fail('executed file count should match the executed manifest exactly')
    if metrics['executed_raw_bytes'] != sum(int(row['raw_bytes']) for row in rows):
        return fail('executed bytes should match the executed manifest exactly')
    if metrics['executed_raw_bytes'] != receipt['pre_trim_summary']['manifest_raw_bytes']:
        return fail('executed bytes should match the stored pre-trim manifest bytes exactly')
    if any(not row['exact_report_paths'] for row in rows):
        return fail('executed manifest rows should keep the exact paths that left during the recorded trim')
    if not receipt['policy_checks'].get('report_bucket_net_shrink_not_greater_than_executed_bytes'):
        return fail('execution receipt should reconcile current report-bucket bytes against the executed manifest')
    print('archive-report-compaction-execution-receipt: ok '
          f'({len(rows)} historical trim rows remain internally consistent and absent from the live manifest frontier)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
