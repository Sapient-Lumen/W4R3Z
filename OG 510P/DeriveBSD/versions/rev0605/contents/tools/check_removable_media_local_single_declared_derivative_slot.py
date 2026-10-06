#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback single declared post-detach derivative slot."""
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
    'post_detach_derivative_slot_scope': 'single-declared-derivative-slot-only-first-cut',
    'post_detach_derivative_slot_binding_posture': 'receipt-visible-derivative-must-come-from-declared-slot',
    'post_detach_derivative_extra_surface_posture': 'no-extra-worker-result-surface-in-this-lane',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'first lane admits only one declared writable derivative slot',
    'extra worker result surface stays out',
    'collect + remeasure the bytes from that declared slot',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_derivative_slot_scope': 'single-declared-derivative-slot-only-first-cut',
        'post_detach_derivative_slot_binding_posture': 'receipt-visible-derivative-must-come-from-declared-slot',
        'post_detach_derivative_extra_surface_posture': 'no-extra-worker-result-surface-in-this-lane',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
if len(ops) < 4 or ops[3].get('op') != 'sanitize':
    errors.append(f'{plan_rel}: fourth operation must stay sanitize for the canonical example')
else:
    params = ops[3].get('params') or {}
    for key, value in {
        'output_path': '/work/output/invoice.sanitized.pdf',
        'output_slot_id': 'sanitized_derivative_slot',
        'output_slot_scope': 'single-declared-derivative-slot-only-first-cut',
        'output_extra_surface_posture': 'out-of-lane-fail-closed',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: sanitize params.{key} must stay {value}')
for token in (
    'first lane admits only one declared writable derivative slot',
    'extra worker result surface stays out',
    'collect + remeasure the bytes from that declared slot',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_derivative_output_path': '/work/output/invoice.sanitized.pdf',
    'post_detach_derivative_slot_id': 'sanitized_derivative_slot',
    'post_detach_derivative_slot_scope': 'single-declared-derivative-slot-only-first-cut',
    'post_detach_derivative_extra_surface_posture': 'no-extra-worker-result-surface-in-this-lane',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

outputs = receipt.get('outputs') or []
deriv = next((o for o in outputs if o.get('role') == 'sanitized-derivative'), None)
if deriv is None:
    errors.append(f'{receipt_rel}: outputs must include role=sanitized-derivative')
else:
    for key, value in {
        'worker_output_path': '/work/output/invoice.sanitized.pdf',
        'worker_output_slot_id': 'sanitized_derivative_slot',
        'worker_output_slot_scope': 'single-declared-derivative-slot-only-first-cut',
        'worker_output_extra_surface_posture': 'no-extra-worker-result-surface-in-this-lane',
    }.items():
        if deriv.get(key) != value:
            errors.append(f'{receipt_rel}: sanitized-derivative {key} must stay {value}')
if 'single-declared-derivative-slot' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'single-declared-derivative-slot'")
for token in (
    'one declared launcher-precreated disposable outbox sink slot',
    'extra worker result surface stayed out in this lane',
    'collected + remeasured the bytes from that declared slot',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

entries = preopen.get('entries') or []
out_entries = [e for e in entries if 'CAP_WRITE' in (e.get('rights') or [])]
if len(out_entries) != 1:
    errors.append(f'{preopen_rel}: later-worker map must keep exactly one writable derivative sink entry')
else:
    out_entry = out_entries[0]
    if out_entry.get('entry_id') != 'sanitized_derivative_sink':
        errors.append(f"{preopen_rel}: writable sink entry_id must stay 'sanitized_derivative_sink'")
    if out_entry.get('path') != '/work/output/invoice.sanitized.pdf':
        errors.append(f"{preopen_rel}: writable sink path must stay '/work/output/invoice.sanitized.pdf'")
    if 'declared-slot' not in (out_entry.get('risk_tags') or []):
        errors.append(f'{preopen_rel}: writable sink risk_tags must include declared-slot')
for token in (
    'one declared launcher-precreated disposable sink file',
    'exactly one declared writable derivative sink slot',
):
    if not any(token in note for note in (preopen.get('notes') or [])):
        errors.append(f'{preopen_rel}: notes missing {token!r}')
if any(e.get('kind') == 'dir' for e in entries):
    errors.append(f'{preopen_rel}: later-worker map must not grant directory authority in this first cut')

DOC_TOKENS = {
    'adrs/ADR-0333-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md': ['single declared slot', 'extra worker result surface stays out', 'plural authoritative outputs'],
    'docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md': ['single declared slot and no extra worker result surface', 'one declared writable derivative slot', 'extra worker result surface stays out'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['The next single-declared-slot cut is explicit too', 'later worker now gets only one declared writable derivative slot'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['The next single-declared-slot cut is fixed too', 'docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md'],
    'docs/410-desktop-viability-checklist.md': ['The next single-declared-slot cut is fixed too', 'extra worker result surface stays out in the first lane'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['The next single-declared-slot cut is fixed too', 'later output surface now stays on one declared writable derivative slot'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['one declared launcher-prepared disposable sink slot', 'collect + remeasure the bytes from that declared slot'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0333-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md'],
    'docs/110-juicy-os-lessons.md': ['one declared writable sink slot only', 'extra worker result surface fail closed'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_single_declared_derivative_slot.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_single_declared_derivative_slot.py'],
    'docs/00-index.md': ['docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md', 'check_removable_media_local_single_declared_derivative_slot.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback single-declared-derivative-slot check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback single-declared-derivative-slot check passed')
