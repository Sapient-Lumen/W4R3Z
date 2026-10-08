#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'settle_archive_truth.py'


def fail(message: str) -> int:
    print(f'archive-truth-settle-tool: {message}', file=sys.stderr)
    return 1


def main() -> int:
    if not TOOL.exists():
        return fail('missing settle_archive_truth.py')
    proc = subprocess.run(['python3', str(TOOL), '--list-steps'], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('list-steps invocation failed')
    plan = json.loads(proc.stdout)
    if plan.get('tool') != 'settle_archive_truth':
        return fail('tool id mismatch')
    steps = plan.get('steps', [])
    if len(steps) != 33:
        return fail(f'unexpected step count: {len(steps)}')
    commands = [row.get('command') for row in steps]
    required = [
        'make test-quick',
        'make update-command-inventory',
        'make update-validator-inventory',
        'make update-artifact-buckets',
        'make update-archive-size-guardrail-card',
        'make update-archive-byte-triage-card',
        'make update-archive-package-cut-card',
        'make update-archive-reentry-card',
        'make update-archive-handoff-pack',
        'make update-archive-revision-cut-card',
        'make update-archive-zip-lineage-card',
        'make update-archive-zip-chronology-card',
        'make update-archive-zip-authority-card',
        'make update-archive-zip-digest-card',
        'make update-archive-zip-size-truth-card',
        'make test-command-inventory',
        'make test-validator-inventory',
        'make test-artifact-buckets',
        'make test-archive-size-guardrail-card',
        'make test-archive-byte-triage-card',
        'make test-archive-package-cut-card',
        'make test-archive-reentry-card',
        'make test-archive-handoff-pack',
        'make test-archive-handoff-pack-verify-tool',
        'make test-archive-revision-cut-card',
        'make test-archive-zip-lineage-card',
        'make test-archive-zip-chronology-card',
        'make test-archive-zip-authority-card',
        'make test-archive-zip-digest-card',
        'make test-authoritative-archive-zip-verify-tool',
        'make test-archive-zip-size-truth-card',
    ]
    for command in required:
        if command not in commands:
            return fail(f'missing required command: {command}')
    if steps[0].get('command') != 'make test-quick':
        return fail('first step must stay make test-quick')
    if steps[0].get('allow_expected_rust_gate_failure') is not True:
        return fail('first step must allow expected rust gate failure')
    dry = subprocess.run(['python3', str(TOOL), '--dry-run'], cwd=ROOT, text=True, capture_output=True)
    if dry.returncode != 0:
        if dry.stdout:
            print(dry.stdout, end='', file=sys.stderr)
        if dry.stderr:
            print(dry.stderr, end='', file=sys.stderr)
        return fail('dry-run invocation failed')
    missing = [frag for frag in [
        'make test-quick',
        'make update-archive-size-guardrail-card',
        'make update-archive-byte-triage-card',
        'make update-archive-package-cut-card',
        'make update-archive-reentry-card',
        'make update-archive-handoff-pack',
        'make update-archive-revision-cut-card',
        'make update-archive-zip-lineage-card',
        'make update-archive-zip-chronology-card',
        'make update-archive-zip-authority-card',
        'make update-archive-zip-digest-card',
        'make update-archive-zip-size-truth-card',
    ] if frag not in dry.stdout]
    if missing:
        return fail(f'dry-run missing fragments: {missing}')
    print(f'archive-truth-settle-tool: ok (steps={len(steps)} first={steps[0]["command"]})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
