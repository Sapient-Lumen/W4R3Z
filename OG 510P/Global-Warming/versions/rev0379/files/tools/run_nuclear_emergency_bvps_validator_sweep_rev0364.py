#!/usr/bin/env python3
"""Execute the fast current-risk BVPS validator sweep for rev0364.

The full executed-validator audit records legacy claim-kernel checks separately.
This sweep is kept short so an operator can rerun the riskiest current controls
without timing out: exact closure-state matching, real evidence gate, inert
fixture policy, source-cluster weighting, and validation status vocabulary.
"""
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
TOOLS = [
    'tools/validate_nuclear_emergency_bvps_watchpager_exceptionbridge_rev0362.py',
    'tools/validate_nuclear_emergency_bvps_watchpager_exceptionbridge_rev0363.py',
    'tools/validate_nuclear_emergency_bvps_evidence_gate_rev0364.py',
    'tools/validate_nuclear_emergency_bvps_inert_fixture_policy_rev0364.py',
    'tools/validate_nuclear_emergency_bvps_source_cluster_weighting_rev0364.py',
    'tools/validate_validation_report_status_vocabulary_rev0364.py',
]
failures = []
for rel in TOOLS:
    proc = subprocess.run([sys.executable, str(ROOT/rel)], cwd=ROOT, text=True, capture_output=True, timeout=30)
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
