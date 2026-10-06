#!/usr/bin/env python3
"""Guardrail for successor data-transfer grants staying same-actor-pair and no-wider-offer."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md": ["`successor_scope_posture`", "same actor pair", "no-wider-offer"],
    "adrs/ADR-0253-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md": ["`successor_scope_posture`", "same reviewed transfer story", "fresh-grant required"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "successor_scope_posture", "no-wider"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "successor_scope_posture", "same or narrower"],
    "docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "successor_scope_posture"],
    "docs/410-desktop-viability-checklist.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "fresh grant"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "widened MIME/byte"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "successor_scope_posture"],
    "docs/99-llm-runbook.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "check_workstation_datatransfer_successor_scope.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_successor_scope.py", "successor-scope"],
    "docs/110-juicy-os-lessons.md": ["Successor transfer grants should stay same-actor-pair and no-wider-offer", "docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md"],
    "README.md": ["docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md", "successor_scope_posture"],
}

def _subset(xs: list[str], ys: list[str]) -> bool:
    return set(xs).issubset(set(ys))


def main() -> int:
    errors = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    schema = json.loads((ROOT / 'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    props = schema.get('properties') or {}
    if 'successor_scope_posture' not in props:
        errors.append('spec/ui.datatransfer.grant.schema.json must define successor_scope_posture')
    else:
        enum = (props.get('successor_scope_posture') or {}).get('enum') or []
        if 'same-actor-pair-and-no-wider-offer' not in enum:
            errors.append('spec/ui.datatransfer.grant.schema.json successor_scope_posture missing enum value: same-actor-pair-and-no-wider-offer')
    allof_text = json.dumps(schema.get('allOf') or [])
    for needle in ['"required": ["supersedes_grant_digest", "successor_scope_posture"]', '"const": "same-actor-pair-and-no-wider-offer"']:
        if needle not in allof_text:
            errors.append(f'spec/ui.datatransfer.grant.schema.json missing successor-scope rule: {needle}')
    id_desc = str((((props.get('offer') or {}).get('properties') or {}).get('id') or {}).get('description', ''))
    if 'not the portable source of truth for renewal continuity or successor scope' not in id_desc:
        errors.append('spec/ui.datatransfer.grant.schema.json offer.id description must reject successor-scope folklore')

    fresh = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.json').read_text(encoding='utf-8'))
    if 'successor_scope_posture' in fresh:
        errors.append('spec/examples/ui.datatransfer.grant.json must not carry successor_scope_posture for fresh-grant')

    retry = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.retry.json').read_text(encoding='utf-8'))
    if retry.get('successor_scope_posture') != 'same-actor-pair-and-no-wider-offer':
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must carry successor_scope_posture = same-actor-pair-and-no-wider-offer')

    for field in ['subject', 'offer_source_subject']:
        if (retry.get(field) or {}).get('digest') != (fresh.get(field) or {}).get('digest'):
            errors.append(f'spec/examples/ui.datatransfer.grant.retry.json must keep {field}.digest equal to the fresh grant example')
    for field in ['direction', 'delivery_mode']:
        if retry.get(field) != fresh.get(field):
            errors.append(f'spec/examples/ui.datatransfer.grant.retry.json must keep {field} equal to the fresh grant example')

    retry_offer = retry.get('offer') or {}
    fresh_offer = fresh.get('offer') or {}
    if not _subset(retry_offer.get('mime_types') or [], fresh_offer.get('mime_types') or []):
        errors.append('spec/examples/ui.datatransfer.grant.retry.json mime_types must stay equal-or-subset of the fresh grant example')

    rmax = retry_offer.get('max_bytes')
    fmax = fresh_offer.get('max_bytes')
    if isinstance(rmax, int) and isinstance(fmax, int):
        if rmax > fmax:
            errors.append('spec/examples/ui.datatransfer.grant.retry.json max_bytes must stay <= the fresh grant example')
    elif fmax is not None and rmax is None:
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must not drop a predecessor max_bytes bound under successor continuity')

    for field in ['redaction_profile_digest', 'content_source']:
        if retry_offer.get(field) != fresh_offer.get(field):
            errors.append(f'spec/examples/ui.datatransfer.grant.retry.json must keep offer.{field} unchanged for successor continuity')

    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer successor scope: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
