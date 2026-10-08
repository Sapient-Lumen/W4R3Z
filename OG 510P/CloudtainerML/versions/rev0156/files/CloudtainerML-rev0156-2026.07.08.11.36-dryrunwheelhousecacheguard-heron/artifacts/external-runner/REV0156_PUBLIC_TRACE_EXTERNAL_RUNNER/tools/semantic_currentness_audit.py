#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
REVNO = int(str(META.get('revision_number', REV.replace('rev', '0'))))
PACKAGE = str(META.get('package_name', ''))
ARCHIVE = str(META.get('archive_name', ''))
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)

TOP_DOCS = [
    'README.md',
    'START_HERE.md',
    'START_HERE_SLIM.md',
    'NEXT-TURN-PROMPT.md',
    'PRIORITY-LIST.md',
    'MISSION-KERNEL.md',
    'PROJECT-CHARTER.md',
]
CURRENT_JSON = [
    'CUBE-META.json',
    'REVISION-RECEIPT.json',
    'EVIDENCE-STATUS.json',
    'SURFACE-STATUS.json',
    'REENTRY-CONTRACT.json',
    'BABY-DATACUBE-CANDIDATE.json',
]
STALE_HIGHLIGHTS = [
    'downloadplangate',
    'runnerclosuretrim',
    'runnermanifestfallback',
    'missionwastesemanticdrift',
    'value-norm',
    'value_norm',
    'REV0148_PUBLIC_TRACE_EXTERNAL_RUNNER',
    'REV0149_PUBLIC_TRACE_EXTERNAL_RUNNER',
    'REV0150_PUBLIC_TRACE_EXTERNAL_RUNNER',
    'REV0151_PUBLIC_TRACE_EXTERNAL_RUNNER',
]
CURRENT_TEXT_KEYS = {
    'current_focus', 'fresh_focus', 'current_primary_change', 'current_risk_focus', 'summary',
    'revision_summary', 'one_line_summary', 'current_best_next_step', 'current_center',
    'current_external_runner_packet', 'current_scientific_artifact', 'current_primary_artifact',
    'primary_artifact', 'current_lineage_artifact', 'primary_lineage_artifact', 'current_run_alias',
    'current_snapshot_prepare_alias', 'current_first_trace_status', 'highlight', 'codename',
}


def load(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'_missing': True}


def current_bad_revision_refs(text: str) -> list[str]:
    refs = sorted(set(m.group(0) for m in re.finditer(r'(?i)rev\d{4}', text)))
    return [r for r in refs if r.lower() != REV]


