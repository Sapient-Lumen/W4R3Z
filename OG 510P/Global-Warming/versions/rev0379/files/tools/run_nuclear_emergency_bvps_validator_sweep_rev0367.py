#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import csv
import io
import runpy
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = [
    'tools/validate_nuclear_emergency_bvps_inert_fixture_policy_rev0364.py',
    'tools/validate_nuclear_emergency_bvps_evidence_intake_contract_rev0365.py',
    'tools/validate_nuclear_emergency_bvps_proofcut_status_rev0366.py',
    'tools/validate_nuclear_emergency_bvps_eof_repair_gate_rev0367.py',
    'tools/validate_nuclear_emergency_bvps_alert_transition_watch_rev0367.py',
    'tools/validate_nuclear_emergency_bvps_proofcut_admissibility_rev0367.py',
    'tools/validate_nuclear_emergency_bvps_columbiana_plan_boundary_rev0367.py',
    'tools/validate_bvps_active_hotpath_manifest_rev0367.py',
    'tools/validate_bvps_hotpath_sqlite_rev0367.py',
]

rows: list[dict[str, str]] = []
failures: list[str] = []

for i, rel in enumerate(TOOLS, 1):
    start = time.time()
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = 0
    print(f'START {i} {rel}', flush=True)
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            runpy.run_path(str(ROOT / rel), run_name='__main__')
    except SystemExit as exc:
        code = int(exc.code or 0) if isinstance(exc.code, int) else 1
    except Exception as exc:  # keep sweep diagnostic instead of hiding trace in a hung subprocess
        code = 1
        stderr.write(repr(exc))
    out = stdout.getvalue().strip()
    err = stderr.getvalue().strip()
    status = 'executed_pass' if code == 0 else 'executed_fail'
    tail = out.splitlines()[-1] if out else ''
    print(f'{rel}: exit={code} {tail}', flush=True)
    rows.append({
        'validator_id': f'VS-0367-{i:03d}',
        'tool_path': rel,
        'status': status,
        'seconds': str(round(time.time() - start, 3)),
        'stdout_tail': out[-500:],
        'stderr_tail': err[-500:],
    })
    if code != 0:
        failures.append(rel)

out_path = ROOT / 'cube/bvps-current-risk-validator-audit-rev0367.csv'
with out_path.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

if failures:
    print('FAIL validator_sweep_rev0367 failures=' + ','.join(failures))
    sys.exit(1)
print('PASS validator_sweep_rev0367 executed_passes=' + str(len(TOOLS)))
