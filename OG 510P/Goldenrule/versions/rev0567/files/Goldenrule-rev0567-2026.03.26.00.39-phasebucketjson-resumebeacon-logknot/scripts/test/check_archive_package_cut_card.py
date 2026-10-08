#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_package_cut_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_PACKAGE_CUT_CARD.md'


def fail(message: str) -> int:
    print(f'archive-package-cut-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(
        ['python3', 'scripts/report/build_archive_package_cut_card.py', '--write'],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('builder drifted or failed')

    if not REPORT_PATH.exists():
        return fail('missing report json')
    if not DOC_PATH.exists():
        return fail('missing rendered doc')

    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    if report.get('card') != 'archive_package_cut_card':
        return fail('card id mismatch')
    mutators = report.get('live_mutators', [])
    steps = report.get('refresh_sequence', [])
    settle = report.get('settle_rule', {})
    if len(mutators) < 2:
        return fail('expected at least two live mutator rows')
    if len(steps) < 15:
        return fail('expected at least fifteen refresh steps')
    commands = [row.get('command') for row in steps]
    required_commands = [
        'make test-quick',
        'make update-command-inventory',
        'make update-validator-inventory',
        'make update-artifact-buckets',
        'make update-archive-size-guardrail-card',
        'make update-archive-byte-triage-card',
        'make update-archive-package-cut-card',
        'make update-archive-reentry-card',
        'make update-archive-revision-cut-card',
        'make update-archive-zip-lineage-card',
        'make update-archive-zip-chronology-card',
        'make update-archive-zip-authority-card',
        'make update-archive-zip-digest-card',
    ]
    for command in required_commands:
        if command not in commands:
            return fail(f'missing required refresh command: {command}')
    if settle.get('fixed_point_pair') != [
        'make update-archive-size-guardrail-card',
        'make update-archive-byte-triage-card',
    ]:
        return fail('unexpected fixed-point pair')
    if report.get('package_hygiene', {}).get('package_boundary_ready') is not True:
        return fail('expected package_boundary_ready to stay true')
    if report.get('canonical_wrapper_command') != 'make settle-archive-truth':
        return fail('canonical wrapper must stay make settle-archive-truth')
    if report.get('revision_planner_command') != 'python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug':
        return fail('revision planner command drifted')
    if report.get('canonical_cut_command') != 'python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"':
        return fail('canonical cut command drifted')
    if report.get('cap_first_markdown_pack_totals', {}).get('recoverable_if_capped_at_128k_bytes', 0) <= 0:
        return fail('recoverable_if_capped_at_128k_bytes must stay positive')

    validation_commands = settle.get('validation_commands', [])
    for command in ['make test-archive-package-cut-card', 'make test-archive-reentry-card', 'make test-archive-handoff-pack-verify-tool', 'make test-authoritative-archive-zip-verify-tool', 'make test-archive-revision-cut-card', 'make test-archive-zip-lineage-card', 'make test-archive-zip-chronology-card', 'make test-archive-zip-authority-card', 'make test-archive-zip-digest-card']:
        if command not in validation_commands:
            return fail(f'missing validation command: {command}')

    text = DOC_PATH.read_text(encoding='utf-8')
    required_fragments = [
        '# Archive Package Cut Card',
        '## Canonical wrapper',
        '`make settle-archive-truth`',
        '`python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`',
        '`python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`',
        '## Live mutators that must run before the final size refresh',
        '`make test-quick`',
        '## Stable package-cut refresh order',
        '## Settle rule',
        'make update-archive-zip-lineage-card',
        'make update-archive-zip-chronology-card',
        'make update-archive-zip-authority-card',
        'make update-archive-zip-digest-card',
        'make test-archive-zip-lineage-card',
        'make test-archive-zip-digest-card',
        'make test-authoritative-archive-zip-verify-tool',
        '## Guardrails',
    ]
    missing = [frag for frag in required_fragments if frag not in text]
    if missing:
        return fail(f'missing required doc fragments: {missing}')

    print(
        'archive-package-cut-card: ok '
        f"(protected_bytes={report['protected_stack_totals']['raw_bytes']} recoverable={report['cap_first_markdown_pack_totals']['recoverable_if_capped_at_128k_bytes']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
