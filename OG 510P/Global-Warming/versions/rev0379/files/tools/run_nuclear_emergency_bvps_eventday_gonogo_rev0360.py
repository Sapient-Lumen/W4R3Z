#!/usr/bin/env python3
"""One-command event-day go/no-go preflight for BVPS evidence capture.

The successful state is capture-ready / claim-frozen. This script never emits
readiness closure.
"""
import argparse, csv, os, sqlite3, sys
from pathlib import Path

def write_csv(path, rows, fields):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def exists(root, rel):
    return (root/rel).exists()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root', default='.')
    p.add_argument('--out', default='cube/nuclear-emergency-bvps-gonogo-run-result-rev0360.csv')
    args=p.parse_args()
    root=Path(args.root)
    checks=[]
    def add(check_id, area, name, rel, expected=True):
        ok=exists(root, Path(rel)) if rel else True
        checks.append({'run_id':'GNG-RUN-REV0360-LIVE','check_id':check_id,'control_area':area,'check_name':name,
                       'observed_state':'pass' if ok else 'fail','operator_result':'capture_ready_no_claim' if ok else 'stop_and_repair',
                       'ready_for_capture':'yes' if ok else 'no','ready_for_readiness_claim':'no','claim_freeze':'active',
                       'next_action':'continue capture only; no readiness claim' if ok else f'repair missing {rel}',
                       'revision_checked':'rev0360'})
    add('GNG-001','package','manifest present','manifest.json')
    add('GNG-002','package','cube manifest present','cube/manifest.json')
    add('GNG-003','canon','latest canon present','567-nuclear-emergency-preparedness-onecommand-gonogo-operatordrill-refactor-compact-canon.md')
    add('GNG-004','sqlite','rev0360 sqlite present','cube/datacube-rev0360-emergency.sqlite')
    add('GNG-005','validator','validator result present','cube/nuclear-emergency-bvps-gonogo-validator-result-rev0360.csv')
    add('GNG-006','fieldkit','operator brief present','field-kits/bvps-rev0360/operator-two-minute-brief.md')
    # Count packet skeleton directories if present.
    packet_root=root/'field-kits/bvps-rev0343/packet-skeletons'
    packet_count=sum(1 for x in packet_root.glob('PKT-*') if x.is_dir()) if packet_root.exists() else 0
    checks.append({'run_id':'GNG-RUN-REV0360-LIVE','check_id':'GNG-007','control_area':'packets','check_name':'60 packet skeleton directories',
                   'observed_state':'pass' if packet_count==60 else 'fail','operator_result':'capture_ready_no_claim' if packet_count==60 else 'stop_and_repair',
                   'ready_for_capture':'yes' if packet_count==60 else 'no','ready_for_readiness_claim':'no','claim_freeze':'active',
                   'next_action':f'packet_count={packet_count}; continue capture only' if packet_count==60 else f'packet_count={packet_count}; repair skeletons',
                   'revision_checked':'rev0360'})
    # SQLite leak query if possible.
    leak_state='not_checked'
    try:
        db=root/'cube/datacube-rev0360-emergency.sqlite'
        con=sqlite3.connect(db)
        n=con.execute('select count(*) from rev0360_public_context_to_local_closure_leak_v').fetchone()[0]
        con.close()
        leak_state='pass' if n==0 else 'fail'
        next_action=f'leak_count={n}; claim freeze remains active'
    except Exception as e:
        leak_state='fail'; next_action=f'sqlite leak query failed: {e}'
    checks.append({'run_id':'GNG-RUN-REV0360-LIVE','check_id':'GNG-008','control_area':'claim_firebreak','check_name':'public-context-to-local-closure leak query',
                   'observed_state':leak_state,'operator_result':'capture_ready_no_claim' if leak_state=='pass' else 'stop_and_repair',
                   'ready_for_capture':'yes' if leak_state=='pass' else 'no','ready_for_readiness_claim':'no','claim_freeze':'active',
                   'next_action':next_action,'revision_checked':'rev0360'})
    write_csv(root/args.out, checks, ['run_id','check_id','control_area','check_name','observed_state','operator_result','ready_for_capture','ready_for_readiness_claim','claim_freeze','next_action','revision_checked'])
    # Nonzero only if preflight structure fails; never indicates readiness.
    return 0 if all(r['observed_state']=='pass' for r in checks) else 2
if __name__=='__main__':
    sys.exit(main())
