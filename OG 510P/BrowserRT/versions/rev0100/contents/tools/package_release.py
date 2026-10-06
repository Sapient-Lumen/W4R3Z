#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = 'RELEASE-MANIFEST.json'
STAMP_RE = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})$')
SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
REV_RE = re.compile(r'^## (rev\d{4}) — (\d{4}-\d{2}-\d{2})(?: — .*)?$', re.M)
CANONICAL_MODE = 0o100644


def fail(msg: str) -> None:
    print(f'[package_release] FAIL: {msg}')
    raise SystemExit(1)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_revision() -> tuple[str, str]:
    txt = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    m = REV_RE.search(txt)
    if not m:
        fail('CHANGELOG.md missing top heading like ## rev0001 — YYYY-MM-DD or ## rev0001 — YYYY-MM-DD — Codename')
    return m.group(1), m.group(2)


def rev_prefix(revision: str) -> str:
    return 'REV' + revision[3:]


def iter_files() -> list[Path]:
    files = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if path.is_dir():
            continue
        if rel.as_posix() == MANIFEST_NAME:
            continue
        if '.git' in rel.parts:
            continue
        if rel.suffix == '.zip':
            continue
        if rel.parts and rel.parts[0] in {'out', '__pycache__', 'node_modules'}:
            continue
        if rel.name.endswith('.pyc'):
            continue
        files.append(rel)
    return sorted(files, key=lambda p: p.as_posix())


def zipinfo(name: str, dt: tuple[int, int, int, int, int, int], compression: int) -> ZipInfo:
    zi = ZipInfo(name)
    zi.date_time = dt
    zi.compress_type = compression
    zi.external_attr = CANONICAL_MODE << 16
    zi.create_system = 3
    return zi


def add_bytes(zf: ZipFile, name: str, data: bytes, dt: tuple[int, int, int, int, int, int], compression: int) -> None:
    zf.writestr(zipinfo(name, dt, compression), data)


def run(cmd: list[str]) -> None:
    print('[package_release] $ ' + ' '.join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def require_passed_json(path: Path, label: str) -> None:
    if not path.exists():
        fail(f'{label} artifact missing: {path}')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f'{label} artifact is not valid JSON: {exc}')
    if data.get('status') != 'passed':
        fail(f'{label} artifact status is {data.get('status')!r}, expected passed: {path}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--timestamp', required=True)
    ap.add_argument('--slug', required=True)
    ap.add_argument('--outdir', default='/mnt/data')
    ap.add_argument('--zip-compression', choices=['deflated', 'stored'], default='stored', help='stored avoids long/partial cloudtainer package writes; deflated keeps smaller archives')
    ap.add_argument('--reuse-validation', action='store_true', help='reuse already-passed release/audit artifacts instead of rerunning the long release sweep')
    args = ap.parse_args()

    m = STAMP_RE.match(args.timestamp)
    if not m:
        fail('timestamp must be YYYY.MM.DD.HH.MM')
    if not SLUG_RE.match(args.slug):
        fail('slug must match lowercase words separated by hyphens')
    dt = tuple(map(int, m.groups())) + (0,)
    compression = ZIP_STORED if args.zip_compression == 'stored' else ZIP_DEFLATED

    revision, revision_date = parse_revision()
    prefix = rev_prefix(revision)

    # Package-time validation is intentionally browser-light. Browser/CDP proofs are
    # available by explicit tier/id, but broad packaging avoids duplicate browser launches.
    # Run the per-turn bootstrap first so cloudtainer sessions get early progress
    # and so package-time smoke does not run after the long release sweep.
    run(['node', 'tools/turn_bootstrap.mjs', '--write'])
    run(['node', 'tools/run_current_proof.mjs', '--write'])
    release_report = ROOT / 'artifacts' / 'validation' / f'{prefix}-TEST-HARNESS-RUN.json'
    if args.reuse_validation:
        require_passed_json(release_report, 'release harness')
    else:
        run(['node', 'tools/run_tests.mjs', '--tier', 'release', '--jobs', 'auto', '--quiet', '--json', f'artifacts/validation/{prefix}-TEST-HARNESS-RUN.json'])
    run(['node', 'tools/update_timing_history.mjs', '--report', f'artifacts/validation/{prefix}-TEST-HARNESS-RUN.json', '--out', f'artifacts/validation/{prefix}-TEST-TIMING-HISTORY.json'])
    run(['node', 'tools/analyze_tests.mjs', '--report', f'artifacts/validation/{prefix}-TEST-HARNESS-RUN.json', '--history', f'artifacts/validation/{prefix}-TEST-TIMING-HISTORY.json', '--out', f'artifacts/validation/{prefix}-TEST-ANALYSIS.json', '--write'])
    run(['node', 'tools/audit_cube_surfaces.mjs', '--json', f'artifacts/audit/{prefix}-CUBE-AUDIT.json'])
    run(['node', 'tools/deep_cube_audit.mjs', '--json', f'artifacts/audit/{prefix}-DEEP-CUBE-AUDIT.json'])
    run(['node', 'tools/foundation_audit.mjs', '--json', f'artifacts/audit/{prefix}-FOUNDATION-AUDIT.json'])
    run(['node', 'tools/current_office_audit.mjs', '--json', f'artifacts/audit/{prefix}-CURRENT-OFFICE-AUDIT.json'])
    run(['node', 'tools/artifact_budget_audit.mjs', '--json', f'artifacts/audit/{prefix}-ARTIFACT-BUDGET-AUDIT.json'])
    if args.reuse_validation:
        for name in ['CUBE-AUDIT', 'DEEP-CUBE-AUDIT', 'FOUNDATION-AUDIT', 'CURRENT-OFFICE-AUDIT', 'ARTIFACT-BUDGET-AUDIT']:
            require_passed_json(ROOT / 'artifacts' / 'audit' / f'{prefix}-{name}.json', name.lower())
    run(['python3', 'tools/check_cube.py'])

    archive_name = f'BrowserRT-{revision}-{args.timestamp}-{args.slug}.zip'
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / archive_name

    files = iter_files()
    # Snapshot file bytes exactly once before computing the release manifest.
    # Some proof artifacts are produced by Node processes and can settle very
    # near package time; reading bytes twice can produce a manifest/zip skew.
    # The release zip is therefore built from this frozen in-memory snapshot.
    file_blobs = []
    rows = []
    for rel in files:
        data = (ROOT / rel).read_bytes()
        file_blobs.append((rel, data))
        rows.append({'path': rel.as_posix(), 'size': len(data), 'sha256': sha256(data)})

    receipt = json.loads((ROOT / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
    manifest = {
        'manifest_version': 1,
        'project': 'BrowserRT',
        'archive_name': archive_name,
        'revision': revision,
        'revision_date': revision_date,
        'packaging_timestamp': args.timestamp,
        'slug': args.slug,
        'summary_highlight': receipt.get('summary_highlight'),
        'codename': receipt.get('codename'),
        'source_file_count': len(rows),
        'files': rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')

    with ZipFile(out_path, 'w', compression=compression) as zf:
        for rel, data in file_blobs:
            add_bytes(zf, rel.as_posix(), data, dt, compression)
        add_bytes(zf, MANIFEST_NAME, manifest_bytes, dt, compression)

    run(['python3', 'tools/verify_release.py', str(out_path)])
    print(out_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
