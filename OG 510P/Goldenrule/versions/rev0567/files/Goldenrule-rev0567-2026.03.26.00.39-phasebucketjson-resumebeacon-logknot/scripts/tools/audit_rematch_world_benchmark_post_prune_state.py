#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RETENTION_EXIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
DEFAULT_PRUNE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_prune_execute_receipt.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_post_prune_audit_receipt.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _resolve(path_value: str | None, root: Path) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    return path if path.is_absolute() else (root / path)


def _relativize(path: Path, root: Path) -> str:
    resolved = path.resolve()
    root_resolved = root.resolve()
    return resolved.relative_to(root_resolved).as_posix() if resolved.is_relative_to(root_resolved) else str(path)


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _sha256_json(node: Any) -> str:
    return _sha256_bytes(json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))


def _path_hash(path: Path) -> str:
    blob = path.read_bytes()
    direct = _sha256_bytes(blob)
    if path.suffix != '.json':
        return direct
    try:
        return _sha256_json(json.loads(blob.decode('utf-8')))
    except Exception:
        return direct


def build_post_prune_audit_receipt(
    retention_exit_receipt: dict[str, Any],
    retention_exit_receipt_path: Path,
    prune_receipt: dict[str, Any],
    prune_receipt_path: Path,
    *,
    root: Path,
) -> dict[str, Any]:
    counts = {
        'durable_count': len(retention_exit_receipt['durable_retained_objects']),
        'durable_hash_match_count': 0,
        'durable_missing_count': 0,
        'transient_count': len(prune_receipt['transient_rows']),
        'transient_absent_or_unlinked_count': 0,
        'transient_still_present_count': 0,
        'blocked_count': 0,
    }

    durable_rows: list[dict[str, Any]] = []
    for row in retention_exit_receipt['durable_retained_objects']:
        path = _resolve(row['path'], root)
        exists = bool(path and path.exists())
        actual_sha256 = _path_hash(path) if exists and path is not None else None
        hash_matches = bool(exists and actual_sha256 == row['sha256'])
        if hash_matches:
            counts['durable_hash_match_count'] += 1
            status = 'durable_hash_match'
        elif exists:
            counts['blocked_count'] += 1
            status = 'durable_hash_mismatch'
        else:
            counts['durable_missing_count'] += 1
            counts['blocked_count'] += 1
            status = 'missing_durable'
        durable_rows.append(
            {
                'label': row['label'],
                'path': _relativize(path, root) if path is not None else row['path'],
                'retention_class': row['retention_class'],
                'byte_count': int(row['byte_count']),
                'sha256': row['sha256'],
                'actual_sha256': actual_sha256,
                'exists': exists,
                'hash_matches': hash_matches,
                'status': status,
            }
        )

    prune_execute_ok = (
        prune_receipt['execution_mode'] == 'execute'
        and bool(prune_receipt['prune_ready'])
        and int(prune_receipt['counts']['blocked_count']) == 0
        and int(prune_receipt['counts']['would_delete_count']) == 0
    )
    if not prune_execute_ok:
        counts['blocked_count'] += 1

    transient_rows: list[dict[str, Any]] = []
    for row in prune_receipt['transient_rows']:
        path = _resolve(row['path'], root)
        if not prune_execute_ok:
            confirmed_absent = False
            status = 'blocked_prune_receipt'
            counts['blocked_count'] += 1
        elif path is None:
            confirmed_absent = True
            status = 'confirmed_unlinked_transient'
            counts['transient_absent_or_unlinked_count'] += 1
        elif path.exists():
            confirmed_absent = False
            status = 'still_present_after_prune'
            counts['transient_still_present_count'] += 1
            counts['blocked_count'] += 1
        else:
            confirmed_absent = True
            status = 'confirmed_absent_after_prune'
            counts['transient_absent_or_unlinked_count'] += 1
        transient_rows.append(
            {
                'label': row['label'],
                'path': _relativize(path, root) if path is not None else None,
                'retention_class': row['retention_class'],
                'prune_status': row['status'],
                'prune_action': row['action'],
                'confirmed_absent': confirmed_absent,
                'status': status,
            }
        )

    cleaned_tree_ready_for_zip = bool(
        prune_execute_ok
        and counts['durable_hash_match_count'] == counts['durable_count']
        and counts['transient_absent_or_unlinked_count'] == counts['transient_count']
        and counts['transient_still_present_count'] == 0
        and counts['blocked_count'] == 0
    )

    if cleaned_tree_ready_for_zip:
        recommended_next_move = (
            'Cut the next revision zip from this cleaned tree; the durable publication spine still hash-matches and every exit-ready transient covered by the prune receipt is now absent or already unlinked.'
        )
    else:
        recommended_next_move = (
            'Do not cut the next revision zip yet; rerun prune execution or repair the blocked durable/transient rows until the tree is clean and the durable publication spine still hash-matches.'
        )

    return {
        'snapshot_date': '2026-03-17',
        'receipt_version': '2026-03-17.rematch_world_benchmark_post_prune_audit_receipt.v1',
        'analysis_script': 'scripts/tools/audit_rematch_world_benchmark_post_prune_state.py',
        'focus': 'prove that a rematch-world tree is safe to zip after pruning by confirming the durable publication spine still hash-matches while every exit-ready transient is absent or already unlinked',
        'retention_exit_receipt_path': _relativize(retention_exit_receipt_path, root),
        'prune_receipt_path': _relativize(prune_receipt_path, root),
        'cleaned_tree_ready_for_zip': cleaned_tree_ready_for_zip,
        'prune_receipt_summary': {
            'execution_mode': prune_receipt['execution_mode'],
            'prune_ready': bool(prune_receipt['prune_ready']),
            'blocked_count': int(prune_receipt['counts']['blocked_count']),
            'would_delete_count': int(prune_receipt['counts']['would_delete_count']),
            'deleted_count': int(prune_receipt['counts']['deleted_count']),
        },
        'counts': counts,
        'durable_rows': durable_rows,
        'transient_rows': transient_rows,
        'recommended_next_move': recommended_next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit a post-prune rematch-world benchmark tree and confirm it is clean to zip while the durable publication spine still hash-matches.')
    parser.add_argument('retention_exit_receipt', nargs='?', default=str(DEFAULT_RETENTION_EXIT), help='Path to the retention-exit receipt JSON.')
    parser.add_argument('prune_receipt', nargs='?', default=str(DEFAULT_PRUNE_RECEIPT), help='Path to the execute-mode prune receipt JSON.')
    parser.add_argument('--root', default=str(ROOT), help='Root used to resolve receipt-relative paths. Defaults to the repository root.')
    parser.add_argument('--output', help='Write the post-prune audit receipt to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact JSON summary.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless the cleaned tree is ready for the next zip.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    retention_exit_receipt_path = _resolve(args.retention_exit_receipt, root)
    prune_receipt_path = _resolve(args.prune_receipt, root)
    if retention_exit_receipt_path is None or prune_receipt_path is None:
        raise SystemExit('missing receipt path')

    retention_exit_receipt = load_json(retention_exit_receipt_path)
    prune_receipt = load_json(prune_receipt_path)
    receipt = build_post_prune_audit_receipt(
        retention_exit_receipt,
        retention_exit_receipt_path,
        prune_receipt,
        prune_receipt_path,
        root=root,
    )

    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    if args.strict and not receipt['cleaned_tree_ready_for_zip']:
        print('rematch-world-benchmark-post-prune-audit: tree is not yet clean to zip', flush=True)
        return 1

    if args.summary_json:
        payload = {
            'cleaned_tree_ready_for_zip': receipt['cleaned_tree_ready_for_zip'],
            'counts': receipt['counts'],
            'prune_receipt_summary': receipt['prune_receipt_summary'],
        }
    else:
        payload = receipt

    rendered = json.dumps(payload, indent=2, sort_keys=True) + '\n'
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
