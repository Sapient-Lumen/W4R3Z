#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'cube/nuclear-emergency-bvps-response-intake-contract-rev0371.csv'
REQUIRED=['file_name','response_id','dispatch_id','request_id','custodian','received_at','artifact_class','scope_jurisdiction','redaction_state','fixture_only']

def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024), b''):
            h.update(c)
    return h.hexdigest()

def classify(row, file_path: Path, allowed_classes: set[str]) -> tuple[str,str]:
    missing=[k for k in REQUIRED if not row.get(k)]
    if missing: return 'rejected_missing_sidecar_field', ';'.join(missing)
    if not file_path.exists(): return 'rejected_missing_file', row.get('file_name','')
    if row.get('fixture_only','').lower()=='yes': return 'fixture_only_no_credit', 'fixture_only=yes'
    if row.get('artifact_class') not in allowed_classes: return 'rejected_unknown_artifact_class', row.get('artifact_class','')
    return 'candidate_unadjudicated_no_closure', 'requires rubric/proofcut adjudication'

def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description='Hash and ledger BVPS records/public-meeting responses without granting readiness credit.')
    ap.add_argument('--input-dir', required=True)
    ap.add_argument('--sidecar', required=True)
    ap.add_argument('--output-ledger', required=True)
    args=ap.parse_args(argv)
    contract=read_csv(CONTRACT)
    allowed={r['intake_class'] for r in contract}
    input_dir=Path(args.input_dir)
    sidecar=Path(args.sidecar)
    out=Path(args.output_ledger)
    rows=[]
    for row in read_csv(sidecar):
        fp=input_dir/row.get('file_name','')
        status,reason=classify(row, fp, allowed)
        digest=sha(fp) if fp.exists() else ''
        rows.append({
            'ledger_id':f"RESPLED-0371-{len(rows)+1:03d}",
            'response_id':row.get('response_id',''),
            'file_name':row.get('file_name',''),
            'dispatch_id':row.get('dispatch_id',''),
            'request_id':row.get('request_id',''),
            'custodian':row.get('custodian',''),
            'received_at':row.get('received_at',''),
            'artifact_class':row.get('artifact_class',''),
            'scope_jurisdiction':row.get('scope_jurisdiction',''),
            'redaction_state':row.get('redaction_state',''),
            'fixture_only':row.get('fixture_only',''),
            'size_bytes':str(fp.stat().st_size) if fp.exists() else '',
            'sha256':digest,
            'intake_status':status,
            'reason':reason,
            'claim_effect':'no_readiness_closure'
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        fieldnames=['ledger_id','response_id','file_name','dispatch_id','request_id','custodian','received_at','artifact_class','scope_jurisdiction','redaction_state','fixture_only','size_bytes','sha256','intake_status','reason','claim_effect']
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)
    bad=[r for r in rows if r['claim_effect']!='no_readiness_closure']
    if bad:
        print('FAIL intake_claim_effect'); return 1
    print(f'PASS response_intake_rev0371 rows={len(rows)} candidates={sum(1 for r in rows if r["intake_status"].startswith("candidate"))} fixtures={sum(1 for r in rows if r["intake_status"].startswith("fixture"))}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
