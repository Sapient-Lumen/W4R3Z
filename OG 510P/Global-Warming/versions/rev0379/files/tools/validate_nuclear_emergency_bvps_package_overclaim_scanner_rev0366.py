#!/usr/bin/env python3
"""Validate package-level overclaim scan has no risky affirmative closure claims."""
from __future__ import annotations
import csv, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
proc=subprocess.run([sys.executable, str(ROOT/'tools/audit_nuclear_emergency_bvps_package_claim_surface_rev0366.py')], cwd=ROOT, text=True, capture_output=True)
print((proc.stdout or '').strip())
if proc.stderr: print(proc.stderr.strip())
if proc.returncode!=0:
    sys.exit(proc.returncode)
with (ROOT/'cube/nuclear-emergency-bvps-package-claim-surface-audit-rev0366.csv').open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
risky=[r for r in rows if r.get('risk_status')=='risky_affirmative_overclaim']
if risky:
    print('FAIL package_overclaim risky=' + ';'.join(r['path']+':'+r['line_number'] for r in risky[:10])); sys.exit(1)
print(f'PASS package_overclaim hits={len(rows)} risky=0')
