#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_REQUIRED = [
    'README.md','START_HERE.md','OPEN_ME.html','PRIORITY-LIST.md','HUNT-QUESTIONS.md',
    'RESEARCH-SOURCE-REGISTRY.json','IDEA-LEDGER.json','QUESTION-LEDGER.json','EXPERIMENT-MATRIX.json',
    'BABY-DATACUBE-CANDIDATE.json','SURFACE-STATUS.json','REENTRY-CONTRACT.json','CUBE-META.json','REVISION-RECEIPT.json',
    'tools/smoke_validate.py','tools/probe_dashboard.py','tools/probe_suite_dashboard.py','tools/cube_audit.py',
    'tools/probe_metric_index.py','tools/probe_graph_specs.py','tools/cache_probe_report.py','tools/traceability_report.py',
    'tools/native_probe_audit.py','tools/native_family_report.py','tools/native_probe_index.py','tools/native_hardening_report.py',
]
FORBIDDEN = ['M' + 'UC', 'Tiddly' + 'Wiki', '.t' + 'id']

def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def revision() -> str:
    try: return load_json('CUBE-META.json').get('revision','rev0000')
    except Exception: return 'rev0000'

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    rev = revision(); revup = rev.upper(); errors=[]; warnings=[]
    for rel in CORE_REQUIRED:
        if not (ROOT / rel).exists(): errors.append(f'missing required file: {rel}')
    current_required = [
        f'artifacts/audit/{revup}_CUBE_AUDIT.json',
        f'artifacts/audit/{revup}_NATIVE_PROBE_AUDIT.json',
        f'artifacts/audit/{revup}_TRACEABILITY_REPORT.json',
        f'artifacts/audit/{revup}_SURPRISE_AUDIT.json',
        f'artifacts/dashboard/{revup}_PROBE_METRIC_INDEX.json',
        f'artifacts/dashboard/{revup}_PROBE_GRAPH_SPECS.json',
        f'artifacts/dashboard/{revup}_CACHE_PROBE_REPORT.json',
        f'artifacts/dashboard/{revup}_NATIVE_FAMILY_REPORT.json',
        f'artifacts/dashboard/{revup}_NATIVE_PROBE_INDEX.json',
        f'artifacts/dashboard/{revup}_NATIVE_HARDENING_REPORT.json',
        f'artifacts/probe-results/{revup}_PROBE_SUITE_DASHBOARD.json',
        'docs/01-research/rev0015-scout-notes.md' if rev == 'rev0015' else f'docs/01-research/{rev}-scout-notes.md',
        'docs/04-audit/rev0015-audit-refactor-notes.md' if rev == 'rev0015' else f'docs/04-audit/{rev}-audit-refactor-notes.md',
    ]
    for rel in current_required:
        if not (ROOT / rel).exists(): errors.append(f'missing current revision artifact: {rel}')
    for rel in ['RESEARCH-SOURCE-REGISTRY.json','IDEA-LEDGER.json','QUESTION-LEDGER.json','EXPERIMENT-MATRIX.json','CUBE-META.json','REVISION-RECEIPT.json','SURFACE-STATUS.json','BABY-DATACUBE-CANDIDATE.json']:
        try: load_json(rel)
        except Exception as e: errors.append(f'json parse failed: {rel}: {e}')
    for rel,key in [('RESEARCH-SOURCE-REGISTRY.json','sources'),('IDEA-LEDGER.json','ideas'),('QUESTION-LEDGER.json','questions'),('EXPERIMENT-MATRIX.json','cells')]:
        try:
            obj=load_json(rel)
            if obj.get('count') != len(obj.get(key, [])): errors.append(f'count mismatch in {rel}')
            if obj.get('revision') != rev: warnings.append(f'{rel} revision field {obj.get("revision")} != {rev}')
        except Exception: pass
    # Current revision must have at least one native smoke output if C++ exists.
    cpp_files = sorted((ROOT/'experiments').glob('*/*.cpp'))
    current_probe_jsons = sorted((ROOT/'artifacts'/'probe-results').glob(f'{revup}_*.json'))
    if cpp_files and not any('SMOKE' in p.name for p in current_probe_jsons): errors.append('no current-revision smoke outputs found for C++ probes')
    # Retired lane byte scan for text-like files.
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.name in {'smoke_validate.py', 'cube_audit.py'}: continue
        if p.suffix.lower() in {'.md','.json','.html','.csv','.txt','.py','.cpp','.hpp'}:
            try: txt=p.read_text(encoding='utf-8')
            except UnicodeDecodeError: continue
            for token in FORBIDDEN:
                if token in txt: errors.append(f'forbidden retired-lane token {token!r} in {p.relative_to(ROOT)}')
    # Manifest validation.
    m=ROOT/'FILE-MANIFEST.json'
    if m.exists():
        try:
            manifest=json.loads(m.read_text(encoding='utf-8'))
            for item in manifest.get('files', []):
                rel=item['path']
                if rel in {'FILE-MANIFEST.json','CHECKSUMS.sha256'}: continue
                fp=ROOT/rel
                if not fp.exists(): errors.append(f'manifest file missing: {rel}')
                elif item.get('sha256') and sha256(fp) != item['sha256']: errors.append(f'sha256 mismatch: {rel}')
        except Exception as e: errors.append(f'manifest parse/verify failed: {e}')
    else:
        warnings.append('FILE-MANIFEST.json missing; manifest validation skipped')
    if errors:
        print('SMOKE VALIDATION FAILED')
        for e in errors: print('-', e)
        if warnings:
            print('Warnings:'); [print('-', w) for w in warnings]
        return 1
    print('SMOKE VALIDATION PASSED')
    if warnings:
        print('Warnings:'); [print('-', w) for w in warnings]
    return 0
if __name__ == '__main__': sys.exit(main())
