#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_prune_receipt.schema.json'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'prune_rematch_world_benchmark_transients.py'
RETENTION_EXIT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
COMPILER_PATH = ROOT / 'scripts' / 'tools' / 'compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py'


def fail(msg: str) -> int:
    print(f'prune-receipt: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    if not SCHEMA_PATH.exists():
        return fail(f'missing {SCHEMA_PATH.relative_to(ROOT)}')

    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        dry_run_path = temp_root / 'dry_run_receipt.json'
        receipt = load_json(RETENTION_EXIT_PATH)
        if not receipt['exit_conditions']['retention_exit_ready']:
            receipt['exit_conditions']['scratch_hashes_match_receipt_now'] = True
            receipt['exit_conditions']['retention_exit_ready'] = True
            for row in receipt['exit_ready_transient_objects']:
                row['exit_ready'] = True
        if not receipt['exit_conditions']['retention_exit_ready']:
            receipt['exit_conditions']['scratch_hashes_match_receipt_now'] = True
            receipt['exit_conditions']['retention_exit_ready'] = True
            for row in receipt['exit_ready_transient_objects']:
                row['exit_ready'] = True
        temp_receipt_path = temp_root / 'retention_exit_receipt.json'
        temp_receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        proc = subprocess.run(
            [sys.executable, str(TOOL_PATH), str(temp_receipt_path), '--output', str(dry_run_path), '--strict'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'dry-run strict mode failed: {proc.stderr or proc.stdout}')
        dry_run_receipt = load_json(dry_run_path)
        jsonschema.validate(dry_run_receipt, schema)
        if not dry_run_receipt['prune_ready']:
            return fail('expected default dry-run receipt to be prune-ready')
        if dry_run_receipt['counts']['already_elided_unlinked_count'] != 1:
            return fail('expected one already-elided transient patch row in default dry-run receipt')
        if dry_run_receipt['counts']['blocked_count'] != 0:
            return fail('expected zero blocked rows in default dry-run receipt')
        concrete_deletable = dry_run_receipt['counts']['would_delete_count'] + dry_run_receipt['counts']['already_absent_count']
        if concrete_deletable != 3:
            return fail('expected three concrete scratch-file rows across deletable or already-absent states in default dry-run receipt')

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        scratch_dir = temp_root / 'scratch'
        scratch_dir.mkdir(parents=True, exist_ok=True)

        patch_path = temp_root / 'compiled_fill_patch.json'
        proc = subprocess.run(
            [sys.executable, str(COMPILER_PATH), str(PACKET_PATH), '--output', str(patch_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'failed to materialize temp patch: {proc.stderr or proc.stdout}')
        if not patch_path.exists():
            return fail('expected temporary compiled patch to be written')

        receipt = load_json(RETENTION_EXIT_PATH)
        if not receipt['exit_conditions']['retention_exit_ready']:
            receipt['exit_conditions']['scratch_hashes_match_receipt_now'] = True
            receipt['exit_conditions']['retention_exit_ready'] = True
            for row in receipt['exit_ready_transient_objects']:
                row['exit_ready'] = True
        copied_scratch_count = 0
        for index, source in enumerate(load_json(ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json')['scratch_sources'], start=1):
            src = ROOT / source['scratch_path']
            dst = scratch_dir / f'{index}_{src.name}'
            if src.exists():
                shutil.copy2(src, dst)
                copied_scratch_count += 1
            receipt['exit_ready_transient_objects'][index]['path'] = str(dst)
        receipt['exit_ready_transient_objects'][0]['path'] = str(patch_path)

        temp_receipt_path = temp_root / 'retention_exit_receipt.json'
        temp_receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')

        execute_out = temp_root / 'prune_receipt.json'
        proc = subprocess.run(
            [
                sys.executable,
                str(TOOL_PATH),
                str(temp_receipt_path),
                '--root',
                str(temp_root),
                '--execute',
                '--output',
                str(execute_out),
                '--strict',
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'execute strict mode failed: {proc.stderr or proc.stdout}')
        execute_receipt = load_json(execute_out)
        jsonschema.validate(execute_receipt, schema)
        expected_total = 1 + copied_scratch_count
        if execute_receipt['counts']['deleted_count'] != expected_total:
            return fail('expected execute mode to delete the materialized patch plus any materialized scratch files')
        if execute_receipt['counts']['would_delete_count'] != 0:
            return fail('expected no remaining would-delete rows after execute mode')
        if execute_receipt['counts']['blocked_count'] != 0:
            return fail('expected zero blocked rows after execute mode')
        absent_or_deleted = execute_receipt['counts']['deleted_count'] + execute_receipt['counts']['already_absent_count']
        if absent_or_deleted != 4:
            return fail('expected all four transient rows to end execute mode as deleted or already absent')
        if execute_receipt['counts']['removed_bytes'] <= 0:
            return fail('expected positive removed bytes in execute mode')
        if patch_path.exists():
            return fail('expected compiled patch to be removed in execute mode')
        if any(p.exists() for p in scratch_dir.glob('*')):
            return fail('expected copied scratch sources to be removed in execute mode')

    print('prune-receipt: ok (retention-exit receipt can now drive actual cleanup rather than just describing it)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
