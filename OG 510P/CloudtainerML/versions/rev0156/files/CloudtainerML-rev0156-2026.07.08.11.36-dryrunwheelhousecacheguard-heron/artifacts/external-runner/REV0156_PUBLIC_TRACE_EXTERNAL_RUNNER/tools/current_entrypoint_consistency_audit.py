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
STABLE_RUN = 'artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh'
STABLE_PREP = 'artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh'
CURRENT_RUN = f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'
CURRENT_PREP = f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh'
REV_SCRIPT_RE = re.compile(r'REV(\d{4})_[A-Z0-9_]+\.sh')


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def stale_script_mentions(text: str) -> list[str]:
    out = []
    for m in REV_SCRIPT_RE.finditer(text):
        rev = 'REV' + m.group(1)
        if rev != REVUP:
            out.append(m.group(0))
    return sorted(set(out))


def main() -> int:
    errors: list[str] = []
    debt: list[str] = []
    stale_near_top: dict[str, list[str]] = {}
    for rel in [STABLE_RUN, STABLE_PREP, CURRENT_RUN, CURRENT_PREP]:
        if not (ROOT / rel).exists():
            errors.append('missing_current_entrypoint:' + rel)
    run_alias = read(STABLE_RUN)
    prep_alias = read(STABLE_PREP)
    if f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in run_alias:
        errors.append('stable_run_alias_not_current_revision')
    if f'{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh' not in prep_alias:
        errors.append('stable_prepare_alias_not_current_revision')
    for rel in TOP_DOCS:
        head = read(rel)[:3500]
        if REV not in head:
            errors.append('top_doc_missing_current_revision:' + rel)
        if 'RUN_CURRENT_PUBLIC_TRACE.sh' not in head and f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in head:
            errors.append('top_doc_missing_current_run_alias:' + rel)
        stale = stale_script_mentions(head)
        if stale:
            stale_near_top[rel] = stale
    if stale_near_top:
        errors.append('stale_revision_entrypoints_near_top')
    capture_scripts = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'artifacts' / 'capture-kit').glob('REV*.sh'))
    old_scripts = [x for x in capture_scripts if not x.startswith(f'artifacts/capture-kit/{REVUP}_')]
    if old_scripts:
        debt.append(f'{len(old_scripts)} historical capture scripts retained as provenance only')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'fail' if errors else ('pass_with_debt' if debt else 'pass'),
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Audit/refactor of the current execution surface. It enforces stable aliases pointing at the current trace packet and prevents top-level docs from reopening old revision wrappers.',
        'stable_run_alias': STABLE_RUN,
        'stable_prepare_alias': STABLE_PREP,
        'current_run_wrapper': CURRENT_RUN,
        'current_prepare_wrapper': CURRENT_PREP,
        'top_docs_checked': TOP_DOCS,
        'stale_revision_entrypoints_near_top': stale_near_top,
        'historical_capture_script_count': len(old_scripts),
        'historical_capture_scripts_sample': old_scripts[-20:],
        'errors': errors,
        'debt': debt,
        'decision': 'current_entrypoint_surface_ok' if not errors else 'repair_top_docs_or_aliases_before_next_capture_attempt',
    }
    (OUT / f'{REVUP}_CURRENT_ENTRYPOINT_CONSISTENCY_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_CURRENT_ENTRYPOINT_CONSISTENCY_AUDIT.md').write_text(
        f'# Current entrypoint consistency audit — {REVUP}\n\n'
        f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        f"Stable run alias: `{STABLE_RUN}`  \nStable prepare alias: `{STABLE_PREP}`\n\n"
        '## Errors\n\n' + ('\n'.join(f'- `{e}`' for e in errors) if errors else '- none') + '\n\n'
        '## Debt\n\n' + ('\n'.join(f'- `{d}`' for d in debt) if debt else '- none') + '\n\n'
        '## Interpretation\n\nThis is the small refactor that prevents execution drag: operators start from one stable alias while revisioned wrappers remain for provenance.\n',
        encoding='utf-8'
    )
    print(json.dumps({'status': audit['status'], 'errors': errors, 'debt': debt}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
