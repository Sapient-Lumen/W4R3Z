#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'lockbox-templates/bvps-rev0370'
ZIP=ROOT/'evidence-bags/bvps-public-meeting-lockbox-rev0370.zip'
MAN=ROOT/'cube/bvps-public-meeting-lockbox-manifest-rev0370.csv'

def sha256(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def main():
    files=sorted([p for p in SRC.rglob('*') if p.is_file()])
    if not files:
        print('FAIL no_lockbox_templates'); raise SystemExit(1)
    rows=[]; ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            inner=str(p.relative_to(ROOT))
            z.write(p, inner)
            info=z.getinfo(inner)
            rows.append({'lockbox_id':'LOCKBOX-0370-001','inner_path':inner,'size_bytes':str(info.file_size),'compressed_size':str(info.compress_size),'sha256':sha256(p),'purpose':'empty_public_meeting_capture_template_no_real_evidence','claim_effect':'template_only_no_readiness_closure'})
    with MAN.open('w',newline='',encoding='utf-8') as f:
        fields=['lockbox_id','inner_path','size_bytes','compressed_size','sha256','purpose','claim_effect']
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    bad=zipfile.ZipFile(ZIP).testzip()
    if bad:
        print('FAIL lockbox_bad_member='+bad); raise SystemExit(1)
    print(f'PASS lockbox_rev0370 files={len(rows)} zip={ZIP.relative_to(ROOT)}')
if __name__=='__main__': main()
