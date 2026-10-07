#!/usr/bin/env python3
"""Keep CONTEXT_PACK.json compact enough to remain a real reentry packet."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

MAX_BYTES = 4096
MAX_MUST_READ = 20
MAX_CONTROL_SURFACES = 16
MAX_QUICK_CHECKS = 8


def check(root: pathlib.Path) -> dict:
    path = root / 'CONTEXT_PACK.json'
    pack = json.loads(path.read_text(encoding='utf-8'))
    size = path.stat().st_size
    must_read = pack.get('must_read', [])
    control_surfaces = pack.get('control_surfaces', {})
    quick_checks = pack.get('quick_checks', {})
    checks = [
        {'name':'max_bytes', 'status':'pass' if size <= MAX_BYTES else 'fail', 'details':f'size={size} max={MAX_BYTES}'},
        {'name':'max_must_read_entries', 'status':'pass' if len(must_read) <= MAX_MUST_READ else 'fail', 'details':f'must_read={len(must_read)} max={MAX_MUST_READ}'},
        {'name':'max_control_surface_entries', 'status':'pass' if len(control_surfaces) <= MAX_CONTROL_SURFACES else 'fail', 'details':f'control_surfaces={len(control_surfaces)} max={MAX_CONTROL_SURFACES}'},
        {'name':'max_quick_checks', 'status':'pass' if len(quick_checks) <= MAX_QUICK_CHECKS else 'fail', 'details':f'quick_checks={len(quick_checks)} max={MAX_QUICK_CHECKS}'},
    ]
    failures = [c for c in checks if c['status'] == 'fail']
    return {
        'status':'pass' if not failures else 'fail',
        'context_pack_path':'CONTEXT_PACK.json',
        'summary':{'checks_passed':len(checks)-len(failures),'checks_failed':len(failures),'bytes':size,'must_read_count':len(must_read),'control_surface_count':len(control_surfaces),'quick_check_count':len(quick_checks)},
        'checks':checks,
        'fail_closed_rule':'If the context pack stops being compact, default to no publication and trim it back before treating it as a reentry packet.'
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--write-report', default='')
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
