#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback attach receipt hint posture."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

errors: list[str] = []

grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'
attach_rel = 'spec/examples/device.attach.receipt.removable-media-local-ingest.json'
plan_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'

grant = load_json(grant_rel)
attach = load_json(attach_rel)
plan = load_json(plan_rel)

constraints = grant.get('constraints') or {}
expected_constraints = {
    'attach_receipt_observation_posture': 'current-presence-hints-evidence-only',
    'reattach_hint_authority': 'no-auto-resume-on-same-hints',
}
for key, value in expected_constraints.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
if constraints.get('attach_receipt_required_observed_hints') != ['transport_locator', 'storage_provider']:
    errors.append(f"{grant_rel}: constraints.attach_receipt_required_observed_hints must stay ['transport_locator', 'storage_provider']")
if constraints.get('attach_receipt_optional_observed_hints') != ['disk_ident', 'physical_path']:
    errors.append(f"{grant_rel}: constraints.attach_receipt_optional_observed_hints must stay ['disk_ident', 'physical_path']")
for token in ('finite current-presence hint bundle', 'evidence-only', 'same-hints-on-reattach non-authoritative'):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

runtime = attach.get('runtime') or {}
mapping = runtime.get('mapping') or {}
observed_hints = mapping.get('observed_hints') or {}
for key in ('transport_locator', 'storage_provider', 'disk_ident', 'physical_path'):
    if not observed_hints.get(key):
        errors.append(f'{attach_rel}: runtime.mapping.observed_hints.{key} must be present in the canonical example')
for key, value in {
    'observed_hint_posture': 'current-presence-hints-evidence-only',
    'observed_hint_absence_posture': 'absence-recorded-no-authority-upgrade',
    'reattach_hint_authority': 'no-auto-resume-on-same-hints',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{attach_rel}: runtime.mapping.{key} must stay {value}')
if mapping.get('selected_provider') != observed_hints.get('storage_provider'):
    errors.append(f'{attach_rel}: runtime.mapping.selected_provider must match observed_hints.storage_provider')
if runtime.get('backend') != 'host-local-removable-ingest':
    errors.append(f"{attach_rel}: runtime.backend must stay 'host-local-removable-ingest'")
for token in ('finite current-presence hint bundle', 'evidence-only', 'same-hints-on-reattach non-authoritative'):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')
DOC_TOKENS = {
    'adrs/ADR-0323-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md': ['observed current-presence hint bundle', 'usbconfig(8)', 'diskinfo(8)', 'camcontrol(8)', 'evidence-only'],
    'docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md': ['observed current-presence hint bundle', 'evidence-only', 'same hints on reattach still do not auto-resume'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['attach-evidence cut is explicit too', 'finite observed current-presence hint bundle'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['attach-evidence cut is fixed too', 'spec/examples/device.attach.receipt.removable-media-local-ingest.json'],
    'docs/410-desktop-viability-checklist.md': ['attach-evidence cut is fixed too', 'docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['finite observed current-presence hint bundle', 'evidence-only and non-authoritative on reattach'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['spec/examples/device.attach.receipt.removable-media-local-ingest.json', 'finite current-presence hint bundle without turning it into durable authority'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0323-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md'],
    'docs/110-juicy-os-lessons.md': ['canonical attach receipt **finite and hint-shaped**'],
    'docs/32-curated-references.md': ['usbconfig(8) (`ugenX.Y` addressing plus current descriptor/summary/interface-driver inspection)', 'devd.conf(5): attach/detach event rules and actions, plus VFS mount/unmount notifications'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_attach_receipt_hints.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_attach_receipt_hints.py'],
    'docs/00-index.md': ['docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md', 'check_removable_media_local_attach_receipt_hints.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')
if errors:
    print('removable-media local-fallback attach receipt hint check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback attach receipt hint check passed')
