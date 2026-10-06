#!/usr/bin/env python3
"""Guardrail for the hardware support qualification-receipt boundary."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load_json(rel:str)->dict: return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def jcs_bytes(obj:dict)->bytes: return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
def digest_obj(obj:dict)->str: return f"sha256:{hashlib.sha256(jcs_bytes(obj)).hexdigest()}"
def main()->int:
    errors=[]
    matrix_schema=load_json('spec/hw.support.matrix.schema.json')
    receipt_schema=load_json('spec/hw.support.qualification.receipt.schema.json')
    report_schema=load_json('spec/hw.compat.report.schema.json')
    qual=(((matrix_schema.get('properties') or {}).get('entries') or {}).get('items') or {}).get('properties', {}).get('qualification', {})
    if 'receipt_digest' not in (qual.get('required') or []): errors.append('spec/hw.support.matrix.schema.json qualification must require receipt_digest')
    if 'receipt_digest' not in (qual.get('properties') or {}): errors.append('spec/hw.support.matrix.schema.json qualification must define receipt_digest')
    for key in ('target','support_claim','qualification','supporting_evidence','decision'):
        if key not in (receipt_schema.get('required') or []): errors.append(f'spec/hw.support.qualification.receipt.schema.json missing required {key}')
    sc_props=((receipt_schema.get('properties') or {}).get('support_claim') or {}).get('properties') or {}
    for key in ('entry_id','support_level','profiles','roles'):
        if key not in sc_props: errors.append(f'spec/hw.support.qualification.receipt.schema.json missing support_claim.{key}')
    if 'matched_qualification_receipt_digests' not in ((((report_schema.get('properties') or {}).get('support_matrix') or {}).get('properties') or {})): errors.append('spec/hw.compat.report.schema.json support_matrix must define matched_qualification_receipt_digests')
    matrix=load_json('spec/examples/hw.support.matrix.json')
    receipt=load_json('spec/examples/hw.support.qualification.receipt.json')
    report=load_json('spec/examples/hw.compat.report.json')
    rd=digest_obj(receipt)
    b=None
    for e in matrix.get('entries',[]):
        if e.get('entry_id')=='b-laptop-intel-trusted-ui-floor-v1': b=e; break
    if not b: errors.append('spec/examples/hw.support.matrix.json missing canonical workstation trusted-UI entry')
    else:
        q=b.get('qualification') or {}
        if q.get('receipt_digest')!=rd: errors.append('spec/examples/hw.support.matrix.json canonical workstation entry qualification.receipt_digest != computed digest of spec/examples/hw.support.qualification.receipt.json')
        claim=receipt.get('support_claim') or {}
        if claim.get('entry_id')!=b.get('entry_id'): errors.append('spec/examples/hw.support.qualification.receipt.json support_claim.entry_id must match canonical workstation matrix entry')
        if claim.get('support_level')!=b.get('support_level'): errors.append('spec/examples/hw.support.qualification.receipt.json support_claim.support_level must match canonical workstation matrix entry')
        if set(claim.get('profiles') or [])!=set(b.get('profiles') or []): errors.append('spec/examples/hw.support.qualification.receipt.json support_claim.profiles must match canonical workstation matrix entry')
        if set(claim.get('roles') or [])!=set(b.get('roles') or []): errors.append('spec/examples/hw.support.qualification.receipt.json support_claim.roles must match canonical workstation matrix entry')
        rq=receipt.get('qualification') or {}
        for key in ('stage','regression_policy','last_verified_at','profile_digest'):
            if rq.get(key)!=q.get(key): errors.append(f'spec/examples/hw.support.qualification.receipt.json qualification.{key} must match canonical workstation matrix entry')
        if set(rq.get('verified_roles') or [])!=set(q.get('verified_roles') or []): errors.append('spec/examples/hw.support.qualification.receipt.json qualification.verified_roles must match canonical workstation matrix entry')
        if set(rq.get('evidence_floor') or [])!=set(q.get('evidence_floor') or []): errors.append('spec/examples/hw.support.qualification.receipt.json qualification.evidence_floor must match canonical workstation matrix entry')
    d=receipt.get('decision') or {}
    if d.get('status')!='accepted' or d.get('published') is not True: errors.append('spec/examples/hw.support.qualification.receipt.json decision must stay accepted + published in the canonical example')
    sm=report.get('support_matrix') or {}
    if rd not in (sm.get('matched_qualification_receipt_digests') or []): errors.append('spec/examples/hw.compat.report.json support_matrix.matched_qualification_receipt_digests must include computed digest of spec/examples/hw.support.qualification.receipt.json')
    if 'b-laptop-intel-trusted-ui-floor-v1' not in (sm.get('matched_entry_ids') or []): errors.append('spec/examples/hw.compat.report.json support_matrix.matched_entry_ids must include the canonical workstation matrix entry')
    doc_checks={
        'docs/320-hardware-compatibility-gates-and-safe-upgrades.md':['`qualification.receipt_digest`','`matched_qualification_receipt_digests`'],
        'docs/410-desktop-viability-checklist.md':['`qualification.receipt_digest`','`matched_qualification_receipt_digests`'],
        'docs/479-hardware-compatibility-posture-by-profile.md':['`qualification.receipt_digest`','`matched_qualification_receipt_digests`'],
        'docs/528-hardware-support-matrix-and-bundled-admission-boundary.md':['`docs/530-hardware-support-qualification-receipt-boundary.md`'],
        'docs/529-hardware-support-promotion-and-qualification-boundary.md':['`qualification.receipt_digest`','`hw.support.qualification.receipt`'],
        'docs/530-hardware-support-qualification-receipt-boundary.md':['`hw.support.qualification.receipt`','`qualification.receipt_digest`','`matched_qualification_receipt_digests`'],
        'docs/266-open-questions-and-risk-register.md':['ADR-0120','`matched_qualification_receipt_digests`'],
        'docs/99-llm-runbook.md':['check_hw_support_qualification_receipt_contract.py','`hw.support.qualification.receipt`'],
        'docs/98-archive-hygiene.md':['check_hw_support_qualification_receipt_contract.py','`qualification.receipt_digest`'],
        'adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md':['`hw.support.qualification.receipt`','`qualification.receipt_digest`','`matched_qualification_receipt_digests`'],
    }
    for rel,needles in doc_checks.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for n in needles:
            if n not in text: errors.append(f'{rel} missing required token: {n}')
    if errors:
        for e in errors: print(f'ERROR: {e}')
        return 1
    print('Hardware support qualification receipt contract: OK')
    return 0
if __name__=='__main__': raise SystemExit(main())
