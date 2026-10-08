#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED_REQUESTS={'RRT-0373-001','RRT-0373-002','RRT-0374-003','RRT-0374-004','RRT-0374-005'}
ALLOWED_PROOFCUTS={'PC-MEET-0374','PC-ANS-0374','PC-EOF-0374','PC-AFN-0374','PC-CAP-0374','PC-CHAIN-0374'}
REQUIRED=['file_name','response_id','dispatch_id','request_id','custodian','received_at','artifact_class','scope_jurisdiction','redaction_state','dlp_status','proofcut_ids','fixture_only']
def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def classify(row, file_path: Path):
    missing=[k for k in REQUIRED if not row.get(k)]
    if missing: return 'rejected_missing_sidecar_field',';'.join(missing)
    if row.get('request_id') not in ALLOWED_REQUESTS: return 'rejected_unknown_request_id',row.get('request_id','')
    pcs=[x.strip() for x in row.get('proofcut_ids','').replace('|',';').split(';') if x.strip()]
    bad=[x for x in pcs if x not in ALLOWED_PROOFCUTS]
    if bad: return 'rejected_unknown_proofcut_id',';'.join(bad)
    if not file_path.exists(): return 'rejected_missing_file',row.get('file_name','')
    if row.get('fixture_only','').lower()=='yes': return 'fixture_only_no_credit','fixture_only=yes'
    if row.get('dlp_status') in {'not_screened','redaction_required','private_only'}:
        return 'candidate_private_or_pending_dlp_no_public_credit',row.get('dlp_status')
    return 'candidate_unadjudicated_no_closure','requires proofcut adjudication'
def main(argv=None):
    ap=argparse.ArgumentParser(description='Hash and DLP-gate BVPS records responses without granting readiness credit.')
    ap.add_argument('--input-dir', required=True)
    ap.add_argument('--sidecar', required=True)
    ap.add_argument('--output-ledger', required=True)
    args=ap.parse_args(argv)
    input_dir=Path(args.input_dir); sidecar=Path(args.sidecar); out=Path(args.output_ledger)
    rows=[]
    for row in read_csv(sidecar):
        fp=input_dir/row.get('file_name','')
        status,reason=classify(row, fp)
        rows.append({'ledger_id':f'RESPLED-0374-{len(rows)+1:03d}','response_id':row.get('response_id',''),'file_name':row.get('file_name',''),'dispatch_id':row.get('dispatch_id',''),'request_id':row.get('request_id',''),'custodian':row.get('custodian',''),'received_at':row.get('received_at',''),'artifact_class':row.get('artifact_class',''),'scope_jurisdiction':row.get('scope_jurisdiction',''),'redaction_state':row.get('redaction_state',''),'dlp_status':row.get('dlp_status',''),'proofcut_ids':row.get('proofcut_ids',''),'fixture_only':row.get('fixture_only',''),'size_bytes':str(fp.stat().st_size) if fp.exists() else '','sha256':sha(fp) if fp.exists() else '','intake_status':status,'reason':reason,'claim_effect':'no_readiness_closure'})
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        fields=['ledger_id','response_id','file_name','dispatch_id','request_id','custodian','received_at','artifact_class','scope_jurisdiction','redaction_state','dlp_status','proofcut_ids','fixture_only','size_bytes','sha256','intake_status','reason','claim_effect']
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f'PASS response_intake_rev0374 rows={len(rows)} candidates={sum(1 for r in rows if r["intake_status"].startswith("candidate"))}')
    return 0
if __name__=='__main__': raise SystemExit(main())
