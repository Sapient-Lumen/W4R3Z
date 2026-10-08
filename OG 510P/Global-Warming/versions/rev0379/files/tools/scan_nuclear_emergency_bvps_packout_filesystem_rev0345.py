#!/usr/bin/env python3
import argparse,csv
from pathlib import Path

def read_csv(p):
    with open(p,newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def write_csv(p,rows):
    rows=list(rows); fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--write',action='store_true'); a=ap.parse_args(); root=Path(a.root)
    pack=read_csv(root/'cube/nuclear-emergency-bvps-eventday-packout-catalog-rev0343.csv'); rows=[]
    for p in pack:
        base=root/f"field-kits/bvps-rev0343/packet-skeletons/{p['packet_id']}"; missing=[]; counts={}
        for role in ['raw','redacted','custody','qa']:
            d=base/role
            if not d.exists(): missing.append(role)
            counts[role]=len([x for x in d.glob('*') if x.is_file() and x.name.lower() not in ('readme.md','.gitkeep')]) if d.exists() else 0
        payload=sum(counts.values())
        rows.append({'packet_id':p['packet_id'],'branch_gate':p.get('branch_gate',''),'packet_name':p.get('packet_name',''),'missing_required_subfolders':';'.join(missing),'total_payload_count_excluding_placeholders':str(payload),'filesystem_state':'skeleton_ready_no_evidence' if not missing and payload==0 else 'payload_present_requires_intake','ready_to_claim':'no','loss_cap_active':'yes'})
    if a.write: write_csv(root/'cube/nuclear-emergency-bvps-packout-filesystem-smoketest-rev0345.csv',rows)
    print('scanned_packets=%d missing_folder_packets=%d skeleton_ready_no_evidence=%d' % (len(rows),sum(1 for r in rows if r['missing_required_subfolders']),sum(1 for r in rows if r['filesystem_state']=='skeleton_ready_no_evidence')))
if __name__=='__main__': main()
