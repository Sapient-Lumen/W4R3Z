#!/usr/bin/env python3
"""Validate the rev0366 BVPS proofcut board and fixture no-credit rule."""
from __future__ import annotations
import csv, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'cube/nuclear-emergency-bvps-proofcut-status-rev0366.csv'
errors=[]
with tempfile.TemporaryDirectory() as td:
    temp=Path(td)/'proofcut.csv'
    proc=subprocess.run([sys.executable, str(ROOT/'tools/compile_nuclear_emergency_bvps_proofcut_status_rev0366.py'), '--out', str(temp.relative_to(ROOT)) if str(temp).startswith(str(ROOT)) else str(temp)], cwd=ROOT, text=True, capture_output=True)
    # If temp is outside ROOT, compiler writes absolute path if passed; the relative trick above may fail. Fallback: run default and read target below.
    if proc.returncode!=0:
        print(proc.stdout); print(proc.stderr); sys.exit(proc.returncode)
# Recompile default to canonical target so the shipped board is reproducible.
proc=subprocess.run([sys.executable, str(ROOT/'tools/compile_nuclear_emergency_bvps_proofcut_status_rev0366.py')], cwd=ROOT, text=True, capture_output=True)
if proc.returncode!=0:
    print(proc.stdout); print(proc.stderr); sys.exit(proc.returncode)
with TARGET.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows) < 12:
    errors.append('too_few_proofcut_rows')
real_total=sum(int(r.get('real_candidate_rows','0') or 0) for r in rows)
fixture_total=sum(int(r.get('fixture_rows','0') or 0) for r in rows)
if real_total != 0:
    errors.append(f'unexpected_real_candidate_rows={real_total}')
if fixture_total < 3:
    errors.append(f'fixture_rows_not_seen={fixture_total}')
for r in rows:
    blob=' '.join(r.values()).lower()
    if 'readiness_closure' not in (r.get('claim_effect','') + ' ' + r.get('forbidden_statement','')).lower():
        errors.append('missing_no_closure_marker:'+r.get('artifact_class',''))
    if r.get('fixture_rows') != '0' and r.get('real_candidate_rows') != '0':
        errors.append('fixture_counted_as_real:'+r.get('artifact_class',''))
if errors:
    print('FAIL proofcut_status ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS proofcut_status rows={len(rows)} real_candidate_rows={real_total} fixture_rows={fixture_total}')
