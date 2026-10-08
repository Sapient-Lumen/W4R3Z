#!/usr/bin/env python3
"""Scan rev0347 live-intake quarantine folders and report missing README materialization."""
import csv
from pathlib import Path
base = Path(__file__).resolve().parents[1]
mat = base/'cube'/'nuclear-emergency-bvps-quarantine-filesystem-materialization-rev0347.csv'
missing=[]
with mat.open(newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        p=base/r['readme_path']
        if not p.exists():
            missing.append(r['readme_path'])
print(f'rev0347 quarantine README missing count: {len(missing)}')
if missing:
    raise SystemExit(1)
