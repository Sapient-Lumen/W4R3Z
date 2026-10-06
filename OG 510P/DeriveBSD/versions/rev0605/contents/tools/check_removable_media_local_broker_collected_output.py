#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback broker-collected post-detach derivative egress."""
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
    'post_detach_derivative_output_posture': 'launcher-precreated-writable-sink-or-equivalent',
    'post_detach_derivative_collection_posture': 'broker-collected-remeasured-before-receipt',
    'post_detach_derivative_namespace_posture': 'no-authoritative-store-write-or-browse-in-worker',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'Any receipt-visible derivative output must leave through launcher-precreated disposable sink objects',
    'worker outbox path remains non-authoritative execution plumbing',
    'collect + remeasure those bytes before the receipt names an authoritative derivative locator',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'post_detach_derivative_output_posture': 'launcher-precreated-writable-sink-or-equivalent',
        'post_detach_derivative_collection_posture': 'broker-collected-remeasured-before-receipt',
        'post_detach_derivative_namespace_posture': 'no-authoritative-store-write-or-browse-in-worker',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
if len(ops) < 4 or ops[3].get('op') != 'sanitize':
    errors.append(f'{plan_rel}: fourth operation must stay sanitize for the canonical example')
else:
    params = ops[3].get('params') or {}
    for key, value in {
        'output_path': '/work/output/invoice.sanitized.pdf',
        'output_posture': 'launcher-precreated-writable-sink-or-equivalent',
        'output_authority_posture': 'worker-outbox-path-not-authoritative',
        'output_collection_posture': 'broker-collects-and-remeasures-before-receipt',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: sanitize params.{key} must stay {value}')
for token in (
    'Later-worker derivative bytes must leave through launcher-precreated disposable outbox sink objects',
    '`/work/output/...` stays execution plumbing rather than authoritative derivative identity',
    'collect + remeasure those bytes before the canonical receipt names the derivative authoritatively',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'post_detach_derivative_output_path': '/work/output/invoice.sanitized.pdf',
    'post_detach_derivative_output_posture': 'launcher-precreated-writable-sink-or-equivalent',
    'post_detach_derivative_collection_posture': 'broker-collected-remeasured-before-receipt',
    'post_detach_derivative_namespace_posture': 'no-authoritative-store-write-or-browse-in-worker',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

outputs = receipt.get('outputs') or []
deriv = next((o for o in outputs if o.get('role') == 'sanitized-derivative'), None)
if deriv is None:
    errors.append(f'{receipt_rel}: outputs must include role=sanitized-derivative')
else:
    for key, value in {
        'path': '/var/derive/quarantine/store/sha256/93/9393939393939393939393939393939393939393939393939393939393939393',
        'locator_kind': 'digest-addressed-store',
        'locator': 'cas:sha256:9393939393939393939393939393939393939393939393939393939393939393',
        'locator_visibility': 'receipt-only-not-worker-visible',
        'worker_output_path': '/work/output/invoice.sanitized.pdf',
        'worker_output_authority_posture': 'disposable-outbox-path-not-authoritative',
        'delivery_posture': 'launcher-precreated-writable-sink-or-equivalent',
        'collection_posture': 'broker-collected-remeasured-before-receipt',
    }.items():
        if deriv.get(key) != value:
            errors.append(f'{receipt_rel}: sanitized-derivative {key} must stay {value}')
if 'broker-collected-derivative-outbox' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'broker-collected-derivative-outbox'")
for token in (
    'launcher-precreated disposable outbox sink at /work/output/invoice.sanitized.pdf',
    'worker path remained non-authoritative execution plumbing',
    'collected + remeasured those bytes before this receipt named the separate authoritative derivative locator',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

entries = preopen.get('entries') or []
input_entry = next((e for e in entries if e.get('entry_id') == 'preserved_subject_ro'), None)
out_entry = next((e for e in entries if e.get('entry_id') == 'sanitized_derivative_sink'), None)
if input_entry is None:
    errors.append(f'{preopen_rel}: entries must include preserved_subject_ro')
else:
    if input_entry.get('path') != '/work/input/preserved-subject.bin':
        errors.append(f"{preopen_rel}: preserved_subject_ro path must stay '/work/input/preserved-subject.bin'")
    if input_entry.get('rights') != ['CAP_READ', 'CAP_FSTAT', 'CAP_SEEK', 'CAP_MMAP_R']:
        errors.append(f'{preopen_rel}: preserved_subject_ro rights must stay read-only input rights')
if out_entry is None:
    errors.append(f'{preopen_rel}: entries must include sanitized_derivative_sink')
else:
    if out_entry.get('path') != '/work/output/invoice.sanitized.pdf':
        errors.append(f"{preopen_rel}: sanitized_derivative_sink path must stay '/work/output/invoice.sanitized.pdf'")
    rights = out_entry.get('rights') or []
    for needed in ('CAP_WRITE', 'CAP_FSTAT'):
        if needed not in rights:
            errors.append(f'{preopen_rel}: sanitized_derivative_sink rights must include {needed}')
    for forbidden in ('CAP_READ', 'CAP_FTRUNCATE'):
        if forbidden in rights:
            errors.append(f'{preopen_rel}: sanitized_derivative_sink rights must omit {forbidden}')
if any(e.get('kind') == 'dir' for e in entries):
    errors.append(f'{preopen_rel}: later-worker map must not grant directory authority in this first cut')
for token in (
    'does not grant any authoritative-store directory preopen',
    'Receipt-visible derivative egress leaves only through launcher-precreated disposable sink files',
    'worker outbox paths are not authoritative derivative identity',
):
    if not any(token in note for note in (preopen.get('notes') or [])):
        errors.append(f'{preopen_rel}: notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0332-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md': ['broker-collected', 'worker-visible outbox path is not the authoritative identity of the derivative', 'authoritative derivative locator'],
    'docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md': ['broker-collected and worker outbox paths stay non-authoritative', 'launcher-prepared disposable sink objects', 'outbox path is not the authoritative identity of the derivative'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['broker-collected derivative-egress cut is explicit too', 'launcher/broker must collect + remeasure those bytes before the canonical receipt names the derivative authoritatively'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['broker-collected derivative-egress cut is fixed too', 'docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md'],
    'docs/410-desktop-viability-checklist.md': ['broker-collected derivative-egress cut is fixed too', 'stays non-authoritative execution plumbing'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['broker-collected derivative-egress cut is fixed too', 'worker outbox paths stay non-authoritative'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['later worker derivative bytes leave only through launcher-prepared disposable sink objects', 'launcher/broker collects + remeasures those bytes'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0332-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md'],
    'docs/110-juicy-os-lessons.md': ['keep later-worker derivative output on launcher-prepared disposable sink objects', 'before any `/work/output/...` path becomes receipt authority'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_broker_collected_output.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_broker_collected_output.py'],
    'docs/00-index.md': ['docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md', 'check_removable_media_local_broker_collected_output.py'],
    'docs/32-curated-references.md': ['rights(4): https://man.freebsd.org/cgi/man.cgi?query=rights&sektion=4'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback broker-collected derivative-output check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback broker-collected derivative-output check passed')
