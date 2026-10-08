#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def fail(message: str) -> int:
    print(f'archive-revision-cut-tool: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(
        [
            'python3',
            'scripts/tools/cut_archive_revision.py',
            '--descriptor',
            'demo-cut',
            '--summary',
            'demo summary bullet',
            '--timestamp',
            '2026.03.23.10.00',
            '--dry-run',
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('dry-run failed')
    payload = json.loads(proc.stdout)
    if payload.get('tool') != 'cut_archive_revision':
        return fail('tool id mismatch')
    current_label = payload.get('current_revision_label')
    next_label = payload.get('next_revision_label')
    if not isinstance(current_label, str) or not current_label.startswith('rev'):
        return fail('current revision label drifted')
    current_num = int(current_label[3:])
    expected_next = f'rev{current_num + 1:04d}'
    if next_label != expected_next:
        return fail('next revision label drifted')
    if payload.get('next_root_name') != f'Goldenrule-{expected_next}-2026.03.23.10.00-demo-cut':
        return fail('unexpected next root name')
    if not str(payload.get('zip_path', '')).endswith(f'Goldenrule-{expected_next}-2026.03.23.10.00-demo-cut.zip'):
        return fail('unexpected zip path stem')
    if payload.get('pre_settle_command') != 'python3 scripts/tools/settle_archive_truth.py':
        return fail('pre-settle command drifted')
    preview = payload.get('changelog_entry_preview', '')
    if f'## {expected_next} - 2026-03-23' not in preview or '- demo summary bullet' not in preview:
        return fail('missing changelog preview')
    for command in [
        'make update-archive-package-cut-card',
        'make update-archive-reentry-card',
        'make update-archive-handoff-pack',
        'make update-archive-revision-cut-card',
        'make update-archive-zip-lineage-card',
        'make update-archive-zip-chronology-card',
        'make update-archive-zip-authority-card',
        'make update-archive-zip-digest-card',
        'make update-archive-zip-size-truth-card',
    ]:
        if command not in payload.get('post_rename_refresh_commands', []):
            return fail(f'missing refresh command: {command}')
    for command in [
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
    ]:
        if command not in payload.get('post_rename_validate_commands', []):
            return fail(f'missing validate command: {command}')
    print(f'archive-revision-cut-tool: ok (next={expected_next} dry_run_json=valid)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
