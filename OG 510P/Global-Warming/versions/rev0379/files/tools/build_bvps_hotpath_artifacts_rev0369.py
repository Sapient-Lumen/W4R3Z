#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, re, sqlite3, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'cube/bvps-hotpath-source-list-rev0369.csv'
DB=ROOT/'cube/datacube-rev0369-hotpath.sqlite'
SQLMAN=ROOT/'cube/bvps-hotpath-sqlite-table-manifest-rev0369.csv'
CAP=ROOT/'evidence-bags/bvps-hotpath-capsule-rev0369.zip'
CAPMAN=ROOT/'cube/bvps-hotpath-capsule-manifest-rev0369.csv'
AUDIT=ROOT/'cube/bvps-hotpath-build-audit-rev0369.csv'

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def table_name(path: str) -> str:
    name=Path(path).stem
    return re.sub(r'[^A-Za-z0-9_]+','_',name).strip('_').lower()

def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)

def main() -> int:
    if not SOURCE.exists():
        print('FAIL missing_source_list='+str(SOURCE)); return 1
    entries=read_csv(SOURCE)
    errors=[]
    seen=set()
    for e in entries:
        rel=e.get('path','')
        if not rel: errors.append('blank_path'); continue
        if rel in seen: errors.append('duplicate_path:'+rel)
        seen.add(rel)
        p=ROOT/rel
        if not p.exists(): errors.append('missing_path:'+rel)
        elif e.get('source_sha256') and e['source_sha256']!=sha256(p): errors.append('hash_drift:'+rel)
    if errors:
        print('FAIL source_list ' + ';'.join(errors[:40])); return 1
    DB.unlink(missing_ok=True)
    con=sqlite3.connect(DB); cur=con.cursor()
    cur.execute('create table manifest(table_name text primary key, path text, row_count integer, column_count integer, source_sha256 text, loaded_at text)')
    sql_rows=[]; total_rows=0
    for e in entries:
        if e.get('include_in_sqlite')!='yes': continue
        rel=e['path']; p=ROOT/rel
        rows=read_csv(p)
        headers=list(rows[0].keys()) if rows else []
        t=table_name(rel)
        cols=', '.join('"'+h.replace('"','""')+'" text' for h in headers) or 'empty_marker text'
        cur.execute(f'drop table if exists "{t}"')
        cur.execute(f'create table "{t}" ({cols})')
        if rows:
            ph=','.join('?' for _ in headers)
            cur.executemany(f'insert into "{t}" values ({ph})', [[r.get(h,'') for h in headers] for r in rows])
        cur.execute('insert into manifest values (?,?,?,?,?,?)', (t, rel, len(rows), len(headers), e.get('source_sha256',''), 'rev0369_build'))
        sql_rows.append({'sqlite_table':t,'path':rel,'row_count':str(len(rows)),'column_count':str(len(headers)),'sha256':e.get('source_sha256',''),'loaded_at':'rev0369_build'})
        total_rows+=len(rows)
    con.commit(); con.close()
    write_csv(SQLMAN, sql_rows, ['sqlite_table','path','row_count','column_count','sha256','loaded_at'])
    CAP.parent.mkdir(parents=True, exist_ok=True)
    cap_rows=[]
    with zipfile.ZipFile(CAP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for e in entries:
            if e.get('include_in_capsule')!='yes': continue
            rel=e['path']; p=ROOT/rel
            z.write(p, rel)
            info=z.getinfo(rel)
            cap_rows.append({'capsule_id':'CAP-0369-001','inner_path':rel,'compressed_size':str(info.compress_size),'size_bytes':str(info.file_size),'sha256':sha256(p),'purpose':e.get('purpose','bounded_current_risk_hotpath')})
        # include generated DB and SQL manifest in the capsule
        for rel in ['cube/datacube-rev0369-hotpath.sqlite','cube/bvps-hotpath-sqlite-table-manifest-rev0369.csv']:
            p=ROOT/rel; z.write(p, rel); info=z.getinfo(rel)
            cap_rows.append({'capsule_id':'CAP-0369-001','inner_path':rel,'compressed_size':str(info.compress_size),'size_bytes':str(info.file_size),'sha256':sha256(p),'purpose':'generated_hotpath_artifact'})
    write_csv(CAPMAN, cap_rows, ['capsule_id','inner_path','compressed_size','size_bytes','sha256','purpose'])
    write_csv(AUDIT, [
        {'metric':'source_list_rows','value':str(len(entries))},
        {'metric':'sqlite_tables','value':str(len(sql_rows))},
        {'metric':'sqlite_rows','value':str(total_rows)},
        {'metric':'capsule_files','value':str(len(cap_rows))},
        {'metric':'capsule_size_bytes','value':str(CAP.stat().st_size)},
        {'metric':'db_size_bytes','value':str(DB.stat().st_size)},
    ], ['metric','value'])
    print(f'PASS built_hotpath_artifacts_rev0369 source_rows={len(entries)} sqlite_tables={len(sql_rows)} capsule_files={len(cap_rows)}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
