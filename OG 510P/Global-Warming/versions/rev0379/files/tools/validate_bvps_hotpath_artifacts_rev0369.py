#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sqlite3, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'cube/bvps-hotpath-source-list-rev0369.csv'
DB=ROOT/'cube/datacube-rev0369-hotpath.sqlite'
SQLMAN=ROOT/'cube/bvps-hotpath-sqlite-table-manifest-rev0369.csv'
CAP=ROOT/'evidence-bags/bvps-hotpath-capsule-rev0369.zip'
CAPMAN=ROOT/'cube/bvps-hotpath-capsule-manifest-rev0369.csv'
required_inner={'576-nuclear-emergency-preparedness-requesttemplates-deadlineclock-hotpathbuilder-refactor-compact-canon.md','cube/nuclear-emergency-bvps-deadline-clock-rev0369.csv','cube/nuclear-emergency-bvps-records-request-templates-rev0369.csv','cube/nuclear-emergency-bvps-gap-to-request-map-rev0369.csv','cube/datacube-rev0369-hotpath.sqlite'}
required_tables={'nuclear_emergency_bvps_deadline_clock_rev0369','nuclear_emergency_bvps_records_request_templates_rev0369','nuclear_emergency_bvps_gap_to_request_map_rev0369','nuclear_emergency_bvps_eof_corrective_action_proofchain_rev0369','nuclear_emergency_bvps_alerting_proofchain_rev0369'}
def sha256_data(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()
errors=[]
for p in [SOURCE, DB, SQLMAN, CAP, CAPMAN]:
    if not p.exists(): errors.append('missing:'+str(p.relative_to(ROOT)))
if not errors:
    src=list(csv.DictReader(SOURCE.open(newline='', encoding='utf-8')))
    if len(src)<30: errors.append('source_list_too_short')
    con=sqlite3.connect(DB); tables={r[0] for r in con.execute("select name from sqlite_master where type='table'")}; con.close()
    for t in required_tables:
        if t not in tables: errors.append('missing_sqlite_table:'+t)
    sql_rows=list(csv.DictReader(SQLMAN.open(newline='', encoding='utf-8')))
    if len(sql_rows)<20: errors.append('sqlite_manifest_too_short')
    cap_rows={r['inner_path']:r for r in csv.DictReader(CAPMAN.open(newline='', encoding='utf-8'))}
    with zipfile.ZipFile(CAP) as z:
        bad=z.testzip()
        if bad: errors.append('testzip_bad:'+bad)
        names=[i.filename for i in z.infolist()]
        if len(names)!=len(set(names)): errors.append('duplicate_capsule_paths')
        for req in required_inner:
            if req not in names: errors.append('missing_required_inner:'+req)
        if len(names)<35: errors.append('too_few_capsule_files')
        for name in names:
            if name not in cap_rows: errors.append('missing_manifest_row:'+name); continue
            actual=sha256_data(z.read(name))
            if cap_rows[name].get('sha256')!=actual: errors.append('hash_mismatch:'+name)
if errors:
    print('FAIL hotpath_artifacts_rev0369 ' + ';'.join(errors[:50])); sys.exit(1)
print(f'PASS hotpath_artifacts_rev0369 capsule_files={len(names)} sqlite_tables={len(tables)}')
