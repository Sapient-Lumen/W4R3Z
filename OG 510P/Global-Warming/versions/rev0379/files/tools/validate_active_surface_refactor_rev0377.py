from __future__ import annotations
import csv, zipfile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cap=ROOT/'evidence-bags/bvps-tristate-dispatch-capsule-rev0377.zip'
if not cap.exists(): raise SystemExit('missing active dispatch capsule')
with zipfile.ZipFile(cap) as z:
    names=set(z.namelist())
required={'584-nuclear-emergency-preparedness-wvlane-dispatchboard-activesurface-refactor-compact-canon.md','records-requests/bvps-rev0377/dispatch-cut-sheet-rev0377.md','records-requests/bvps-rev0377/rrt-0377-011-wv-dhs-wvemd-hancock-bvps-exercise-evaluator-materials.md','records-requests/bvps-rev0377/rrt-0377-012-hancock-county-oem-bvps-exercise-alerting-eoc-afn-capa.md','cube/bvps-tristate-custodian-dispatch-board-rev0377.csv'}
missing=required-names
if missing: raise SystemExit(f'capsule missing {sorted(missing)}')
if len(names)>80: raise SystemExit(f'capsule too large for active surface: {len(names)} files')
print(f'PASS active dispatch capsule compact files={len(names)}')
