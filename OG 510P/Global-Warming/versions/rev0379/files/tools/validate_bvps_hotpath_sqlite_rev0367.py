#!/usr/bin/env python3
from __future__ import annotations
import csv, sqlite3, subprocess, sys, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'cube/bvps-hotpath-sqlite-table-manifest-rev0367.csv'
OUT=ROOT/'cube/datacube-rev0367-hotpath.sqlite'
errors=[]
proc=subprocess.run([sys.executable, str(ROOT/'tools/build_bvps_hotpath_sqlite_rev0367.py')], cwd=ROOT, text=True, capture_output=True, timeout=60)
print((proc.stdout or '').strip())
if proc.returncode!=0:
    print(proc.stderr); sys.exit(proc.returncode)
with MAN.open(newline='', encoding='utf-8') as f:
    entries=list(csv.DictReader(f))
if len(entries)<15: errors.append('too_few_sqlite_tables')
if not OUT.exists(): errors.append('missing_sqlite')
if OUT.exists() and OUT.stat().st_size > 5_000_000: errors.append('sqlite_too_large')
con=sqlite3.connect(OUT); cur=con.cursor()
cur.execute('select count(*) from manifest'); manifest_count=cur.fetchone()[0]
if manifest_count != len(entries): errors.append(f'manifest_count_mismatch={manifest_count}/{len(entries)}')
for e in entries:
    t=e['sqlite_table']
    try:
        cur.execute(f'select count(*) from "{t}"')
        n=cur.fetchone()[0]
    except Exception as ex:
        errors.append('missing_table:'+t); continue
    expected=int(e.get('row_count','0') or 0)
    if n != expected:
        errors.append(f'row_count_mismatch:{t}:{n}/{expected}')
con.close()
if errors:
    print('FAIL hotpath_sqlite_rev0367 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS hotpath_sqlite_rev0367 tables={len(entries)} size_bytes={OUT.stat().st_size}')
