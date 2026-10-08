#!/usr/bin/env python3
import csv, sys, math
from pathlib import Path

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    inp=root/'cube'/'nuclear-emergency-bvps-crc-station-queue-model-rev0330.csv'
    out=root/'cube'/'nuclear-emergency-bvps-crc-queue-model-summary-rev0330.csv'
    rows=list(csv.DictReader(open(inp, newline='', encoding='utf-8')))
    by={}
    for r in rows:
        by.setdefault(r['loadcase_id'],[]).append(r)
    outrows=[]
    for lc, rs in by.items():
        bott=[r for r in rs if r['bottleneck_flag']=='yes']
        worst=max(rs, key=lambda r: float(r['hours_to_clear_synthetic']))
        outrows.append({'loadcase_id':lc,'loadcase_name':rs[0]['loadcase_name'],'station_count':len(rs),'bottleneck_count':len(bott),'worst_station':worst['station_id'],'worst_hours_to_clear_synthetic':worst['hours_to_clear_synthetic'],'claim_effect':'synthetic pressure model only; creates evidence demand; no local closure','status':'open_evidence_demand' if bott else 'sample_verification_required'})
    with open(out,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(outrows[0].keys())); w.writeheader(); w.writerows(outrows)
    print(f'wrote {len(outrows)} queue summaries')
if __name__=='__main__': main()
