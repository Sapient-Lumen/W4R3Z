#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback append-open post-detach derivative slot."""
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

APPEND_POSTURE = {
    'posture_io': 'append-open-no-readback-no-truncate',
    'open': 'launcher-preopened-o_append-no-worker-reopen',
    'append_protection': 'append-only-protected-during-worker-execution',
    'seek': 'cap-seek-ballast-on-seekable-file-not-rewrite-authority',
}

constraints = grant.get('constraints') or {}
for key, value in {
    'post_detach_derivative_slot_io_posture': APPEND_POSTURE['posture_io'],
    'post_detach_derivative_slot_open_posture': APPEND_POSTURE['open'],
    'post_detach_derivative_slot_append_protection_posture': APPEND_POSTURE['append_protection'],
    'post_detach_derivative_slot_seek_posture': APPEND_POSTURE['seek'],
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'already opened O_APPEND',
    'append-only-protected while the worker runs',
    'omits CAP_READ/CAP_FTRUNCATE/CAP_FCNTL',
    'CAP_SEEK on that seekable file as implementation ballast',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_derivative_slot_io_posture': APPEND_POSTURE['posture_io'],
        'post_detach_derivative_slot_open_posture': APPEND_POSTURE['open'],
        'post_detach_derivative_slot_append_protection_posture': APPEND_POSTURE['append_protection'],
        'post_detach_derivative_slot_seek_posture': APPEND_POSTURE['seek'],
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
if len(ops) < 4 or ops[3].get('op') != 'sanitize':
    errors.append(f'{plan_rel}: fourth operation must stay sanitize for the canonical example')
else:
    params = ops[3].get('params') or {}
    for key, value in {
        'output_slot_io_posture': APPEND_POSTURE['posture_io'],
        'output_slot_open_posture': APPEND_POSTURE['open'],
        'output_slot_append_protection_posture': APPEND_POSTURE['append_protection'],
        'output_slot_seek_posture': APPEND_POSTURE['seek'],
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: sanitize params.{key} must stay {value}')
for token in (
    'already opened O_APPEND',
    'append-only-protected while the worker runs',
    'omits CAP_READ/CAP_FTRUNCATE/CAP_FCNTL',
    'CAP_SEEK on that seekable file as implementation ballast',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_derivative_slot_io_posture': APPEND_POSTURE['posture_io'],
    'post_detach_derivative_slot_open_posture': APPEND_POSTURE['open'],
    'post_detach_derivative_slot_append_protection_posture': APPEND_POSTURE['append_protection'],
    'post_detach_derivative_slot_seek_posture': APPEND_POSTURE['seek'],
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

outputs = receipt.get('outputs') or []
deriv = next((o for o in outputs if o.get('role') == 'sanitized-derivative'), None)
if deriv is None:
    errors.append(f'{receipt_rel}: outputs must include role=sanitized-derivative')
else:
    for key, value in {
        'worker_output_io_posture': APPEND_POSTURE['posture_io'],
        'worker_output_open_posture': APPEND_POSTURE['open'],
        'worker_output_append_protection_posture': APPEND_POSTURE['append_protection'],
        'worker_output_seek_posture': APPEND_POSTURE['seek'],
    }.items():
        if deriv.get(key) != value:
            errors.append(f'{receipt_rel}: sanitized-derivative {key} must stay {value}')
if 'append-open-derivative-slot' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'append-open-derivative-slot'")
for token in (
    'already opened O_APPEND',
    'append-only-protected while the worker ran',
    'omitted CAP_READ/CAP_FTRUNCATE/CAP_FCNTL',
    'CAP_SEEK on that seekable file as implementation ballast',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

entries = preopen.get('entries') or []
out_entry = next((e for e in entries if e.get('entry_id') == 'sanitized_derivative_sink'), None)
if out_entry is None:
    errors.append(f'{preopen_rel}: entries must include sanitized_derivative_sink')
else:
    rights = out_entry.get('rights') or []
    for needed in ('CAP_WRITE', 'CAP_FSTAT', 'CAP_SEEK'):
        if needed not in rights:
            errors.append(f'{preopen_rel}: sanitized_derivative_sink rights must include {needed}')
    for forbidden in ('CAP_READ', 'CAP_FTRUNCATE', 'CAP_FCNTL'):
        if forbidden in rights:
            errors.append(f'{preopen_rel}: sanitized_derivative_sink rights must omit {forbidden}')
    for tag in ('append-open', 'append-only-protected', 'seek-ballast'):
        if tag not in (out_entry.get('risk_tags') or []):
            errors.append(f'{preopen_rel}: sanitized_derivative_sink risk_tags must include {tag!r}')
    if 'already opened O_APPEND' not in (out_entry.get('intent') or '') and 'handed over O_APPEND' not in (out_entry.get('intent') or ''):
        errors.append(f'{preopen_rel}: sanitized_derivative_sink intent must mention O_APPEND handoff')
for token in (
    'handed to the worker already opened O_APPEND',
    'no CAP_READ, CAP_FTRUNCATE, or CAP_FCNTL',
    'CAP_SEEK appears only as seekable-file ballast',
    'sink stays append-only-protected while the worker runs',
):
    if not any(token in note for note in (preopen.get('notes') or [])):
        errors.append(f'{preopen_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0335-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md': [
        'append-open and append-only-protected on seekable file delivery',
        'append-only-protected while the worker runs',
        'CAP_SEEK',
    ],
    'docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md': [
        'append-open and append-only-protected on seekable file delivery',
        '`O_APPEND`',
        'append-only-protected while the worker runs',
        'any `CAP_SEEK` on that sink is seekable-file ballast',
    ],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': [
        'The next append-open-derivative-slot cut is explicit too',
        '`O_APPEND`',
        'append-only-protected while the worker runs',
    ],
    'docs/278-device-grants-and-devfs-rulesets.md': [
        'The next append-open-derivative-slot cut is fixed too',
        '`O_APPEND`',
    ],
    'docs/410-desktop-viability-checklist.md': [
        'The next append-open-derivative-slot cut is fixed too',
        '`O_APPEND`',
    ],
    'docs/458-removable-media-and-usb-posture-by-profile.md': [
        'The next append-open-derivative-slot cut is fixed too',
        'append-only-protected while the worker runs',
    ],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': [
        'append-open and append-only-protected',
        '`CAP_SEEK` remains ballast rather than rewrite authority',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'ADR-0335-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md',
    ],
    'docs/110-juicy-os-lessons.md': [
        'handed over `O_APPEND`',
        'append-only-protected while the worker runs',
    ],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_append_open_derivative_slot.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_append_open_derivative_slot.py'],
    'docs/00-index.md': [
        'docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md',
        'check_removable_media_local_append_open_derivative_slot.py',
    ],
    'docs/32-curated-references.md': [
        'cap_rights_init(3): https://man.freebsd.org/cgi/man.cgi?query=cap_rights_init&sektion=3',
        'open(2): https://man.freebsd.org/cgi/man.cgi?query=open&sektion=2',
        'chflags(2): https://man.freebsd.org/cgi/man.cgi?query=chflags&sektion=2',
    ],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback append-open-derivative-slot check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback append-open-derivative-slot check passed')
