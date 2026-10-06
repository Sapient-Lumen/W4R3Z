#!/usr/bin/env python3
"""Guardrail for explicit data-transfer grant renewal lineage."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md": ["`renewal_posture`", "`supersedes_grant_digest`", "new artifact plus predecessor digest"],
    "adrs/ADR-0252-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md": ["`renewal_posture`", "`supersedes_grant_digest`", "new artifact plus predecessor digest"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "renewal_posture", "supersedes_grant_digest"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "renewal_posture", "supersedes_grant_digest"],
    "docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "renewal_posture"],
    "docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "renewal_posture"],
    "docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "renewal_posture"],
    "docs/410-desktop-viability-checklist.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "successor grant"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "supersedes_grant_digest"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "supersedes_grant_digest"],
    "docs/99-llm-runbook.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "check_workstation_datatransfer_renewal_lineage.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_renewal_lineage.py", "renewal-lineage"],
    "docs/110-juicy-os-lessons.md": ["Reviewed transfer retries should mint successor grants, not mutate prior grants in place", "docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md"],
    "README.md": ["docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md", "renewal_posture"],
}

def main() -> int:
    errors = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    schema = json.loads((ROOT / 'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    required = schema.get('required') or []
    props = schema.get('properties') or {}
    if 'renewal_posture' not in required:
        errors.append('spec/ui.datatransfer.grant.schema.json must require renewal_posture')
    rp = props.get('renewal_posture') or {}
    enums = rp.get('enum') or []
    for value in ['fresh-grant', 'supersedes-prior-grant']:
        if value not in enums:
            errors.append(f'spec/ui.datatransfer.grant.schema.json renewal_posture missing enum value: {value}')
    if 'supersedes_grant_digest' not in props:
        errors.append('spec/ui.datatransfer.grant.schema.json must define supersedes_grant_digest')
    allof_text = json.dumps(schema.get('allOf') or [])
    for needle in ['"const": "supersedes-prior-grant"', '"required": ["supersedes_grant_digest"]', '"const": "fresh-grant"']:
        if needle not in allof_text:
            errors.append(f'spec/ui.datatransfer.grant.schema.json missing renewal lineage rule: {needle}')
    id_desc = str((((props.get('offer') or {}).get('properties') or {}).get('id') or {}).get('description', ''))
    if 'not the portable source of truth for renewal continuity' not in id_desc:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.id description must reject renewal continuity folklore')

    fresh = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.json').read_text(encoding='utf-8'))
    if fresh.get('renewal_posture') != 'fresh-grant':
        errors.append('spec/examples/ui.datatransfer.grant.json must carry renewal_posture = fresh-grant')
    if 'supersedes_grant_digest' in fresh:
        errors.append('spec/examples/ui.datatransfer.grant.json must not carry supersedes_grant_digest for fresh-grant')

    ocr = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.ocr-inspection-text.json').read_text(encoding='utf-8'))
    if ocr.get('renewal_posture') != 'fresh-grant':
        errors.append('spec/examples/ui.datatransfer.grant.ocr-inspection-text.json must carry renewal_posture = fresh-grant')

    retry = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.retry.json').read_text(encoding='utf-8'))
    if retry.get('renewal_posture') != 'supersedes-prior-grant':
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must carry renewal_posture = supersedes-prior-grant')
    if not str(retry.get('supersedes_grant_digest', '')).startswith('sha256:'):
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must carry sha256 supersedes_grant_digest')

    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer renewal lineage: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
