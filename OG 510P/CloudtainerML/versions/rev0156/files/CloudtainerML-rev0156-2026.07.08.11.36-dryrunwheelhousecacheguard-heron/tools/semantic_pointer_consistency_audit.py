#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
REVNO = int(META.get('revision_number', REV.replace('rev','0')))
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
CURRENT_FILES = ['CUBE-META.json','REVISION-RECEIPT.json','EVIDENCE-STATUS.json','SURFACE-STATUS.json','REENTRY-CONTRACT.json','BABY-DATACUBE-CANDIDATE.json']
KEY_RE = re.compile(r'^(current|latest|active|primary|fresh|next|operator)_|^(external_runner_packet|primary_artifact|primary_scientific_artifact|primary_audit|summary|revision_summary|one_line_summary|highlight|codename|revision|revision_kind|revision_name|package_name|archive_name)$|(_entrypoint|_lineage_artifact|_scientific_artifact|_external_runner)$')
HISTORICAL_KEY_RE = re.compile(r'^(rev\d{4}|evidence_summary_rev\d{4}).*', re.I)
STALE_REV_RE = re.compile(r'(?i)rev\d{4}|REV\d{4}')
ALLOW_PREVIOUS_SUFFIX = {'previous_revision','source_revision','previous_revision_int','source_revision_int'}
EXPECTED = {
    'current_external_runner_packet': f'artifacts/external-runner/{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip',
    'latest_external_runner': f'artifacts/external-runner/{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip',
    'external_runner_packet': f'artifacts/external-runner/{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip',
    'current_scientific_artifact': f'artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json',
    'primary_scientific_artifact': f'artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json',
    'current_lineage_artifact': f'MISSION-AUDIT-{REVUP}.md',
    'primary_lineage_artifact': f'MISSION-AUDIT-{REVUP}.md',
    'latest_online_research_note': f'artifacts/research/{REVUP}_ONLINE_RESEARCH_NOTES.md',
}


def walk(obj: Any, prefix=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f'{prefix}.{k}' if prefix else k
            if KEY_RE.search(k) and not HISTORICAL_KEY_RE.match(k):
                yield path, k, v
            if isinstance(v, (dict, list)):
                yield from walk(v, path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                yield from walk(v, f'{prefix}[{i}]')


def stale_refs(text: str):
    refs = sorted(set(m.group(0) for m in STALE_REV_RE.finditer(text)))
    return [r for r in refs if r.lower() != REV]


def main() -> int:
    errors = []
    warnings = []
    per_file = {}
    for rel in CURRENT_FILES:
        path = ROOT / rel
        if not path.exists():
            errors.append(f'missing_current_pointer_file:{rel}')
            continue
        data = json.loads(path.read_text(encoding='utf-8'))
        file_errors = []
        for key, expected in EXPECTED.items():
            if key in data and data.get(key) != expected:
                file_errors.append(f'{key}:{data.get(key)!r}!={expected!r}')
        for dotted, key, value in walk(data):
            if key in ALLOW_PREVIOUS_SUFFIX or dotted.endswith('.previous_revision') or dotted.endswith('.source_revision'):
                continue
            if isinstance(value, (str, int, float, bool)):
                bad = stale_refs(str(value))
                if bad:
                    file_errors.append(f'{dotted}:stale_revision_refs:{bad}')
            elif isinstance(value, list):
                bad = stale_refs(json.dumps(value, sort_keys=True))
                if bad:
                    file_errors.append(f'{dotted}:stale_revision_refs:{bad}')
        per_file[rel] = file_errors
        errors.extend(f'{rel}:{e}' for e in file_errors)
    audit = {
        'revision': REV,
        'revision_number': REVNO,
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'REV0153 audit for semantic pointer drift. It checks current/latest/active/primary/fresh/next runner-facing metadata fields, including fields that were not caught by the narrower REV0152 semantic-currentness veto.',
        'expected': EXPECTED,
        'per_file_errors': per_file,
        'errors': errors,
        'warnings': warnings,
        'decision': 'semantic_pointer_consistency_ok' if not errors else 'repair_latest_current_metadata_before_more_work',
    }
    (OUT / f'{REVUP}_SEMANTIC_POINTER_CONSISTENCY_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [f'# Semantic pointer consistency audit — {REVUP}', '', f"Status: `{audit['status']}`  ", 'Promotion allowed: `false`', '', audit['summary'], '', '## Errors']
    md.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    (OUT / f'{REVUP}_SEMANTIC_POINTER_CONSISTENCY_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
