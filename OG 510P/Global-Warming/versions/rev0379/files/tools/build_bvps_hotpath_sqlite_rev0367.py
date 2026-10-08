#!/usr/bin/env python3
from __future__ import annotations
import csv, sqlite3, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'cube/bvps-hotpath-sqlite-table-manifest-rev0367.csv'
OUT=ROOT/'cube/datacube-rev0367-hotpath.sqlite'

def table_name(path: str) -> str:
    name=Path(path).stem
    name=re.sub(r'[^A-Za-z0-9_]+','_',name).strip('_').lower()
    return 't_'+name

def read_rows(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def main() -> int:
    if not MAN.exists():
        print('FAIL missing manifest '+str(MAN)); return 1
    entries=read_rows(MAN)
    OUT.unlink(missing_ok=True)
    con=sqlite3.connect(OUT)
    cur=con.cursor()
    cur.execute('create table manifest(table_name text primary key, path text, row_count integer, column_count integer, source_sha256 text, loaded_at text)')
    total_rows=0
    for e in entries:
        path=e['path']; p=ROOT/path
        if not p.exists():
            print('FAIL missing table path '+path); return 1
        rows=read_rows(p)
        headers=list(rows[0].keys()) if rows else []
        t=e.get('sqlite_table') or table_name(path)
        cols=', '.join('"'+h.replace('"','""')+'" text' for h in headers) or 'empty_marker text'
        cur.execute(f'drop table if exists "{t}"')
        cur.execute(f'create table "{t}" ({cols})')
        if rows:
            ph=','.join('?' for _ in headers)
            cur.executemany(f'insert into "{t}" values ({ph})', [[r.get(h,'') for h in headers] for r in rows])
        cur.execute('insert into manifest values (?,?,?,?,?,?)', (t, path, len(rows), len(headers), e.get('sha256',''), 'rev0367_build'))
        total_rows += len(rows)
    con.commit(); con.close()
    print(f'PASS built_hotpath_sqlite tables={len(entries)} total_rows={total_rows} out={OUT}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
