#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0099'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
CANON = ROOT / 'OPEN-QUESTIONS.md'
SHIM = ROOT / 'OPEN_QUESTIONS.md'


def main() -> int:
    errors: list[str] = []
    debt: list[str] = []
    canon_text = CANON.read_text(encoding='utf-8', errors='replace') if CANON.exists() else ''
    shim_text = SHIM.read_text(encoding='utf-8', errors='replace') if SHIM.exists() else ''
    if not CANON.exists():
        errors.append('missing_canonical_open_questions')
    if not SHIM.exists():
        errors.append('missing_compatibility_open_questions_shim')
    if REV not in canon_text[:500]:
        errors.append('canonical_open_questions_not_current')
    if REV not in shim_text[:500]:
        errors.append('shim_open_questions_not_current')
    if 'Canonical file: `OPEN-QUESTIONS.md`' not in shim_text:
        errors.append('open_questions_shim_not_pointing_to_canonical')
    if len(shim_text.splitlines()) > 8:
        debt.append('shim_too_long_for_compatibility_surface')
    if 'ALLOW_NETWORK_DRY_RUN=1' not in canon_text:
        errors.append('canonical_questions_missing_dry_run_gate_question')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'fail' if errors else ('pass_with_debt' if debt else 'pass'),
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Small refactor audit for duplicated open-question surfaces. The hyphenated file is canonical; the underscore file is a current compatibility shim only.',
        'canonical': 'OPEN-QUESTIONS.md',
        'shim': 'OPEN_QUESTIONS.md',
        'errors': errors,
        'debt': debt,
    }
    (OUT / f'{REVUP}_OPEN_QUESTIONS_SURFACE_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_OPEN_QUESTIONS_SURFACE_AUDIT.md').write_text(
        f'# Open questions surface audit — {REVUP}\n\n'
        f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        '## Errors\n\n' + ('\n'.join(f'- `{e}`' for e in errors) if errors else '- none') + '\n\n'
        '## Debt\n\n' + ('\n'.join(f'- `{d}`' for d in debt) if debt else '- none') + '\n\n'
        '## Interpretation\n\nThis is a small anti-bureaucracy refactor: retain the compatibility filename, but prevent two divergent open-question surfaces from accumulating stale mission guidance.\n',
        encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'debt': debt}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
