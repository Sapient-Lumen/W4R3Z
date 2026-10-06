#!/usr/bin/env python3
"""Guardrail for successor data-transfer grants keeping foreground requirement exact."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md": ["requires_foreground", "foreground", "fresh-grant required"],
    "adrs/ADR-0256-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md": ["requires_foreground", "foreground", "same reviewed transfer story"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "requires_foreground", "background-capable"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "requires_foreground", "background-capable"],
    "docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "requires_foreground", "foreground"],
    "docs/410-desktop-viability-checklist.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "foreground"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "requires_foreground", "background-capable"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "requires_foreground", "foreground"],
    "docs/99-llm-runbook.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "check_workstation_datatransfer_successor_foreground.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_successor_foreground.py", "successor-foreground"],
    "docs/110-juicy-os-lessons.md": ["Successor transfer grants should keep foreground requirement exact", "docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md"],
    "README.md": ["docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md", "requires_foreground", "foreground"],
}

def main() -> int:
    errors=[]
    for rel, needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    schema=json.loads((ROOT/'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    constraints=(((schema.get('properties') or {}).get('constraints') or {}).get('properties') or {})
    desc=str((constraints.get('requires_foreground') or {}).get('description',''))
    if 'successor continuity' not in desc or 'fresh-grant required' not in desc:
        errors.append('spec/ui.datatransfer.grant.schema.json constraints.requires_foreground description must state exact successor continuity and fresh-grant requirement')
    fresh=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.json').read_text(encoding='utf-8'))
    retry=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.retry.json').read_text(encoding='utf-8'))
    f=((fresh.get('constraints') or {}).get('requires_foreground', None))
    r=((retry.get('constraints') or {}).get('requires_foreground', None))
    if f != r:
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must keep constraints.requires_foreground equal to the fresh grant example')
    if ((fresh.get('constraints') or {}).get('requires_foreground', '__missing__') == '__missing__') != (((retry.get('constraints') or {}).get('requires_foreground', '__missing__') == '__missing__')):
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must preserve constraints.requires_foreground presence/absence parity with the fresh grant example')
    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer successor foreground requirement: OK')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
