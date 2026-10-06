#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback preopened post-detach delivery posture."""
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
preopen_rel = 'spec/examples/preopen.map.removable-media-local-ingest-post-detach.json'

grant = load_json(grant_rel)
plan = load_json(plan_rel)
detach = load_json(detach_rel)
receipt = load_json(receipt_rel)
preopen = load_json(preopen_rel)

constraints = grant.get('constraints') or {}
for key, value in {
    'post_detach_projection_delivery_posture': 'launcher-preopened-readonly-object-or-equivalent-before-later-ops',
    'post_detach_projection_reopen_posture': 'no-worker-path-reopen-or-store-rebind',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'later delivery stays launcher-preopened read-only',
    'worker-visible path is compatibility-only plumbing',
    'must not reopen the preserved subject through broader path or store lookup',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_projection_delivery_posture': 'launcher-preopened-readonly-object-or-equivalent-before-later-ops',
        'post_detach_projection_reopen_posture': 'no-worker-path-reopen-or-store-rebind',
        'post_detach_capture_projection_path': '/work/input/preserved-subject.bin',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
for token in (
    'launcher/broker must prepare it as one launcher-preopened read-only object',
    'later operations must not reacquire the subject through broader path or store lookup',
    'worker-visible projection path is only plumbing',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_projection_delivery_posture': 'launcher-preopened-readonly-object-or-equivalent-before-later-ops',
    'post_detach_projection_reopen_posture': 'no-worker-path-reopen-or-store-rebind',
    'post_detach_capture_projection_path': '/work/input/preserved-subject.bin',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

outputs = receipt.get('outputs') or []
cap = next((o for o in outputs if o.get('role') == 'captured-subject'), None)
if cap is None:
    errors.append(f'{receipt_rel}: outputs must include role=captured-subject')
else:
    for key, value in {
        'projection_path': '/work/input/preserved-subject.bin',
        'projection_delivery_posture': 'launcher-preopened-readonly-object-or-equivalent-before-later-ops',
        'projection_reopen_posture': 'no-worker-path-reopen-or-store-rebind',
    }.items():
        if cap.get(key) != value:
            errors.append(f'{receipt_rel}: captured-subject {key} must stay {value}')

if 'preopened-readonly-delivery' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'preopened-readonly-delivery'")
for token in (
    'launcher/broker prepared it as one launcher-preopened read-only object',
    'later worker did not reacquire the subject through broader path or store lookup',
    'synthetic worker-visible delivery',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

entries = preopen.get('entries') or []
input_entry = next((e for e in entries if e.get('entry_id') == 'preserved_subject_ro'), None)
if input_entry is None:
    errors.append(f'{preopen_rel}: entries must include preserved_subject_ro')
else:
    expected_rights = ['CAP_READ', 'CAP_FSTAT', 'CAP_SEEK', 'CAP_MMAP_R']
    if input_entry.get('kind') != 'file':
        errors.append(f'{preopen_rel}: preserved_subject_ro kind must stay file')
    if input_entry.get('path') != '/work/input/preserved-subject.bin':
        errors.append(f"{preopen_rel}: preserved_subject_ro path must stay '/work/input/preserved-subject.bin'")
    if input_entry.get('rights') != expected_rights:
        errors.append(f'{preopen_rel}: preserved_subject_ro rights must stay {expected_rights}')
for token in (
    'does not grant any authoritative-store directory preopen',
    'worker-visible input path is compatibility-only plumbing',
    'Path re-open, store rebinding',
):
    if not any(token in note for note in (preopen.get('notes') or [])):
        errors.append(f'{preopen_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0331-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md': ['launcher-preopened read-only', 'path re-open stays out', 'worker-visible path is compatibility-only'],
    'docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md': ['launcher-preopened read-only and path re-open stays out', 'worker-visible path is compatibility-only plumbing', 'tiny `preopen.map`'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['launcher-preopened delivery cut is explicit too', 'worker may not reacquire the subject through broader path or authoritative-store lookup'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['launcher-preopened delivery cut is fixed too', 'docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md'],
    'docs/410-desktop-viability-checklist.md': ['launcher-preopened delivery cut is fixed too', 'worker path stays compatibility-only plumbing'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['launcher-preopened delivery cut is fixed too', 'later worker may not reacquire the subject through broader path or authoritative-store lookup'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['launcher-preopened read-only (or equivalent)', 'does not reacquire the subject through broader path or store lookup'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0331-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md'],
    'docs/110-juicy-os-lessons.md': ['keep execution on one launcher-preopened read-only object', 'worker may reopen for authority'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_preopened_delivery.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_preopened_delivery.py'],
    'docs/00-index.md': ['docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md', 'check_removable_media_local_preopened_delivery.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback preopened-delivery check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback preopened-delivery check passed')
