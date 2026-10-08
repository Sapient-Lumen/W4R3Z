#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, os, re, shutil, sys, tempfile
from pathlib import Path
from datetime import datetime, timezone

IGNORE_NAMES = {'.DS_Store'}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read_active_ids(root: Path) -> set[str]:
    board = root / 'records-requests/bvps-rev0379/operator-submit-board-rev0379.csv'
    if not board.exists():
        board = root / 'cube/bvps-canonical-dispatch-batch-rev0378.csv'
    if not board.exists():
        raise SystemExit('No active dispatch board found')
    with board.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    key = 'request_id' if rows and 'request_id' in rows[0] else 'active_request_id'
    return {r[key] for r in rows if r.get(key)}

def import_files(root: Path, request_id: str, input_dir: Path, dry_run: bool=False) -> Path:
    active = read_active_ids(root)
    if request_id not in active:
        raise SystemExit(f'Request id {request_id} is not in the active dispatch board')
    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f'Input directory not found: {input_dir}')
    files = [p for p in input_dir.rglob('*') if p.is_file() and p.name not in IGNORE_NAMES]
    if not files:
        raise SystemExit(f'No files found in input directory: {input_dir}')
    out_dir = root / 'evidence-intake/bvps-rev0379/imported' / request_id
    sidecar_dir = root / 'evidence-intake/bvps-rev0379/receipt-sidecars'
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for p in files:
        rel = p.relative_to(input_dir)
        dest = out_dir / rel
        digest = sha256_file(p)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
        manifest_rows.append({
            'request_id': request_id,
            'source_path': str(p),
            'stored_path': str(dest.relative_to(root)),
            'file_name': p.name,
            'bytes': p.stat().st_size,
            'sha256': digest,
            'imported_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),
            'dlp_status': 'pending_manual_screen',
            'proofcut_mapping_status': 'pending_manual_adjudication',
        })
    manifest_path = out_dir / 'response-file-manifest.csv'
    if not dry_run:
        with manifest_path.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
            w.writeheader(); w.writerows(manifest_rows)
    sidecar_path = sidecar_dir / f'sidecar-{request_id}.md'
    if not dry_run:
        with sidecar_path.open('a', encoding='utf-8') as f:
            f.write('\n\n## Rev0379 automated import manifest\n\n')
            f.write(f'- Imported UTC: {manifest_rows[0]["imported_utc"]}\n')
            f.write(f'- Stored manifest: `{manifest_path.relative_to(root)}`\n')
            f.write('- DLP status: pending_manual_screen\n')
            f.write('- Proofcut mapping: pending_manual_adjudication\n\n')
            f.write('| file_name | bytes | sha256 | stored_path |\n|---|---:|---|---|\n')
            for row in manifest_rows:
                f.write(f'| {row["file_name"]} | {row["bytes"]} | `{row["sha256"]}` | `{row["stored_path"]}` |\n')
    return manifest_path

def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / 'cube'
        root.mkdir()
        board = root / 'records-requests/bvps-rev0379'
        board.mkdir(parents=True)
        with (board/'operator-submit-board-rev0379.csv').open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['request_id'])
            w.writeheader(); w.writerow({'request_id':'RRT-TEST-001'})
        inp = root / 'inbox'
        inp.mkdir()
        (inp/'receipt.txt').write_text('test receipt', encoding='utf-8')
        manifest = import_files(root, 'RRT-TEST-001', inp, dry_run=False)
        if not manifest.exists():
            raise AssertionError('self-test manifest missing')
        print('self-test passed')
        return 0

def main() -> int:
    ap = argparse.ArgumentParser(description='Import BVPS response/receipt files with hashes and sidecar append.')
    ap.add_argument('--root', default='.', help='datacube root directory')
    ap.add_argument('--request-id', help='active request id, e.g. RRT-0378-013')
    ap.add_argument('--input-dir', help='directory containing receipt/response files to import')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.request_id or not args.input_dir:
        ap.error('--request-id and --input-dir are required unless --self-test is used')
    manifest = import_files(Path(args.root).resolve(), args.request_id, Path(args.input_dir).resolve(), args.dry_run)
    print(f'manifest: {manifest}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
