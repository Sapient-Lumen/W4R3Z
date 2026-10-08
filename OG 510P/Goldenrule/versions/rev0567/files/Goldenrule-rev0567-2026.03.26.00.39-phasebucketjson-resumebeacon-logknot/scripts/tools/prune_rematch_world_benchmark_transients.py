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
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_prune_receipt.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _resolve(path_value: str | None, root: Path) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    return path if path.is_absolute() else (root / path)


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _sha256_json(node: Any) -> str:
    return _sha256_bytes(json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))


def _relativize(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    root_resolved = root.resolve()
    return resolved.relative_to(root_resolved).as_posix() if resolved.is_relative_to(root_resolved) else str(path)


def _prune_empty_parents(path: Path, root: Path) -> int:
    removed = 0
    for parent in path.parents:
        if parent == root or not parent.is_relative_to(root):
            break
        if any(parent.iterdir()):
            break
        parent.rmdir()
        removed += 1
    return removed


def build_prune_receipt(
    retention_exit_receipt: dict[str, Any],
    retention_exit_receipt_path: Path,
    *,
    root: Path,
    execute: bool,
    prune_empty_dirs: bool,
) -> dict[str, Any]:
    exit_ready = bool(retention_exit_receipt['exit_conditions']['retention_exit_ready'])
    rows: list[dict[str, Any]] = []

    counts = {
        'total_transient_count': len(retention_exit_receipt['exit_ready_transient_objects']),
        'eligible_count': 0,
        'concrete_path_count': 0,
        'already_elided_unlinked_count': 0,
        'would_delete_count': 0,
        'deleted_count': 0,
        'already_absent_count': 0,
        'blocked_count': 0,
        'empty_dirs_removed_count': 0,
        'concrete_exit_bytes': 0,
        'removed_bytes': 0,
    }

    for transient in retention_exit_receipt['exit_ready_transient_objects']:
        row = dict(transient)
        path_value = row.get('path')
        path = _resolve(path_value, root)
        eligible = bool(exit_ready and row.get('exit_ready'))
        exists_before = bool(path and path.exists())
        exists_after = exists_before
        hash_matches_before: bool | None = None
        status = 'blocked_not_exit_ready'
        action = 'block'

        if eligible:
            counts['eligible_count'] += 1

        if path is None:
            counts['already_elided_unlinked_count'] += 1
            status = 'unlinked_transient'
            action = 'none'
        elif eligible:
            counts['concrete_path_count'] += 1
            counts['concrete_exit_bytes'] += int(row['byte_count'])
            if not exists_before:
                counts['already_absent_count'] += 1
                status = 'already_absent'
                action = 'none'
            else:
                blob = path.read_bytes()
                hash_matches_before = _sha256_bytes(blob) == row['sha256'] and len(blob) == int(row['byte_count'])
                if not hash_matches_before and path.suffix == '.json':
                    try:
                        hash_matches_before = _sha256_json(json.loads(blob.decode('utf-8'))) == row['sha256']
                    except Exception:
                        hash_matches_before = False
                if not hash_matches_before:
                    counts['blocked_count'] += 1
                    status = 'blocked_hash_mismatch'
                    action = 'block'
                elif execute:
                    path.unlink()
                    exists_after = False
                    counts['deleted_count'] += 1
                    counts['removed_bytes'] += int(row['byte_count'])
                    status = 'deleted'
                    action = 'unlink'
                    if prune_empty_dirs:
                        counts['empty_dirs_removed_count'] += _prune_empty_parents(path, root)
                else:
                    counts['would_delete_count'] += 1
                    status = 'would_delete'
                    action = 'planned_unlink'
        else:
            counts['blocked_count'] += 1

        rows.append(
            {
                'label': row['label'],
                'path': _relativize(path, root) if path is not None else None,
                'retention_class': row['retention_class'],
                'byte_count': int(row['byte_count']),
                'sha256': row['sha256'],
                'exit_ready': bool(row.get('exit_ready')),
                'eligible': eligible,
                'exists_before': exists_before,
                'exists_after': exists_after,
                'hash_matches_before': hash_matches_before,
                'status': status,
                'action': action,
            }
        )

    prune_ready = bool(exit_ready and counts['blocked_count'] == 0)
    if not exit_ready:
        recommended_next_move = (
            'Do not prune yet; first satisfy the retention-exit conditions so provenance, preflight, patch-elision, and spine-audit checks all agree.'
        )
    elif counts['blocked_count']:
        recommended_next_move = (
            'Do not prune yet; repair the transient-path drift or hash mismatch rows until every exit-ready transient either matches and can be deleted or is already absent.'
        )
    elif execute:
        recommended_next_move = (
            'Transient cleanup is complete for the current receipt; refresh the archive size profile and cut the next revision zip from the cleaned retained tree.'
        )
    else:
        recommended_next_move = (
            'This receipt is prune-ready in dry-run mode; rerun with --execute when you want to delete the concrete exit-ready scratch/intermediate files covered by the retention-exit receipt.'
        )

    return {
        'snapshot_date': '2026-03-17',
        'receipt_version': '2026-03-17.rematch_world_benchmark_prune_receipt.v1',
        'analysis_script': 'scripts/tools/prune_rematch_world_benchmark_transients.py',
        'focus': 'turn the rematch-world retention-exit receipt into an explicit cleanup action so scratch traces and reconstructible intermediates leave by rule rather than by memory',
        'retention_exit_receipt_path': _relativize(retention_exit_receipt_path, root) or str(retention_exit_receipt_path),
        'execution_mode': 'execute' if execute else 'dry_run',
        'prune_ready': prune_ready,
        'counts': counts,
        'transient_rows': rows,
        'recommended_next_move': recommended_next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Prune exit-ready rematch-world benchmark transient files from a retention-exit receipt, or emit a dry-run receipt describing what would be removed.')
    parser.add_argument('retention_exit_receipt', nargs='?', default=str(DEFAULT_RETENTION_EXIT), help='Path to the rematch-world retention-exit receipt JSON.')
    parser.add_argument('--root', default=str(ROOT), help='Root used to resolve relative transient paths. Defaults to the repository root.')
    parser.add_argument('--execute', action='store_true', help='Delete concrete exit-ready files instead of emitting a dry-run receipt.')
    parser.add_argument('--no-prune-empty-dirs', action='store_true', help='Do not remove newly empty parent directories after deleting files.')
    parser.add_argument('--output', help='Write the prune receipt to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact JSON summary.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless the receipt is prune-ready and, in execute mode, nothing remains to delete.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    receipt_path = _resolve(args.retention_exit_receipt, root)
    if receipt_path is None:
        raise SystemExit('missing retention exit receipt path')
    retention_exit_receipt = load_json(receipt_path)
    receipt = build_prune_receipt(
        retention_exit_receipt,
        receipt_path,
        root=root,
        execute=args.execute,
        prune_empty_dirs=not args.no_prune_empty_dirs,
    )

    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    if args.strict:
        strict_ok = bool(receipt['prune_ready'])
        if args.execute:
            strict_ok = strict_ok and receipt['counts']['would_delete_count'] == 0 and receipt['counts']['blocked_count'] == 0
        if not strict_ok:
            print('rematch-world-benchmark-prune: prune conditions not yet satisfied', flush=True)
            return 1

    if args.summary_json:
        summary = {
            'execution_mode': receipt['execution_mode'],
            'prune_ready': receipt['prune_ready'],
            'concrete_path_count': receipt['counts']['concrete_path_count'],
            'would_delete_count': receipt['counts']['would_delete_count'],
            'deleted_count': receipt['counts']['deleted_count'],
            'blocked_count': receipt['counts']['blocked_count'],
            'concrete_exit_bytes': receipt['counts']['concrete_exit_bytes'],
            'removed_bytes': receipt['counts']['removed_bytes'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path = _resolve(args.output, root)
        assert output_path is not None
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(
            'rematch-world-benchmark-prune: '
            f'wrote {_relativize(output_path, root)} '
            f'(mode={receipt["execution_mode"]}, prune_ready={str(receipt["prune_ready"]).lower()})'
        )
    else:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
