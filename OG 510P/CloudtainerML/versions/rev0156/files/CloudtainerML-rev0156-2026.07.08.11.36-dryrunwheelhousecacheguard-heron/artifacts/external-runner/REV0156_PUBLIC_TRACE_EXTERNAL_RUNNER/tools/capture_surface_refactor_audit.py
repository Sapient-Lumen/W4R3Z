#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0096'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
ACTIVE = [
    f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh',
    f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh',
    f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh',
    'artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh',
    'artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh',
]
TOP_DOCS = ['START_HERE.md','START_HERE_SLIM.md','README.md','PRIORITY-LIST.md','NEXT-TURN-PROMPT.md','MISSION-KERNEL.md']


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def main() -> int:
    scripts = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'artifacts'/'capture-kit').glob('REV*.sh'))
    historical = [s for s in scripts if not s.startswith(f'artifacts/capture-kit/{REVUP}_')]
    docs = {rel: read(rel)[:5000] for rel in TOP_DOCS}
    errors: list[str] = []
    debt: list[str] = []
    for active in ACTIVE:
        if not (ROOT/active).exists():
            errors.append('missing_active_capture_script:' + active)
    for rel, text in docs.items():
        if REV not in text:
            errors.append('top_doc_not_current_near_top:' + rel)
        if rel in ['START_HERE.md','START_HERE_SLIM.md','PRIORITY-LIST.md','NEXT-TURN-PROMPT.md']:
            if 'RUN_CURRENT_PUBLIC_TRACE.sh' not in text and f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in text:
                errors.append('top_doc_missing_current_trace_entrypoint:' + rel)
    if len(historical) > 10:
        debt.append('capture_kit_history_retained_but_deprioritized')
    if len(list(ROOT.glob('MISSION-AUDIT-REV*.md'))) > 12:
        debt.append('mission_audit_history_retained_but_deprioritized')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'fail' if errors else ('pass_with_debt' if debt else 'pass'),
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Audit/refactor of the live capture surface. the current revision accepts stable RUN_CURRENT/PREPARE_CURRENT aliases as the active surface while retaining revision-specific wrappers for provenance and checksums.',
        'active_capture_scripts': ACTIVE,
        'historical_capture_script_count': len(historical),
        'historical_capture_scripts_sample': historical[:25],
        'top_docs_checked': TOP_DOCS,
        'errors': errors,
        'debt': debt,
        'refactor_actions': [
            'kept stable RUN_CURRENT_PUBLIC_TRACE.sh alias to stop top-level docs chasing revision-numbered wrappers',
            'added runtime surface probe before capture',
            'added exact HF snapshot materializer before capture',
            'left old scripts and audits as provenance, not current instructions'
        ],
    }
    json_path = OUT / f'{REVUP}_CAPTURE_SURFACE_REFACTOR_AUDIT.json'
    md_path = OUT / f'{REVUP}_CAPTURE_SURFACE_REFACTOR_AUDIT.md'
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md_path.write_text('# Capture surface refactor audit — ' + REVUP + '\n\n'
        + f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        + '## Active scripts\n\n' + '\n'.join(f'- `{s}`' for s in ACTIVE) + '\n\n'
        + f"Historical capture scripts retained: `{len(historical)}`\n\n"
        + '## Errors\n\n' + ('\n'.join(f'- `{e}`' for e in errors) if errors else '- none') + '\n\n'
        + '## Debt\n\n' + ('\n'.join(f'- `{d}`' for d in debt) if debt else '- none') + '\n\n'
        + '## Interpretation\n\nThe live path is now stable alias -> current revision-specific packet. Historical files remain for provenance and should not be edited before the real trace/timing question is resolved.\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'debt': debt}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
