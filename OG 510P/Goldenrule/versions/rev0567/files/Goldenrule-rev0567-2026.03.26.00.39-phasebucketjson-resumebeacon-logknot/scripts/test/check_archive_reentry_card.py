#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_reentry_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_REENTRY_CARD.md'


def fail(message: str) -> int:
    print(f'archive-reentry-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(
        ['python3', 'scripts/report/build_archive_reentry_card.py', '--write'],
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
    if report.get('card') != 'archive_reentry_card':
        return fail('card id mismatch')
    identity = report.get('archive_identity', {})
    blocked = report.get('blocked_cloudtainer_role', {})
    rust = report.get('first_rust_machine_role', {})
    package = report.get('package_cut_role', {})
    align = report.get('changelog_alignment', {})

    if not str(identity.get('root_name', '')).startswith('Goldenrule-rev'):
        return fail('unexpected root_name')
    if blocked.get('primary_command') != 'make cloudtainer-shadow-pass-medium':
        return fail('blocked primary command drifted')
    if rust.get('quick_foothold_prefix') != 1:
        return fail('quick foothold prefix must stay 1')
    if rust.get('full_closure_prefix') != 10:
        return fail('full closure prefix must stay 10')
    if package.get('primary_gate_command') != 'make test-quick':
        return fail('package primary gate must stay make test-quick')
    if package.get('primary_settle_command') != 'make settle-archive-truth':
        return fail('package primary settle command must stay make settle-archive-truth')
    if package.get('handoff_pack_open_doc') != 'docs/ARCHIVE_HANDOFF_PACK.md':
        return fail('package handoff pack doc drifted')
    if package.get('handoff_pack_verify_command') != 'make test-archive-handoff-pack':
        return fail('package handoff pack verify command drifted')
    if package.get('revision_planner_command') != 'python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug':
        return fail('package revision planner command drifted')
    if package.get('canonical_cut_command') != 'python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"':
        return fail('package canonical cut command drifted')
    if package.get('external_digest_verify_command') != 'python3 scripts/tools/verify_authoritative_archive_zip.py':
        return fail('external digest verify command drifted')
    if package.get('package_boundary_ready') is not True:
        return fail('package boundary should stay ready')
    if align.get('aligned_to_root') is not True:
        return fail('changelog head must align to root revision')
    if not package.get('diet_first_paths'):
        return fail('expected diet_first_paths to be non-empty')

    text = DOC_PATH.read_text(encoding='utf-8')
    required_fragments = [
        '# Archive Reentry Card',
        '## Current archive head',
        '## Blocked cloudtainer role',
        '## First Rust-capable machine role',
        '## Package-cut steward role',
        '`make cloudtainer-shadow-pass-medium`',
        '`make settle-archive-truth`',
        '`docs/ARCHIVE_HANDOFF_PACK.md`',
        '`make test-archive-handoff-pack`',
        '`python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`',
        '`python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`',
        '`python3 scripts/tools/verify_authoritative_archive_zip.py`',
        '`make test-quick`',
    ]
    missing = [frag for frag in required_fragments if frag not in text]
    if missing:
        return fail(f'missing required doc fragments: {missing}')

    print(
        'archive-reentry-card: ok '
        f"(root={identity['revision_label']} blocked={blocked['current_state_code']} package_ready={package['package_boundary_ready']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
