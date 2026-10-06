#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback present-device-instance-only approval scope."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


errors: list[str] = []

grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'
plan_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'
receipt_rel = 'spec/examples/content.import.receipt.removable-media-local-ingest.json'

grant = load_json(grant_rel)
plan = load_json(plan_rel)
receipt = load_json(receipt_rel)

constraints = grant.get('constraints') or {}
expected = {
    'approval_scope': 'present-device-instance-only-first-cut',
    'detach_revocation_posture': 'auto-revoke-on-detach-expiry-or-explicit-revoke',
    'reattach_posture': 'fresh-grant-required',
    'remembered_approval_scope': 'current-presence-only',
}
for key, value in expected.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'present-device-instance-only',
    'reattaching the same nominal medium requires a fresh grant',
    'serial or disk-ident hints look the same',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

for rel, text in ((plan_rel, plan.get('notes') or ''), (receipt_rel, ((receipt.get('metadata') or {}).get('notes') or ''))):
    for token in (
        'present-device-instance-only',
        'requires a fresh grant',
        'serial or disk-ident hints look the same',
    ):
        if token not in text:
            errors.append(f'{rel}: notes missing {token!r}')

if 'present-device-only' not in (receipt.get('result') or {}).get('message', ''):
    errors.append(f'{receipt_rel}: result.message must mention present-device-only')

DOC_TOKENS = {
    'adrs/ADR-0322-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md': [
        'present-device-instance-only', 'reattach requires a fresh grant', 'devd.conf(5)', 'camcontrol(8)', 'diskinfo(8)'
    ],
    'docs/732-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md': [
        'present-device-instance-only', 'reattach requires a fresh grant', 'lease/revocation spine'
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'present-device-instance-only', 'reattach requires a fresh grant'
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'present-device-instance-only', 'reattach requires a fresh grant'
    ],
    'docs/410-desktop-viability-checklist.md': [
        'present-device-instance-only', 'reattach requires a fresh grant'
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'present-device-instance-only', 'reattach requires a fresh grant'
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0322-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md'
    ],
    'docs/110-juicy-os-lessons.md': [
        'present-device-instance-only', 'reattach requires a fresh grant'
    ],
    'docs/32-curated-references.md': [
        'FreeBSD `camcontrol(8)`', 'FreeBSD `diskinfo(8)`'
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_present_device_scope.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_present_device_scope.py'],
    'docs/00-index.md': ['docs/732-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md', 'check_removable_media_local_present_device_scope.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback present-device-instance-only approval check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('removable-media local-fallback present-device-instance-only approval check passed')
