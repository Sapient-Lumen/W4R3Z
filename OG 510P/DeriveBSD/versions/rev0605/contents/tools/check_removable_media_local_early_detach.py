#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback verified-capture early-detach posture."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

errors: list[str] = []

grant_rel = 'spec/examples/device.attach.grant.removable-media-local-ingest.json'
plan_rel = 'spec/examples/content.import.plan.removable-media-local-ingest.json'
detach_rel = 'spec/examples/device.detach.receipt.removable-media-local-ingest.json'
receipt_rel = 'spec/examples/content.import.receipt.removable-media-local-ingest.json'

grant = load_json(grant_rel)
plan = load_json(plan_rel)
detach = load_json(detach_rel)
receipt = load_json(receipt_rel)

constraints = grant.get('constraints') or {}
for key, value in {
    'post_capture_detach_posture': 'detach-after-verified-capture-before-later-ops',
    'post_capture_detach_evidence': 'device-detach-receipt-required-before-later-ops',
    'post_capture_device_presence': 'not-required-after-verified-capture',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'device.detach.receipt',
    'after capture verifies',
    'before later classify/scan/sanitize work continues',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_capture_detach_posture': 'detach-after-verified-capture-before-later-ops',
        'post_capture_detach_evidence': 'device-detach-receipt-required-before-later-ops',
        'post_capture_device_presence': 'not-required-after-verified-capture',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')

if detach.get('kind') != 'device-detach-receipt':
    errors.append(f'{detach_rel}: kind must stay device-detach-receipt')
if detach.get('reason') != 'manual':
    errors.append(f"{detach_rel}: reason must stay 'manual' for verified-capture early detach example")
runtime = detach.get('runtime') or {}
if runtime.get('backend') != 'host-local-removable-ingest':
    errors.append(f"{detach_rel}: runtime.backend must stay 'host-local-removable-ingest'")
mapping = runtime.get('mapping') or {}
for key, value in {
    'selected_provider': '/dev/da0s1',
    'detached_mount_posture': 'detach-after-verified-capture-before-later-ops',
    'detach_trigger': 'selected-subject-capture-verified',
    'later_ops_dependency': 'no-device-presence-required-after-detach',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

for token in (
    'device.detach.receipt',
    'after capture verification',
    'before later operations continued',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md': ['device.detach.receipt', 'before later classify/scan/sanitize work continues', 'must not require continued medium presence'],
    'docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md': ['emit `device.detach.receipt` before later classify/scan/sanitize work continues', 'Later ops must stay device-independent', 'device to remain present'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['detach-early cut is explicit too', 'emit `device.detach.receipt` before later classify/scan/sanitize work continues'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['detach-early cut is fixed too', 'spec/examples/device.detach.receipt.removable-media-local-ingest.json'],
    'docs/410-desktop-viability-checklist.md': ['detach-early cut is fixed too', 'docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['detach-early cut is fixed too', 'device.detach.receipt before later classify/scan/sanitize work continues'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['verified capture lets the host end the medium session early', 'device.detach.receipt'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md'],
    'docs/110-juicy-os-lessons.md': ['after capture verification, end the removable-medium session before later ops continue', 'docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_early_detach.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_early_detach.py'],
    'docs/00-index.md': ['docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md', 'check_removable_media_local_early_detach.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback early-detach check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback early-detach check passed')
