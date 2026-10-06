#!/usr/bin/env python3
"""Guardrail for successor data-transfer grants keeping payload lineage and redaction posture exact."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md": ["`offer.content_source`", "`offer.redaction_profile_digest`", "fresh-grant required"],
    "adrs/ADR-0254-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md": ["same reviewed transfer story", "offer.content_source", "offer.redaction_profile_digest"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "payload lineage", "redaction posture"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "payload lineage", "redaction posture"],
    "docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "payload lineage", "redaction posture"],
    "docs/410-desktop-viability-checklist.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "fresh grant"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "payload lineage", "redaction posture"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "content_source", "redaction_profile_digest"],
    "docs/99-llm-runbook.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "check_workstation_datatransfer_successor_payload_lineage.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_successor_payload_lineage.py", "payload-lineage"],
    "docs/110-juicy-os-lessons.md": ["Successor transfer grants should keep payload lineage and redaction posture exact", "docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md"],
    "README.md": ["docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md", "payload lineage", "redaction posture"],
}

def main() -> int:
    errors = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    schema = json.loads((ROOT / 'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    offer_props = (((schema.get('properties') or {}).get('offer') or {}).get('properties') or {})
    redaction_desc = str((offer_props.get('redaction_profile_digest') or {}).get('description', ''))
    content_desc = str((offer_props.get('content_source') or {}).get('description', ''))
    id_desc = str((offer_props.get('id') or {}).get('description', ''))
    if 'successor continuity keeps this exact' not in redaction_desc:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.redaction_profile_digest description must state exact successor continuity')
    if 'successor continuity keeps this exact when present' not in content_desc:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.content_source description must state exact successor continuity when present')
    if 'payload lineage' not in id_desc:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.id description must reject payload-lineage folklore')

    fresh = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.json').read_text(encoding='utf-8'))
    retry = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.retry.json').read_text(encoding='utf-8'))
    fresh_offer = fresh.get('offer') or {}
    retry_offer = retry.get('offer') or {}
    for field in ['redaction_profile_digest', 'content_source']:
        if retry_offer.get(field) != fresh_offer.get(field):
            errors.append(f'spec/examples/ui.datatransfer.grant.retry.json must keep offer.{field} unchanged for successor continuity')
        if (field in retry_offer) != (field in fresh_offer):
            errors.append(f'spec/examples/ui.datatransfer.grant.retry.json must preserve offer.{field} presence/absence parity with the fresh grant example')

    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer successor payload lineage: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
