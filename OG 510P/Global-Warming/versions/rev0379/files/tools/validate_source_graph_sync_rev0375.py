#!/usr/bin/env python3
from __future__ import annotations
import csv, re, sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def sids(text): return [tok for tok in re.split(r'[;|,\s]+', text or '') if re.fullmatch(r'S\d+', tok)]
def norm_file_id(x):
    x=(x or '').strip(); return str(int(x)) if re.fullmatch(r'\d+', x) else x
def sid_sort(s): return int(s[1:]) if re.fullmatch(r'S\d+', s or '') else 10**9
source={r['source_id']:r for r in rows('cube/source.csv')}
register_text=(ROOT/'sources/register.md').read_text(encoding='utf-8')
register=set(re.findall(r'\*\*(S\d+)\*\*', register_text))
index=rows('cube/index.csv')
usage=defaultdict(set); expected_edges=set()
for r in index:
    fid=(r.get('id') or '').strip()
    for sid in sids(r.get('source_ids','')):
        usage[sid].add(fid); expected_edges.add((fid,sid))
ledger={r['source_id']:r for r in rows('cube/source-use-ledger.csv')}
edge={(r['file_id'],r['source_id']) for r in rows('cube/source-edge-table.csv')}
fse={(norm_file_id(r.get('file_id','')),r.get('source_id','')) for r in rows('cube/file-source-edge.csv')}
problems=[]
if set(source)-register: problems.append('source_missing_register='+','.join(sorted(set(source)-register, key=sid_sort)[:20]))
if set(usage)-set(source): problems.append('index_missing_source='+','.join(sorted(set(usage)-set(source), key=sid_sort)[:20]))
if set(usage)-set(ledger): problems.append('index_missing_ledger='+','.join(sorted(set(usage)-set(ledger), key=sid_sort)[:20]))
for sid in source:
    exp=sorted(usage.get(sid,set()), key=lambda x:int(x) if x.isdigit() else 10**9)
    row=ledger.get(sid)
    if not row: problems.append('ledger_missing_'+sid); continue
    got=sorted(set(x for x in (row.get('used_in_files','') or '').split(';') if x), key=lambda x:int(x) if x.isdigit() else 10**9)
    try: count=int(row.get('used_in_count',''))
    except Exception: count=-1
    if count!=len(exp) or got!=exp: problems.append(f'ledger_mismatch_{sid}')
missing_edge=expected_edges-edge
if missing_edge: problems.append('source_edge_missing='+str(len(missing_edge)))
missing_fse={(norm_file_id(fid),sid) for fid,sid in expected_edges}-fse
if missing_fse: problems.append('file_source_edge_missing='+str(len(missing_fse)))
for sid in [f'S{i}' for i in range(1356,1385)]:
    if sid not in source or sid not in register or sid not in ledger:
        problems.append('rev0375_expected_tail_missing_'+sid)
if problems:
    print('FAIL source_graph_sync_rev0375 '+ '; '.join(problems[:25])); sys.exit(1)
print(f'PASS source_graph_sync_rev0375 sources={len(source)} index_s_ids={len(usage)} edges={len(expected_edges)}')
