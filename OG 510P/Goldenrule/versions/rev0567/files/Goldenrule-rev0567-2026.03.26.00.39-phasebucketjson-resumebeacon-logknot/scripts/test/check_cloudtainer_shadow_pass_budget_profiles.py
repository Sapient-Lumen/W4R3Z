#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'tools' / 'cloudtainer_shadow_pass.py'
FRONTIER = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_frontier.json'

def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['python3', str(SCRIPT), *args], cwd=ROOT, capture_output=True, text=True)

def main() -> int:
    listed = run('--list-budget-profiles')
    if listed.returncode != 0 or 'short_budget:' not in listed.stdout or 'medium_budget:' not in listed.stdout or 'long_budget:' not in listed.stdout:
        sys.stderr.write(listed.stdout)
        sys.stderr.write(listed.stderr)
        print('shadow-pass-budget-profiles: could not list known profiles', file=sys.stderr)
        return 1

    bad = run('--budget-profile', 'short_budget', '--stop-after-step', '1')
    if bad.returncode == 0 or '--budget-profile cannot be combined with --stop-after-step' not in (bad.stderr + bad.stdout):
        sys.stderr.write(bad.stdout)
        sys.stderr.write(bad.stderr)
        print('shadow-pass-budget-profiles: expected option conflict to fail', file=sys.stderr)
        return 1

    report = json.loads(FRONTIER.read_text(encoding='utf-8'))
    frontier_by_label = {str(entry['label']): entry for entry in report.get('frontiers') or []}
    profile_by_label = {str(entry['label']): entry for entry in report.get('recommended_budget_prefixes') or []}
    short_frontier = frontier_by_label[str(profile_by_label['short_budget']['frontier_label'])]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        checkpoint = tmp / 'shadow_checkpoint.json'
        receipt = tmp / 'shadow_receipt.json'
        first = run('--budget-profile', 'short_budget', '--checkpoint', str(checkpoint), '--output', str(receipt), '--print-path-only')
        if first.returncode != 0:
            sys.stderr.write(first.stdout)
            sys.stderr.write(first.stderr)
            print('shadow-pass-budget-profiles: short budget run failed', file=sys.stderr)
            return 1
        if not checkpoint.exists() or receipt.exists():
            print('shadow-pass-budget-profiles: expected checkpoint without final receipt after intentional budget stop', file=sys.stderr)
            return 1
        partial = json.loads(checkpoint.read_text(encoding='utf-8'))
        if partial.get('run_status') != 'intentional_stop':
            print('shadow-pass-budget-profiles: checkpoint did not record intentional_stop', file=sys.stderr)
            return 1
        expected_index = int(short_frontier['step_index'])
        if partial.get('completed_step_count') != expected_index or partial.get('next_step_index') != expected_index:
            print('shadow-pass-budget-profiles: checkpoint step counts do not match short_budget frontier', file=sys.stderr)
            return 1
        completed_ids = partial.get('completed_step_ids') or []
        if not completed_ids or completed_ids[-1] != short_frontier['step_id']:
            print('shadow-pass-budget-profiles: checkpoint stopped on the wrong frontier step', file=sys.stderr)
            return 1

    print(f"shadow-pass-budget-profiles: ok (short_budget stops at step {short_frontier['step_index']} id={short_frontier['step_id']})")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
