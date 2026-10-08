#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path

def rows(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def add(out, check_id, check, passed, observed, expected, detail=''):
    out.append({'check_id':check_id,'check':check,'status':'pass' if passed else 'fail','observed':str(observed),'expected':str(expected),'detail':detail})

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--contract', required=True)
    ap.add_argument('--query-set', required=True)
    ap.add_argument('--normalized', required=True)
    ap.add_argument('--dedupe-results', required=True)
    ap.add_argument('--source-canonical', required=True)
    ap.add_argument('--output', required=True)
    args=ap.parse_args(argv)
    out=[]
    contract=rows(args.contract); queries=rows(args.query_set); norm=rows(args.normalized); dedupe=rows(args.dedupe_results); sc=rows(args.source_canonical)
    add(out,'VAL-0326-001','feed_contract_rows',len(contract)>=8,len(contract),'>=8')
    add(out,'VAL-0326-002','all_feeds_no_auto_closure',all(r.get('closure_effect')=='no_auto_closure' for r in contract),sum(1 for r in contract if r.get('closure_effect')=='no_auto_closure'),len(contract))
    tri={'042007','039029','054029'}
    q_geo={r.get('fips_geocode') for r in queries}
    add(out,'VAL-0326-003','tri_state_county_queries_present',tri.issubset(q_geo),';'.join(sorted(q_geo & tri)),'042007;039029;054029')
    add(out,'VAL-0326-004','query_rows_postprocess_required',all(r.get('postprocess_required')=='yes' for r in queries),sum(1 for r in queries if r.get('postprocess_required')=='yes'),len(queries))
    add(out,'VAL-0326-005','normalized_cap_rows',len(norm)==10,len(norm),'10')
    add(out,'VAL-0326-006','normalized_no_auto_closure',all('closure' not in r.get('closure_effect','').lower() or r.get('closure_effect')!='auto_close' for r in norm),0,'0 auto closures')
    add(out,'VAL-0326-007','lineage_cancel_reopen_present',any(r.get('lineage_state')=='cancel_signal' and r.get('closure_effect')=='accepted_reopen_signal' for r in norm),sum(1 for r in norm if r.get('lineage_state')=='cancel_signal'),'cancel reopen signal')
    add(out,'VAL-0326-008','lineage_error_reopen_present',any(r.get('lineage_state')=='error_signal' and r.get('closure_effect')=='accepted_reopen_signal' for r in norm),sum(1 for r in norm if r.get('lineage_state')=='error_signal'),'error reopen signal')
    add(out,'VAL-0326-009','deduplicated_archive_row_present',any(r.get('lineage_state')=='deduplicated_archive_row' for r in norm),sum(1 for r in norm if r.get('lineage_state')=='deduplicated_archive_row'),'>=1')
    add(out,'VAL-0326-010','dedupe_result_all_pass',all(r.get('status')=='pass' for r in dedupe),sum(1 for r in dedupe if r.get('status')=='pass'),len(dedupe))
    add(out,'VAL-0326-011','source_canonical_aliases_present',any(r.get('is_alias')=='true' for r in sc),sum(1 for r in sc if r.get('is_alias')=='true'),'>0')
    add(out,'VAL-0326-012','source_canonical_no_alias_weight_gt0',all(float(r.get('evidence_independence_weight','0') or 0) <= 1.0 for r in sc),max(float(r.get('evidence_independence_weight','0') or 0) for r in sc),'<=1')
    fields=['check_id','check','status','observed','expected','detail']
    with Path(args.output).open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
    return 0 if all(r['status']=='pass' for r in out) else 1
if __name__=='__main__':
    raise SystemExit(main())
