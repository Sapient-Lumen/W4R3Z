#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_revision_cut_card.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_REVISION_CUT_CARD.md'


def fail(message: str) -> int:
    print(f'archive-revision-cut-card: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(['python3', 'scripts/report/build_archive_revision_cut_card.py', '--write'], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout, end='', file=sys.stderr)
        print(proc.stderr, end='', file=sys.stderr)
        return fail('builder drifted or failed')
    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    identity = report['current_archive_identity']
    next_plan = report['next_revision_plan']
    prereq = report['cut_prerequisites']
    if report.get('card') != 'archive_revision_cut_card':
        return fail('card id mismatch')
    if report['changelog_alignment']['aligned_to_root'] is not True:
        return fail('changelog head must align to current root')
    if next_plan['next_revision_label'] != f"rev{int(identity['revision']) + 1:04d}":
        return fail('next revision label must be current revision + 1')
    if prereq['settle_command'] != 'make settle-archive-truth':
        return fail('settle command drifted')
    if prereq['package_boundary_ready'] is not True:
        return fail('package boundary must stay ready')
    plan_proc = subprocess.run(['python3', 'scripts/tools/plan_archive_revision_cut.py', '--descriptor', 'head-pointer-guard', '--timestamp', '2026.03.23.09.27'], cwd=ROOT, text=True, capture_output=True)
    if plan_proc.returncode != 0:
        print(plan_proc.stdout, end='', file=sys.stderr)
        print(plan_proc.stderr, end='', file=sys.stderr)
        return fail('planner tool failed')
    plan = json.loads(plan_proc.stdout)
    if plan['next_revision_label'] != next_plan['next_revision_label']:
        return fail('planner tool and card disagree on next revision label')
    if plan['next_root_name'] != f"Goldenrule-{next_plan['next_revision_label']}-2026.03.23.09.27-head-pointer-guard":
        return fail('unexpected next_root_name')
    if next_plan['cutter_command_template'] != 'python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"':
        return fail('cutter command drifted')
    text = DOC_PATH.read_text(encoding='utf-8')
    for frag in ['# Archive Revision Cut Card', '## Current head and alignment', '## Next revision naming contract', '## Cut prerequisites', '`make settle-archive-truth`', '`python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`', '`python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`']:
        if frag not in text:
            return fail(f'missing doc fragment: {frag}')
    print(f"archive-revision-cut-card: ok (current={identity['revision_label']} next={next_plan['next_revision_label']})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
