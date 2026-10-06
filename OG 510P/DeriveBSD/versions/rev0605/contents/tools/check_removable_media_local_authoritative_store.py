#!/usr/bin/env python3
"""Guardrail for removable-media local-fallback authoritative preserved-capture store posture."""
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
    'captured_subject_authority_posture': 'commit-to-authoritative-quarantine-store-before-detach',
    'captured_subject_locator_posture': 'digest-addressed-store-locator-required',
    'post_detach_capture_consumption_posture': 'later-ops-read-readonly-store-projection',
}.items():
    if constraints.get(key) != value:
        errors.append(f'{grant_rel}: constraints.{key} must stay {value}')
for token in (
    'commit into authoritative quarantine store before detach',
    'read a read-only projection of the stored preserved capture',
    'authoritative quarantine store',
):
    if token not in (constraints.get('notes') or ''):
        errors.append(f'{grant_rel}: constraints.notes missing {token!r}')

ops = plan.get('operations') or []
if not ops or ops[0].get('op') != 'capture':
    errors.append(f'{plan_rel}: first operation must stay capture')
else:
    params = ops[0].get('params') or {}
    for key, value in {
        'captured_subject_authority_posture': 'commit-to-authoritative-quarantine-store-before-detach',
        'captured_subject_locator_posture': 'digest-addressed-store-locator-required',
        'post_detach_capture_consumption_posture': 'later-ops-read-readonly-store-projection',
        'post_detach_capture_projection_path': '/work/input/preserved-subject.bin',
    }.items():
        if params.get(key) != value:
            errors.append(f'{plan_rel}: capture params.{key} must stay {value}')
    if params.get('destination_path') != '/work/stage/subject.bin':
        errors.append(f"{plan_rel}: capture params.destination_path must stay '/work/stage/subject.bin'")
for idx, name in [(1, 'classify'), (2, 'scan'), (3, 'sanitize')]:
    if (ops[idx].get('params') or {}).get('input_path') != '/work/input/preserved-subject.bin':
        errors.append(f"{plan_rel}: {name} params.input_path must stay '/work/input/preserved-subject.bin'")
for token in (
    'commit into authoritative quarantine store before detach',
    'read a read-only projection of the stored preserved capture',
    'authoritative quarantine store',
):
    if token not in (plan.get('notes') or ''):
        errors.append(f'{plan_rel}: notes missing {token!r}')

mapping = (detach.get('runtime') or {}).get('mapping') or {}
for key, value in {
    'captured_subject_authority_posture': 'committed-to-authoritative-quarantine-store-before-detach',
    'captured_subject_locator_kind': 'digest-addressed-store',
    'post_detach_capture_consumption_posture': 'later-ops-read-readonly-store-projection',
    'post_detach_capture_projection_path': '/work/input/preserved-subject.bin',
}.items():
    if mapping.get(key) != value:
        errors.append(f'{detach_rel}: runtime.mapping.{key} must stay {value}')

outputs = receipt.get('outputs') or []
subject_digest = ((receipt.get('subject') or {}).get('digest'))
cap = next((o for o in outputs if o.get('role') == 'captured-subject'), None)
san = next((o for o in outputs if o.get('role') == 'sanitized-derivative'), None)
if cap is None:
    errors.append(f'{receipt_rel}: outputs must include role=captured-subject')
else:
    if cap.get('digest') != subject_digest:
        errors.append(f'{receipt_rel}: captured-subject digest must match subject.digest')
    if cap.get('locator_kind') != 'digest-addressed-store':
        errors.append(f"{receipt_rel}: captured-subject locator_kind must stay 'digest-addressed-store'")
    if cap.get('locator') != f'cas:{subject_digest}':
        errors.append(f'{receipt_rel}: captured-subject locator must stay cas:<subject.digest>')
    if cap.get('projection_path') != '/work/input/preserved-subject.bin':
        errors.append(f"{receipt_rel}: captured-subject projection_path must stay '/work/input/preserved-subject.bin'")
    if cap.get('path') == '/work/capture/subject.bin':
        errors.append(f'{receipt_rel}: captured-subject path may not stay disposable /work/capture authority')
if san is None:
    errors.append(f'{receipt_rel}: outputs must include role=sanitized-derivative')
else:
    if san.get('source_digest') != subject_digest:
        errors.append(f'{receipt_rel}: sanitized-derivative source_digest must match subject.digest')

if 'authoritative-store-before-detach' not in ((receipt.get('result') or {}).get('message') or ''):
    errors.append(f"{receipt_rel}: result.message must mention 'authoritative-store-before-detach'")
for token in (
    'committed into authoritative quarantine store before device detach',
    'read-only projection of that stored copy',
    'authoritative quarantine store',
):
    if token not in ((receipt.get('metadata') or {}).get('notes') or ''):
        errors.append(f'{receipt_rel}: metadata.notes missing {token!r}')

DOC_TOKENS = {
    'adrs/ADR-0328-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md': ['commit into authoritative quarantine store before detach', 'read the stored preserved capture', 'scratch'],
    'docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md': ['authoritative quarantine store', 'read-only projection', 'scratch'],
    'docs/279-usb-quarantine-and-removable-media-workflow.md': ['authoritative-store cut is explicit too', 'read a read-only projection of the stored preserved capture'],
    'docs/278-device-grants-and-devfs-rulesets.md': ['authoritative-store cut is fixed too', 'docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md'],
    'docs/410-desktop-viability-checklist.md': ['authoritative-store cut is fixed too', 'docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md'],
    'docs/458-removable-media-and-usb-posture-by-profile.md': ['authoritative-store cut is fixed too', 'authoritative quarantine store before detach'],
    'docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md': ['authoritative quarantine store before detach', 'read a read-only projection of the stored preserved capture'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0328-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md'],
    'docs/110-juicy-os-lessons.md': ['commit the verified capture into authoritative quarantine store before detach', 'read a read-only projection of the stored preserved capture'],
    'docs/98-archive-hygiene.md': ['check_removable_media_local_authoritative_store.py'],
    'docs/99-llm-runbook.md': ['check_removable_media_local_authoritative_store.py'],
    'docs/00-index.md': ['docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md', 'check_removable_media_local_authoritative_store.py'],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('removable-media local-fallback authoritative-store check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)
print('removable-media local-fallback authoritative-store check passed')
