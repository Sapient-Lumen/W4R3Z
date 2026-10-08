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
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_post_prune_audit_receipt.schema.json'
RETENTION_EXIT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
EVIDENCE_RECEIPT_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
COMPILER_PATH = ROOT / 'scripts' / 'tools' / 'compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py'
PRUNE_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'prune_rematch_world_benchmark_transients.py'
AUDIT_TOOL_PATH = ROOT / 'scripts' / 'tools' / 'audit_rematch_world_benchmark_post_prune_state.py'


def fail(msg: str) -> int:
    print(f'post-prune-audit: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def copy_rel(src: Path, temp_root: Path) -> Path:
    dst = temp_root / src.relative_to(ROOT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        retention_exit = load_json(RETENTION_EXIT_PATH)
        evidence_receipt = load_json(EVIDENCE_RECEIPT_PATH)

        for row in retention_exit['durable_retained_objects']:
            copy_rel(ROOT / row['path'], temp_root)
        copy_rel(PACKET_PATH, temp_root)

        patch_rel = Path('examples/scratch/rematch_world_benchmark/compiled_fill_patch.json')
        patch_path = temp_root / patch_rel
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [sys.executable, str(COMPILER_PATH), str(temp_root / PACKET_PATH.relative_to(ROOT)), '--output', str(patch_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'failed to materialize temp patch: {proc.stderr or proc.stdout}')

        temp_retention_exit = json.loads(json.dumps(retention_exit))
        temp_retention_exit['exit_conditions']['scratch_hashes_match_receipt_now'] = True
        temp_retention_exit['exit_conditions']['retention_exit_ready'] = True
        for row in temp_retention_exit['exit_ready_transient_objects']:
            row['exit_ready'] = True
        patch_blob = json.loads(patch_path.read_text(encoding='utf-8'))
        patch_bytes = json.dumps(patch_blob, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        temp_retention_exit['exit_ready_transient_objects'][0]['path'] = patch_rel.as_posix()
        temp_retention_exit['exit_ready_transient_objects'][0]['byte_count'] = len(patch_path.read_bytes())
        import hashlib
        temp_retention_exit['exit_ready_transient_objects'][0]['sha256'] = hashlib.sha256(patch_bytes).hexdigest()

        for index, source in enumerate(evidence_receipt['scratch_sources'], start=1):
            src = ROOT / source['scratch_path']
            target_rel = Path(source['scratch_path'])
            if src.exists():
                copied = copy_rel(src, temp_root)
                temp_retention_exit['exit_ready_transient_objects'][index]['path'] = copied.relative_to(temp_root).as_posix()
            else:
                temp_retention_exit['exit_ready_transient_objects'][index]['path'] = target_rel.as_posix()

        temp_retention_exit_path = temp_root / 'examples' / 'snapshots' / 'retention_exit_receipt.json'
        temp_retention_exit_path.parent.mkdir(parents=True, exist_ok=True)
        temp_retention_exit_path.write_text(json.dumps(temp_retention_exit, indent=2, sort_keys=True) + '\n', encoding='utf-8')

        dry_run_path = temp_root / 'examples' / 'snapshots' / 'dry_run_prune_receipt.json'
        proc = subprocess.run(
            [sys.executable, str(PRUNE_TOOL_PATH), str(temp_retention_exit_path), '--root', str(temp_root), '--output', str(dry_run_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'dry-run prune failed: {proc.stderr or proc.stdout}')
        dry_audit_path = temp_root / 'examples' / 'snapshots' / 'dry_run_post_prune_audit.json'
        proc = subprocess.run(
            [sys.executable, str(AUDIT_TOOL_PATH), str(temp_retention_exit_path), str(dry_run_path), '--root', str(temp_root), '--output', str(dry_audit_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'dry-run audit failed: {proc.stderr or proc.stdout}')
        dry_receipt = load_json(dry_audit_path)
        jsonschema.validate(dry_receipt, schema)
        if dry_receipt['cleaned_tree_ready_for_zip']:
            return fail('expected dry-run prune receipt to leave cleaned_tree_ready_for_zip false')

        execute_prune_path = temp_root / 'examples' / 'snapshots' / 'prune_execute_receipt.json'
        proc = subprocess.run(
            [sys.executable, str(PRUNE_TOOL_PATH), str(temp_retention_exit_path), '--root', str(temp_root), '--execute', '--output', str(execute_prune_path), '--strict'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'execute prune failed: {proc.stderr or proc.stdout}')

        execute_audit_path = temp_root / 'examples' / 'snapshots' / 'post_prune_audit_receipt.json'
        proc = subprocess.run(
            [sys.executable, str(AUDIT_TOOL_PATH), str(temp_retention_exit_path), str(execute_prune_path), '--root', str(temp_root), '--output', str(execute_audit_path), '--strict'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return fail(f'execute audit strict failed: {proc.stderr or proc.stdout}')
        receipt = load_json(execute_audit_path)
        jsonschema.validate(receipt, schema)
        if not receipt['cleaned_tree_ready_for_zip']:
            return fail('expected execute-mode post-prune audit to report cleaned_tree_ready_for_zip true')
        if receipt['counts']['durable_hash_match_count'] != receipt['counts']['durable_count']:
            return fail('expected every durable object to hash-match after prune')
        if receipt['counts']['transient_absent_or_unlinked_count'] != receipt['counts']['transient_count']:
            return fail('expected every transient row to be absent or unlinked after prune')
        if receipt['counts']['transient_still_present_count'] != 0:
            return fail('expected zero transient rows to remain present after prune')
        if receipt['counts']['blocked_count'] != 0:
            return fail('expected zero blocked rows after execute prune audit')

    print('post-prune-audit: ok (a cleaned rematch-world tree can now be audited as safe to zip after transient cleanup)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
