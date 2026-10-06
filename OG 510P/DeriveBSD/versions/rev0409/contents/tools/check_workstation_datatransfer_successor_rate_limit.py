#!/usr/bin/env python3
"""Guardrail for successor data-transfer grants keeping rate-limit posture exact."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md": ["constraints.rate_limit", "fresh-grant required", "same reviewed transfer story"],
    "adrs/ADR-0258-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md": ["constraints.rate_limit", "fresh-grant required", "same reviewed transfer story"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "constraints.rate_limit", "fresh-grant required"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "constraints.rate_limit", "fresh-grant required"],
    "docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "constraints.rate_limit", "fresh-grant required"],
    "docs/410-desktop-viability-checklist.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "rate-limit posture exact"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "constraints.rate_limit", "fresh-grant required"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "constraints.rate_limit", "fresh-grant required"],
    "docs/99-llm-runbook.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "check_workstation_datatransfer_successor_rate_limit.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_successor_rate_limit.py", "successor-rate-limit"],
    "docs/110-juicy-os-lessons.md": ["Successor transfer grants should keep rate-limit posture exact", "docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md"],
    "README.md": ["docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md", "constraints.rate_limit", "fresh-grant required"],
}

def main() -> int:
    errors=[]
    for rel, needles in DOCS.items():
        text=(ROOT/rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    schema=json.loads((ROOT/'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    desc=str((((schema.get('properties') or {}).get('constraints') or {}).get('properties') or {}).get('rate_limit',{}).get('description',''))
    if 'successor continuity' not in desc or 'constraints.rate_limit' not in desc or 'fresh-grant required' not in desc:
        errors.append('spec/ui.datatransfer.grant.schema.json constraints.rate_limit description must state exact successor continuity and fresh-grant requirement')
    fresh=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.json').read_text(encoding='utf-8'))
    retry=json.loads((ROOT/'spec/examples/ui.datatransfer.grant.retry.json').read_text(encoding='utf-8'))
    fresh_rl=((fresh.get('constraints') or {}).get('rate_limit'))
    retry_rl=((retry.get('constraints') or {}).get('rate_limit'))
    if fresh_rl != retry_rl:
        errors.append('spec/examples/ui.datatransfer.grant.retry.json must keep constraints.rate_limit equal to the fresh grant example')
    if not fresh_rl:
        errors.append('spec/examples/ui.datatransfer.grant.json must carry constraints.rate_limit in the canonical successor-parity example')
    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer successor rate-limit posture: OK')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
