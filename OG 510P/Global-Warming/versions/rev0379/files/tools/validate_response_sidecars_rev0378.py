from __future__ import annotations
import csv, sys, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
board=ROOT/'cube/bvps-response-sidecar-board-rev0378.csv'
rows=list(csv.DictReader(board.open(newline='',encoding='utf-8')))
if len(rows)!=8:
    raise SystemExit(f'expected 8 sidecar rows, found {len(rows)}')
for r in rows:
    p=ROOT/r['sidecar_path']
    if not p.exists():
        raise SystemExit(f'missing sidecar file {p}')
    txt=p.read_text(encoding='utf-8')
    for marker in ['Dispatch receipt','Custodian response','Files received','Required DLP and release gate','Proofcut effect']:
        if marker not in txt:
            raise SystemExit(f'{p} missing marker {marker}')
    if r['hash_gate']!='not_satisfied' or r['dlp_gate']!='not_satisfied' or r['proofcut_mapping_gate']!='not_satisfied':
        raise SystemExit(f'{r["request_id"]} gate should remain not_satisfied')
print(f'PASS response_sidecars_rev0378 sidecars={len(rows)}')
