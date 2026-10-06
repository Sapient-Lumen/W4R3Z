#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = 'RELEASE-MANIFEST.json'
STAMP_RE = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})$')
SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
REV_RE = re.compile(r'^## (rev\d{4}) — (\d{4}-\d{2}-\d{2})$', re.M)
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
        fail('CHANGELOG.md missing top heading like ## rev0001 — YYYY-MM-DD')
    return m.group(1), m.group(2)


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


def zipinfo(name: str, dt: tuple[int, int, int, int, int, int]) -> ZipInfo:
    zi = ZipInfo(name)
    zi.date_time = dt
    zi.compress_type = ZIP_DEFLATED
    zi.external_attr = CANONICAL_MODE << 16
    zi.create_system = 3
    return zi


def add_bytes(zf: ZipFile, name: str, data: bytes, dt: tuple[int, int, int, int, int, int]) -> None:
    zf.writestr(zipinfo(name, dt), data)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--timestamp', required=True)
    ap.add_argument('--slug', required=True)
    ap.add_argument('--outdir', default='/mnt/data')
    args = ap.parse_args()

    m = STAMP_RE.match(args.timestamp)
    if not m:
        fail('timestamp must be YYYY.MM.DD.HH.MM')
    if not SLUG_RE.match(args.slug):
        fail('slug must match lowercase words separated by hyphens')
    dt = tuple(map(int, m.groups())) + (0,)

    subprocess.run(['node', 'tools/run_rev0005_proof.mjs', '--write'], cwd=ROOT, check=True)
    subprocess.run(['node', 'tools/capability_survey.mjs', '--json', 'artifacts/validation/REV0005-CAPABILITY-SURVEY.json'], cwd=ROOT, check=True)
    subprocess.run(['node', 'tools/plan_tests.mjs', '--tier', 'release', '--changed', 'src/browserrt.mjs,tools/run_tests.mjs', '--json', 'artifacts/validation/REV0005-TEST-PLAN-SANITY.json'], cwd=ROOT, check=True)
    subprocess.run(['node', 'tools/validate_test_surface.mjs', '--write'], cwd=ROOT, check=True)
    subprocess.run(['node', 'tools/run_tests.mjs', '--tier', 'release', '--jobs', 'auto', '--json', 'artifacts/validation/REV0005-TEST-HARNESS-RUN.json'], cwd=ROOT, check=True)
    subprocess.run(['node', 'tools/update_timing_history.mjs', '--report', 'artifacts/validation/REV0005-TEST-HARNESS-RUN.json', '--out', 'artifacts/validation/REV0005-TEST-TIMING-HISTORY.json'], cwd=ROOT, check=True)
    subprocess.run(['node', 'tools/analyze_tests.mjs', '--report', 'artifacts/validation/REV0005-TEST-HARNESS-RUN.json', '--history', 'artifacts/validation/REV0005-TEST-TIMING-HISTORY.json', '--out', 'artifacts/validation/REV0005-TEST-ANALYSIS.json', '--write'], cwd=ROOT, check=True)
    subprocess.run(['node', 'tools/turn_bootstrap.mjs', '--write'], cwd=ROOT, check=True)
    subprocess.run(['python3', 'tools/check_cube.py'], cwd=ROOT, check=True)

    revision, revision_date = parse_revision()
    archive_name = f'BrowserRT-{revision}-{args.timestamp}-{args.slug}.zip'
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / archive_name

    files = iter_files()
    rows = []
    for rel in files:
        data = (ROOT / rel).read_bytes()
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

    with ZipFile(out_path, 'w', compression=ZIP_DEFLATED) as zf:
        for rel in files:
            add_bytes(zf, rel.as_posix(), (ROOT / rel).read_bytes(), dt)
        add_bytes(zf, MANIFEST_NAME, manifest_bytes, dt)

    subprocess.run(['python3', 'tools/verify_release.py', str(out_path)], cwd=ROOT, check=True)
    print(out_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
