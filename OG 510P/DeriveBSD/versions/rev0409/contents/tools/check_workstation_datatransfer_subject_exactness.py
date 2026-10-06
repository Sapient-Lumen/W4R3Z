#!/usr/bin/env python3
"""Guardrail for exact source/destination subjects on workstation data transfer evidence."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md": ["offer_source_subject","which compartment offered the data and which compartment accepted it","subject remains the exact holder of the grant/receipt"],
    "adrs/ADR-0248-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subject-exactly.md": ["offer_source_subject","which compartment offered the data and which compartment accepted it","subject remains the exact holder of the grant/receipt"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md","offer_source_subject"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md","offer_source_subject","subject remains the consumer/recipient"],
    "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": ["docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md","offer_source_subject"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md","offer_source_subject"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md","offer_source_subject"],
    "docs/99-llm-runbook.md": ["docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md","check_workstation_datatransfer_subject_exactness.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_subject_exactness.py","offer-source/recipient exactness"],
    "docs/110-juicy-os-lessons.md": ["Transfer receipts should name both the offer-side subject and the receiving subject","docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md"],
    "README.md": ["docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md","offer_source_subject"],
}

def _subject_has_fields(obj,prefix,errors,rel):
    req=obj.get('required') or []
    if prefix not in req: errors.append(f"{rel} must require {prefix}")
    props=obj.get('properties') or {}
    subj=props.get(prefix) or {}
    subj_req=subj.get('required') or []
    for name in ['name','digest']:
        if name not in subj_req: errors.append(f"{rel} must keep {prefix} requiring {name}")

def main():
    errors=[]
    for rel,needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text: errors.append(f"{rel} missing required token: {needle}")
    for rel in ['spec/ui.datatransfer.grant.schema.json','spec/ui.datatransfer.receipt.schema.json']:
        schema=json.loads((ROOT/rel).read_text(encoding='utf-8'))
        _subject_has_fields(schema,'subject',errors,rel)
        _subject_has_fields(schema,'offer_source_subject',errors,rel)
    for rel in ['spec/examples/ui.datatransfer.grant.json','spec/examples/ui.datatransfer.receipt.json','spec/examples/ui.datatransfer.grant.ocr-inspection-text.json','spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json']:
        obj=json.loads((ROOT/rel).read_text(encoding='utf-8'))
        if 'offer_source_subject' not in obj: errors.append(f"{rel} must carry offer_source_subject")
        elif not all(k in (obj.get('offer_source_subject') or {}) for k in ['name','digest']): errors.append(f"{rel} offer_source_subject must carry name + digest")
    grant=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.ocr-inspection-text.json').read_text(encoding='utf-8'))
    if ((grant.get('offer_source_subject') or {}).get('name'))!='app.document-viewer': errors.append('spec/examples/ui.datatransfer.grant.ocr-inspection-text.json must keep offer_source_subject.name=app.document-viewer')
    if ((grant.get('subject') or {}).get('name'))!='app.notes': errors.append('spec/examples/ui.datatransfer.grant.ocr-inspection-text.json must keep subject.name=app.notes')
    receipt=json.loads((ROOT/'spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json').read_text(encoding='utf-8'))
    if ((receipt.get('offer_source_subject') or {}).get('name'))!='app.document-viewer': errors.append('spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json must keep offer_source_subject.name=app.document-viewer')
    if ((receipt.get('subject') or {}).get('name'))!='app.notes': errors.append('spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json must keep subject.name=app.notes')
    if errors:
        [print(f"ERROR: {e}") for e in errors]
        return 1
    print('Workstation data-transfer offer-source/recipient exactness: OK')
    return 0
if __name__=='__main__': raise SystemExit(main())
