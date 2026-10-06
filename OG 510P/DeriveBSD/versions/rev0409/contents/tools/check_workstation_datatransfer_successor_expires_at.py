#!/usr/bin/env python3
"""Guardrail for successor data-transfer grants keeping absolute expiry posture exact."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md": ["constraints.expires_at", "fresh-grant required", "same reviewed transfer story"],
    "adrs/ADR-0259-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md": ["constraints.expires_at", "fresh-grant required", "same reviewed transfer story"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "constraints.expires_at", "fresh-grant required"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "constraints.expires_at", "fresh-grant required"],
    "docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "constraints.expires_at", "fresh-grant required"],
    "docs/410-desktop-viability-checklist.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "absolute expiry posture exact"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "constraints.expires_at", "fresh-grant required"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "constraints.expires_at", "fresh-grant required"],
    "docs/99-llm-runbook.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "check_workstation_datatransfer_successor_expires_at.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_successor_expires_at.py", "successor-expires-at"],
    "docs/110-juicy-os-lessons.md": ["Successor transfer grants should keep absolute expiry posture exact", "docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md"],
    "README.md": ["docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md", "constraints.expires_at", "fresh-grant required"],
}

def main() -> int:
    errors = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    grant_schema = json.loads((ROOT / 'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    props = grant_schema.get('properties') or {}
    constraints_props = ((props.get('constraints') or {}).get('properties') or {})
    exp_desc = str((constraints_props.get('expires_at') or {}).get('description', ''))
    for needle in ['effective_until', 'successor continuity keeps this exact', 'fresh-grant required']:
        if needle not in exp_desc:
            errors.append(f'spec/ui.datatransfer.grant.schema.json constraints.expires_at description missing: {needle}')
    eff_desc = str((props.get('effective_until') or {}).get('description', ''))
    for needle in ['constraints.expires_at', 'no later than']:
        if needle not in eff_desc:
            errors.append(f'spec/ui.datatransfer.grant.schema.json effective_until description missing: {needle}')

    grant = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.json').read_text(encoding='utf-8'))
    retry = json.loads((ROOT / 'spec/examples/ui.datatransfer.grant.retry.json').read_text(encoding='utf-8'))
    gexp = ((grant.get('constraints') or {}).get('expires_at'))
    rexp = ((retry.get('constraints') or {}).get('expires_at'))
    if gexp is None:
        errors.append('spec/examples/ui.datatransfer.grant.json must carry constraints.expires_at for successor expiry-parity coverage')
    if rexp is None:
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must carry constraints.expires_at for successor expiry-parity coverage')
    if gexp is not None and rexp is not None and gexp != rexp:
        errors.append('spec/examples/ui.datatransfer.grant.retry.json constraints.expires_at must match spec/examples/ui.datatransfer.grant.json under successor continuity')
    if retry.get('renewal_posture') != 'supersedes-prior-grant':
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must stay successor-shaped')

    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer successor absolute expiry posture: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
