#!/usr/bin/env python3
"""Guardrail for successor data-transfer grants keeping delivery mode exact."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md": ["delivery_mode", "single-delivery", "fresh-grant required"],
    "adrs/ADR-0257-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md": ["delivery_mode", "single-delivery", "same reviewed transfer story"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "delivery_mode", "multi-delivery"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "delivery_mode", "multi-delivery"],
    "docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "delivery_mode", "multi-delivery"],
    "docs/410-desktop-viability-checklist.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "delivery mode"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "delivery_mode", "multi-delivery"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "delivery_mode", "multi-delivery"],
    "docs/99-llm-runbook.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "check_workstation_datatransfer_successor_delivery_mode.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_successor_delivery_mode.py", "successor-delivery-mode"],
    "docs/110-juicy-os-lessons.md": ["Successor transfer grants should keep delivery mode exact", "docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md"],
    "README.md": ["docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md", "delivery_mode", "multi-delivery"],
}

def main() -> int:
    errors=[]
    for rel, needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    schema=json.loads((ROOT/'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    desc=str(((schema.get('properties') or {}).get('delivery_mode') or {}).get('description',''))
    if 'successor continuity' not in desc or 'keeps delivery_mode exact' not in desc or 'fresh-grant required' not in desc:
        errors.append('spec/ui.datatransfer.grant.schema.json delivery_mode description must state exact successor continuity and fresh-grant requirement')
    fresh=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.json').read_text(encoding='utf-8'))
    retry=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.retry.json').read_text(encoding='utf-8'))
    if fresh.get('delivery_mode') != retry.get('delivery_mode'):
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must keep delivery_mode equal to the fresh grant example')
    if retry.get('delivery_mode') != 'single-delivery':
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must stay on the single-delivery lane in the canonical successor example')
    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer successor delivery mode: OK')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
