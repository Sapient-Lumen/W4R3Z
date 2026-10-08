#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
AUDIT_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_post_prune_audit_receipt.json'
PRUNE_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_prune_execute_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_post_prune_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_post_prune_snapshot_20260316.md'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_post_prune_audit_receipt.schema.json'


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 6)


def build_snapshot() -> dict[str, Any]:
    audit_receipt = json.loads(AUDIT_RECEIPT_PATH.read_text(encoding='utf-8'))
    prune_receipt = json.loads(PRUNE_RECEIPT_PATH.read_text(encoding='utf-8'))
    counts = audit_receipt['counts']
    durable_bytes = sum(int(row['byte_count']) for row in audit_receipt['durable_rows'])
    findings = [
        (
            f"The post-prune audit proves the cleaned example tree is safe to zip: {counts['durable_hash_match_count']} durable objects still hash-match while {counts['transient_absent_or_unlinked_count']} transient rows are absent or already unlinked."
        ),
        (
            f"The execute-mode prune receipt deleted {prune_receipt['counts']['deleted_count']} transient files totaling {prune_receipt['counts']['removed_bytes']} bytes ({_mib(int(prune_receipt['counts']['removed_bytes']))} MiB) before the audit confirmed the durable publication spine remained intact."
        ),
        (
            f"The durable publication spine now dominates the cleaned example surface at {durable_bytes} bytes ({_mib(durable_bytes)} MiB), which means the next revision zip can be cut without carrying the reconstructed patch or scratch sources forward by inertia."
        ),
    ]
    return {
        'focus': 'prove that a post-prune rematch-world tree is safe to zip by confirming the durable publication spine still hash-matches after transient cleanup',
        'snapshot_date': '2026-03-17',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_post_prune_snapshot.py',
        'audit_receipt_path': AUDIT_RECEIPT_PATH.relative_to(ROOT).as_posix(),
        'prune_receipt_path': PRUNE_RECEIPT_PATH.relative_to(ROOT).as_posix(),
        'audit_receipt': audit_receipt,
        'headline_findings': findings,
    }


def render_md(snapshot: dict[str, Any]) -> str:
    receipt = snapshot['audit_receipt']
    counts = receipt['counts']
    lines = [
        '# Rematch World Benchmark Post-Prune Snapshot',
        '',
        f"- snapshot_date: {snapshot['snapshot_date']}",
        f"- audit_receipt_path: `{snapshot['audit_receipt_path']}`",
        f"- prune_receipt_path: `{snapshot['prune_receipt_path']}`",
        f"- cleaned_tree_ready_for_zip: `{str(receipt['cleaned_tree_ready_for_zip']).lower()}`",
        '',
        '## Headline findings',
        '',
    ]
    for finding in snapshot['headline_findings']:
        lines.append(f'- {finding}')
    lines.extend([
        '',
        '## Audit counts',
        '',
        f"- durable objects: `{counts['durable_count']}`",
        f"- durable hash matches: `{counts['durable_hash_match_count']}`",
        f"- durable missing: `{counts['durable_missing_count']}`",
        f"- transient rows: `{counts['transient_count']}`",
        f"- transient absent or unlinked: `{counts['transient_absent_or_unlinked_count']}`",
        f"- transient still present: `{counts['transient_still_present_count']}`",
        f"- blocked rows: `{counts['blocked_count']}`",
        '',
        '## Durable publication spine rows',
        '',
        '| label | path | byte_count | status |',
        '|---|---|---:|---|',
    ])
    for row in receipt['durable_rows']:
        lines.append(f"| {row['label']} | `{row['path']}` | {row['byte_count']} | {row['status']} |")
    lines.extend([
        '',
        '## Exit-ready transient rows after prune',
        '',
        '| label | path | prune_status | status |',
        '|---|---|---|---|',
    ])
    for row in receipt['transient_rows']:
        path = '`' + row['path'] + '`' if row['path'] is not None else '`null`'
        lines.append(f"| {row['label']} | {path} | {row['prune_status']} | {row['status']} |")
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    snapshot = build_snapshot()
    schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(snapshot['audit_receipt'], schema)
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'rematch-world-benchmark-post-prune-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-post-prune-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
