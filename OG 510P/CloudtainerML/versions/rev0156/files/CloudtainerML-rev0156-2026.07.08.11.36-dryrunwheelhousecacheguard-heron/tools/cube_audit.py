#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / 'artifacts' / 'audit'

def revision() -> str:
    try:
        return json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8')).get('revision', 'rev0007')
    except Exception:
        return 'rev0007'

REVISION = revision()
REVUP = REVISION.upper()
FORBIDDEN = ['M' + 'UC', 'Tiddly' + 'Wiki', '.t' + 'id']


def load(name: str) -> Any:
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def scan_forbidden() -> list[dict[str, str]]:
    hits = []
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.name in {'smoke_validate.py', 'cube_audit.py'}:
            continue
        if p.suffix.lower() not in {'.md', '.json', '.html', '.csv', '.txt', '.py'}:
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        for token in FORBIDDEN:
            if token in text:
                hits.append({'file': str(p.relative_to(ROOT)), 'token': token})
    return hits


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    src = load('RESEARCH-SOURCE-REGISTRY.json')
    ideas = load('IDEA-LEDGER.json')
    qs = load('QUESTION-LEDGER.json')
    cells = load('EXPERIMENT-MATRIX.json')

    if src.get('count') != len(src.get('sources', [])):
        errors.append('source count mismatch')
    if ideas.get('count') != len(ideas.get('ideas', [])):
        errors.append('idea count mismatch')
    if qs.get('count') != len(qs.get('questions', [])):
        errors.append('question count mismatch')
    if cells.get('count') != len(cells.get('cells', [])):
        errors.append('cell count mismatch')

    source_ids = {s['id'] for s in src['sources']}
    idea_ids = {i['id'] for i in ideas['ideas']}
    cell_ids = {c['cell_id'] for c in cells['cells']}
    missing_source_refs = []
    for obj_type, items, sid_key in [('idea', ideas['ideas'], 'source_ids'), ('cell', cells['cells'], 'source_ids')]:
        for item in items:
            for sid in item.get(sid_key, []):
                if sid not in source_ids:
                    missing_source_refs.append({'type': obj_type, 'id': item.get('id') or item.get('cell_id'), 'missing_source': sid})
    if missing_source_refs:
        errors.append(f'missing source refs: {len(missing_source_refs)}')

    missing_idea_refs = [c for c in cells['cells'] if c.get('idea_id') not in idea_ids]
    if missing_idea_refs:
        errors.append(f'missing idea refs: {len(missing_idea_refs)}')

    duplicate_arxiv = []
    seen = {}
    for s in src['sources']:
        a = s.get('arxiv')
        if a and a in seen:
            duplicate_arxiv.append({'arxiv': a, 'first': seen[a], 'dupe': s['id']})
        elif a:
            seen[a] = s['id']
    if duplicate_arxiv:
        warnings.append(f'duplicate arxiv ids: {len(duplicate_arxiv)}')

    forbidden_hits = scan_forbidden()
    if forbidden_hits:
        errors.append(f'forbidden retired-lane byte hits: {len(forbidden_hits)}')

    probe_jsons = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'artifacts' / 'probe-results').glob('*.json'))
    experiment_py = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'experiments').glob('*/*.py'))
    cell_note_count = len(list((ROOT / 'docs' / '02-experiment-cells').glob('cell-*.md'))) if (ROOT / 'docs' / '02-experiment-cells').exists() else 0
    if cell_note_count and cell_note_count < len(cells['cells']):
        warnings.append(f'cell notes fewer than matrix cells: {cell_note_count} < {len(cells["cells"])}')

    total_bytes = sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
    report = {
        'project': 'CloudtainerML',
        'revision': REVISION,
        'status': 'pass' if not errors else 'fail',
        'errors': errors,
        'warnings': warnings,
        'counts': {
            'sources': len(src['sources']),
            'ideas': len(ideas['ideas']),
            'questions': len(qs['questions']),
            'cells': len(cells['cells']),
            'cell_notes': cell_note_count,
            'probe_json_outputs': len(probe_jsons),
            'experiment_py_files': len(experiment_py),
            'total_files': sum(1 for p in ROOT.rglob('*') if p.is_file()),
            'total_bytes': total_bytes,
        },
        'missing_source_refs': missing_source_refs[:50],
        'missing_idea_refs': [c.get('cell_id') for c in missing_idea_refs[:50]],
        'duplicate_arxiv': duplicate_arxiv,
        'forbidden_hits': forbidden_hits[:20],
        'probe_jsons': probe_jsons,
        'experiment_py': experiment_py,
        'audit_note': f'{REVISION} audit focuses on structural consistency, retired-lane absence, probe-output discoverability, and rev-local artifact hygiene.',
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / f'{REVUP}_CUBE_AUDIT.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    md = [
        f'# Cube audit — {REVISION}',
        '',
        f"Status: **{report['status']}**",
        '',
        '## Counts',
        '',
    ]
    for k, v in report['counts'].items():
        md.append(f'- {k}: {v}')
    md.extend(['', '## Errors', ''])
    md.extend([f'- {e}' for e in errors] or ['- none'])
    md.extend(['', '## Warnings', ''])
    md.extend([f'- {w}' for w in warnings] or ['- none'])
    (AUDIT_DIR / f'{REVUP}_CUBE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'counts': report['counts'], 'errors': errors}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
