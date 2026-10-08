#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_history.json'
PROCESS_DIR = ROOT / 'artifacts' / 'process'


def main() -> int:
    payload = json.loads(REPORT.read_text(encoding='utf-8'))
    receipts = sorted(path for path in PROCESS_DIR.glob('cloudtainer_shadow_pass_*.json') if path.name != 'cloudtainer_shadow_pass_checkpoint.json')
    timeline = payload.get('receipt_timeline') or []
    summary = payload.get('summary') or {}
    growth = payload.get('profile_growth') or {}
    frontier_ranges = payload.get('current_profile_frontier_ranges') or []
    heaviest = payload.get('recurring_heaviest_steps') or []

    if len(timeline) != len(receipts) or int(summary.get('receipt_count', -1)) != len(receipts):
        print('shadow-pass-history: receipt count mismatch', file=sys.stderr)
        return 1
    if str(summary.get('latest_receipt')) != receipts[-1].relative_to(ROOT).as_posix():
        print('shadow-pass-history: latest receipt mismatch', file=sys.stderr)
        return 1
    max_step_count = max(int(entry.get('step_count', 0)) for entry in timeline)
    if int(summary.get('current_profile_step_count', -1)) != max_step_count:
        print('shadow-pass-history: current profile step count mismatch', file=sys.stderr)
        return 1
    expected_current_profile_count = sum(1 for entry in timeline if int(entry.get('step_count', 0)) == max_step_count)
    if int(summary.get('current_profile_receipt_count', -1)) != expected_current_profile_count:
        print('shadow-pass-history: current profile receipt count mismatch', file=sys.stderr)
        return 1
    if int(growth.get('latest_step_count', -1)) != max_step_count:
        print('shadow-pass-history: profile growth latest step count mismatch', file=sys.stderr)
        return 1
    frontier_labels = {str(entry.get('label')) for entry in frontier_ranges}
    required_frontiers = {'boundary_known', 'maps_contracts_coverage', 'queue_inputs_ready', 'static_comeback_plan_closed', 'archive_hygiene_synced', 'full_shadow_pass'}
    if not required_frontiers.issubset(frontier_labels):
        print('shadow-pass-history: missing frontier stability rows', file=sys.stderr)
        return 1
    if not heaviest:
        print('shadow-pass-history: missing recurring heaviest steps', file=sys.stderr)
        return 1

    print(
        'shadow-pass-history: ok '
        f"(receipts={len(receipts)} current_profile={expected_current_profile_count} latest={Path(str(summary.get('latest_receipt'))).name})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
