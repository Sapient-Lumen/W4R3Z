#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, re, textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEMPLATES=ROOT/'cube/nuclear-emergency-bvps-records-request-templates-rev0369.csv'
ROUTES=ROOT/'cube/nuclear-emergency-bvps-records-route-verification-rev0370.csv'
OUTDIR=ROOT/'records-requests/bvps-rev0370'
MANIFEST=ROOT/'cube/nuclear-emergency-bvps-submission-packet-manifest-rev0370.csv'
LEDGER=ROOT/'cube/nuclear-emergency-bvps-request-dispatch-ledger-rev0370.csv'

def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def slug(s):
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:72] or 'request'

def sha256(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def main():
    rows=read_csv(TEMPLATES)
    route_rows=read_csv(ROUTES)
    route_text='\n'.join([f"- {r['route_id']}: {r['route_name']} — {r['current_route_note']} ({r['official_route_or_context_url']})" for r in route_rows])
    OUTDIR.mkdir(parents=True, exist_ok=True)
    manifest=[]; ledger=[]
    for r in rows:
        tid=r['template_id']
        path=OUTDIR/f"{tid.lower()}-{slug(r['custodian_or_route'])}.md"
        body=f"""
        # {r['subject_line']}

        Template ID: {tid}  
        Priority: {r['priority']}  
        Custodian/route: {r['custodian_or_route']}  
        Request type: {r['request_type']}  
        Date range: {r['date_range']}  
        Linked requests: {r['linked_request_ids']}  
        Linked blockers: {r['linked_blockers']}  
        Claim effect: {r['claim_effect']}  
        Dispatch status: staged_not_sent_from_static_archive

        ## Request body

        {r['request_body']}

        ## Target artifacts

        {r['target_artifacts']}

        ## Redaction / privacy instruction

        {r['redaction_instruction']}

        ## Route verification notes

        {route_text}

        ## Non-closure warning

        This request draft is not evidence. A request submission is not evidence. A response is only candidate evidence after it is received, hashed, linked to a custodian/source, checked against the response-adjudication rubric, and assigned a bounded claim effect. No readiness closure is permitted from this packet alone.
        """
        path.write_text(textwrap.dedent(body).lstrip(), encoding='utf-8')
        manifest.append({'packet_id':f'PACK-0370-{len(manifest)+1:03d}','template_id':tid,'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'size_bytes':str(path.stat().st_size),'linked_blockers':r['linked_blockers'],'claim_effect':'request_packet_only_no_readiness_closure'})
        ledger.append({'dispatch_id':f'DISP-0370-{len(ledger)+1:03d}','template_id':tid,'packet_path':str(path.relative_to(ROOT)),'custodian_or_route':r['custodian_or_route'],'planned_send_window':r.get('send_window',''), 'dispatch_status':'staged_not_sent','route_verification_required':'yes','linked_blockers':r['linked_blockers'],'linked_request_ids':r['linked_request_ids'],'claim_effect':'request_not_sent_not_evidence_no_readiness_closure'})
    # include the public meeting card if present
    card=OUTDIR/'public-meeting-question-card-rev0370.md'
    if card.exists():
        manifest.append({'packet_id':f'PACK-0370-{len(manifest)+1:03d}','template_id':'PUBLIC-MEETING-CARD-0370','path':str(card.relative_to(ROOT)),'sha256':sha256(card),'size_bytes':str(card.stat().st_size),'linked_blockers':'BLK-0368-001;BLK-0368-002;BLK-0368-003;BLK-0368-004;BLK-0368-005','claim_effect':'capture_card_only_no_readiness_closure'})
    write_csv(MANIFEST, manifest, ['packet_id','template_id','path','sha256','size_bytes','linked_blockers','claim_effect'])
    write_csv(LEDGER, ledger, ['dispatch_id','template_id','packet_path','custodian_or_route','planned_send_window','dispatch_status','route_verification_required','linked_blockers','linked_request_ids','claim_effect'])
    print(f'PASS submission_packet_rev0370 packets={len(manifest)} ledger_rows={len(ledger)}')
if __name__=='__main__': main()
