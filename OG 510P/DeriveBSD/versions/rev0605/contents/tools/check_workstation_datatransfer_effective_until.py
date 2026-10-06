#!/usr/bin/env python3
"""Guardrail for exact datatransfer effective_until lifetime semantics."""
from __future__ import annotations
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md": ["exact `effective_until`", "late delivery after `effective_until` fails closed", "fresh explicit grant / re-offer required"],
    "adrs/ADR-0251-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md": ["must carry exact `effective_until`", "late delivery after `effective_until` fails closed", "fresh explicit grant / re-offer"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until", "late delivery fails closed"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until", "fresh grant / re-offer required"],
    "docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until"],
    "docs/410-desktop-viability-checklist.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until"],
    "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until"],
    "docs/99-llm-runbook.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "check_workstation_datatransfer_effective_until.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_effective_until.py", "effective-until"],
    "docs/110-juicy-os-lessons.md": ["Transfer grants should publish exact effective-until and fail closed on late delivery", "docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md"],
    "README.md": ["docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md", "effective_until"],
}

def parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(timezone.utc)

def main() -> int:
    errors = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    grant_schema = json.loads((ROOT / 'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    required = grant_schema.get('required') or []
    props = grant_schema.get('properties') or {}
    if 'effective_until' not in required:
        errors.append('spec/ui.datatransfer.grant.schema.json must require effective_until')
    if 'effective_until' not in props:
        errors.append('spec/ui.datatransfer.grant.schema.json must define effective_until')
    else:
        desc = str((props.get('effective_until') or {}).get('description', ''))
        for needle in ['exact end of ordinary transfer authority', 'no later than', 'late delivery fails closed']:
            if needle not in desc:
                errors.append(f'spec/ui.datatransfer.grant.schema.json effective_until description missing: {needle}')
    ttl_desc = str((((props.get('offer') or {}).get('properties') or {}).get('ttl_seconds') or {}).get('description', ''))
    if 'exact `effective_until`' not in ttl_desc:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.ttl_seconds description must mention exact `effective_until`')
    exp_desc = str((((props.get('constraints') or {}).get('properties') or {}).get('expires_at') or {}).get('description', ''))
    if 'effective_until' not in exp_desc:
        errors.append('spec/ui.datatransfer.grant.schema.json constraints.expires_at description must mention effective_until')

    receipt_schema = json.loads((ROOT / 'spec/ui.datatransfer.receipt.schema.json').read_text(encoding='utf-8'))
    transferred_desc = str((((receipt_schema.get('properties') or {}).get('transferred_at')) or {}).get('description', ''))
    if 'effective_until' not in transferred_desc:
        errors.append('spec/ui.datatransfer.receipt.schema.json transferred_at description must mention joined grant effective_until')

    pairs = [
        ('spec/examples/ui.datatransfer.grant.json', 'spec/examples/ui.datatransfer.receipt.json'),
        ('spec/examples/ui.datatransfer.grant.ocr-inspection-text.json', 'spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json'),
    ]
    for grant_rel, receipt_rel in pairs:
        grant = json.loads((ROOT / grant_rel).read_text(encoding='utf-8'))
        receipt = json.loads((ROOT / receipt_rel).read_text(encoding='utf-8'))
        if 'effective_until' not in grant:
            errors.append(f'{grant_rel} must carry effective_until')
            continue
        gi = parse_dt(grant['issued_at'])
        ge = parse_dt(grant['effective_until'])
        ttl = (((grant.get('offer') or {}).get('ttl_seconds')))
        if ttl is not None and ge > gi + timedelta(seconds=int(ttl)):
            errors.append(f'{grant_rel} effective_until must be <= issued_at + ttl_seconds')
        expires_at = ((grant.get('constraints') or {}).get('expires_at'))
        if expires_at is not None and ge > parse_dt(expires_at):
            errors.append(f'{grant_rel} effective_until must be <= constraints.expires_at')
        rt = parse_dt(receipt['transferred_at'])
        if rt > ge:
            errors.append(f'{receipt_rel} transferred_at must be <= joined grant effective_until')

    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer exact effective_until lifetime: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
