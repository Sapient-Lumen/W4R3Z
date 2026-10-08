#!/usr/bin/env python3
"""Execute the current BVPS nuclear-emergency validator sweep.

Returns non-zero if any validator command fails. This script is intentionally
thin: it verifies that reported passes are executable passes, not planned or
reserved checks.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = [
    'tools/validate_nuclear_emergency_bvps_end_to_end_claim_kernel_rev0358.py',
    'tools/validate_nuclear_emergency_bvps_safe_statement_rev0359.py',
    'tools/validate_nuclear_emergency_bvps_gonogo_rev0360.py',
    'tools/validate_nuclear_emergency_bvps_live_watchdog_rev0361.py',
    'tools/validate_nuclear_emergency_bvps_watchpager_exceptionbridge_rev0362.py',
    'tools/validate_nuclear_emergency_bvps_watchpager_exceptionbridge_rev0363.py',
]
failures = []
for rel in TOOLS:
    proc = subprocess.run([sys.executable, str(ROOT/rel)], cwd=ROOT, text=True, capture_output=True)
    out = (proc.stdout or '').strip()
    err = (proc.stderr or '').strip()
    print(f'{rel}: exit={proc.returncode} {out}')
    if err:
        print(f'{rel}: stderr={err}')
    if proc.returncode != 0:
        failures.append(rel)
if failures:
    print('FAIL validator_sweep failures=' + ','.join(failures))
    sys.exit(1)
print('PASS validator_sweep executed_passes=' + str(len(TOOLS)))
