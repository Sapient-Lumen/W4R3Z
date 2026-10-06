#!/usr/bin/env python3
"""Guardrail for exact datatransfer receipt joins back to grant artifacts."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md": ["grant_digest", "exact `ui.datatransfer.grant` artifact", "offer_id`, `lease_id`, or broker memory"],
    "adrs/ADR-0249-workstation-datatransfer-receipts-join-exact-grants-by-digest.md": ["grant_digest", "exact `ui.datatransfer.grant` artifact", "offer_id`, `lease_id`, or broker-side state"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "grant_digest"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "grant_digest", "which exact grant artifact was consumed"],
    "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "grant_digest"],
    "docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "grant_digest"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "grant_digest"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "grant_digest"],
    "docs/99-llm-runbook.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "check_workstation_datatransfer_grant_digest_join.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_grant_digest_join.py", "grant-digest join"],
    "docs/110-juicy-os-lessons.md": ["Transfer receipts should point back to the exact transfer grant artifact", "docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md"],
    "README.md": ["docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md", "grant_digest"],
}

def main():
    errors=[]
    for rel,needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    schema=json.loads((ROOT/'spec/ui.datatransfer.receipt.schema.json').read_text(encoding='utf-8'))
    if 'grant_digest' not in (schema.get('required') or []):
        errors.append('spec/ui.datatransfer.receipt.schema.json must require grant_digest')
    if 'grant_digest' not in (schema.get('properties') or {}):
        errors.append('spec/ui.datatransfer.receipt.schema.json must define grant_digest')
    else:
        if ((schema['properties']['grant_digest']).get('type')) != 'string':
            errors.append('spec/ui.datatransfer.receipt.schema.json grant_digest must be a string')
    for rel in ['spec/examples/ui.datatransfer.receipt.json','spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json']:
        obj=json.loads((ROOT/rel).read_text(encoding='utf-8'))
        if 'grant_digest' not in obj:
            errors.append(f'{rel} must carry grant_digest')
        elif not str(obj.get('grant_digest','')).startswith('sha256:'):
            errors.append(f'{rel} grant_digest must look like a sha256 digest')
    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer exact grant-digest join: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