def walk_current_fields(obj: Any, prefix: str = '') -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f'{prefix}.{k}' if prefix else k
            if k in CURRENT_TEXT_KEYS or k.startswith('current_') or k in {'revision', 'revision_number', 'revision_int', 'current_revision', 'current_revision_int', 'evidence_revision', 'package_name', 'archive_name', 'revision_name'}:
                out.append((path, v))
            if isinstance(v, (dict, list)):
                out.extend(walk_current_fields(v, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                out.extend(walk_current_fields(v, f'{prefix}[{i}]'))
    return out


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    per_doc: dict[str, Any] = {}

    expected = {
        'package_name': PACKAGE,
        'archive_name': ARCHIVE,
        'current_external_runner_packet': f'artifacts/external-runner/{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip',
        'current_scientific_artifact': f'artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json',
        'current_lineage_artifact': f'MISSION-AUDIT-{REVUP}.md',
        'primary_lineage_artifact': f'MISSION-AUDIT-{REVUP}.md',
    }

    for rel in TOP_DOCS:
        p = ROOT / rel
        if not p.exists():
            errors.append(f'missing_top_doc:{rel}')
            continue
        head = p.read_text(encoding='utf-8', errors='replace')[:5000]
        stale_refs = current_bad_revision_refs(head)
        stale_terms = [term for term in STALE_HIGHLIGHTS if term in head]
        per_doc[rel] = {'stale_revision_refs': stale_refs, 'stale_terms': stale_terms}
        if REV not in head:
            errors.append(f'{rel}:missing_current_revision_near_top')
        if stale_refs:
            errors.append(f'{rel}:stale_revision_refs_near_top:{stale_refs}')
        if stale_terms:
            errors.append(f'{rel}:stale_terms_near_top:{stale_terms}')
        if 'RUN_CURRENT_PUBLIC_TRACE.sh' not in head and 'RUN_CURRENT_FIRST_REAL_TRACE.sh' not in head and 'RUN_PUBLIC_TRACE.sh' not in head:
            errors.append(f'{rel}:missing_current_runner_entrypoint')

    per_json: dict[str, Any] = {}
    for rel in CURRENT_JSON:
        data = load(rel)
        per_json[rel] = {'present': not data.get('_missing', False), 'errors': []}
        if data.get('_missing'):
            errors.append(f'missing_current_json:{rel}')
            continue
        for key, val in [('revision', REV), ('current_revision', REV), ('evidence_revision', REV), ('package_name', PACKAGE), ('archive_name', ARCHIVE), ('revision_name', PACKAGE)]:
            if key in data and data.get(key) != val:
                msg = f'{rel}:{key}:{data.get(key)!r}!={val!r}'
                errors.append(msg); per_json[rel]['errors'].append(msg)
        for key, val in [('revision_number', REVNO), ('revision_int', REVNO), ('current_revision_int', REVNO)]:
            if key in data and int(data.get(key, -1)) != val:
                msg = f'{rel}:{key}:{data.get(key)!r}!={val!r}'
                errors.append(msg); per_json[rel]['errors'].append(msg)
        for key, val in expected.items():
            if key in data and data.get(key) != val:
                msg = f'{rel}:{key}:{data.get(key)!r}!={val!r}'
                errors.append(msg); per_json[rel]['errors'].append(msg)
        for path, value in walk_current_fields(data):
            if path.endswith('previous_revision') or path.endswith('source_revision'):
                continue
            if isinstance(value, (str, int, float, bool)):
                text = str(value)
                bad_refs = current_bad_revision_refs(text)
                bad_terms = [term for term in STALE_HIGHLIGHTS if term in text]
                if bad_refs:
                    msg = f'{rel}:{path}:stale_revision_refs:{bad_refs}'
                    errors.append(msg); per_json[rel]['errors'].append(msg)
                if bad_terms:
                    msg = f'{rel}:{path}:stale_terms:{bad_terms}'
                    errors.append(msg); per_json[rel]['errors'].append(msg)
            elif isinstance(value, list):
                text = json.dumps(value, sort_keys=True)
                bad_terms = [term for term in STALE_HIGHLIGHTS if term in text]
                if bad_terms:
                    msg = f'{rel}:{path}:stale_terms:{bad_terms}'
                    errors.append(msg); per_json[rel]['errors'].append(msg)

    # Derived runner retention and bytecode are semantic-currentness issues: they cause old surfaces to stay hot.
    pyc = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*.pyc'))
    pycache = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('__pycache__') if p.is_dir())
    if pyc or pycache:
        errors.append('generated_python_bytecode_present')
    ext = ROOT / 'artifacts' / 'external-runner'
    stale_runner = []
    if ext.exists():
        for p in ext.glob('REV*_PUBLIC_TRACE_EXTERNAL_RUNNER*'):
            if not p.name.startswith(f'{REVUP}_'):
                stale_runner.append(p.relative_to(ROOT).as_posix())
    if stale_runner:
        errors.append(f'stale_derived_external_runner_packets:{stale_runner}')

    status = 'pass' if not errors else 'fail'
    audit = {
        'revision': REV,
        'revision_number': REVNO,
        'package_name': PACKAGE,
        'archive_name': ARCHIVE,
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Hard smoke veto for semantic currentness: top docs, baby datacube, current metadata, stable runner references, generated bytecode, and derived external-runner retention must all point at the current first-real-trace lane.',
        'top_docs': per_doc,
        'current_json': per_json,
        'generated_bytecode': {'pyc': pyc, 'pycache': pycache},
        'stale_external_runner_packets': stale_runner,
        'errors': errors,
        'warnings': warnings,
        'decision': 'semantic_currentness_ok' if not errors else 'repair_current_surface_before_more_doctrine',
    }
    (OUT / f'{REVUP}_SEMANTIC_CURRENTNESS_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Semantic currentness audit — {REVUP}',
        '',
        f"Status: `{status}`  ",
        'Promotion allowed: `false`',
        '',
        audit['summary'],
        '',
        '## Errors',
    ]
    md.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    md.extend(['', '## Stale external runner packets'])
    md.extend([f'- `{e}`' for e in stale_runner] if stale_runner else ['- none'])
    (OUT / f'{REVUP}_SEMANTIC_CURRENTNESS_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
