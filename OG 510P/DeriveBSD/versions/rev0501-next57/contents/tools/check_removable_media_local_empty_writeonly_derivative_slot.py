#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback empty write-only post-detach derivative slot."""
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
    'post_detach_derivative_slot_initialization_posture': 'launcher-precreated-empty-regular-file',
    'post_detach_derivative_slot_io_posture': 'append-open-no-readback-no-truncate',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'launcher-precreated empty regular file',
    'omits CAP_READ/CAP_FTRUNCATE/CAP_FCNTL',
    'no worker readback or truncate',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if len(ops) < 4 or ops[3].get('op') != 'sanitize':
    errors.append(f'{plan_rel}: fourth operation must stay sanitize for the canonical example')
else:
    params = ops[3].get('params') or {}
    for key, value in {
        'output_slot_initialization_posture': 'launcher-precreated-empty-regular-file',
        'output_slot_io_posture': 'append-open-no-readback-no-truncate',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: sanitize params.{key} must stay {value}')
for token in (
    'launcher-precreated empty regular file',
    'omits CAP_READ/CAP_FTRUNCATE/CAP_FCNTL',
    'no worker readback or truncate',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_derivative_slot_initialization_posture': 'launcher-precreated-empty-regular-file',
    'post_detach_derivative_slot_io_posture': 'append-open-no-readback-no-truncate',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

outputs = receipt.get('outputs') or []
deriv = next((o for o in outputs if o.get('role') == 'sanitized-derivative'), None)
if deriv is None:
    errors.append(f'{receipt_rel}: outputs must include role=sanitized-derivative')
else:
    for key, value in {
        'worker_output_initialization_posture': 'launcher-precreated-empty-regular-file',
        'worker_output_io_posture': 'append-open-no-readback-no-truncate',
    }.items():
        if deriv.get(key) != value:
            errors.append(f'{receipt_rel}: sanitized-derivative {key} must stay {value}')
if 'empty-writeonly-derivative-slot' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'empty-writeonly-derivative-slot'")
for token in (
    'launcher-precreated empty regular file',
    'omitted CAP_READ/CAP_FTRUNCATE/CAP_FCNTL',
    'no worker readback or truncate',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

entries = preopen.get('entries') or []
out_entries = [e for e in entries if e.get('entry_id') == 'sanitized_derivative_sink']
if len(out_entries) != 1:
    errors.append(f'{preopen_rel}: later-worker map must keep exactly one sanitized_derivative_sink entry')
else:
    out_entry = out_entries[0]
    rights = out_entry.get('rights') or []
    for needed in ('CAP_WRITE', 'CAP_FSTAT'):
        if needed not in rights:
            errors.append(f"{preopen_rel}: writable sink rights must include {needed}")
    forbidden = {'CAP_READ', 'CAP_FTRUNCATE', 'CAP_FCNTL'}
    if forbidden & set(rights):
        errors.append(f'{preopen_rel}: writable sink must omit CAP_READ/CAP_FTRUNCATE/CAP_FCNTL')
    for tag in ('write-only', 'forward-only'):
        if tag not in (out_entry.get('risk_tags') or []):
            errors.append(f'{preopen_rel}: writable sink risk_tags must include {tag!r}')
for token in (
    'launcher-precreated empty regular file',
    'no CAP_READ, CAP_FTRUNCATE, or CAP_FCNTL',
    'no worker readback or truncate',
):
    if not any(token in note for note in (preopen.get('notes') or [])):
        errors.append(f'{preopen_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0334-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md': ['empty regular file', 'no readback or truncate', 'CAP_READ', 'CAP_FTRUNCATE'],
    'docs/744-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md': ['starts empty write-only and no readback or truncate', 'launcher-precreated empty regular file', 'readback and truncate stay out'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['The next empty-write-only-slot cut is explicit too', 'launcher-precreated empty regular file'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['The next empty-write-only-slot cut is fixed too', 'keeps worker readback/truncate out'],
    'docs/410-desktop-viability-checklist.md': ['The next empty-write-only-slot cut is fixed too', 'keeps worker readback/truncate out'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['The next empty-write-only-slot cut is fixed too', 'launcher-precreated empty regular file'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['one declared launcher-prepared empty sink slot', 'no readback or truncate'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0334-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md'],
    'docs/110-juicy-os-lessons.md': ['empty declared derivative slot', 'keep worker readback/truncate out'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_empty_writeonly_derivative_slot.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_empty_writeonly_derivative_slot.py'],
    'docs/00-index.md': ['docs/744-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md', 'check_removable_media_local_empty_writeonly_derivative_slot.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback empty-writeonly-derivative-slot check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback empty-writeonly-derivative-slot check passed')
