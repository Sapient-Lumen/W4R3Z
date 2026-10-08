#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_volatility.json'
PROCESS_DIR = ROOT / 'artifacts' / 'process'
REQUIRED_FRONTIERS = {
    'boundary_known',
    'maps_contracts_coverage',
    'queue_inputs_ready',
    'static_comeback_plan_closed',
    'archive_hygiene_synced',
    'full_shadow_pass',
}
ALLOWED_CLASSES = {'single_sample', 'stable', 'watch', 'jittery'}


def main() -> int:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    summary = report.get('summary') or {}
    lane_stats = report.get('current_profile_lane_stats') or []
    frontier_stats = report.get('frontier_step_stats') or []
    step_stats = report.get('step_stats') or []
    jittery = report.get('top_jittery_steps') or []
    stable = report.get('most_stable_nontrivial_steps') or []

    receipts = sorted(path for path in PROCESS_DIR.glob('cloudtainer_shadow_pass_*.json') if path.name != 'cloudtainer_shadow_pass_checkpoint.json')
    if not receipts:
        print('shadow-pass-volatility: no receipts found', file=sys.stderr)
        return 1

    payloads = [json.loads(path.read_text(encoding='utf-8')) for path in receipts]
    max_step_count = max(len(payload.get('steps') or []) for payload in payloads)
    current_profile_count = sum(1 for payload in payloads if len(payload.get('steps') or []) == max_step_count)

    if int(summary.get('receipt_count', -1)) != len(receipts):
        print('shadow-pass-volatility: receipt count mismatch', file=sys.stderr)
        return 1
    if int(summary.get('current_profile_receipt_count', -1)) != current_profile_count:
        print('shadow-pass-volatility: current-profile receipt count mismatch', file=sys.stderr)
        return 1
    if int(summary.get('current_profile_step_count', -1)) != max_step_count:
        print('shadow-pass-volatility: current-profile step count mismatch', file=sys.stderr)
        return 1
    if str(summary.get('latest_receipt')) != receipts[-1].relative_to(ROOT).as_posix():
        print('shadow-pass-volatility: latest receipt mismatch', file=sys.stderr)
        return 1
    if not lane_stats or not frontier_stats or not step_stats:
        print('shadow-pass-volatility: missing expected sections', file=sys.stderr)
        return 1

    frontier_labels = {str(entry.get('label')) for entry in frontier_stats}
    if not REQUIRED_FRONTIERS.issubset(frontier_labels):
        print('shadow-pass-volatility: missing frontier labels', file=sys.stderr)
        return 1

    classes = {str(entry.get('volatility_class')) for entry in step_stats}
    if not classes.issubset(ALLOWED_CLASSES):
        print('shadow-pass-volatility: unexpected volatility class', file=sys.stderr)
        return 1
    if 'stable' not in classes:
        print('shadow-pass-volatility: expected at least one stable step', file=sys.stderr)
        return 1
    if not jittery:
        print('shadow-pass-volatility: expected at least one jittery step', file=sys.stderr)
        return 1
    if not stable:
        print('shadow-pass-volatility: expected at least one stable nontrivial step', file=sys.stderr)
        return 1

    print(
        'shadow-pass-volatility: ok '
        f"(current_profile={current_profile_count} latest={Path(str(summary.get('latest_receipt'))).name} jittery={len(jittery)})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
