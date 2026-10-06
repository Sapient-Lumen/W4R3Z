#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback single-object post-detach projection posture."""
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
    'post_detach_capture_projection_scope': 'single-preserved-subject-only',
    'post_detach_authoritative_store_visibility': 'not-browseable-from-later-worker',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'single-object synthetic projection',
    'authoritative quarantine-store locator remains receipt-visible evidence',
    'may not browse the store namespace',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_capture_projection_scope': 'single-preserved-subject-only',
        'post_detach_authoritative_store_visibility': 'not-browseable-from-later-worker',
        'post_detach_capture_projection_path': '/work/input/preserved-subject.bin',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
for idx, name in [(1, 'classify'), (2, 'scan'), (3, 'sanitize')]:
    if (ops[idx].get('params') or {}).get('input_path') != '/work/input/preserved-subject.bin':
        errors.append(f"{plan_rel}: {name} params.input_path must stay '/work/input/preserved-subject.bin'")
for token in (
    'single-object synthetic projection path',
    'not through a browseable authoritative-store namespace',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_capture_projection_scope': 'single-preserved-subject-only',
    'post_detach_authoritative_store_visibility': 'not-browseable-from-later-worker',
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
        'projection_scope': 'single-preserved-subject-only',
        'locator_visibility': 'receipt-only-not-worker-visible',
    }.items():
        if cap.get(key) != value:
            errors.append(f'{receipt_rel}: captured-subject {key} must stay {value}')
    if cap.get('path', '').startswith('/work/'):
        errors.append(f'{receipt_rel}: captured-subject path must stay authoritative store, not /work scratch')

if 'single-object-projection' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'single-object-projection'")
for token in (
    'single-object synthetic projection',
    'receipt-visible evidence',
    'rather than worker-browseable namespace',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0329-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md': ['single-object only', 'authoritative store locator stays evidence', 'browseable authoritative-store directory/subtree view'],
    'docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md': ['single-object and store-opaque', 'synthetic worker-local single-object projection path', 'authoritative stored locator remains receipt-visible evidence'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['single-object projection cut is explicit too', 'must not receive a browseable authoritative-store mount'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['single-object projection cut is fixed too', 'docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md'],
    'docs/410-desktop-viability-checklist.md': ['single-object projection cut is fixed too', 'docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['single-object projection cut is fixed too', 'may not browse the authoritative quarantine-store namespace'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['single-object projection of the stored preserved capture', 'not a browseable authoritative-store subtree'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0329-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md'],
    'docs/110-juicy-os-lessons.md': ['hand later tools only one read-only preserved subject', 'not a browseable authoritative-store namespace'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_single_object_projection.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_single_object_projection.py'],
    'docs/00-index.md': ['docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md', 'check_removable_media_local_single_object_projection.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback single-object projection check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback single-object projection check passed')
