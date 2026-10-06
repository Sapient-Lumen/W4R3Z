#!/usr/bin/env python3
"""Guardrail for one-shot semantics on ordinary single-delivery workstation transfer grants."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md": ["delivery_mode = single-delivery", "first successful read-side transfer exhausts the grant", "fresh explicit grant / re-offer"],
    "adrs/ADR-0250-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md": ["delivery_mode = single-delivery", "first successful read-side transfer exhausts the grant", "fresh explicit grant / re-offer"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "fresh grant / re-offer required", "grant_exhausted"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "first successful read-side transfer exhausts the grant", "fresh grant / re-offer required"],
    "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "fresh grant / re-offer required"],
    "docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "grant_exhausted = true"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "fresh grant / re-offer required"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "fresh grant / re-offer required"],
    "docs/410-desktop-viability-checklist.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "fresh grant / re-offer required"],
    "docs/99-llm-runbook.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "check_workstation_datatransfer_single_delivery_exhaustion.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_single_delivery_exhaustion.py", "single-delivery exhaustion"],
    "docs/110-juicy-os-lessons.md": ["Single-delivery transfer grants should be one-shot and fresh-grant-required after success", "docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md"],
    "README.md": ["docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md", "fresh grant / re-offer required"],
}

def main() -> int:
    errors=[]
    for rel,needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    grant_schema=json.loads((ROOT/'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    delivery=(grant_schema.get('properties') or {}).get('delivery_mode') or {}
    if 'first successful read-side transfer exhausts the grant' not in str(delivery.get('description','')):
        errors.append('spec/ui.datatransfer.grant.schema.json delivery_mode description must state that first successful read-side transfer exhausts the grant')
    receipt_schema=json.loads((ROOT/'spec/ui.datatransfer.receipt.schema.json').read_text(encoding='utf-8'))
    required=receipt_schema.get('required') or []
    if 'grant_exhausted' not in required:
        errors.append('spec/ui.datatransfer.receipt.schema.json must require grant_exhausted')
    prop=(receipt_schema.get('properties') or {}).get('grant_exhausted') or {}
    if prop.get('type')!='boolean':
        errors.append('spec/ui.datatransfer.receipt.schema.json grant_exhausted must be boolean')
    desc=str(prop.get('description',''))
    for needle in ['True for the ordinary single-delivery case', 'fresh grant / re-offer']:
        if needle not in desc:
            errors.append(f'spec/ui.datatransfer.receipt.schema.json grant_exhausted description missing: {needle}')
    for rel in ['spec/examples/ui.datatransfer.receipt.json','spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json']:
        obj=json.loads((ROOT/rel).read_text(encoding='utf-8'))
        if obj.get('grant_exhausted') is not True:
            errors.append(f'{rel} must keep grant_exhausted=true for the ordinary single-delivery lane')
    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer single-delivery exhaustion: OK')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
