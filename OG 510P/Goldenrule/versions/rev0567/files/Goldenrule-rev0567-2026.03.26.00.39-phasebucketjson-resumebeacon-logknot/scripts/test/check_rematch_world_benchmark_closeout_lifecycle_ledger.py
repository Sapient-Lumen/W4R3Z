#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_closeout_lifecycle_ledger.py'
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_closeout_lifecycle_ledger.json'
DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md'


def fail(msg: str) -> int:
    print(f'rematch-world-benchmark-closeout-lifecycle-ledger: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in [SCRIPT, REPORT, DOC]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return fail(f'builder exited nonzero: {proc.stderr or proc.stdout}')

    report = load_json(REPORT)
    counts = report['lifecycle_counts']
    flags = report['status_flags']

    expected_counts = {
        'durable_retained_object_count': 6,
        'durable_retained_bytes': 93320,
        'closeout_receipt_count': 7,
        'closeout_receipt_bytes': 32301,
        'transient_exit_object_count': 4,
        'transient_exit_bytes': 3728,
        'transient_deleted_count': 1,
        'transient_already_absent_count': 3,
        'final_retained_object_count': 13,
        'final_retained_bytes': 125621,
    }
    if counts != expected_counts:
        return fail(f'unexpected lifecycle counts: {counts}')

    expected_flags = {
        'retention_exit_ready': False,
        'publication_spine_ready': True,
        'cleaned_tree_ready_for_zip': True,
        'overall_chain_ready': True,
        'package_ready': True,
    }
    if flags != expected_flags:
        return fail(f'unexpected status flags: {flags}')

    if len(report['durable_rows']) != 6:
        return fail('expected 6 durable rows')
    if len(report['transient_rows']) != 4:
        return fail('expected 4 transient rows')
    if len(report['closeout_receipt_rows']) != 7:
        return fail('expected 7 closeout receipt rows')
    if len(report['lifecycle_rows']) != 17:
        return fail('expected 17 total lifecycle rows')

    labels = {row['label'] for row in report['closeout_receipt_rows']}
    for label in [
        'frozen_handoff_audit_receipt',
        'copy_forward_audit_receipt',
        'retention_exit_receipt',
        'prune_execute_receipt',
        'post_prune_audit_receipt',
        'publication_chain_receipt',
        'package_receipt',
    ]:
        if label not in labels:
            return fail(f'missing closeout receipt row: {label}')

    text = DOC.read_text(encoding='utf-8')
    for needle in [
        '# Rematch-world benchmark closeout lifecycle ledger',
        '## Lifecycle counts',
        '## Durable publication set',
        '## Exit-ready transient surface',
        '## Closeout proof receipts',
        '## Exact lifecycle ledger',
    ]:
        if needle not in text:
            return fail(f'missing markdown section: {needle}')

    print('rematch-world-benchmark-closeout-lifecycle-ledger: ok (the rematch-world closeout now has one exact lifecycle ledger for durable objects, exit-ready transients, and the final authority receipts)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
