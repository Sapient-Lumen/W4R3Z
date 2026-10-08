#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_verification_ladder.json'
EXECUTION_TOOL = ROOT / 'scripts' / 'tools' / 'emit_rust_standing_bootstrap_execution_plan.py'


def _execution_plan(target_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ['python3', str(EXECUTION_TOOL), '--target-root', str(target_root), '--json'],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit('rust-standing-bootstrap-verification-ladder: execution-plan tool failed\n' + proc.stdout + proc.stderr)
    return json.loads(proc.stdout)


def inspect(target_root: Path, report_path: Path) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding='utf-8'))
    execution = _execution_plan(target_root)
    plan = execution['plan']
    precondition_satisfied = execution['recognized'] and execution['matched_state_id'] == report['summary']['final_state_precondition']
    result: dict[str, Any] = {
        'target_root': str(target_root),
        'report_path': str(report_path),
        'precondition_satisfied': precondition_satisfied,
        'recognized': execution['recognized'],
        'matched_state_id': execution['matched_state_id'],
        'matched_label': execution['matched_label'],
        'observed_combined_hash': execution['observed_combined_hash'],
        'expected_final_combined_hash': report['summary']['expected_final_combined_hash'],
    }
    if precondition_satisfied:
        result['summary'] = 'final_full recognized: run the standing-focused verification ladder.'
        result['apply_first_commands'] = []
        result['verification_stages'] = report['stages']
    else:
        result['summary'] = 'verification ladder withheld until the checkout reaches final_full; apply sequencing still comes first.'
        result['apply_first_commands'] = list(plan.get('apply_commands') or [])
        result['verification_stages'] = []
        result['precondition_failure'] = {
            'action_kind': plan.get('action_kind'),
            'route_kind': plan.get('route_kind'),
            'execution_plan_summary': plan.get('summary'),
            'post_apply_expectation': plan.get('post_apply_expectation'),
        }
    return result


def _render_text(result: dict[str, Any]) -> str:
    lines = [
        f"precondition_satisfied: {str(result['precondition_satisfied']).lower()}",
        f"matched_state_id: {result['matched_state_id'] or 'none'}",
        f"summary: {result['summary']}",
        f"expected_final_combined_hash: {result['expected_final_combined_hash']}",
    ]
    if result['apply_first_commands']:
        lines.append('apply_first_commands:')
        for cmd in result['apply_first_commands']:
            lines.append(f'  - {cmd}')
    if result['verification_stages']:
        lines.append('verification_stages:')
        for stage in result['verification_stages']:
            lines.append(f"  - {stage['stage_id']}: {len(stage['commands'])} commands")
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-root', type=Path, default=ROOT)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if not args.report.exists():
        print(f'missing verification-ladder report: {args.report}', file=sys.stderr)
        return 1
    result = inspect(args.target_root, args.report)
    if args.json:
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write('\n')
    else:
        print(_render_text(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
