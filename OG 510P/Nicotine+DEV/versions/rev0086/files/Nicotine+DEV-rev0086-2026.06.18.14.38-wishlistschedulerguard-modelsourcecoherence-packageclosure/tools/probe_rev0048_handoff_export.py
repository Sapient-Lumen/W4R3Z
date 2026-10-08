#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path

BUNDLES = [
    '01-transfer-session-identity',
    '02-peer-primary-election',
    '03-search-response-source-admission',
    '04-search-response-parser-budget',
]
FORBIDDEN = ('__pycache__', '.pytest_cache', 'source-trees', 'git-full', '.git')

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    cube=Path(__file__).resolve().parents[1]
    errors=[]; checks=[]
    handoff=cube/'handoff/rev0048'
    if not (handoff/'HANDOFF-INDEX.md').is_file():
        errors.append('missing handoff/rev0048/HANDOFF-INDEX.md')
    for bundle in BUNDLES:
        bdir=handoff/bundle
        missing=[]
        for rel in ['README.md','MANIFEST.sha256']:
            if not (bdir/rel).is_file(): missing.append(rel)
        for sub in ['reports','patches','tests','evidence']:
            if not (bdir/sub).is_dir(): missing.append(sub+'/')
        if missing: errors.append(f'{bundle}: missing {missing}')
        checks.append({'check':'bundle structure','bundle':bundle,'status':'pass' if not missing else 'fail','missing':missing})
    manifest_path=cube/'data/rev0048_handoff_export_manifest.csv'
    rows=[]
    if not manifest_path.is_file():
        errors.append('missing data/rev0048_handoff_export_manifest.csv')
    else:
        rows=list(csv.DictReader(manifest_path.open(encoding='utf-8')))
        for row in rows:
            rel=row['handoff_path']
            if any(part in rel.split('/') for part in FORBIDDEN):
                errors.append(f'forbidden path component in manifest: {rel}')
                continue
            p=cube/rel
            if not p.is_file():
                errors.append(f'missing exported file: {rel}')
                continue
            got=sha256(p)
            if got != row['sha256']:
                errors.append(f'sha256 mismatch: {rel}')
        checks.append({'check':'handoff manifest hashes','status':'pass' if not errors else 'fail','rows':len(rows)})
    # Validate per-bundle MANIFEST.sha256 files.
    for bundle in BUNDLES:
        bdir=handoff/bundle
        m=bdir/'MANIFEST.sha256'
        per=[]
        if m.is_file():
            for line in m.read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                digest, rel = line.split('  ', 1)
                p=bdir/rel
                if not p.is_file(): per.append(f'missing {rel}')
                elif sha256(p) != digest: per.append(f'digest mismatch {rel}')
        if per: errors.extend([f'{bundle}: {x}' for x in per])
        checks.append({'check':'per-bundle manifest','bundle':bundle,'status':'pass' if not per else 'fail','errors':per})
    pre=cube/'evidence/rev0048-rev0047-preflight-rerun.json'
    if pre.is_file():
        try:
            data=json.loads(pre.read_text(encoding='utf-8'))
            if data.get('status') != 'pass': errors.append('rev0047 preflight rerun is not pass')
        except Exception as exc:
            errors.append(f'could not parse rev0047 preflight rerun: {exc}')
    else:
        errors.append('missing evidence/rev0048-rev0047-preflight-rerun.json')
    # Scope guard for the handoff folder.
    for p in handoff.rglob('*'):
        parts=set(p.relative_to(handoff).parts)
        bad=parts.intersection(FORBIDDEN)
        if bad: errors.append(f'forbidden handoff path: {p.relative_to(cube)}')
    out={'revision':'rev0048','status':'pass' if not errors else 'fail','bundle_count':len(BUNDLES),'manifest_rows':len(rows),'checks':checks,'errors':errors}
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1
if __name__ == '__main__':
    raise SystemExit(main())
