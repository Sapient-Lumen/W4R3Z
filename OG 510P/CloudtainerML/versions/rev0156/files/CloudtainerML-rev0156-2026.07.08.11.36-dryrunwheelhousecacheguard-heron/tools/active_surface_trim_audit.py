#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0098'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
TOP_DOCS = ['START_HERE.md', 'START_HERE_SLIM.md', 'README.md', 'PRIORITY-LIST.md', 'NEXT-TURN-PROMPT.md', 'MISSION-KERNEL.md']
ACTIVE = f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'
STABLE = 'artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh'
PREPARE = 'artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh'
REV_SCRIPT_RE = re.compile(r'REV(\d{4})_[A-Z0-9_]+\.sh')


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def stale_script_mentions(text: str) -> list[str]:
    out = []
    for m in REV_SCRIPT_RE.finditer(text):
        if 'REV' + m.group(1) != REVUP:
            out.append(m.group(0))
    return sorted(set(out))


def main() -> int:
    errors: list[str] = []
    debt: list[str] = []
    stale_near_top: dict[str, list[str]] = {}
    for rel in [ACTIVE, STABLE, PREPARE]:
        if not (ROOT / rel).exists():
            errors.append('missing_active_surface:' + rel)
    if f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in read(STABLE):
        errors.append('stable_run_alias_not_current')
    if f'{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh' not in read(PREPARE):
        errors.append('stable_prepare_alias_not_current')
    for rel in TOP_DOCS:
        text = read(rel)
        head = text[:3500]
        if REV not in head:
            errors.append('top_doc_missing_current_revision:' + rel)
        if 'RUN_CURRENT_PUBLIC_TRACE.sh' not in head and f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in head:
            errors.append('top_doc_missing_current_trace_entrypoint:' + rel)
        stales = stale_script_mentions(head)
        if stales:
            stale_near_top[rel] = stales
    if stale_near_top:
        errors.append('stale_previous_entrypoints_near_top')
    scripts = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'artifacts' / 'capture-kit').glob('REV*.sh'))
    historical = [s for s in scripts if not s.startswith(f'artifacts/capture-kit/{REVUP}_')]
    if historical:
        errors.append(f'historical_revision_specific_capture_scripts_retained:{len(historical)}')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'fail' if errors else ('pass_with_debt' if debt else 'pass'),
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Refactor audit for live entrypoints. The current revision keeps stable RUN_CURRENT/PREPARE_CURRENT aliases so future docs do not keep chasing revision-numbered wrappers.',
        'active_wrapper': ACTIVE,
        'stable_current_wrapper': STABLE,
        'stable_prepare_wrapper': PREPARE,
        'top_docs_checked': TOP_DOCS,
        'stale_previous_entrypoints_near_top': stale_near_top,
        'historical_capture_script_count': len(historical),
        'errors': errors,
        'debt': debt,
    }
    (OUT / f'{REVUP}_ACTIVE_SURFACE_TRIM_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_ACTIVE_SURFACE_TRIM_AUDIT.md').write_text(
        f'# Active surface trim audit — {REVUP}\n\n'
        f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        f"Stable run wrapper: `{STABLE}`  \nStable prepare wrapper: `{PREPARE}`\n\n"
        '## Errors\n\n' + ('\n'.join(f'- `{e}`' for e in errors) if errors else '- none') + '\n\n'
        '## Debt\n\n' + ('\n'.join(f'- `{d}`' for d in debt) if debt else '- none') + '\n\n'
        '## Interpretation\n\nThis removes execution drag: a future runner can use the stable alias and still land on the current revision-specific packet. Historical scripts are now pruned from the active capture-kit; provenance remains in prior archives and PRUNED-ARTIFACTS records.\n',
        encoding='utf-8'
    )
    print(json.dumps({'status': audit['status'], 'errors': errors, 'debt': debt}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
