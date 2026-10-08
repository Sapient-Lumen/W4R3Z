#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'cube/bvps-official-findings-watchlist-rev0375.csv').open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
problems=[]
if len(rows)<4: problems.append('watchlist_too_small')
text='\n'.join(' '.join(r.values()) for r in rows).lower()
for needle in ['fema region 3','columbiana','11:00','final report','eof','not evidence until']:
    if needle not in text: problems.append('missing_'+needle.replace(' ','_').replace(':',''))
for r in rows:
    if 'open' not in r.get('status',''): problems.append('non_open_'+r.get('watch_id',''))
    if 'imported' not in r.get('not_evidence_until','').lower() and 'official' not in r.get('not_evidence_until','').lower(): problems.append('weak_not_evidence_'+r.get('watch_id',''))
if problems:
    print('FAIL findings_watchlist_rev0375 '+ '; '.join(problems)); sys.exit(1)
print(f'PASS findings_watchlist_rev0375 rows={len(rows)}')
