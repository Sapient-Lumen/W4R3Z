#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_rustup_plan.json'
MD_PATH = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md'


def main() -> int:
    if not JSON_PATH.exists():
        print('cloudtainer-userspace-rustup-plan: missing json report', file=sys.stderr)
        return 1
    if not MD_PATH.exists():
        print('cloudtainer-userspace-rustup-plan: missing markdown report', file=sys.stderr)
        return 1

    payload = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    summary = payload.get('summary') or {}
    plan = payload.get('plan') or {}
    phase_ids = [phase.get('phase_id') for phase in (plan.get('phases') or [])]
    expected = ['env', 'bootstrap', 'toolchain', 'warm_cache', 'first_proof', 'cleanup']
    if phase_ids != expected:
        print(f'cloudtainer-userspace-rustup-plan: unexpected phase ids {phase_ids!r}', file=sys.stderr)
        return 1
    if summary.get('current_state_code') != 'junest_binary_missing':
        print('cloudtainer-userspace-rustup-plan: expected junest_binary_missing state in current cloudtainer', file=sys.stderr)
        return 1
    transient = summary.get('transient_roots') or []
    if transient != ['.local/cargo', '.local/rustup', '.local/target']:
        print(f'cloudtainer-userspace-rustup-plan: unexpected transient roots {transient!r}', file=sys.stderr)
        return 1
    shellish = '\n'.join(cmd for phase in plan['phases'] for cmd in (phase.get('commands') or []))
    for needle in ['cargo fetch --locked', 'CARGO_TARGET_DIR', 'rustup toolchain install stable --profile minimal --component rustfmt']:
        if needle not in shellish:
            print(f'cloudtainer-userspace-rustup-plan: missing command fragment {needle!r}', file=sys.stderr)
            return 1
    md = MD_PATH.read_text(encoding='utf-8')
    for needle in ['make show-cloudtainer-userspace-rustup-plan', 'transient roots', 'cargo fetch --locked']:
        if needle not in md:
            print(f'cloudtainer-userspace-rustup-plan: markdown missing {needle!r}', file=sys.stderr)
            return 1

    print('cloudtainer-userspace-rustup-plan: ok (state=junest_binary_missing phases=6)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
