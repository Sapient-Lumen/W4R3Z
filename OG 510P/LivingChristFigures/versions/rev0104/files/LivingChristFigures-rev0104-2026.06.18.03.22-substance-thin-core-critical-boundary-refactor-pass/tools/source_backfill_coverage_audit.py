#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, sys
from collections import defaultdict
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['coverage_id','source_id','domain','candidate_ids','source_registry_row_present','backfill_action_count','latest_backfill_revision','latest_backfill_status','duplicate_action_count','coverage_status','severity','status','action_needed']
REV_ORDER={'rev0077':77,'rev0078':78,'rev0079':79,'rev0080':80,'rev0081':81,'rev0082':82,'rev0083':83,'rev0084':84,'rev0085':85,'rev0086':86}

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

def run(root: Path):
    sources=read_csv(root/'Source-Registry-current.csv')
    backfills=read_csv(root/'META/Source-Metadata-Backfill-current.csv')
    by=defaultdict(list)
    for r in backfills:
        by[r.get('source_id','')].append(r)
    rows=[]
    for src in sources:
        sid=src.get('source_id','')
        acts=by.get(sid, [])
        latest={}
        if acts:
            latest=sorted(acts, key=lambda r:(REV_ORDER.get(r.get('batch_revision',''),0), r.get('backfill_id','')))[-1]
        missing=not acts
        rows.append({
            'coverage_id':f'sbc_{len(rows)+1:04d}',
            'source_id':sid,
            'domain':src.get('domain',''),
            'candidate_ids':src.get('candidate_ids',''),
            'source_registry_row_present':'true',
            'backfill_action_count':str(len(acts)),
            'latest_backfill_revision':latest.get('batch_revision',''),
            'latest_backfill_status':latest.get('backfill_status',''),
            'duplicate_action_count':str(max(0,len(acts)-1)),
            'coverage_status':'missing_backfill_coverage' if missing else 'covered',
            'severity':'high' if missing else 'info',
            'status':'fail' if missing else 'pass',
            'action_needed':'add a backfill ledger row or an explicit out-of-scope coverage disposition' if missing else ('duplicate action history; keep as cumulative history, not coverage count' if len(acts)>1 else 'none'),
        })
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-missing', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-Backfill-Coverage-Audit-current.csv',FIELDS,rows,'Source Backfill Coverage Audit','tools/source_backfill_coverage_audit.py',columns=['coverage_id','source_id','domain','backfill_action_count','latest_backfill_revision','latest_backfill_status','duplicate_action_count','coverage_status','status','action_needed'],intro_lines=['One row per Source Registry source_id. This audit separates cumulative action history from coverage: duplicate action rows are allowed as history, but missing coverage fails the release gate.'],max_md_rows=220)
    bad=[r for r in rows if r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} source backfill coverage rows={len(rows)} missing={len(bad)}")
    if args.fail_on_missing and bad: sys.exit(1)
if __name__=='__main__': main()
