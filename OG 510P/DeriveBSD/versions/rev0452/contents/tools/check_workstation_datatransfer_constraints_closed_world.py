#!/usr/bin/env python3
"""Guardrail for ordinary workstation data-transfer constraints staying closed-world."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md": ["closed-world typed vocabulary", "no hidden successor execution posture", "future extra posture needs an ADR/spec change"],
    "adrs/ADR-0260-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md": ["closed-world", "same reviewed transfer story", "unknown or product-local extra `constraints.*` keys are **not baseline**"],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "closed-world", "hidden extra `constraints.*` keys"],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "closed-world", "hidden extra `constraints.*` keys"],
    "docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "closed-world typed vocabulary"],
    "docs/410-desktop-viability-checklist.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "closed-world typed `constraints` vocabulary"],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "closed-world"],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "hidden extra `constraints.*` keys"],
    "docs/99-llm-runbook.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "check_workstation_datatransfer_constraints_closed_world.py"],
    "docs/98-archive-hygiene.md": ["check_workstation_datatransfer_constraints_closed_world.py", "constraints-closed-world"],
    "docs/110-juicy-os-lessons.md": ["closed-world and no hidden successor posture", "docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md"],
    "README.md": ["docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md", "closed-world typed vocabulary"],
}

def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    schema = json.loads((ROOT / 'spec/ui.datatransfer.grant.schema.json').read_text(encoding='utf-8'))
    constraints = ((schema.get('properties') or {}).get('constraints') or {})
    if constraints.get('additionalProperties') is not False:
        errors.append('spec/ui.datatransfer.grant.schema.json constraints.additionalProperties must be false')
    desc = str(constraints.get('description', ''))
    for needle in ['closed-world typed vocabulary', 'requires_foreground', 'rate_limit', 'expires_at']:
        if needle not in desc:
            errors.append(f'spec/ui.datatransfer.grant.schema.json constraints description missing: {needle}')
    props = set((constraints.get('properties') or {}).keys())
    expected = {'requires_foreground', 'rate_limit', 'expires_at'}
    if props != expected:
        errors.append(f'spec/ui.datatransfer.grant.schema.json constraints properties must equal {sorted(expected)}, got {sorted(props)}')

    for rel in ['spec/examples/ui.datatransfer.grant.json', 'spec/examples/ui.datatransfer.grant.retry.json']:
        obj = json.loads((ROOT / rel).read_text(encoding='utf-8'))
        keys = set((obj.get('constraints') or {}).keys())
        if not keys.issubset(expected):
            errors.append(f'{rel} contains non-baseline constraints keys: {sorted(keys - expected)}')

    if errors:
        for e in errors:
            print(f'ERROR: {e}')
        return 1
    print('Workstation data-transfer constraints closed-world: OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
