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
REVNO = int(str(META.get('revision_number', REV.replace('rev','0'))))
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
EXT = ROOT / 'artifacts' / 'external-runner'
RUNNER_RE = re.compile(r'REV(\d{4})_PUBLIC_TRACE_EXTERNAL_RUNNER(?:\.zip)?$')


def classify(path: Path) -> dict[str, Any]:
    m = RUNNER_RE.match(path.name)
    revno = int(m.group(1)) if m else None
    return {
        'path': path.relative_to(ROOT).as_posix(),
        'name': path.name,
        'is_dir': path.is_dir(),
        'is_file': path.is_file(),
        'bytes': sum(p.stat().st_size for p in path.rglob('*') if p.is_file()) if path.is_dir() else (path.stat().st_size if path.is_file() else 0),
        'revision_number': revno,
        'current': revno == REVNO,
        'derived_external_runner_packet': bool(m),
    }


def main() -> int:
    items = [classify(p) for p in sorted(EXT.iterdir()) if RUNNER_RE.match(p.name)] if EXT.exists() else []
    stale = [x for x in items if x.get('derived_external_runner_packet') and not x.get('current')]
    current = [x for x in items if x.get('current')]
    errors: list[str] = []
    warnings: list[str] = []
    if len(current) < 2:
        errors.append('missing_current_external_runner_dir_or_zip')
    if stale:
        warnings.append('stale_derived_external_runner_packets_present')
    audit = {
        'revision': REV,
        'revision_number': REVNO,
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors and not stale else ('warn' if not errors else 'fail'),
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Retention audit for derived external-runner packets. Only the current compact runner should stay hot in the active package; older runner packets are derivable from prior revision archives and add confusion/bytes without moving the first real trace forward.',
        'external_runner_dir': EXT.relative_to(ROOT).as_posix(),
        'items': items,
        'current_items': current,
        'stale_items': stale,
        'stale_bytes': sum(int(x.get('bytes') or 0) for x in stale),
        'errors': errors,
        'warnings': warnings,
        'decision': 'current_external_runner_only_hot' if not errors and not stale else 'prune_stale_derived_external_runner_packets',
    }
    (OUT / f'{REVUP}_CURRENT_EXTERNAL_RUNNER_RETENTION_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Current external runner retention audit — {REVUP}',
        '',
        f"Status: `{audit['status']}`  ",
        'Promotion allowed: `false`',
        '',
        audit['summary'],
        '',
        f"Stale derived runner bytes: `{audit['stale_bytes']}`",
        '',
        '## Stale items',
        '',
    ]
    md.extend([f"- `{x['path']}` ({x['bytes']} bytes)" for x in stale] if stale else ['- none'])
    md.extend(['', '## Errors', ''])
    md.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    md.extend(['', '## Warnings', ''])
    md.extend([f'- `{w}`' for w in warnings] if warnings else ['- none'])
    (OUT / f'{REVUP}_CURRENT_EXTERNAL_RUNNER_RETENTION_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'stale_count': len(stale), 'stale_bytes': audit['stale_bytes'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
