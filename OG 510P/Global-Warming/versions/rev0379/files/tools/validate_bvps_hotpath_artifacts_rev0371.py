#!/usr/bin/env python3
from __future__ import annotations
import csv, sqlite3, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'cube/bvps-hotpath-source-list-rev0371.csv'
DB=ROOT/'cube/datacube-rev0371-hotpath.sqlite'
CAP=ROOT/'evidence-bags/bvps-hotpath-capsule-rev0371.zip'
SQLMAN=ROOT/'cube/bvps-hotpath-sqlite-table-manifest-rev0371.csv'
CAPMAN=ROOT/'cube/bvps-hotpath-capsule-manifest-rev0371.csv'
AUDIT=ROOT/'cube/bvps-hotpath-prune-audit-rev0371.csv'

def read(p):
    with p.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def fail(msg): print('FAIL '+msg); sys.exit(1)
rows=read(SRC); sql=read(SQLMAN); cap=read(CAPMAN); audit=read(AUDIT)
if not DB.exists(): fail('missing_db')
if not CAP.exists(): fail('missing_capsule')
with zipfile.ZipFile(CAP) as z:
    bad=z.testzip(); names=z.namelist()
if bad: fail('bad_capsule_entry='+bad)
if len(rows)>=76: fail('hotpath_not_pruned source_rows='+str(len(rows)))
for forbidden in ['cube/source-canonical-url-map-rev0369.csv','cube/source-canonical-cluster-summary-rev0369.csv']:
    if forbidden in [r['path'] for r in rows]: fail('stale_duplicate_in_hotpath='+forbidden)
for required in ['578-nuclear-emergency-preparedness-responseintake-docketproof-hotpathprune-refactor-compact-canon.md','cube/nuclear-emergency-bvps-response-intake-contract-rev0371.csv','cube/nuclear-emergency-bvps-docket-release-watch-rev0371.csv']:
    if required not in [r['path'] for r in rows]: fail('missing_required_hotpath='+required)
con=sqlite3.connect(DB); cur=con.cursor(); cur.execute('select count(*) from manifest'); dbtables=cur.fetchone()[0]; con.close()
if dbtables != len(sql): fail(f'sql_manifest_mismatch db={dbtables} csv={len(sql)}')
metrics={r['metric']:r['value'] for r in audit}
if int(metrics.get('rev0370_source_rows','0')) <= int(metrics.get('rev0371_source_rows','999')): fail('prune_metric_not_lower')
print(f'PASS hotpath_artifacts_rev0371 source_rows={len(rows)} capsule_files={len(names)} sqlite_tables={dbtables}')
