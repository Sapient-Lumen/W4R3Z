#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'tools' / 'cloudtainer_shadow_pass.py'
STEP_IDS = 'doctor_probe,update_rust_surface_inventory,test_rust_surface_inventory'

def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['python3', str(SCRIPT), *args], cwd=ROOT, capture_output=True, text=True)

def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        checkpoint = tmp / 'shadow_checkpoint.json'
        receipt = tmp / 'shadow_receipt.json'
        first = run('--step-ids', STEP_IDS, '--checkpoint', str(checkpoint), '--output', str(receipt), '--stop-after-step', '2', '--print-path-only')
        if first.returncode != 0:
            sys.stderr.write(first.stdout)
            sys.stderr.write(first.stderr)
            print('shadow-pass-resume: first partial run failed', file=sys.stderr)
            return 1
        if not checkpoint.exists() or receipt.exists():
            print('shadow-pass-resume: bad partial-run artifacts', file=sys.stderr)
            return 1
        partial = json.loads(checkpoint.read_text(encoding='utf-8'))
        if partial.get('run_status') != 'intentional_stop' or partial.get('next_step_index') != 2 or partial.get('completed_step_count') != 2:
            print('shadow-pass-resume: checkpoint mismatch after intentional stop', file=sys.stderr)
            return 1
        second = run('--step-ids', STEP_IDS, '--checkpoint', str(checkpoint), '--output', str(receipt), '--resume', '--print-path-only')
        if second.returncode != 0:
            sys.stderr.write(second.stdout)
            sys.stderr.write(second.stderr)
            print('shadow-pass-resume: resumed run failed', file=sys.stderr)
            return 1
        if checkpoint.exists() or not receipt.exists():
            print('shadow-pass-resume: bad final artifacts after resume', file=sys.stderr)
            return 1
        final = json.loads(receipt.read_text(encoding='utf-8'))
        checkpointing = final.get('checkpointing') or {}
        steps = final.get('steps') or []
        if final.get('receipt_type') != 'cloudtainer_shadow_pass' or final.get('receipt_version') != 2:
            print('shadow-pass-resume: final receipt header mismatch', file=sys.stderr)
            return 1
        if checkpointing.get('resumed_from_checkpoint') is not True or checkpointing.get('initial_completed_rows') != 2:
            print('shadow-pass-resume: resume metadata mismatch', file=sys.stderr)
            return 1
        if final.get('selected_step_ids') != STEP_IDS.split(',') or len(steps) != 3:
            print('shadow-pass-resume: final step selection mismatch', file=sys.stderr)
            return 1
        if steps[0].get('status') != 'blocked' or steps[0].get('id') != 'doctor_probe':
            print('shadow-pass-resume: expected blocked doctor probe in subset run', file=sys.stderr)
            return 1
        if [row.get('id') for row in steps[1:]] != ['update_rust_surface_inventory', 'test_rust_surface_inventory']:
            print('shadow-pass-resume: resumed steps mismatch', file=sys.stderr)
            return 1
        print('shadow-pass-resume: ok (partial stop + resume landed 3-step receipt)')
        return 0

if __name__ == '__main__':
    raise SystemExit(main())
