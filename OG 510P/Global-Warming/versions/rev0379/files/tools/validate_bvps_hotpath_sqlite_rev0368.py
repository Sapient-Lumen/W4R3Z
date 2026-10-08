#!/usr/bin/env python3
from __future__ import annotations
import csv, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'cube/datacube-rev0368-hotpath.sqlite'
MAN=ROOT/'cube/bvps-hotpath-sqlite-table-manifest-rev0368.csv'
required=['nuclear_emergency_bvps_ans_transition_admissibility_matrix_rev0368','nuclear_emergency_bvps_eof_ler_adams_watch_rev0368','nuclear_emergency_bvps_public_records_request_queue_rev0368','nuclear_emergency_bvps_closure_blocker_board_rev0368']
errors=[]
if not DB.exists(): errors.append('missing_db')
if not MAN.exists(): errors.append('missing_manifest')
if not errors:
    con=sqlite3.connect(DB)
    tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for req in required:
        if req not in tables: errors.append('missing_table:'+req)
        else:
            count=con.execute(f'SELECT COUNT(*) FROM "{req}"').fetchone()[0]
            if count==0: errors.append('empty_table:'+req)
    con.close()
    rows=list(csv.DictReader(MAN.open(newline='', encoding='utf-8')))
    if len(rows)<15: errors.append('too_few_manifest_tables')
if errors:
    print('FAIL hotpath_sqlite_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS hotpath_sqlite_rev0368 tables={len(tables)} size_bytes={DB.stat().st_size}')
