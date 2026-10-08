#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCKBOX=ROOT/'evidence-bags/bvps-response-intake-lockbox-rev0371.zip'
MAN=ROOT/'cube/bvps-response-intake-lockbox-manifest-rev0371.csv'
FILES=[
 'lockbox-templates/bvps-response-rev0371/README.md',
 'lockbox-templates/bvps-response-rev0371/response-sidecar-template.csv',
 'lockbox-templates/bvps-response-rev0371/response-hash-ledger-template.csv',
 'lockbox-templates/bvps-response-rev0371/response-adjudication-ledger-template.csv',
 'lockbox-templates/bvps-response-rev0371/nonresponsive-response-ledger-template.csv',
 'lockbox-templates/bvps-response-rev0371/redaction-and-exemption-ledger-template.csv',
 'lockbox-templates/bvps-response-rev0371/followup-task-ledger-template.csv',
 'cube/nuclear-emergency-bvps-response-intake-contract-rev0371.csv',
 'cube/nuclear-emergency-bvps-response-to-proofcut-map-rev0371.csv',
 'cube/nuclear-emergency-bvps-response-rejection-reasons-rev0371.csv',
]
def sha(p: Path) -> str:
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def main() -> int:
    LOCKBOX.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    with zipfile.ZipFile(LOCKBOX,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel in FILES:
            p=ROOT/rel
            if not p.exists():
                print('FAIL missing_lockbox_source='+rel); return 1
            z.write(p, rel)
            info=z.getinfo(rel)
            rows.append({'lockbox_id':'RESPLOCK-0371-001','inner_path':rel,'size_bytes':str(info.file_size),'compressed_size':str(info.compress_size),'sha256':sha(p),'purpose':'response_intake_template_or_contract'})
    with MAN.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['lockbox_id','inner_path','size_bytes','compressed_size','sha256','purpose']); w.writeheader(); w.writerows(rows)
    with zipfile.ZipFile(LOCKBOX) as z:
        bad=z.testzip()
    if bad:
        print('FAIL lockbox_bad_entry='+bad); return 1
    print(f'PASS built_response_intake_lockbox_rev0371 files={len(rows)} size={LOCKBOX.stat().st_size}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
