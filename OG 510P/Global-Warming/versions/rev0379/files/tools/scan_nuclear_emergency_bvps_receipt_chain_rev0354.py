#!/usr/bin/env python3
import csv, os, hashlib
base=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
rows=[]
for i in range(1,61):
    pkt=f'PKT-{i:03d}'
    path=os.path.join(base,'field-kits','bvps-rev0349','receipts',f'{pkt}-receipt.md')
    h='MISSING'
    if os.path.exists(path):
        sha=hashlib.sha256();
        with open(path,'rb') as f:
            for b in iter(lambda:f.read(1048576),b''):
                sha.update(b)
        h=sha.hexdigest()
    rows.append({'packet_id':pkt,'receipt_path':path,'sha256':h})
out=os.path.join(base,'cube','nuclear-emergency-bvps-receipt-scan-runtime-rev0354.csv')
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['packet_id','receipt_path','sha256']); w.writeheader(); w.writerows(rows)
print(out)
