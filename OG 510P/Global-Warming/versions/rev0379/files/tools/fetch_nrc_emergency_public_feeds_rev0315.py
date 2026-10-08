#!/usr/bin/env python3
"""Fetch rev0315 public feed targets, write sha256 and bytes; never upgrades readiness claims."""
import csv, hashlib, sys, urllib.request
from pathlib import Path
contract=Path(sys.argv[1] if len(sys.argv)>1 else "cube/nuclear-emergency-public-feed-acquisition-contract-rev0315.csv")
out=Path(sys.argv[2] if len(sys.argv)>2 else "cube/nuclear-emergency-public-feed-download-attempt-rev0315.csv")
rows=list(csv.DictReader(contract.open(newline="")))
fields=["attempt_id","feed_id","source_id","feed_name","url","outcome","bytes","sha256","error_class","error_detail","status"]
outs=[]
for i,r in enumerate([x for x in rows if x["feed_class"].startswith("official_machine")],1):
    try:
        data=urllib.request.urlopen(r["feed_url"],timeout=20).read()
        outs.append({"attempt_id":f"FETCH0315_{i:03d}","feed_id":r["feed_id"],"source_id":r["source_id"],"feed_name":r["feed_name"],"url":r["feed_url"],"outcome":"downloaded","bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"error_class":"","error_detail":"","status":"downloaded_hash_only_no_claim_upgrade"})
    except Exception as e:
        outs.append({"attempt_id":f"FETCH0315_{i:03d}","feed_id":r["feed_id"],"source_id":r["source_id"],"feed_name":r["feed_name"],"url":r["feed_url"],"outcome":"failed","bytes":0,"sha256":"","error_class":type(e).__name__,"error_detail":str(e),"status":"open_fetch_blocker"})
with out.open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(outs)
