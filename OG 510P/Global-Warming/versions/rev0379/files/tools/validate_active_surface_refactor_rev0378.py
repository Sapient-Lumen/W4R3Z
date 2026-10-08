from __future__ import annotations
import csv, zipfile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cap=ROOT/'evidence-bags/bvps-canonical-dispatch-capsule-rev0378.zip'
if not cap.exists():
    raise SystemExit('missing rev0378 capsule')
with zipfile.ZipFile(cap) as z:
    names=z.namelist()
required=['cube/bvps-canonical-dispatch-batch-rev0378.csv','cube/records-request-supersession-ledger-rev0378.csv','cube/bvps-dispatch-deadline-clock-rev0378.csv','records-requests/bvps-rev0378/dispatch-cut-sheet-rev0378.md']
for r in required:
    if r not in names:
        raise SystemExit(f'capsule missing {r}')
if any('rrt-0369' in n for n in names):
    raise SystemExit('capsule should not include old rrt-0369 packets')
if len(names)>60:
    raise SystemExit(f'capsule too large for active surface: {len(names)} entries')
print(f'PASS active_surface_refactor_rev0378 entries={len(names)}')
