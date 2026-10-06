#!/usr/bin/env python3
"""Guardrail for successor data-transfer grants staying exact-payload-bound."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md": ["payload digest", "semantic-equivalence", "fresh-grant required"],
    "adrs/ADR-0255-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md": ["same reviewed transfer story", "offer.payload_digest", "semantic-equivalence"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "payload digest", "semantic-equivalence"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "payload digest", "semantic-equivalence"],
    "docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "payload digest", "semantic-equivalence"],
    "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": ["payload_digest", "exact transferred payload", "docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md"],
    "docs/410-desktop-viability-checklist.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "payload digest"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "payload digest", "same reviewed payload"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "payload digest", "semantic-equivalence"],
    "docs/99-llm-runbook.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "check_workstation_datatransfer_successor_payload_digest.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_successor_payload_digest.py", "payload-digest"],
    "docs/110-juicy-os-lessons.md": ["Successor transfer grants should stay exact-payload-bound", "docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md"],
    "README.md": ["docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md", "payload digest", "semantic-equivalence"],
}

def main() -> int:
    errors=[]
    for rel,needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for n in needles:
            if n not in text:
                errors.append(f"{rel} missing required token: {n}")
    grant=json.loads((ROOT/'spec/ui.datatransfer.grant.schema.json').read_text())
    offer=(((grant.get('properties') or {}).get('offer') or {}).get('properties') or {})
    pd=str((offer.get('payload_digest') or {}).get('description',''))
    idd=str((offer.get('id') or {}).get('description',''))
    if 'exact offered payload' not in pd or 'successor continuity' not in pd:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.payload_digest description must state exact successor payload binding')
    if 'exact payload binding' not in idd:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.id description must reject exact-payload folklore')
    if '"offer": {"required": ["payload_digest"]}' not in json.dumps(grant.get('allOf') or []):
        errors.append('spec/ui.datatransfer.grant.schema.json must require offer.payload_digest for successor continuity')
    receipt=json.loads((ROOT/'spec/ui.datatransfer.receipt.schema.json').read_text())
    sp=(((receipt.get('properties') or {}).get('summary') or {}).get('properties') or {})
    if 'exact transferred payload' not in str((sp.get('payload_digest') or {}).get('description','')):
        errors.append('spec/ui.datatransfer.receipt.schema.json summary.payload_digest description must state exact transferred payload')
    fresh=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.json').read_text())
    retry=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.retry.json').read_text())
    ocrg=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.ocr-inspection-text.json').read_text())
    rec=json.loads((ROOT/'spec/examples/ui.datatransfer.receipt.json').read_text())
    ocrr=json.loads((ROOT/'spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json').read_text())
    fpd=(fresh.get('offer') or {}).get('payload_digest'); rpd=(retry.get('offer') or {}).get('payload_digest'); opd=(ocrg.get('offer') or {}).get('payload_digest')
    if not fpd: errors.append('spec/examples/ui.datatransfer.grant.json must carry offer.payload_digest')
    if rpd != fpd: errors.append('spec/examples/ui.datatransfer.grant.retry.json must keep offer.payload_digest equal to the fresh grant example')
    if (rec.get('summary') or {}).get('payload_digest') != fpd: errors.append('spec/examples/ui.datatransfer.receipt.json summary.payload_digest must echo the fresh grant payload digest')
    if not opd: errors.append('spec/examples/ui.datatransfer.grant.ocr-inspection-text.json must carry offer.payload_digest')
    if (ocrr.get('summary') or {}).get('payload_digest') != opd: errors.append('spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json summary.payload_digest must echo the OCR grant payload digest')
    if errors:
        for e in errors: print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer successor payload digest: OK')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
